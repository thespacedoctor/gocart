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
        - ``mapPath`` -- path to the multiorder FITS file
        - ``outputFolder`` -- path to output the results to
        - ``settings`` -- the settings dictionary
        - ``meta`` -- extra meta data to present on plots. Default: {}

    **Usage:**

    To setup your logger and settings, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_).

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
            meta={}
    ):
        self.log = log
        log.debug("instansiating a new 'aitoff' object")
        self.settings = settings
        self.mapPath = mapPath
        self.outputFolder = outputFolder
        self.meta = meta
        # xt-self-arg-tmpx

        return None

    def convert(
        self,
        contours=True,
        galacticPlane=True,
        sunmoon=True,
        sunmoonContour=True
    ):
        """
        *convert the healpix map to an aitoff plot*

        **Key Arguments:**
            - ``contours`` -- plot 50 and 90% contours. Default *True*
            - ``galacticPlane`` -- plot galactic plane contours. Default *True*
            - ``sunmoon`` -- plot sun and moon. Default *True*
            - ``sunmoonContour`` -- show contours within 33 deg of sun and 20 deg from moon

        **Return:**
            - ``plotPath`` -- path to the printed plot
        """
        self.log.debug('starting the ``convert`` method')

        import matplotlib.pyplot as plt
        from . import healpix2cart
        import astropy.units as u
        import numpy as np
        from astropy.coordinates import SkyCoord, Galactic, get_sun, get_moon
        from matplotlib.projections.geo import GeoAxes
        from matplotlib.cm import get_cmap
        import matplotlib.patches as mpatches
        from matplotlib.lines import Line2D
        from astropy.time import Time

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

        xsize = mapDF["PIXEL_X"].max() - mapDF["PIXEL_X"].min() + 1
        ysize = mapDF["PIXEL_Y"].max() - mapDF["PIXEL_Y"].min() + 1

        # RA RANGES FROM 0-360 ... NEED TO FLIP 360-0, AND THEN SHIFT BY 180 TO MATCH MATPLOTLIB FRAME
        mapDF = mapDF.iloc[::-1].reset_index()
        mapDF["RASHIFTED"] = -mapDF["RA"] + 180
        data = mapDF["PROB"].values.reshape((ysize, xsize))
        long = np.deg2rad(mapDF["RASHIFTED"].values).reshape((ysize, xsize))
        lat = np.deg2rad(mapDF["DEC"].values).reshape((ysize, xsize))

        # long = mapDF["RASHIFTED"].values.reshape((ysize, xsize))
        # lat = mapDF["DEC"].values.reshape((ysize, xsize))

        # MATPLOTLIB IS DOING THE PROJECTION
        cmap = get_cmap("hot_r")
        fig = plt.figure()

        # AITOFF DOES NOT PLAY WELL WITH ADDING LABELS - USE HAMMER PROJECTION INSTEAD
        ax = fig.add_subplot(111, projection='hammer')

        # RASTERIZED MAKES THE MAP BITMAP WHILE THE LABELS REMAIN VECTORIAL
        std = data.std()
        mean = data.mean()
        # image = ax.pcolormesh(long, lat, data, rasterized=False, cmap=cmap, vmin=mean, vmax=mean + 5 * std)

        # GRATICULE
        ax.set_longitude_grid(30)
        ax.set_latitude_grid(15)
        ax.xaxis.set_major_formatter(ThetaFormatterShiftPi(30))
        ax.set_longitude_grid_ends(90)

        if sunmoonContour:
            t = Time(header['DATE-OBS'], scale='utc')

            # FIND SUN AND PLACE ON CORRECT PLOT COORDINATE
            sun = get_sun(t)
            sun.ra.degree = -sun.ra.degree + 180
            if sun.ra.degree > 180.:
                sun.ra.degree -= 360
            sun.ra.radian = np.deg2rad(sun.ra.degree)

            # COMPUTE LONS AND LATS OF DAY/NIGHT TERMINATOR.
            nlons = 1441
            nlats = ((nlons - 1) / 2) + 1

            # COLOR IN THE SUN
            lons2 = np.linspace(-np.pi, np.pi, nlons)
            lats2 = np.linspace(-np.pi / 2, np.pi / 2, int(nlats))
            lons2, lats2 = np.meshgrid(lons2, lats2)
            sunlight = np.ones(lons2.shape)
            raSep = sun.ra.radian - lons2
            raSep[raSep > np.pi] = 2 * np.pi - raSep[raSep > np.pi]
            separation = ((raSep * np.cos((sun.dec.radian + lats2) / 2))**2 + (sun.dec.radian - lats2)**2)**0.5
            sunlight[separation < np.radians(33)] = 0
            sunyellow = matplotlib.colors.colorConverter.to_rgba('#b58900', alpha=0.2)
            ax.contourf(lons2, lats2, sunlight, 1, colors=[sunyellow, (0.0, 0.0, 0.0, 0.0)], zorder=3)

            # PLOT THE MOON
            moon = get_moon(t)
            moon.ra.degree = -moon.ra.degree + 180
            if moon.ra.degree > 180.:
                moon.ra.degree -= 360
            moon.ra.radian = np.deg2rad(moon.ra.degree)

            # COMPUTE LONS AND LATS OF DAY/NIGHT TERMINATOR.
            nlons = 1441
            nlats = ((nlons - 1) / 2) + 1

            # COLOR IN THE SUN
            lons2 = np.linspace(-np.pi, np.pi, nlons)
            lats2 = np.linspace(-np.pi / 2, np.pi / 2, int(nlats))
            lons2, lats2 = np.meshgrid(lons2, lats2)
            moonlight = np.ones(lons2.shape)
            raSep = moon.ra.radian - lons2
            raSep[raSep > np.pi] = 2 * np.pi - raSep[raSep > np.pi]
            separation = ((raSep * np.cos((moon.dec.radian + lats2) / 2))**2 + (moon.dec.radian - lats2)**2)**0.5
            moonlight[separation < np.radians(20)] = 0
            moonblue = matplotlib.colors.colorConverter.to_rgba('#268bd2', alpha=0.2)
            ax.contourf(lons2, lats2, moonlight, 1, colors=[moonblue, (0.0, 0.0, 0.0, 0.0)], zorder=3)

        # PLOT THE SUN
        if sunmoon:
            t = Time(header['DATE-OBS'], scale='utc')

            # FIND SUN AND PLACE ON CORRECT PLOT COORDINATE
            sun = get_sun(t)
            sun.ra.degree = -sun.ra.degree + 180
            if sun.ra.degree > 180.:
                sun.ra.degree -= 360
            sun.ra.radian = np.deg2rad(sun.ra.degree)

            label = "Sun"
            if sunmoonContour:
                label += " (within $33^o$)"
            ax.scatter(sun.ra.radian, sun.dec.radian, color="#b58900", alpha=0.8, s=20, marker="o", edgecolors="#cb4b16", linewidths=0.5, label=label, zorder=30)

            # PLOT THE MOON
            moon = get_moon(t)
            moon.ra.degree = -moon.ra.degree + 180
            if moon.ra.degree > 180.:
                moon.ra.degree -= 360
            moon.ra.radian = np.deg2rad(moon.ra.degree)

            label = "Moon"
            if sunmoonContour:
                label += " (within $20^o$)"
            ax.scatter(moon.ra.radian, moon.dec.radian, color="#268bd2", alpha=0.8, s=20, marker="o", edgecolors="#1e6ea7", linewidths=0.5, label=label, zorder=29)

        handles, labels = plt.gca().get_legend_handles_labels()
        if galacticPlane:
            # LON:LAT is lon 0-360 at lat=0
            lon_array = np.arange(0, 360, 0.5)
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
            planeColour = "#dc322f"
            ax.scatter(np.radians(gx), np.radians(gDec),
                       color=planeColour, alpha=1, s=1)
            line = Line2D([0], [0], label='Galactic Plane', color=planeColour)
            handles.append(line)

        if contours:
            mapDF.sort_values(["PROB"],
                              ascending=[False], inplace=True)
            mapDF["CUMPROB"] = np.cumsum(mapDF['PROB'])
            mapDF["CUMPROB"] = mapDF["CUMPROB"] * 100. * mapDF["PROB"].sum()
            mapDF.sort_index(inplace=True)
            contours = mapDF["CUMPROB"].values.reshape((ysize, xsize))

            colors = ['#474973', '#a69cac', '#03F7EB']
            levels = [90, 50, 10]

            z = 10

            for c, l in zip(colors, levels):
                z += 1
                ax.contourf(long, lat,
                            contours, levels=[0, l], colors=c, zorder=z, alpha=0.8)
                if "EXTRA" in self.meta and f"area{l}" in self.meta["EXTRA"]:
                    area = self.meta["EXTRA"][f"area{l}"]
                    label = f"{l}%: {area:.1f} deg$^2$"
                else:
                    label = f"{l}%"
                patch = mpatches.Patch(color=c, label=label)
                handles.append(patch)

        if len(self.meta):
            data = ""
            data += f"Event: {self.meta['ALERT']['superevent_id']}\n"
            eventDate = Time(self.meta['HEADER']['DATE-OBS'], scale='utc').to_datetime().strftime("%Y-%m-%d %H:%M:%S")
            data += f"Event time: {eventDate}\n"

            data += "\n"
            data += f"Alert: {self.meta['ALERT']['alert_type'].replace('_',' ')}\n"
            alertDate = Time(self.meta['ALERT']['time_created'], scale='utc').to_datetime().strftime("%Y-%m-%d %H:%M:%S")
            data += f"Alert time: {alertDate}\n"
            instruments = (",").join(self.meta['ALERT']['event']['instruments'])
            data += f"Instruments: {instruments}\n"
            data += f"Localisation: {self.meta['HEADER']['CREATOR']}\n"

            far = 1 / (float(self.meta['ALERT']['event']['far']) * 60. * 60. * 24.)
            if far > 1000:
                far /= 365.
                data += f"FAR: 1 per {far:0.1f} yrs\n"
            else:
                data += f"FAR: 1 per {far:0.1f} days\n"

            data += f"Dist: {self.meta['HEADER']['DISTMEAN']:.2f} (±{self.meta['HEADER']['DISTSTD']:.2f}) Mpc\n"

            data += "\n"
            for k, v in self.meta['ALERT']['event']['classification'].items():
                data += f"{k}: {v:.2f}\n"

            data += "\n"
            for k, v in self.meta['ALERT']['event']['properties'].items():
                data += f"{k}: {v:.2f}\n"

            plt.text(3.42, 0.2, data, ha='left', va='top', fontsize=5, linespacing=1.8)

        # this = ax.clabel(line_c, inline=True, fontsize=6, colors=['#93a1a1'], fmt='{:.0f} '.format)

        ax.tick_params(axis='x', labelsize=12)
        ax.tick_params(axis='y', labelsize=12)
        ax.grid(color='#657b83', alpha=0.2, linestyle='dotted')
        plt.grid(True)
        plt.legend(handles=handles, loc='upper left', scatterpoints=1, bbox_to_anchor=(1.01, 1), fontsize=6)
        ax.xaxis.zorder = 40

        plt.savefig(self.outputFolder + "/skymap.png", bbox_inches='tight', dpi=300)

        plt.close()

        self.log.debug('completed the ``convert`` method')
        return None
