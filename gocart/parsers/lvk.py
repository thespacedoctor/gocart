#!/usr/bin/env python
# encoding: utf-8
"""
*Parse Ligo-Virgo-Kagra GCN Notices*

:Author:
    David Young

:Date Created:
    March 19, 2023
"""
from gocart.commonutils import generate_skymap_stats
from gocart.convert import ascii
from fundamentals import tools
from builtins import object
import sys
import os
os.environ['TERM'] = 'vt100'


class lvk(object):
    """
    *The LVK event parser*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary
        - ``record`` -- the kafka record to parse.

    **Usage:**

    To setup your logger and settings, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_).

    To parse LVK kafka alerts, use the following:

    ```python
    from gocart.parsers import lvk
    parser = lvk(
        log=log,
        record=record,
        settings=settings
    ).parse()
    ```

    """

    def __init__(
            self,
            log,
            record,
            settings=False,

    ):
        import json

        self.log = log
        log.debug("instansiating a new 'lvk' object")
        self.settings = settings
        self.record = json.loads(record)

        import inspect
        import yaml
        # COLLECT ADVANCED SETTINGS IF AVAILABLE
        parentDirectory = os.path.dirname(__file__)
        advs = parentDirectory + "/advanced_settings.yaml"
        level = 0
        exists = False
        count = 1
        while not exists and len(advs) and count < 10:
            count += 1
            level -= 1
            exists = os.path.exists(advs)
            if not exists:
                advs = "/".join(parentDirectory.split("/")
                                [:level]) + "/advanced_settings.yaml"
        if not exists:
            advs = {}
        else:
            with open(advs, 'r') as stream:
                advs = yaml.safe_load(stream)
        # MERGE ADVANCED SETTINGS AND USER SETTINGS (USER SETTINGS OVERRIDE)
        self.settings = {**advs, **self.settings}

        # WHICH EVENTS ARE WE TO PARSE?
        parse_mock_events = self.settings["lvk"]["parse_mock_events"]
        parse_real_events = self.settings["lvk"]["parse_real_events"]

        if self.record['superevent_id'][0] == 'M' and not parse_mock_events:
            return
        if self.record['superevent_id'][0] != 'M' and not parse_real_events:
            return

        # WHERE TO DOWNLOAD MAPS TO
        if "download_dir" in self.settings["lvk"] and self.settings["lvk"]["download_dir"]:
            self.download_dir = self.settings["lvk"]["download_dir"]
            # MAKE RELATIVE HOME PATH ABSOLUTE
            from os.path import expanduser
            home = expanduser("~")
            if self.download_dir == "~":
                self.download_dir = self.download_dir.replace("~", home)
        else:
            self.download_dir = "."

        self.mockDir = self.download_dir + "/mockevents/"
        self.eventDir = self.download_dir + "/superevents/"
        if parse_mock_events:
            if not os.path.exists(self.mockDir):
                os.makedirs(self.mockDir)
        if parse_real_events:
            if not os.path.exists(self.eventDir):
                os.makedirs(self.eventDir)

        return None

    def parse(self):
        """
        *parse the lvk events and write meta data and maps to file
        """
        self.log.debug('starting the ``parse`` method')

        from base64 import b64decode
        from io import BytesIO
        from astropy.table import Table
        import astropy_healpix as ah
        import numpy as np
        from astropy.time import Time
        from datetime import datetime
        import yaml
        import json

        # WHICH EVENTS ARE WE TO PARSE?
        parse_mock_events = self.settings["lvk"]["parse_mock_events"]
        parse_real_events = self.settings["lvk"]["parse_real_events"]
        if self.record['superevent_id'][0] == 'M' and not parse_mock_events:
            return
        if self.record['superevent_id'][0] != 'M' and not parse_real_events:
            return

        print("\n----------------------------------------")
        if "event" in self.record and self.record["event"]:
            timeDelta = (Time(self.record["time_created"], scale='utc') - Time(self.record["event"]["time"], scale='utc')).to_value(unit='min')
            far = 1 / (float(self.record['event']['far']) * 60. * 60. * 24.)
            if far > 1000:
                far /= 365.
                far = f"1 per {far:0.1f} yrs"
            else:
                far = f"1 per {far:0.1f} days"
            print(f'EVENT: {self.record["superevent_id"]} detected at {self.record["event"]["time"].replace("Z","")} UTC ({self.record["event"]["group"]})')
            print(f'ALERT: {self.record["alert_type"].replace("_"," ")} reported at {self.record["time_created"].replace("Z","")} UTC (+{timeDelta:.2f} mins)')
            print(f'FAR: {far}')
            if "classification" in self.record['event']:
                for k, v in self.record['event']['classification'].items():
                    self.record['event']['classification'][k] = float(f'{v:.2f}')
                print(f"CLASSIFICATION: {self.record['event']['classification']}")
            if "properties" in self.record['event']:
                print(f"PROPERTIES: {self.record['event']['properties']})")
        else:
            print(f'EVENT: {self.record["superevent_id"]}')
            print(f'ALERT: {self.record["alert_type"].replace("_"," ")} reported at {self.record["time_created"].replace("Z","")} UTC')

        # PARSE SKY MAP
        header, extras, fitsPath = {}, {}, None
        localisation = False
        if self.record.get('event', {}):
            skymap_str = self.record.get('event', {}).pop('skymap')

            if skymap_str:
                # Decode, parse skymap, and print most probable sky location
                skymap_bytes = b64decode(skymap_str)
                skymap = Table.read(BytesIO(skymap_bytes))
                localisation = skymap.meta["CREATOR"].lower()
                header = {k: v for k, v in skymap.meta.items() if k != "HISTORY"}
                # GENERATE SOME EXTRA STATS
                extras = generate_skymap_stats(
                    log=self.log,
                    skymap=skymap,
                )

        # MERGE HEADER AND ALERT INTO ONE FILE
        try:
            self.record.pop('external_coinc')
        except:
            pass
        meta = {"HEADER": header, "ALERT": self.record, "EXTRA": extras}

        # DOES ALERT PASS THE FILTERS?
        if 'filters' in self.settings["lvk"]:
            if self.settings["lvk"]["filters"]:
                if not self.filter_alert(meta):
                    print("----------------------------------------\n\n")
                    return
        print("----------------------------------------\n\n")

        # DON'T WRITE RETRACTION ALERT IF NO OTHER ALERT EXISTS ON FILE
        if self.record['alert_type'].lower() == "retraction":
            if self.record["superevent_id"][0] == 'M':
                eventDir = self.mockDir + self.record["superevent_id"]
            else:
                eventDir = self.eventDir + self.record["superevent_id"]
            if not os.path.exists(eventDir):
                return

        # ADD EVENT FILTERING HERE
        # ONCE WE HAVE DECIDED TO SAVE THE EVENT/ALERT
        # RECURSIVELY CREATE MISSING DIRECTORIES
        alertTime = self.record["time_created"].replace("-", "").replace(":", "").replace(" ", "").replace("Z", "")
        if self.record["superevent_id"][0] == 'M':
            alertDir = self.mockDir + self.record["superevent_id"] + "/" + alertTime + "_" + self.record["alert_type"].lower()
        else:
            alertDir = self.eventDir + self.record["superevent_id"] + "/" + alertTime + "_" + self.record["alert_type"].lower()
        if not os.path.exists(alertDir):
            os.makedirs(alertDir)

        if self.settings["lvk"]["json"]:
            jsonName = self.record["superevent_id"] + "-" + self.record["alert_type"].lower() + ".json"
            jsonPath = alertDir + "/" + jsonName
            # DUMP JSON TO FILE
            writeFile = open(jsonPath, "w")
            json.dump(self.record, writeFile, indent=4)
            writeFile.close()

        # WRITE SKY MAP
        if localisation:
            fitsPath = f"{alertDir}/{localisation}.multiorder.fits"
            with open(fitsPath, "wb") as f:
                f.write(skymap_bytes)

        # WRITE META
        with open(alertDir + "/meta.yaml", 'w') as stream:
            yaml.dump(meta, stream, default_flow_style=False)

        if fitsPath:
            if self.settings["lvk"]["ascii_map"]["convert"]:
                c = ascii(
                    log=self.log,
                    mapPath=fitsPath,
                    nside=self.settings["lvk"]["ascii_map"]["nside"],
                    settings=self.settings
                )
                asciiContent = c.convert(outputFilepath=alertDir + "/skymap.csv")

            if self.settings["lvk"]["aitoff"]["convert"]:
                from gocart.convert import aitoff
                c = aitoff(
                    log=self.log,
                    mapPath=fitsPath,
                    outputFolder=alertDir,
                    settings=self.settings,
                    meta=meta
                )
                c.convert(
                    galacticPlane=self.settings["lvk"]["aitoff"]["galactic_plane"],
                    sunmoonContour=self.settings["lvk"]["aitoff"]["sun_moon_contour"],
                    sunmoon=self.settings["lvk"]["aitoff"]["sun_moon"])

        self.log.debug('completed the ``parse`` method')
        return lvk

    def filter_alert(
            self,
            alert):
        """*filter the alert record with filtering criteria in the settings file and return true (pass) or false (fail)*

        **Key Arguments:**
            - ``alert`` -- the alert record

        **Return:**
            - ``passing`` -- True or False. True is alert passes one or more filter
        """
        self.log.debug('starting the ``filter_alert`` method')

        filterResults = []
        for f in self.settings["lvk"]["filters"]:

            # SOME SETUP
            try:
                f['alert_types'][:] = [g.lower() for g in f['alert_types']]
            except:
                pass

            passing = True
            message = []
            if 'alert_types' in f and not alert['ALERT']['alert_type'].lower() in f['alert_types']:
                passing = False
                message.append(f"Alert type is {alert['ALERT']['alert_type'].lower()}")
            if "ns_lower" in f and 'event' in alert['ALERT'] and alert['ALERT']['event'] and 'classification' in alert['ALERT']['event'] and not alert['ALERT']['event']['classification']['BNS'] + alert['ALERT']['event']['classification']['NSBH'] >= f["ns_lower"]:
                passing = False
                message.append(f"BNS+NSBH = {alert['ALERT']['event']['classification']['BNS'] + alert['ALERT']['event']['classification']['NSBH']} (< {f['ns_lower']})")
            if "far_upper" in f and 'event' in alert['ALERT'] and alert['ALERT']['event'] and not alert['ALERT']['event']['far'] < f["far_upper"]:
                passing = False
                message.append(f"FAR = {alert['ALERT']['event']['far']} (> {f['far_upper']})")
            if "dist_upper" in f and 'DISTMEAN' in alert['HEADER'] and alert['HEADER']['DISTMEAN'] and not alert['HEADER']['DISTMEAN'] < f["dist_upper"]:
                passing = False
                message.append(f"DISTMEAN = {alert['HEADER']['DISTMEAN']} (> {f['dist_upper']})")
            if "area90_upper" in f and 'EXTRA' in alert and 'area90' in alert['EXTRA'] and not alert['EXTRA']['area90'] < f["area90_upper"]:
                passing = False
                message.append(f"area90 = {alert['EXTRA']['area90']} (> {f['area90_upper']})")
            if "hasns_lower" in f and 'event' in alert['ALERT'] and alert['ALERT']['event'] and 'properties' in alert['ALERT']['event'] and not alert['ALERT']['event']['properties']['HasNS'] >= f["hasns_lower"]:
                passing = False
                message.append(f"HasNS = {alert['ALERT']['event']['properties']['HasNS']} (< {f['hasns_lower']})")
            if "hasremnant_lower" in f and 'event' in alert['ALERT'] and alert['ALERT']['event'] and 'properties' in alert['ALERT']['event'] and not alert['ALERT']['event']['properties']['HasRemnant'] >= f["hasremnant_lower"]:
                passing = False
                message.append(f"HasRemnant = {alert['ALERT']['event']['properties']['HasRemnant']} (< {f['hasremnant_lower']})")

            filterResults.append(passing)

            if passing:
                print(f"The alert passes the {f['name']} filter")
            else:
                message = (" and ").join(message)
                print(f"The alert fails the {f['name']} filter. {message}.")

        self.log.debug('completed the ``filter_alert`` method')
        if True in filterResults:
            return True
        else:
            return False

        # use the tab-trigger below for new method
        # xt-class-method
