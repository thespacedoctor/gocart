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
        - ``mapPath`` -- path the the healpix map
        - ``settings`` -- the settings dictionary

    **Usage:**

    To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_). 

    To initiate a ascii object, use the following:

    ```eval_rst
    .. todo::

        - add usage info
        - create a sublime snippet for usage
        - create cl-util for this class
        - add a tutorial about ``ascii`` to documentation
        - create a blog post about what ``ascii`` does
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
        log.debug("instansiating a new 'ascii' object")
        self.settings = settings
        self.mapPath = mapPath

        self.hdus, self.table = flatten_healpix_map(
            log=log,
            mapPath=self.mapPath,
            nside=64
        )

        # hdus.writeto('/tmp/filename.fits', checksum=True)

        return None

    def convert(
            self,
            outputFilepath=False):
        """
        *get the ascii object*

        **Key Arguments:**
            - ``outputFilepath`` -- optionally write content to file. Default *False*

        **Return:**
            - ``ascii``

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

        tableData = self.table.to_pandas()

        asciiContent = tableData.to_csv(index=False)

        if outputFilepath:
            import codecs
            with codecs.open(outputFilepath, encoding='utf-8', mode='w') as writeFile:
                writeFile.write(asciiContent)

        self.log.debug('completed the ``get`` method')
        return asciiContent

    # xt-class-method

    # 5. @flagged: what actions of the base class(es) need ammending? ammend them here
    # Override Method Attributes
    # method-override-tmpx
