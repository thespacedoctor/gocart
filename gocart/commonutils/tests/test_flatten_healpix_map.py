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

class test_flatten_healpix_map(unittest.TestCase):

    def test_flatten_healpix_map_function(self):

        from gocart.commonutils import flatten_healpix_map
        hdus, table = flatten_healpix_map(
            log=log,
            mapPath=pathToOutputDir + "/bayestar.multiorder.fits",
            nside=64
        )
        hdus.writeto(pathToOutputDir + "/bayestar.nside64.fits", checksum=True)

    def test_flatten_healpix_map_function_exception(self):

        from gocart.commonutils import flatten_healpix_map
        try:
            hdus, table = flatten_healpix_map(
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
