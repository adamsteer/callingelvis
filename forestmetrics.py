#! /usr/bin/python3

"""
Placeholder for forest metric computation functions

Re-writing MATLAB code produced by Prof. Albert Van Dijk in Python+PDAL

"""

import pdal
from osgeo import gdal
import numpy as np


# from TERN:
# VH(xm,ym) = median(zs3(ir3==1 &  class3~=2 & class3~=6 & class3~=9 )) -DEMh ;

#veg cover fraction
#VCF = (nFirst - Nsingle) / Nfirst

#canopy layering index
# CLI =

# noting here that most LiDAR is only accurate to +-0.3m (ICSM spec)
# so a threshold height below 0.25m may be noise, or it may be signal...
threshold_heights =[0.05, 0.10, 0.25, 0.5, 1, 2, 3]

def vh(input_points, resolution):
    """
    function to create vegetation heights, or normalised heights from input lidar
    points.
    - uses only vegetation classes
    - emits a gap filled raster
    - relies on a 'ground class'

    Using a PDAL approach we:
    - read a file
    -
    - apply an ELM filter and tag low points as noise
    - compute height above ground
    - write a GDAL raster at the required resolution

    """

    pipeline = {
      "pipeline": [
        {
            "type": "readers.las",
            "filename": infile
        },
        {
            "type":"filters.elm",
            "class":18
        },
        {
          "type": "filters.ferry",
          "dimensions": "=>HeightAboveGround"
        },
        {
            "type":"filters.hag",
        }
      ]
    }
