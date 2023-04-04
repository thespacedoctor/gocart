# gocart

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





