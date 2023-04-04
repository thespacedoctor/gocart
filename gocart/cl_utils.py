#!/usr/bin/env python
# encoding: utf-8
"""
Documentation for gocart can be found here: http://gocart.readthedocs.org

Usage:
    gocart init
    gocart echo <daysAgo> [-s <pathToSettingsFile>]
    gocart [-t] listen [-s <pathToSettingsFile>]


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

    if "gcn-kafka" in settings and settings["gcn-kafka"]["group_id"] == "XXXX":

        import uuid as pyuuid
        group_id = pyuuid.uuid1().int
        settings["gcn-kafka"]["group_id"] = group_id

        from os.path import expanduser
        home = expanduser("~")
        filepath = home + "/.config/gocart/gocart.yaml"
        import codecs
        with codecs.open(filepath, encoding='utf-8', mode='r') as readFile:
            content = readFile.read().replace("group_id: XXXX", f"group_id: {group_id}")
        with codecs.open(filepath, encoding='utf-8', mode='w') as writeFile:
            writeFile.write(content)
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

    # CALL FUNCTIONS/OBJECTS
    if a['listen']:
        from gcn_kafka import Consumer
        from confluent_kafka import TopicPartition
        from gocart.parsers import lvk

        config = {'group.id': settings["gcn-kafka"]["group_id"],
                  'auto.offset.reset': 'earliest',
                  'enable.auto.commit': False}

        consumer = Consumer(config=config, client_id=settings['gcn-kafka']['client_id'],
                            client_secret=settings['gcn-kafka']['client_secret'], domain='gcn.nasa.gov')
        consumer.subscribe([topic])

        stop = False
        while not stop:
            for message in consumer.consume():

                parser = lvk(
                    log=log,
                    record=message.value(),
                    settings=settings
                ).parse()

                if a["testFlag"]:
                    stop = True

    if a['echo'] and a['daysAgo']:
        # GET MESSAGES OCCURRING IN LAST N DAYS
        from gcn_kafka import Consumer
        from confluent_kafka import TopicPartition
        from gocart.parsers import lvk
        import datetime

        consumer = Consumer(client_id=settings['gcn-kafka']['client_id'],
                            client_secret=settings['gcn-kafka']['client_secret'], domain='gcn.nasa.gov')

        nowInMicrosec = int((datetime.datetime.now()).timestamp() * 1000)
        timestamp1 = int((datetime.datetime.now() - datetime.timedelta(days=int(a['daysAgo']))).timestamp() * 1000)
        timestamp2 = nowInMicrosec - 3600000  # now minus 3 mins

        start = consumer.offsets_for_times(
            [TopicPartition(topic, 0, timestamp1)])
        end = consumer.offsets_for_times(
            [TopicPartition(topic, 0, timestamp2)])

        consumer.assign(start)
        for message in consumer.consume(end[0].offset - start[0].offset):
            parser = lvk(
                log=log,
                record=message.value(),
                settings=settings
            ).parse()

    ## FINISH LOGGING ##
    endTime = times.get_now_sql_datetime()
    runningTime = times.calculate_time_difference(startTime, endTime)
    log.info('-- FINISHED ATTEMPT TO RUN THE cl_utils.py AT %s (RUNTIME: %s) --' %
             (endTime, runningTime, ))

    return


if __name__ == '__main__':
    main()
