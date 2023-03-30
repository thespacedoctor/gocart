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
        alertDir = self.download_dir + "/" + self.record["superevent_id"] + "/" + alertTime + "_" + self.record["alert_type"].lower()
        if not os.path.exists(alertDir):
            os.makedirs(alertDir)

        # PARSE SKY MAP
        header, extras, fitsPath = {}, {}, None
        if self.record.get('event', {}):
            skymap_str = self.record.get('event', {}).pop('skymap')
            if skymap_str:
                # Decode, parse skymap, and print most probable sky location
                skymap_bytes = b64decode(skymap_str)
                skymap = Table.read(BytesIO(skymap_bytes))

                level, ipix = ah.uniq_to_level_ipix(
                    skymap[np.argmax(skymap['PROBDENSITY'])]['UNIQ']
                )
                ra, dec = ah.healpix_to_lonlat(ipix, ah.level_to_nside(level),
                                               order='nested')
                print(f'Most probable sky location (RA, Dec) = ({ra.deg}, {dec.deg})')

                # Print some information from FITS header
                print(f'Distance = {skymap.meta["DISTMEAN"]} +/- {skymap.meta["DISTSTD"]}')

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
            c = ascii(
                log=self.log,
                mapPath=fitsPath,
                settings=self.settings
            )
            asciiContent = c.convert(outputFilepath=alertDir + "/skymap.csv")

            from gocart.convert import aitoff
            c = aitoff(
                log=self.log,
                mapPath=fitsPath,
                outputFolder=alertDir,
                settings=self.settings
            )
            c.convert()

        self.log.debug('completed the ``parse`` method')
        return lvk
