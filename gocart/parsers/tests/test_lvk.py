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
if not os.path.exists(pathToOutputDir + "/lvk_events/"):
    os.makedirs(pathToOutputDir + "/lvk_events/")

testAlerts = [
    'MS181101ab-earlywarning.json',
    'MS181101ab-initial.json',
    'MS181101ab-preliminary.json',
    'MS181101ab-retraction.json',
    'MS181101ab-update.json'
]


settings["lvk"]["download_dir"] = pathToOutputDir + "/lvk_events/"


# xt-setup-unit-testing-files-and-folders
# xt-utkit-refresh-database

class test_lvk(unittest.TestCase):

    def test_lvk_function(self):

        for a in testAlerts:
            # READ THE FILE TO MEMORY (LIKE ALERT STREAM)
            with open(f'{pathToInputDir}/{a}', 'r') as f:
                record = f.read()

            from gocart.parsers import lvk
            parser = lvk(
                log=log,
                record=record,
                settings=settings
            ).parse()

    def test_lvk_function_exception(self):

        from gocart import lvk
        try:
            this = lvk(
                log=log,
                settings=settings,
                fakeKey="break the code"
            )
            this.get()
            assert False
        except Exception as e:
            assert True
            print(str(e))

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
