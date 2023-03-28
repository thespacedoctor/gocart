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
    *Convert Healpix Map to Aitoff projection with options to include galactic plane and sun position*

    **Key Arguments:**
        - ``log`` -- logger
        - ``mapPath`` -- path to the multiorder FITS file.
        - ``settings`` -- the settings dictionary

    **Usage:**

    To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_).

    To print the healpix map as an aitoff projection, use the following:

    ```python
    from gocart.convert import aitoff
    converter = aitoff(
        log=log,
        mapPath="path/to/bayestar.multiorder.fits",
        settings=settings
    )
    converter.convert()
    ```

    """

    def __init__(
            self,
            log,
            mapPath,
            outputFolder,
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'aitoff' object")
        self.settings = settings
        self.mapPath = mapPath
        self.outputFolder = outputFolder
        # xt-self-arg-tmpx

        return None

    def convert(
            self,
            contours=True,
            galacticPlane=True,
            daynight=True):
        """
        *convert the healpix map to an aitoff plot*

        **Key Arguments:**
            - ``contours`` -- plot 50 and 90% contours. Default *True*
            - ``galacticPlane`` -- plot galactic plane contours. Default *True*
            - ``daynight`` -- show sun-position and day/night terminator. Default *True*

        **Return:**
            - ``plotPath`` -- path to the printed plot
        """
        self.log.debug('starting the ``convert`` method')

        import matplotlib.pyplot as plt
        from . import healpix2cart
        import astropy.units as u
        import numpy as np
        from astropy.coordinates import SkyCoord, Galactic, get_sun
        from matplotlib.projections.geo import GeoAxes
        from matplotlib.cm import get_cmap

        import matplotlib
        matplotlib.use('PDF')

        class ThetaFormatterShiftPi(GeoAxes.ThetaFormatter):
            """SHIFTS LABELLING BY PI
            SHIFTS LABELLING FROM -180,180 TO 360-0"""

            def __call__(self, x, pos=None):
                x -= np.pi
                x = -x
                return GeoAxes.ThetaFormatter.__call__(self, x, pos)

        # CONVERT TO RECTILINEAR GRID
        converter = healpix2cart(
            log=self.log,
            mapPath=self.mapPath,
            settings=self.settings
        )
        wcs, mapDF, header = converter.convert()

        # RA RANGES FROM 0-360 ... NEED TO FLIP 360-0, AND THEN SHIFT BY 180 TO MATCH MATPLOTLIB FRAME
        mapDF = mapDF.iloc[::-1].reset_index()
        mapDF["RASHIFTED"] = -mapDF["RA"] + 180
        data = mapDF["PROB"].values.reshape((mapDF["PIXEL_Y"].max() + 1, mapDF["PIXEL_X"].max() + 1))
        long = np.deg2rad(mapDF["RASHIFTED"].values).reshape((mapDF["PIXEL_Y"].max() + 1, mapDF["PIXEL_X"].max() + 1))
        lat = np.deg2rad(mapDF["DEC"].values).reshape((mapDF["PIXEL_Y"].max() + 1, mapDF["PIXEL_X"].max() + 1))

        # MATPLOTLIB IS DOING THE PROJECTION
        cmap = get_cmap("hot_r")
        fig = plt.figure()

        # AITOFF DOES NOT PLAY WELL WITH ADDING LABELS - USE HAMMER PROJECTION INSTEAD
        ax = fig.add_subplot(111, projection='hammer')

        # RASTERIZED MAKES THE MAP BITMAP WHILE THE LABELS REMAIN VECTORIAL
        std = data.std()
        mean = data.mean()
        image = ax.pcolormesh(long, lat, data, rasterized=False, cmap=cmap, vmin=mean, vmax=mean + 5 * std)

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

            # CONVERT TO EQUATORIAL COORDINATES
            equatorial_array = galc.icrs
            gRa = equatorial_array.ra.degree
            gDec = equatorial_array.dec.degree
            gx = np.remainder(gRa + 180, 360)
            # SCALE CONVERSION TO [-180, 180] & FLIP RA
            ind = gx > 180
            gx[ind] -= 360
            gx = -gx
            ax.scatter(np.radians(gx), np.radians(gDec),
                       color="#EFEEEC", alpha=0.3, s=100)

        if daynight:
            from astropy.time import Time
            t = Time(header['DATE-OBS'], scale='utc')

            # FIND SUN AND PLACE ON CORRECT PLOT COORDINATE
            sun = get_sun(t).icrs
            if sun.ra.degree > 180.:
                sun.ra.degree -= 360
            sun.ra.degree = -sun.ra.degree

            # COMPUTE LONS AND LATS OF DAY/NIGHT TERMINATOR.
            nlons = 1441
            nlats = ((nlons - 1) / 2) + 1
            lons, lats = terminator(sun.ra.radian, sun.dec.radian, nlons)

            # PLOT THE SUN
            ax.scatter(sun.ra.radian, sun.dec.radian, color="#b58900", alpha=0.8, s=20, marker="o", edgecolors="#cb4b16", linewidths=0.5)
            # DRAW THIN TERMINATOR LINE
            ax.plot(lons, lats, '#002b36', linewidth=0.3)

            # COLOR IN THE NIGHT
            lons2 = np.linspace(-np.pi, np.pi, nlons)
            lats2 = np.linspace(-np.pi / 2, np.pi / 2, int(nlats))
            lons2, lats2 = np.meshgrid(lons2, lats2)
            daynight = np.ones(lons2.shape)
            for nlon in range(nlons):
                daynight[:, nlon] = np.where(lats2[:, nlon] < lats[nlon], 0, daynight[:, nlon])
            ax.contourf(lons2, lats2, daynight, 1, colors=[(0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.05)])

        if contours:
            # SORT BY PROB, CALCULATE CUMULATIVE PROB AND RESORT BY INDEX
            mapDF.sort_values(["PROB"],
                              ascending=[False], inplace=True)
            mapDF["CUMPROB"] = np.cumsum(mapDF['PROB'])
            mapDF["CUMPROB"] = mapDF["CUMPROB"] * 100. * mapDF["PROB"].sum()
            mapDF.sort_index(inplace=True)
            contours = mapDF["CUMPROB"].values.reshape((mapDF["PIXEL_Y"].max() + 1, mapDF["PIXEL_X"].max() + 1))

            line_c = ax.contour(long, lat,
                                contours, levels=[90], colors=['#93a1a1'], linewidths=0.5, zorder=2)
            this = ax.clabel(line_c, inline=True, fontsize=6, colors=['#93a1a1'], fmt='{:.0f} '.format)

        ax.tick_params(axis='x', labelsize=12)
        ax.tick_params(axis='y', labelsize=12)
        plt.grid(True)

        plt.savefig(self.outputFolder + "/skymap.png", bbox_inches='tight', dpi=300)

        self.log.debug('completed the ``convert`` method')
        return None


def terminator(ra, dec, nlons):
    import numpy as np
    lons = np.linspace(-np.pi, np.pi, nlons)
    longitude = lons + ra
    lats = np.arctan(-np.cos(longitude) / np.tan(dec))
    return lons, lats
