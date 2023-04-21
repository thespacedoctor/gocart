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
        self.evertDir = self.download_dir + "/superevents/"
        if parse_mock_events:
            if not os.path.exists(self.mockDir):
                os.makedirs(self.mockDir)
        if parse_real_events:
            if not os.path.exists(self.evertDir):
                os.makedirs(self.evertDir)

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

        # ADD EVENT FILTERING HERE
        # ONCE WE HAVE DECIDED TO SAVE THE EVENT/ALERT
        # RECURSIVELY CREATE MISSING DIRECTORIES
        alertTime = self.record["time_created"].replace("-", "").replace(":", "").replace(" ", "").replace("Z", "")
        if self.record["superevent_id"][0] == 'M':
            alertDir = self.mockDir + self.record["superevent_id"] + "/" + alertTime + "_" + self.record["alert_type"].lower()
        else:
            alertDir = self.evertDir + self.record["superevent_id"] + "/" + alertTime + "_" + self.record["alert_type"].lower()
        if not os.path.exists(alertDir):
            os.makedirs(alertDir)

        if "event" in self.record and self.record["event"]:
            timeDelta = (Time(self.record["time_created"], scale='utc') - Time(self.record["event"]["time"], scale='utc')).to_value(unit='min')
            far = 1 / (float(self.record['event']['far']) * 60. * 60. * 24.)
            if far > 1000:
                far /= 365.
                far = f"1 per {far:0.1f} yrs"
            else:
                far = f"1 per {far:0.1f} days"
            print(f'EVENT: {self.record["superevent_id"]} detected at {self.record["event"]["time"].replace("Z","")} UTC')
            print(f'ALERT: {self.record["alert_type"].replace("_"," ")} reported at {self.record["time_created"].replace("Z","")} UTC (+{timeDelta:.2f} mins)')
            print(f'FAR: {far}')
            for k, v in self.record['event']['classification'].items():
                self.record['event']['classification'][k] = float(f'{v:.2f}')
            print(f"CLASSIFICATION: {self.record['event']['classification']}")
            print(f"PROPERTIES: {self.record['event']['properties']})\n\n")
        else:
            print(f'EVENT: {self.record["superevent_id"]}')
            print(f'ALERT: {self.record["alert_type"].replace("_"," ")} reported at {self.record["time_created"].replace("Z","")} UTC\n\n')

        # PARSE SKY MAP
        header, extras, fitsPath = {}, {}, None
        if self.record.get('event', {}):
            skymap_str = self.record.get('event', {}).pop('skymap')
            if skymap_str:
                # Decode, parse skymap, and print most probable sky location
                skymap_bytes = b64decode(skymap_str)
                skymap = Table.read(BytesIO(skymap_bytes))

                localisation = skymap.meta["CREATOR"].lower()

                fitsPath = f"{alertDir}/{localisation}.multiorder.fits"
                with open(fitsPath, "wb") as f:
                    f.write(skymap_bytes)

                header = {k: v for k, v in skymap.meta.items() if k != "HISTORY"}

                # GENERATE SOME EXTRA STATS
                extras = generate_skymap_stats(
                    log=self.log,
                    skymap=skymap,
                )

        # MERGE HEADER AND ALERT INTO ONE FILE
        meta = {"HEADER": header, "ALERT": self.record, "EXTRA": extras}

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
