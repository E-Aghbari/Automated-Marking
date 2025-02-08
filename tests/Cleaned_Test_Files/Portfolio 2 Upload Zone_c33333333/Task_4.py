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
    simg1 = image1.flatten()
    simg2 = image2.flatten()
    dot = 0;
    s1 = 0
    s2 = 0
    for i in range(0, len(simg1)):
        dot += simg1[i] * simg2[i]
        s1 += simg1[i] * simg1[i]
        s2 += simg2[i] * simg2[i]
    cosine = dot / (sqrt(s1) * sqrt(s2))
    return cosine

# This function computes RMSE distance between two images.
# These images are as read from Helper.readAndResize function and are in RGB format.
# Use appropriate type transformation as needed.
# Do not transform to grayscale. Do not remove channels.
#
def computeRMSEDistance(image1: numpy.typing.NDArray, image2: numpy.typing.NDArray) -> float:
    # Remember: the images are in RGB format. DO NOT TRANSFORM THEM TO GRAYSCALE.
    simg1 = image1.flatten()
    simg2 = image2.flatten()
    mse = 0
    for i in range(0,len(simg1)):
        mse += pow(simg1[i]-simg2[i],2)
    mse = mse/len(simg1)
    rmse = sqrt(mse)
    return rmse

##########################################################################################
# Here are teacher-defined similarity and distance functions you can use for Task 1
# DO NOT OVERRIDE
def computePSNRSimilarity(image1: numpy.typing.NDArray, image2: numpy.typing.NDArray) -> float:
    return sewar.psnr(image1,image2)

def computeRASEDistance(image1: numpy.typing.NDArray, image2: numpy.typing.NDArray) -> float:
    return sewar.rase(image1,image2)