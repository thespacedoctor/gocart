#!/usr/bin/env python
# encoding: utf-8
"""
Documentation for gocart can be found here: http://gocart.readthedocs.org

Usage:
    gocart init
    gocart echo <daysAgo> [-s <pathToSettingsFile>]
    gocart listen [-s <pathToSettingsFile>]


Options:
    init                                   setup the gocart settings file for the first time
    echo <daysAgo>                         relisten to alerts from N <daysAgo> until now and then exit
    listen                                 reconnect to kafka stream and listen from where you left off (or from now on if connectiong for the first time).

    -h, --help                             show this help message
    -v, --version                          show version
    -s, --settings <pathToSettingsFile>    the settings file
    -t, --test                             test, only collect 1 map
"""
from subprocess import Popen, PIPE, STDOUT
from fundamentals import tools, times
from docopt import docopt
import pickle
import glob
import readline
import sys
import os
os.environ['TERM'] = 'vt100'


def tab_complete(text, state):
    return (glob.glob(text + '*') + [None])[state]


def main(arguments=None):
    """
    *The main function used when `cl_utils.py` is run as a single script from the cl, or when installed as a cl command*
    """
    # setup the command-line util settings
    su = tools(
        arguments=arguments,
        docString=__doc__,
        logLevel="WARNING",
        options_first=False,
        projectName="gocart",
        defaultSettingsFile=True
    )
    arguments, settings, log, dbConn = su.setup()

    # tab completion for raw_input
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(tab_complete)

    # UNPACK REMAINING CL ARGUMENTS USING `EXEC` TO SETUP THE VARIABLE NAMES
    # AUTOMATICALLY
    a = {}
    for arg, val in list(arguments.items()):
        if arg[0] == "-":
            varname = arg.replace("-", "") + "Flag"
        else:
            varname = arg.replace("<", "").replace(">", "")
        a[varname] = val
        log.debug('%s = %s' % (varname, val,))

    firstConnect = False
    if "gcn-kafka" in settings and (not settings["gcn-kafka"]["group_id"] or len(str(settings["gcn-kafka"]["group_id"])) < 7):

        from os.path import expanduser
        import uuid as pyuuid
        import re
        group_id = pyuuid.uuid1().int
        settings["gcn-kafka"]["group_id"] = group_id

        home = expanduser("~")
        filepath = home + "/.config/gocart/gocart.yaml"
        import codecs
        with codecs.open(filepath, encoding='utf-8', mode='r') as readFile:
            content = readFile.read()
            regex = re.compile(r'group_id\:.*')
            content = regex.sub(f"group_id: {group_id}", content, count=1)
        with codecs.open(filepath, encoding='utf-8', mode='w') as writeFile:
            writeFile.write(content)
        firstConnect = True
    elif "gcn-kafka" not in settings:
        return

    ## START LOGGING ##
    startTime = times.get_now_sql_datetime()
    log.info(
        '--- STARTING TO RUN THE cl_utils.py AT %s' %
        (startTime,))

    if a["init"]:
        from os.path import expanduser
        home = expanduser("~")
        filepath = home + "/.config/gocart/gocart.yaml"

        try:
            cmd = """open %(filepath)s""" % locals()
            p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        except:
            pass
        try:
            cmd = """start %(filepath)s""" % locals()
            p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        except:
            pass
        return

    topic = 'igwn.gwalert'

    if len(settings['gcn-kafka']['client_id']) < 6 or len(settings['gcn-kafka']['client_secret']) < 6:
        print("Please add your gcn-kafka client ID and secret to the gocart.yaml settings file.")
        return

    if a['listen'] or a['echo']:

        if a['listen']:
            verb = "Listening for"
        else:
            verb = "Echoing"

        parse_mock_events = settings["lvk"]["parse_mock_events"]
        parse_real_events = settings["lvk"]["parse_real_events"]
        # WHERE TO DOWNLOAD MAPS TO
        if "download_dir" in settings["lvk"] and settings["lvk"]["download_dir"]:
            download_dir = settings["lvk"]["download_dir"]
            # MAKE RELATIVE HOME PATH ABSOLUTE
            from os.path import expanduser
            home = expanduser("~")
            if download_dir == "~":
                download_dir = download_dir.replace("~", home)
        else:
            download_dir = "."

        mockDir = download_dir + "/mockevents/"
        evertDir = download_dir + "/superevents/"
        if parse_mock_events:
            print(f"{verb} Mockevents")
            if not os.path.exists(mockDir):
                os.makedirs(mockDir)
        if parse_real_events:
            print(f"{verb} Superevents")
            if not os.path.exists(evertDir):
                os.makedirs(evertDir)

    # CALL FUNCTIONS/OBJECTS
    if a['listen']:
        from gcn_kafka import Consumer
        from confluent_kafka import TopicPartition
        from gocart.parsers import lvk

        config = {
            'group.id': settings["gcn-kafka"]["group_id"],
            'enable.auto.commit': False,
            'auto.offset.reset': 'earliest'
        }

        consumer = Consumer(config=config, client_id=settings['gcn-kafka']['client_id'],
                            client_secret=settings['gcn-kafka']['client_secret'], domain='gcn.nasa.gov')
        consumer.subscribe([topic])

        stop = False
        test = 0
        more = True
        while not stop:
            # IF FISRT TIME CONNECTING THEN SKIP MESSAGES
            if firstConnect:
                count = 0
                print("Marking previous messages as read, this can take a few minutes ...")
                while more:
                    messages = consumer.consume(num_messages=300, timeout=10)

                    for message in messages:
                        count += 1
                        consumer.commit(message)
                    if not len(messages):
                        more = False

                firstConnect = False
                print(f"This is your first time using the listen command. gocart will now listen for all new incoming alerts (skipping the {count} previous alerts currently in this topic). If you stop listening and restart sometime later, gocart will immediately collect all alerts missed while off-line.")
            for message in consumer.consume(timeout=1):
                parser = lvk(
                    log=log,
                    record=message.value(),
                    settings=settings
                ).parse()
                consumer.commit(message)

    if a['echo'] and a['daysAgo']:
        # GET MESSAGES OCCURRING IN LAST N DAYS
        from gcn_kafka import Consumer
        from confluent_kafka import TopicPartition
        from gocart.parsers import lvk
        import datetime

        consumer = Consumer(client_id=settings['gcn-kafka']['client_id'],
                            client_secret=settings['gcn-kafka']['client_secret'], domain='gcn.nasa.gov')

        since_utc = datetime.datetime.now() - datetime.timedelta(days=float(a['daysAgo']))
        timestamp1 = int((since_utc).timestamp() * 1000)
        since_utc = since_utc.strftime("%Y-%m-%d %H:%M:%S")
        print(f"Echoing alerts since {since_utc} UTC")

        start = consumer.offsets_for_times(
            [TopicPartition(topic, 0, timestamp1)])

        consumer.assign(start)

        more = True
        while more:
            messages = consumer.consume(num_messages=1, timeout=10)
            for message in messages:
                parser = lvk(
                    log=log,
                    record=message.value(),
                    settings=settings
                ).parse()
            if not len(messages):
                more = False

    ## FINISH LOGGING ##
    endTime = times.get_now_sql_datetime()
    runningTime = times.calculate_time_difference(startTime, endTime)
    log.info('-- FINISHED ATTEMPT TO RUN THE cl_utils.py AT %s (RUNTIME: %s) --' %
             (endTime, runningTime, ))

    return


if __name__ == '__main__':
    main()
