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


# OR YOU CAN REMOVE THE CLASS BELOW AND ADD A WORKER FUNCTION ... SNIPPET TRIGGER BELOW
# xt-worker-def

class flatten_healpix_map(object):
    """
    *The worker class for the flatten_healpix_map module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``mapPath`` -- path to the multiorder map.
        - ``settings`` -- the settings dictionary

    **Usage:**

    To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_). 

    To initiate a flatten_healpix_map object, use the following:

    ```eval_rst
    .. todo::

        - add usage info
        - create a sublime snippet for usage
        - create cl-util for this class
        - add a tutorial about ``flatten_healpix_map`` to documentation
        - create a blog post about what ``flatten_healpix_map`` does
    ```

    ```python
    from gocart.commonutils import flatten_healpix_map
    f = flatten_healpix_map(
        log=self.log,
        settings=self.settings,
        mapPath=self.mapPath
    )
    hdus = f.flatten()
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
        log.debug("instansiating a new 'flatten_healpix_map' object")
        self.settings = settings
        self.mapPath = mapPath

        # xt-self-arg-tmpx

        # 2. @flagged: what are the default attrributes each object could have? Add them to variable attribute set here
        # Variable Data Atrributes

        # 3. @flagged: what variable attrributes need overriden in any baseclass(es) used
        # Override Variable Data Atrributes

        # Initial Actions

        return None

    # 4. @flagged: what actions does each object have to be able to perform? Add them here
    # Method Attributes
    def flatten(
            self,
            nside=64):
        """
        *flatten the multi-order map to nsides*

        **Return:**
            - ``flatten_healpix_map``

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
        self.log.debug('starting the ``get`` method')

        import astropy_healpix as ah
        from astropy.io import fits
        from ligo.skymap.bayestar import rasterize
        from ligo.skymap.io import read_sky_map, write_sky_map
        from astropy.table import Table
        import tempfile

        hdus = fits.open(self.mapPath)
        order = ah.nside_to_level(nside)
        ordering = hdus[1].header['ORDERING']
        if ordering != 'NUNIQ':
            self.log.info("Map is already flattened")
        table = read_sky_map(hdus, moc=True)
        table = rasterize(table, order=order)
        with tempfile.NamedTemporaryFile(suffix='.fits') as f:
            write_sky_map(f.name, table, nest=True)
            hdus = fits.open(f.name)

        self.log.debug('completed the ``get`` method')
        return hdus

    # xt-class-method

    # 5. @flagged: what actions of the base class(es) need ammending? ammend them here
    # Override Method Attributes
    # method-override-tmpx
