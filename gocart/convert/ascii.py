#!/usr/bin/env python
# encoding: utf-8
"""
*Convert Healpix Map to ascii map format*

:Author:
    David Young

:Date Created:
    March 29, 2023
"""
from gocart.commonutils import flatten_healpix_map
from fundamentals import tools
from builtins import object
import sys
import os
os.environ['TERM'] = 'vt100'


class ascii(object):
    """
    *Take a healpix map and convert to an ascii map with one row per ~deg2*

    **Key Arguments:**
        - ``log`` -- logger
        - ``mapPath`` -- path the the healpix map or an astropy skymap table
        - ``nside`` -- size of healpix pixels to resolve the sky to
        - ``settings`` -- the settings dictionary

    **Usage:**

    To setup your logger and settings, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_).

    To convert a healpix map to ascii, run:

    ```python
    from gocart.convert import ascii
    c = ascii(
        log=log,
        mapPath="/path/to/bayestar.multiorder.fits",
        nside=64,
        settings=settings
    )
    asciiContent = c.convert(outputFilepath="/path/to/skymap.csv")
    ```
    """

    def __init__(
            self,
            log,
            mapPath,
            nside=64,
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'ascii' object")
        self.settings = settings
        self.mapPath = mapPath
        self.nside = nside

        self.hdus, self.table = flatten_healpix_map(
            log=log,
            mapPath=self.mapPath,
            nside=self.nside
        )

        return None

    def convert(
            self,
            outputFilepath=False):
        """
        *Convert the healpix map to ascii format and optionally save the ascii map to file*

        **Key Arguments:**
            - ``outputFilepath`` -- optionally write content to file. Default *False*

        **Return:**
            - ``ascii`` -- the CSV version of the healpix file (nside=64)
        """
        self.log.debug('starting the ``get`` method')

        import astropy_healpix as ah
        from astropy.coordinates import SkyCoord

        tableData = self.table.to_pandas()

        # CREATE RA AND DEC COLUMNS
        ra, dec = ah.healpix_to_lonlat(tableData.index, 64, order='nested')
        tableData["RA"] = ra.deg
        tableData["DEC"] = dec.deg

        # ALSO GLON GLAT COLUMNS
        galacticCoords = SkyCoord(ra.deg, dec.deg, frame='icrs', unit='deg').galactic
        tableData["GLON"] = galacticCoords.l.degree
        tableData["GLAT"] = galacticCoords.b.degree

        # DROP COLUMNS
        try:
            tableData.drop(columns=['DISTNORM'], inplace=True)
        except:
            pass

        # CREATE HEADER FOR FILE
        header = f"# EVENT:{self.table.meta['objid']}\n"
        header += f"# NSIDE:{self.nside}\n"

        tableData.index.names = ['IPIX']
        asciiContent = tableData.to_csv(index=True)
        asciiContent = header + asciiContent

        if outputFilepath:
            import codecs
            with codecs.open(outputFilepath, encoding='utf-8', mode='w') as writeFile:
                writeFile.write(asciiContent)

        self.log.debug('completed the ``get`` method')
        return asciiContent
