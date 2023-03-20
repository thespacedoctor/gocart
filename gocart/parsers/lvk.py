#!/usr/bin/env python
# encoding: utf-8
"""
*Parse Ligo-Virgo-Kagra GCN Notices*

:Author:
    David Young

:Date Created:
    March 19, 2023
"""
from fundamentals import tools
from builtins import object
import sys
import os
os.environ['TERM'] = 'vt100'


# OR YOU CAN REMOVE THE CLASS BELOW AND ADD A WORKER FUNCTION ... SNIPPET TRIGGER BELOW
# xt-worker-def

class lvk(object):
    """
    *The worker class for the lvk module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary
        - ``record`` -- the kafka record to parse.

    **Usage:**

    To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_). 

    To initiate a lvk object, use the following:

    ```eval_rst
    .. todo::

        - add usage info
        - create a sublime snippet for usage
        - create cl-util for this class
        - add a tutorial about ``lvk`` to documentation
        - create a blog post about what ``lvk`` does
    ```

    ```python
    usage code 
    ```

    """
    # Initialisation
    # 1. @flagged: what are the unique attrributes for each object? Add them
    # to __init__

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
        else:
            self.download_dir = "."

        return None

    def parse(self):
        """
        *parse the lvk events*

        **Return:**
            - ``lvk``

        **Usage:**

        ```eval_rst
        .. todo::

            - add usage info
            - create a sublime snippet for usage
            - create cl-util for this method
            - update the package tutorial if needed
        ```

        ```python
        usage code 
        ```
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
        alertTime = self.record["time_created"].replace("-", "").replace(":", "").replace("Z", "")
        alertDir = self.download_dir + "/" + self.record["superevent_id"] + "/" + alertTime + "_" + self.record["alert_type"].lower()
        if not os.path.exists(alertDir):
            os.makedirs(alertDir)

        # PARSE SKY MAP
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

                with open(f"{alertDir}/{localisation}.multiorder.fits", "wb") as f:
                    f.write(skymap_bytes)

                header = {k: v for k, v in skymap.meta.items()}

                # WRITE ALERT TO YAML FILE
                with open(alertDir + "/header.yaml", 'w') as stream:
                    yaml.dump(header, stream, default_flow_style=False)

        # WRITE ALERT TO YAML FILE
        with open(alertDir + "/alert.yaml", 'w') as stream:
            yaml.dump(self.record, stream, default_flow_style=False)

            # SAVE THE FITS MAP

        self.log.debug('completed the ``parse`` method')
        return lvk

    # xt-class-method

    # 5. @flagged: what actions of the base class(es) need ammending? ammend them here
    # Override Method Attributes
    # method-override-tmpx
