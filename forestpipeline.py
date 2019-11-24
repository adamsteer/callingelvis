#! /usr/bin/python3
"""
Pipeline for running forest structure metrics



"""

import forestmetrics

import numpy as np

import pdal
from osgeo import gdal
import shapely

import boto3
import os
import sys

from callingelvis.anybodyhome import anybodyhome


def forestpipeline(elvisparams):


    bbox = elvisparams["bbox"]
    pointtype = elvisparams["pointtype"]
    collection = elvisparams["collection"]
    year = elvisparams["year"]
    heightref = elvisparams["heightref"]
    
    ## first call elvis
    files = callelvis(bbox, pointtype, collection, year, heightref)


    ## next parse results into an array that can be delivered to an
    # iterative *or* parallel processing pipeline



    ## next fetch results and process.
