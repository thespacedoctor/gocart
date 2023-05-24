#!/usr/bin/env python
# encoding: utf-8
"""
*Flatten a Healpix Multi-Order Map*

:Author:
    David Young

:Date Created:
    March 24, 2023
"""
from fundamentals import tools
from builtins import object
import sys
import os
os.environ['TERM'] = 'vt100'


def flatten_healpix_map(
        log,
        mapPath,
        nside=64):
    """flatten a multiorder healpix map to a specific nside*

    **Key Arguments:**
        - ``log`` -- logger
        - ``mapPath`` -- path to the multiorder map
        - ``nside`` -- the nside index to flatten the map to. Default *64* (~0.9 deg2 pixels)

    **Return:**
        - ``skymap`` -- the astropy table of the map

    ```eval_rst
    .. todo::

        - create a sublime snippet for usage
        - add a tutorial about ``subtract_calibrations`` to documentation
    ```

    ```python
    from gocart.commonutils import flatten_healpix_map
    skymap = flatten_healpix_map(
        log=log,
        mapPath=pathToOutputDir + "/bayestar.multiorder.fits",
        nside=64
    )
    ```
    """
    log.debug('starting the ``flatten_healpix_map`` function')

    from mhealpy.pixelfunc.moc import uniq2range
    import tempfile
    from astropy.io import fits
    from astropy.table import Table
    import astropy_healpix as ah
    import astropy.units as u
    import numpy as np
    import pandas as pd
    from tabulate import tabulate

    # OPEN MAP TO DATAFRAME
    skymap = Table.read(mapPath)
    tableData = skymap.to_pandas()
    # FIND LEVEL AND NSIDE PIXEL INDEX FOR EACH MULTI-RES PIXEL
    tableData['LEVEL'], tableData['IPIX'] = ah.uniq_to_level_ipix(tableData['UNIQ'])
    tableData['NSIDE'] = ah.level_to_nside(tableData['LEVEL'])
    # DETERMINE THE PIXEL AREA AND PROB OF EACH PIXEL
    tableData['AREA'] = ah.nside_to_pixel_area(tableData['NSIDE']).to_value(u.steradian)
    tableData['PROB'] = tableData['AREA'] * tableData["PROBDENSITY"]

    level = ah.nside_to_level(nside)

    # UPSAMPLE TABLE
    # FIND THE HIGH-LEVEL PIXEL INDEXES FOR EACH UNIQ PIXEL
    # MAKE A NEW DATAFRAME WITH IPIX64, UNIQ
    # MATCH EACH NEW UNIQ AGAIN ORIGINAL FRAME UNIQ TO GENERATE DATA FOR IPIX^$ FRAME
    mask = tableData['NSIDE'] <= nside
    upTable = tableData.loc[mask].copy()
    upTable.reset_index(inplace=True)
    this = uniq2range(nside, upTable['UNIQ'])
    upTable[f'IPIX{nside}'] = [list(range(i, j)) for i, j in zip(this[0], this[1])]
    upTable[f'UNIQLIST'] = upTable.apply(lambda x: [x['UNIQ']] * len(x[f'IPIX{nside}']), axis=1)

    ipixNside = np.concatenate(upTable[f'IPIX{nside}'])
    uniqList = np.concatenate(upTable[f'UNIQLIST'])
    # CREATE DATA FRAME FROM A DICTIONARY OF LISTS
    myDict = {
        f'IPIX{nside}': ipixNside,
        f'UNIQ': uniqList
    }
    upTable = pd.DataFrame(myDict)
    # MERGE DATAFRAMES
    upTable = upTable.merge(tableData, on=['UNIQ'], how='inner')[[f'IPIX{nside}', 'PROBDENSITY', 'DISTMU', 'DISTSIGMA', 'DISTNORM']]
    pixArea = ah.nside_to_pixel_area(nside).to_value(u.steradian)
    upTable["PROB"] = upTable["PROBDENSITY"] * pixArea
    # REMOVE COLUMN FROM DATA FRAME
    upTable.drop(columns=['PROBDENSITY'], inplace=True)

    # DOWNSAMPLE TABLE
    mask = tableData['NSIDE'] > nside
    downTable = tableData.loc[mask].copy()
    downTable.reset_index(inplace=True)

    # FIND THE PIXEL INDEX AT ORDER NSIDE
    downTable[f'IPIX{nside}'] = np.floor_divide(tableData.loc[mask, 'IPIX'], np.power(4, (tableData.loc[mask, 'LEVEL'].values - level)))
    # GROUP RESULTS
    downTable = downTable.groupby([f'IPIX{nside}']).agg({'PROB': 'sum', 'DISTMU': 'mean', 'DISTSIGMA': 'mean', 'DISTNORM': 'mean'})
    downTable.reset_index(inplace=True)

    skymap = pd.concat([downTable, upTable], ignore_index=True)
    # SORT BY COLUMN NAME
    skymap.sort_values([f'IPIX{nside}'],
                       ascending=[True], inplace=True)

    # SET INDEX AND SORT DATA FRAME
    skymap.reset_index(inplace=True)
    skymap.drop(columns=[f'IPIX{nside}', 'index'], inplace=True)

    # REMOVE FILTERED ROWS FROM DATA FRAME
    mask = (skymap['DISTMU'].isnull())
    skymap.loc[mask, 'DISTMU'] = np.inf

    log.debug('completed the ``flatten_healpix_map`` function')
    return skymap
