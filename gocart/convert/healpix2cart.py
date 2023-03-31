#!/usr/bin/env python
# encoding: utf-8
"""
*Convert Healpix Map to a Cartesian WCS*

:Author:
    David Young

:Date Created:
    March 23, 2023
"""
from fundamentals import tools
from builtins import object
import sys
import os
os.environ['TERM'] = 'vt100'


class healpix2cart(object):
    """
    *Take a healpix map and convert to a rectilinear projection.*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary
        - ``mapPath`` -- path the the healpix map

    **Usage:**

    To setup your logger and settings, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_).

    To initiate a healpix2cart object, use the following:

    ```python
    from gocart.convert import healpix2cart
    converter = healpix2cart(
        log=log,
        mapPath=pathToOutputDir + "/bayestar.multiorder.fits",
        settings=settings
    )
    wcs, mapDF, header = converter.convert()
    ```

    """

    def __init__(
            self,
            log,
            mapPath,
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'healpix2cart' object")
        self.settings = settings
        self.mapPath = mapPath
        # xt-self-arg-tmpx

        return None

    def convert(self):
        """
        *convert the healpix map to a cartesian WCS and image*

        **Return:**
            - ``wcs`` -- an astropy wcs object
            - ``mapDF`` -- the map converted cartesian format and recorded in a pandas dataframe.
            - ``header`` -- the map header

        **Usage:**

        ```python
        from gocart.convert import healpix2cart
        converter = healpix2cart(
            log=log,
            mapPath=pathToOutputDir + "/bayestar.multiorder.fits",
            settings=settings
        )
        wcs, mapDF, header = converter.convert()
        ```
        """
        self.log.debug('starting the ``get`` method')

        import matplotlib.pyplot as plt
        from astropy.table import Table
        import astropy.units as u
        import pandas as pd
        import numpy as np
        import astropy_healpix as ah
        from astropy import wcs as awcs
        import healpy as hp

        wcs, mapDF = create_wcs_and_pixels(self.log)

        # CONVERT HEALPIX MAP TO DATAFRAME
        skymap = Table.read(self.mapPath)
        tableData = skymap.to_pandas()

        # FIND LEVEL AND NSIDE PIXEL INDEX FOR EACH MULTI-RES PIXEL
        tableData['LEVEL'], tableData['IPIX'] = ah.uniq_to_level_ipix(tableData['UNIQ'])
        tableData['NSIDE'] = ah.level_to_nside(tableData['LEVEL'])
        # DETERMINE THE PIXEL AREA AND PROB OF EACH PIXEL
        tableData['AREA'] = ah.nside_to_pixel_area(tableData['NSIDE']).to_value(u.steradian)
        tableData['PROB'] = tableData['AREA'] * tableData["PROBDENSITY"]

        # DETERMINE THE INDEX OF MULTI-RES PIX AT HIGHEST HEALPIX RESOLUTION
        max_level = 29
        max_nside = ah.level_to_nside(max_level)
        tableData['INDEX29'] = tableData['IPIX'] * (2**(max_level - tableData['LEVEL']))**2

        # DETERMINE THE HIGH-RES PIXEL LOCATION FOR EACH RA AND DEC
        match_ipix = ah.lonlat_to_healpix(mapDF["ra"].values * u.deg, mapDF["dec"].values * u.deg, max_nside, order='nested')

        # RETURNS THE INDICES THAT WOULD SORT THIS ARRAY
        sorter = np.argsort(tableData['INDEX29'])
        # FIND INDICES WHERE ELEMENTS SHOULD BE INSERTED TO MAINTAIN ORDER -- CLOSET MATCH TO THE RIGHT
        matchedIndices = sorter[np.searchsorted(tableData['INDEX29'].values, match_ipix, side='right', sorter=sorter) - 1]

        # MERGE TABLES
        mapDF = pd.concat([mapDF, tableData.iloc[matchedIndices].set_index(mapDF.index)], axis=1)

        # CLEAN UP COLUMNS
        mapDF.columns = [d.upper() for d in mapDF.columns]
        mapDF.drop(columns=['AREA', 'UNIQ', 'LEVEL', 'IPIX', 'NSIDE', 'PROB', 'INDEX29'], inplace=True)
        # ADD PIXEL PROB
        mapDF["PROBDENSITY_DEG2"] = mapDF["PROBDENSITY"] / (1 * u.steradian).to_value(u.degree * u.degree)
        mapDF["PROB"] = mapDF["PROBDENSITY_DEG2"] * mapDF["PIXEL_AREA_DEG2"]

        # SANITY CHECK
        totalProb = mapDF["PROB"].sum()
        # print(totalProb)

        self.log.debug('completed the ``get`` method')
        return wcs, mapDF, skymap.meta


def create_wcs_and_pixels(log):
    """*create the all-sky rectilinear wcs*

    **Key Arguments:**
        - ``log`` -- logger

    **Return:**
        - ``wcs`` -- the cartesian wcs.
        - ``mapDF`` -- the pixel data in a dataframe.

    **Usage:**

    ```python
    from gocart.convert import create_wcs_and_pixels
    wcs, mapDF = create_wcs_and_pixels(log=log)
    ```
    """
    log.debug('starting the ``create_wcs_and_pixels`` method')

    from astropy.wcs import WCS
    import pandas as pd
    import numpy as np
    import astropy.units as u

    # CREATE A NEW WCS OBJECT.
    wcs = WCS(naxis=2)

    # DETERMINE THE PIXEL GRID X,Y RANGES
    pixelSizeDeg = 1.
    raRange = 360
    decRange = 180
    xRange = int(raRange / pixelSizeDeg)
    yRange = int(decRange / pixelSizeDeg)

    # SET THE PIXEL SIZE
    wcs.wcs.cdelt = np.array([pixelSizeDeg, pixelSizeDeg])
    # SET THE REFERENCE PIXEL TO THE CENTRE PIXEL .. BOTTOM LEFT PIXEL IS 0,0 IN PYTHON (HENCE ADDTION OF 1)
    wcs.wcs.crpix = [(xRange + 1) / 2., (yRange + 1) / 2.]

    # FOR AN ORTHOGONAL GRID THE CRVAL2 VALUE MUST BE ZERO AND CRPIX2
    # MUST REFLECT THIS
    wcs.wcs.crpix[1] -= wcs.wcs.crval[1] / wcs.wcs.cdelt[1]
    wcs.wcs.crval[1] = 0
    wcs.wcs.crval[0] = raRange / 2

    # SET COORDINATE TYPE TO CARTESIAN
    wcs.wcs.ctype = ["RA---CAR", "DEC--CAR"]

    # CREATE THE DATA GRID
    x = np.arange(0, xRange, 1)
    y = np.arange(0, yRange, 1)
    X, Y = np.meshgrid(x, y)

    # FITS FORMAT -- BOTTOM LEFT PIXEL CENTRE IS 1,1, BUT WE ARE WORKING WITH PYTHON SO USE 0,0
    ra, dec = wcs.wcs_pix2world(X, Y, 0)
    area = np.sin(np.deg2rad(np.abs(dec + 90))) * pixelSizeDeg ** 2

    # CREATE DATA FRAME FROM A DICTIONARY OF LISTS
    myDict = {
        "pixel_x": X.ravel(),
        "pixel_y": Y.ravel(),
        "ra": ra.ravel(),
        "dec": dec.ravel(),
        "pixel_area_deg2": area.ravel()
    }
    mapDF = pd.DataFrame(myDict)

    log.debug('completed the ``create_wcs_and_pixels`` method')
    return wcs, mapDF

    # use the tab-trigger below for new method
    # xt-class-method
