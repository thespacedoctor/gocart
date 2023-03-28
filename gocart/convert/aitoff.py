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

    def convert(
            self,
            contours=True,
            galacticPlane=True):
        """
        *convert the map to an aitoff plot*

        **Key Arguments:**
            - ``contours`` -- plot 50 and 90% contours. Default *True*
            - ``galacticPlane`` -- plot galactic plane contours. Default *True*

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
        from matplotlib.cm import get_cmap

        class ThetaFormatterShiftPi(GeoAxes.ThetaFormatter):
            """SHIFTS LABELLING BY PI
            SHIFTS LABELLING FROM -180,180 TO 360-0"""

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

        # RA RANGES FROM 0-360 ... NEED TO FLIP 360-0, AND THEN SHIFT BY 180 TO MATCH MATPLOTLIB FRAME
        mapDF = mapDF.iloc[::-1].reset_index()
        mapDF["RASHIFTED"] = -mapDF["RA"] + 180
        data = mapDF["PROB"].values.reshape((mapDF["PIXEL_Y"].max() + 1, mapDF["PIXEL_X"].max() + 1))
        long = np.deg2rad(mapDF["RASHIFTED"].values).reshape((mapDF["PIXEL_Y"].max() + 1, mapDF["PIXEL_X"].max() + 1))
        lat = np.deg2rad(mapDF["DEC"].values).reshape((mapDF["PIXEL_Y"].max() + 1, mapDF["PIXEL_X"].max() + 1))

        # MATPLOTLIB IS DOING THE PROJECTION
        cmap = "YlOrRd"
        cmap = get_cmap("gist_heat_r")
        fig = plt.figure()
        std = data.std()
        mean = data.mean()

        # AITOFF DOES NOT PLAY WELL WITH ADDING LABELS - USE HAMMER
        ax = fig.add_subplot(111, projection='hammer')
        # RASTERIZED MAKES THE MAP BITMAP WHILE THE LABELS REMAIN VECTORIAL
        image = ax.pcolormesh(long, lat, data, rasterized=True, cmap=cmap, vmin=mean, vmax=mean + std)

        # GRATICULE
        ax.set_longitude_grid(30)
        ax.set_latitude_grid(15)
        ax.xaxis.set_major_formatter(ThetaFormatterShiftPi(30))
        ax.set_longitude_grid_ends(90)

        if galacticPlane:
            # LON:LAT is lon 0-360 at lat=0
            lon_array = np.arange(0, 360)
            lat_arry = np.full_like(lon_array, 0)
            galc = SkyCoord(l=lon_array, b=lat_arry, frame=Galactic, unit=u.deg)
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

        if contours:
            # SORT BY PROB, CALCULATE CUMULATIVE PROB AND RESORT BY INDEX
            mapDF.sort_values(["PROB"],
                              ascending=[False], inplace=True)
            mapDF["CUMPROB"] = np.cumsum(mapDF['PROB'])
            mapDF["CUMPROB"] = mapDF["CUMPROB"] * 100. * mapDF["PROB"].sum()
            mapDF.sort_index(inplace=True)
            contours = mapDF["CUMPROB"].values.reshape((mapDF["PIXEL_Y"].max() + 1, mapDF["PIXEL_X"].max() + 1))

            line_c = ax.contour(long, lat,
                                contours, levels=[90.], colors=['black'], linewidths=1, alpha=0.5, zorder=2)
            this = ax.clabel(line_c, inline=True, fontsize=12, colors=['black'], fmt='{:.0f} '.format)

        ax.tick_params(axis='x', labelsize=12)
        ax.tick_params(axis='y', labelsize=12)

        # # REMOVE WHITE SPACE AROUND FIGURE
        # spacing = 0.01
        # plt.subplots_adjust(bottom=spacing, top=1 - spacing,
        #                     left=spacing, right=1 - spacing)

        plt.grid(True)
        plt.show()

        # plt.savefig('/tmp/figureName.png', bbox_inches='tight', dpi=300)

        self.log.debug('completed the ``convert`` method')
        return None

    # xt-class-method

    # 5. @flagged: what actions of the base class(es) need ammending? ammend them here
    # Override Method Attributes
    # method-override-tmpx
