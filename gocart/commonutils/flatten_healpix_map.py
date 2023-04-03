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
        - ``hdus`` -- the flatten map HDUs
        - ``table`` -- the astropy table of the map

    ```eval_rst
    .. todo::

        - create a sublime snippet for usage
        - add a tutorial about ``subtract_calibrations`` to documentation
    ```

    ```python
    from gocart.commonutils import flatten_healpix_map
    hdus = flatten_healpix_map(
        log=log,
        mapPath=pathToOutputDir + "/bayestar.multiorder.fits",
        nside=64
    )
    hdus.writeto('/tmp/filename.fits', checksum=True)
    ```
    """
    log.debug('starting the ``flatten_healpix_map`` function')

    import astropy_healpix as ah
    from astropy.io import fits
    from ligo.skymap.bayestar import rasterize
    from ligo.skymap.io import read_sky_map, write_sky_map
    from astropy.table import Table
    import tempfile

    hdus = fits.open(mapPath)
    order = ah.nside_to_level(nside)
    ordering = hdus[1].header['ORDERING']
    if ordering != 'NUNIQ':
        log.info("Map is already flattened")
    table = read_sky_map(hdus, moc=True)
    table = rasterize(table, order=order)
    with tempfile.NamedTemporaryFile(suffix='.fits') as f:
        write_sky_map(f.name, table, nest=True)
        hdus = fits.open(f.name)

    log.debug('completed the ``flatten_healpix_map`` function')
    return hdus, table
