#!/usr/bin/env python
# encoding: utf-8
"""
*Plot multiorder FITS in an aitoff projection*

:Author:
    David Young

:Date Created:
    March 21, 2023
"""
from fundamentals import tools
from builtins import object
import sys
import os
os.environ['TERM'] = 'vt100'


class aitoff(object):
    """
    *The worker class for the aitoff module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``mapPath`` -- path to the multiorder FITS file.
        - ``settings`` -- the settings dictionary

    **Usage:**

    To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_).

    To initiate a aitoff object, use the following:

    ```eval_rst
    .. todo::

        - add usage info
        - create a sublime snippet for usage
        - create cl-util for this class
        - add a tutorial about ``aitoff`` to documentation
        - create a blog post about what ``aitoff`` does
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
            mapPath,
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'aitoff' object")
        self.settings = settings
        self.mapPath = mapPath
        # xt-self-arg-tmpx

        # 2. @flagged: what are the default attrributes each object could have? Add them to variable attribute set here
        # Variable Data Atrributes

        # 3. @flagged: what variable attrributes need overriden in any baseclass(es) used
        # Override Variable Data Atrributes

        # Initial Actions

        return None

    def convert(self):
        """
        *convert the map to an aitoff plot*

        **Return:**
            - ``aitoff``

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
        self.log.debug('starting the ``convert`` method')

        import matplotlib.pyplot as plt
        from . import healpix2cart
        import astropy.units as u
        import numpy as np
        from astropy.coordinates import (SkyCoord, Galactic)

        from matplotlib.projections.geo import GeoAxes

        class ThetaFormatterShiftPi(GeoAxes.ThetaFormatter):
            """Shifts labelling by pi
            Shifts labelling from -180,180 to 0-360"""

            def __call__(self, x, pos=None):
                x -= np.pi
                x = -x
                return GeoAxes.ThetaFormatter.__call__(self, x, pos)

        converter = healpix2cart(
            log=self.log,
            mapPath=self.mapPath,
            settings=self.settings
        )
        wcs, mapDF = converter.convert()

        # from tabulate import tabulate
        # print(tabulate(mapDF.head(100), headers='keys', tablefmt='psql'))
        # print(mapDF["RA"].min(), mapDF["RA"].max())
        # print(mapDF["DEC"].min(), mapDF["DEC"].max())
        # sys.exit(0)
        mapDF = mapDF.iloc[::-1]
        # RA RANGES FROM 0-360 ... NEED TO FLIP 360-0, AND THEN SHIFT BY 180 TO MATCH MATPLOTLIB FRAME
        mapDF["RASHIFTED"] = -mapDF["RA"] + 180
        data = mapDF["PROBDENSITY_DEG2"].values.reshape((mapDF["PIXEL_Y"].max() + 1, mapDF["PIXEL_X"].max() + 1))

        long = np.deg2rad(mapDF["RASHIFTED"].values).reshape((mapDF["PIXEL_Y"].max() + 1, mapDF["PIXEL_X"].max() + 1))
        lat = np.deg2rad(mapDF["DEC"].values).reshape((mapDF["PIXEL_Y"].max() + 1, mapDF["PIXEL_X"].max() + 1))

        # MATPLOTLIB IS DOING THE PROJECTION
        cmap = "YlOrRd"
        fig = plt.figure()

        std = data.std()
        mean = data.mean()

        ax = fig.add_subplot(111, projection='aitoff')
        # RASTERIZED MAKES THE MAP BITMAP WHILE THE LABELS REMAIN VECTORIAL
        # FLIP LONGITUDE TO THE ASTRO CONVENTION
        image = ax.pcolormesh(long, lat, data, rasterized=True, cmap=cmap, vmin=mean, vmax=mean + 5 * std)

        # GRATICULE
        ax.set_longitude_grid(30)
        ax.set_latitude_grid(15)
        ax.xaxis.set_major_formatter(ThetaFormatterShiftPi(30))
        ax.set_longitude_grid_ends(90)

        if 1 == 1 or galacticPlane:
            # LON:LAT is lon 0-360 at lat=0
            lon_array = np.arange(0, 360)
            lat = np.full_like(lon_array, 0)
            galc = SkyCoord(l=lon_array, b=lat, frame=Galactic, unit=u.deg)
            # INITATE AN ARRAY OF [0:0]
            equatorial_array = galc.icrs
            gRa = equatorial_array.ra.degree
            gDec = equatorial_array.dec.degree
            gx = np.remainder(gRa + 180, 360)
            # SCALE CONVERSION TO [-180, 180]
            ind = gx > 180
            gx[ind] -= 360
            # REVERSE RA SCALE
            gx = -gx

            ax.scatter(np.radians(gx), np.radians(gDec),
                       color="#EFEEEC", alpha=1, s=100)

        plt.show()

        # # Save to FITS file
        # hdu.writeto('/tmp/test.fits', overwrite=True)

        # return

        plt.subplot(projection=wcs)
        plt.imshow(data, origin='lower')
        plt.grid(color='white', ls='solid')

        plt.show()

        return

        import matplotlib.pyplot as plt
        from astropy.table import Table
        import astropy.units as u
        import pandas as pd
        import numpy as np
        import astropy_healpix as ah
        from astropy import wcs as awcs
        import healpy as hp

        skymap = Table.read(self.mapPath)
        tableData = skymap.to_pandas()

        # FIND LEVEL AND NSIDE PIXEL INDEX FOR EACH MULTI-RES PIXEL
        tableData['LEVEL'], tableData['IPIX'] = ah.uniq_to_level_ipix(tableData['UNIQ'])
        tableData['NSIDE'] = ah.level_to_nside(tableData['LEVEL'])
        # DETERMINE THE PIXEL AREA AND PROB OF EACH PIXEL
        tableData['AREA'] = ah.nside_to_pixel_area(tableData['NSIDE']).to_value(u.steradian)
        tableData['PROB'] = tableData['AREA'] * tableData["PROBDENSITY"]

        # SANITY CHECK
        totalProb = tableData["PROB"].sum()
        print(totalProb)

        # PIXEL WITH HIGHEST PROB WILL HAVE THE HIGHEST RESOLUTION
        # CONVERT THE MAP TO A NESTED HEALPIX
        i = np.argmax(skymap['PROBDENSITY'])
        uniq = skymap[i]['UNIQ']
        level, ipix = ah.uniq_to_level_ipix(uniq)
        nside = ah.level_to_nside(level)

        # CREATE A NEW WCS OBJECT
        w = awcs.WCS(naxis=2)
        # SET THE REQUIRED PIXEL SIZE
        pixelSizeDeg = 1.0
        w.wcs.cdelt = np.array([pixelSizeDeg, pixelSizeDeg])
        w.wcs.crval = [180, 0]

        # MAP VISULISATION RATIO IS ALWAYS 1/2
        xRange = 2000
        yRange = int(xRange / 2.)

        # SET THE REFERENCE PIXEL TO THE CENTRE PIXEL
        w.wcs.crpix = [xRange / 2., yRange / 2.]

        # FULL-SKY MAP SO PLOT FULL RA AND DEC RANGES
        dec = np.linspace(-90 * u.deg, 90 * u.deg, yRange)
        ra = np.linspace(0 * u.deg, 360 * u.deg, xRange)
        ra, dec = np.meshgrid(ra, dec)
        ra = np.ravel(ra)
        dec = np.ravel(dec)

        # PROJECT THE MAP TO A RECTANGULAR MATRIX xRange X yRange

        # DETERMINE THE INDEX OF MULTI-RES PIX AT HIGHEST HEALPIX RESOLUTION
        max_level = 29
        max_nside = ah.level_to_nside(max_level)
        tableData['INDEX29'] = tableData['IPIX'] * (2**(max_level - tableData['LEVEL']))**2

        # DETERMINE THE HIGH-RES PIXEL LOCATION FOR EACH RA AND DEC
        match_ipix = ah.lonlat_to_healpix(ra, dec, max_nside, order='nested')

        print(ra)

        # RETURNS THE INDICES THAT WOULD SORT THIS ARRAY
        sorter = np.argsort(tableData['INDEX29'])
        # FIND INDICES WHERE ELEMENTS SHOULD BE INSERTED TO MAINTAIN ORDER -- CLOSET MATCH TO THE RIGHT
        matchedIndices = sorter[np.searchsorted(tableData['INDEX29'].values, match_ipix, side='right', sorter=sorter) - 1]

        print(tableData[matchedIndices]['PROBDENSITY'] * (np.pi / 180)**2)

        probs = aMap[healpixIds]

        # healpixIds = np.reshape(healpixIds, (1, -1))[0]

        # CTYPE FOR THE FITS HEADER
        thisctype = projectionDict[projection]
        w.wcs.ctype = ["RA---%(thisctype)s" %
                       locals(), "DEC--%(thisctype)s" % locals()]

        # ALL PROJECTIONS IN FITS SEEM TO BE MER
        w.wcs.ctype = ["RA---MER" %
                       locals(), "DEC--MER" % locals()]

        # MATPLOTLIB IS DOING THE PROJECTION
        ax = fig.add_subplot(111, projection=projection)

        # RASTERIZED MAKES THE MAP BITMAP WHILE THE LABELS REMAIN VECTORIAL
        # FLIP LONGITUDE TO THE ASTRO CONVENTION
        image = ax.pcolormesh(longitude[
            ::-1], latitude, probs, rasterized=True, cmap=cmap)

        # GRATICULE
        ax.set_longitude_grid(30)
        ax.set_latitude_grid(15)
        ax.xaxis.set_major_formatter(ThetaFormatterShiftPi(30))
        ax.set_longitude_grid_ends(90)

        # CONTOURS - NEED TO ADD THE CUMMULATIVE PROBABILITY
        i = np.flipud(np.argsort(aMap))
        cumsum = np.cumsum(aMap[i])
        cls = np.empty_like(aMap)
        cls[i] = cumsum * 99.99999999 * stampProb

        # EXTRACT CONTOUR VALUES AT HEALPIX INDICES
        contours = []
        contours[:] = [cls[i] for i in healpixIds]
        # contours = np.reshape(np.array(contours), (yRange, xRange))

        CS = ax.contour(longitude[::-1], latitude,
                        contours, linewidths=.5, alpha=0.7, zorder=2)

        CS.set_alpha(0.5)
        CS.clabel(fontsize=10, inline=True,
                  fmt='%2.1f', fontproperties=font, alpha=0.0)

        # COLORBAR
        if colorBar:
            cb = fig.colorbar(image, orientation='horizontal',
                              shrink=.6, pad=0.05, ticks=[0, 1])
            cb.ax.xaxis.set_label_text("likelihood")
            cb.ax.xaxis.labelpad = -8
            # WORKAROUND FOR ISSUE WITH VIEWERS, SEE COLORBAR DOCSTRING
            cb.solids.set_edgecolor("face")

        ax.tick_params(axis='x', labelsize=12)
        ax.tick_params(axis='y', labelsize=12)
        # lon.set_ticks_position('bt')
        # lon.set_ticklabel_position('b')
        # lon.set_ticklabel(size=20)
        # lat.set_ticklabel(size=20)
        # lon.set_axislabel_position('b')
        # lat.set_ticks_position('lr')
        # lat.set_ticklabel_position('l')
        # lat.set_axislabel_position('l')

        # # REMOVE TICK LABELS
        # ax.xaxis.set_ticklabels([])
        # ax.yaxis.set_ticklabels([])
        # # REMOVE GRID
        # ax.xaxis.set_ticks([])
        # ax.yaxis.set_ticks([])

        # REMOVE WHITE SPACE AROUND FIGURE
        spacing = 0.01
        plt.subplots_adjust(bottom=spacing, top=1 - spacing,
                            left=spacing, right=1 - spacing)

        plt.grid(True)

        # # INITIALISE FIGURE
        # fig = plt.figure()

        # pathToProbMap = self.moFitsPath

        # # READ HEALPIX MAPS FROM FITS FILE
        # # THIS FILE IS A ONE COLUMN FITS BINARY, WITH EACH CELL CONTAINING AN
        # # ARRAY OF PROBABILITIES (3,072 ROWS)
        # # READ IN THE HEALPIX FITS FILE
        # m = HealpixMap(contents, uniq, density = True)
        # aMap, mapHeader = hp.read_map(self.moFitsPath, h=True, verbose=False)
        # # DETERMINE THE SIZE OF THE HEALPIXELS
        # nside = hp.npix2nside(len(aMap))

        self.log.debug('completed the ``convert`` method')
        return None

    # xt-class-method

    # 5. @flagged: what actions of the base class(es) need ammending? ammend them here
    # Override Method Attributes
    # method-override-tmpx
