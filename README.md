# gocart

[![](https://zenodo.org/badge/614846695.svg)](https://zenodo.org/badge/latestdoi/614846695)  

<!-- INFO BADGES -->  

[![](https://img.shields.io/pypi/pyversions/gocart)](https://pypi.org/project/gocart/)
[![](https://img.shields.io/pypi/v/gocart)](https://pypi.org/project/gocart/)
[![](https://img.shields.io/conda/vn/conda-forge/gocart)](https://anaconda.org/conda-forge/gocart)
[![](https://pepy.tech/badge/gocart)](https://pepy.tech/project/gocart)
[![](https://img.shields.io/github/license/thespacedoctor/gocart)](https://github.com/thespacedoctor/gocart)


<!-- STATUS BADGES -->  

[![](https://soxs-eso-data.org/ci/buildStatus/icon?job=gocart%2Fmain&subject=build%20main)](https://soxs-eso-data.org/ci/blue/organizations/jenkins/gocart/activity?branch=main)
[![](https://soxs-eso-data.org/ci/buildStatus/icon?job=gocart%2Fdevelop&subject=build%20dev)](https://soxs-eso-data.org/ci/blue/organizations/jenkins/gocart/activity?branch=develop)
[![](https://cdn.jsdelivr.net/gh/thespacedoctor/gocart@main/coverage.svg)](https://raw.githack.com/thespacedoctor/gocart/main/htmlcov/index.html)
[![](https://readthedocs.org/projects/gocart/badge/?version=main)](https://gocart.readthedocs.io/en/main/)
[![](https://img.shields.io/github/issues/thespacedoctor/gocart/type:%20bug?label=bug%20issues)](https://github.com/thespacedoctor/gocart/issues?q=is%3Aissue+is%3Aopen+label%3A%22type%3A+bug%22+)  

*gocart is a python package and command-line suite used to consume [GCN Kafka streams](https://gcn.nasa.gov).*.

Documentation for gocart is hosted by [Read the Docs](https://gocart.readthedocs.io/en/main/) ([development version](https://gocart.readthedocs.io/en/develop/) and [main version](https://gocart.readthedocs.io/en/main/)). The code lives on [github](https://github.com/thespacedoctor/gocart). Please report any issues you find [here](https://github.com/thespacedoctor/gocart/issues).

## Features

- Listen to GCN Kafka streams (currently  LIGO-Virgo-KAGRA only) and write alerts and skymaps to the local filesystem.
- Ability to 'echo' the Kafka stream by re-listening to the last N days of alerts (provided the alerts are still hosted on the GCN Kafka cluster).
- Alert content, FITS Header data and some extra value-added event parameters are written to a single machine-readable YAML file.
- The healpix skymaps are optionally converted to ascii files (one row per healpix pixel) and/or rendered as aitoff plots.
- Create your own plugin scripts to run whenever an alert is parsed.


## Installation

The easiest way to install gocart is to use `conda`:

``` bash
conda create -n gocart python=3.9 pip gocart -c conda-forge
conda activate gocart
```

To upgrade to the latest version of gocart use the command:

``` bash
conda upgrade gocart -c conda-forge
```

It is also possible to install via pip if required:

``` bash
pip install gocart
```

Or you can clone the [github repo](https://github.com/thespacedoctor/gocart) and install from a local version of the code:

``` bash
git clone git@github.com:thespacedoctor/gocart.git
cd gocart
python setup.py install
```

To check installation was successful run `gocart -v`. This should return the version number of the install.

## Initialising gocart

Before using gocart you need to use the `init` command to generate a user settings file. Running the following creates a [yaml](https://learnxinyminutes.com/docs/yaml/) settings file in your home folder under `~/.config/gocart/gocart.yaml`:

```bash
gocart init
```

The file is initially populated with gocart's default settings which can be adjusted to your preference.

If at any point the user settings file becomes corrupted or you just want to start afresh, simply trash the `gocart.yaml` file and rerun `gocart init`.

## GCN Kafka Credentials

When you first come to use gocart, you will need to add a GCN Kafka Client ID and Secret to the `gocart.yaml` settings file. To get these credentials you will need to signup for a [GCN Notices account here](https://gcn.nasa.gov/quickstart).

[![](https://live.staticflickr.com/65535/52790651039_d88a05a4f5_b.jpg)](https://live.staticflickr.com/65535/52790651039_d88a05a4f5_b.jpg)

Once signed in, fill in a suitable name for your new client (any name will do, so gocart is as good a name as any). Fill in the captcha and click 'Create New Credentials'.

[![](https://live.staticflickr.com/65535/52790654254_2b3611c714_z.png)](https://live.staticflickr.com/65535/52790654254_2b3611c714_o.png)

In the 'Customize Alerts' section, don't be concerned about what Notice Types to select as these are only used to generate template code in the next section. Not selecting any is fine. Click the 'Generate Code' button. You will now be presented with your newly created client credentials within the body of the code snippet:

[![](https://live.staticflickr.com/65535/52790833500_7535fd6b34_z.png)](https://live.staticflickr.com/65535/52790833500_7535fd6b34_o.png)

Open your gocart settings file at `~/.config/gocart/gocart.yaml` and copy and paste these credentials into the appropriate place.

[![](https://live.staticflickr.com/65535/52790845580_b5a1145e13_z.png)](https://live.staticflickr.com/65535/52790845580_b5a1145e13_o.png)

Don't worry about the `group_id` parameter, it's initially set to XXXX but gocart will replace this with a unique value when it's first run. It is this `group_id` that allows GCN Kafka to remember which alerts you have or have not heard before. Note the example client above has been deleted, so the credentials quoted here will not work.

You are now ready to start using gocart.

## How to cite gocart

If you use `gocart` in your work, please cite using the following BibTeX entry: 

```bibtex
@software{Young_gocart,
author = {Young, David R.},
doi = {10.5281/zenodo.7970743},
license = {GPL-3.0-only},
title = {{gocart}},
url = {https://github.com/thespacedoctor/gocart}
}
```
