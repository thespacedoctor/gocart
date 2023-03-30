from __future__ import print_function
from builtins import str
import os
import unittest
import shutil
import unittest
import yaml
from gocart.utKit import utKit
from fundamentals import tools
from os.path import expanduser
home = expanduser("~")

packageDirectory = utKit("").get_project_root()
settingsFile = packageDirectory + "/test_settings.yaml"
# settingsFile = home + \
#     "/git_repos/_misc_/settings/gocart/test_settings.yaml"

su = tools(
    arguments={"settingsFile": settingsFile},
    docString=__doc__,
    logLevel="DEBUG",
    options_first=False,
    projectName=None,
    defaultSettingsFile=False
)
arguments, settings, log, dbConn = su.setup()

# SETUP PATHS TO COMMON DIRECTORIES FOR TEST DATA
moduleDirectory = os.path.dirname(__file__)
pathToInputDir = moduleDirectory + "/input/"
pathToOutputDir = moduleDirectory + "/output/"

try:
    shutil.rmtree(pathToOutputDir)
except:
    pass
# COPY INPUT TO OUTPUT DIR
shutil.copytree(pathToInputDir, pathToOutputDir)

# Recursively create missing directories
if not os.path.exists(pathToOutputDir):
    os.makedirs(pathToOutputDir)


# xt-setup-unit-testing-files-and-folders
# xt-utkit-refresh-database

class test_healpix2cart(unittest.TestCase):

    def test_create_wcs_and_pixels(self):

        from gocart.convert import create_wcs_and_pixels
        wcs, mapDF = create_wcs_and_pixels(log=log)
        from tabulate import tabulate
        print(tabulate(mapDF.head(100), headers='keys', tablefmt='psql'))

    def test_healpix2cart_function(self):

        from gocart.convert import healpix2cart
        converter = healpix2cart(
            log=log,
            mapPath=pathToOutputDir + "/bayestar.multiorder.fits",
            settings=settings
        )
        converter.convert()

    def test_healpix2cart_function_exception(self):

        from gocart.convert import healpix2cart
        try:
            this = healpix2cart(
                log=log,
                settings=settings,
                fakeKey="break the code"
            )
            assert False
        except Exception as e:
            assert True
            print(str(e))

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
