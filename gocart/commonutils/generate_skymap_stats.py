#!/usr/bin/env python
# encoding: utf-8
"""
*Generate some extra stats for a given Healpix map*

:Author:
    David Young

:Date Created:
    March 30, 2023
"""
from fundamentals import tools
from builtins import object
import sys
import os
os.environ['TERM'] = 'vt100'


def generate_skymap_stats(
        skymap,
        log):
    """*Generate some extra stats for a given Healpix map*

    **Key Arguments:**
        - ``skymap`` -- either a path to a healpix map FITS file or a skymap in astropy table format
        - ``log`` -- logger

    **Return:**
        - ``extras`` -- a diction of value added map stats

    ```python
    from gocart.commonutils import generate_skymap_stats
    extras = generate_skymap_stats(
        log=log,
        skymap="path/to/bayestar.multiorder.fits",
    )
    ```
    """
    log.debug('starting the ``generate_skymap_stats`` function')

    from astropy.table import Table
    import astropy_healpix as ah
    import astropy.units as u
    import numpy as np
    if isinstance(skymap, str):
        skymap = Table.read(skymap)

    tableData = skymap.to_pandas()

    # FIND LEVEL AND NSIDE PIXEL INDEX FOR EACH MULTI-RES PIXEL
    tableData['LEVEL'], tableData['IPIX'] = ah.uniq_to_level_ipix(tableData['UNIQ'])
    tableData['NSIDE'] = ah.level_to_nside(tableData['LEVEL'])
    # DETERMINE THE PIXEL AREA AND PROB OF EACH PIXEL
    tableData['AREA'] = ah.nside_to_pixel_area(tableData['NSIDE']).to_value(u.steradian)
    tableData['PROB'] = tableData['AREA'] * tableData["PROBDENSITY"]
    tableData['AREA'] = ah.nside_to_pixel_area(tableData['NSIDE']).to_value(u.deg**2)

    # SORT BY PROB, CALCULATE CUMULATIVE PROB AND RESORT BY INDEX
    tableData.sort_values(["PROB"],
                          ascending=[False], inplace=True)
    tableData["CUMPROB"] = np.cumsum(tableData['PROB'])

    # FILTER DATA FRAME
    # FIRST CREATE THE MASK
    mask = (tableData["CUMPROB"] < 0.9)
    area90 = tableData.loc[mask, 'AREA'].sum()
    mask = (tableData["CUMPROB"] < 0.5)
    area50 = tableData.loc[mask, 'AREA'].sum()
    mask = (tableData["CUMPROB"] < 0.1)
    area10 = tableData.loc[mask, 'AREA'].sum()

    area90 = float(f'{area90:.3f}')
    area50 = float(f'{area50:.3f}')
    area10 = float(f'{area10:.3f}')

    extras = {"area90": area90, "area50": area50, "area10": area10}

    level, ipix = ah.uniq_to_level_ipix(
        skymap[np.argmax(skymap['PROBDENSITY'])]['UNIQ']
    )
    ra, dec = ah.healpix_to_lonlat(ipix, ah.level_to_nside(level),
                                   order='nested')

    from astropy.coordinates import SkyCoord
    galacticCoords = SkyCoord(ra, dec, frame='icrs').galactic
    glon = galacticCoords.l.degree
    glat = galacticCoords.b.degree

    extras["central coordinate"] = {
        "equatorial": f"{ra.deg:.6f} {dec.deg:.6f}",
        "galactic": f"{glon:.6f} {glat:.6f}"
    }

    log.debug('completed the ``generate_skymap_stats`` function')
    return extras
