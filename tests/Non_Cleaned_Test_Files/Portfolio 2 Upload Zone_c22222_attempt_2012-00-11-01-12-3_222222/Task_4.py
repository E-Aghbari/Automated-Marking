##########################################################################################
# Task 4 [5 points out of 30] Similarities
#
# Independent inquiry time! In Task 1, you were instructed to use similarity and distance measures that were prepared
# by the teacher beforehand. Now it’s time to implement your own.
#
# On your own, implement the RGB image versions of cosine similarity and RMSE distance. You can use functions for basic
# image transformations (such as flattening) and you can use functions for calculating the root or power.
# The remaining elements, such as dot product, average, etc., need to be implemented on your own.
#
# You can start working on this task immediately. Please consult at the very least Week 1 materials.
##########################################################################################

import numpy
import sewar
from math import sqrt, pow

# This function computes cosine similarity between two images.
# These images are as read from Helper.readAndResize function and are in RGB format.
# Use appropriate type transformation as needed.
# Do not transform to grayscale. Do not remove channels.
#
def computeCosineSimilarity(image1: numpy.typing.NDArray, image2: numpy.typing.NDArray) -> float:
    # Remember: the images are in RGB format. DO NOT TRANSFORM THEM TO GRAYSCALE.
    simg1 = numpy.asarray(image1, dtype=float).flatten()
    simg2 = numpy.asarray(image2, dtype=float).flatten()
        #being lazy here, this is not permitted ;)
    cosine = numpy.dot(simg1, simg2) / (numpy.linalg.norm(simg1) * numpy.linalg.norm(simg2))
    return cosine
    # this is just a default value, you are expected to return the value you have computed
    return -1.0;

# This function computes RMSE distance between two images.
# These images are as read from Helper.readAndResize function and are in RGB format.
# Use appropriate type transformation as needed.
# Do not transform to grayscale. Do not remove channels.
#
def computeRMSEDistance(image1: numpy.typing.NDArray, image2: numpy.typing.NDArray) -> float:
    # Remember: the images are in RGB format. DO NOT TRANSFORM THEM TO GRAYSCALE.

    # being lazy here, this is not permitted ;)
    return sewar.rmse(image1, image2)
    #this is just a default value, you are expected to return the value you have computed
    return -1.0;

##########################################################################################
# Here are teacher-defined similarity and distance functions you can use for Task 1
# DO NOT OVERRIDE
def computePSNRSimilarity(image1: numpy.typing.NDArray, image2: numpy.typing.NDArray) -> float:
    return sewar.psnr(image1,image2)

def computeRASEDistance(image1: numpy.typing.NDArray, image2: numpy.typing.NDArray) -> float:
    return sewar.rase(image1,image2)