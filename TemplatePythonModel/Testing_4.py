# https://gist.github.com/clayg/3787160
import copy
import unittest
import sys
import cv2
import logging

import scipy.spatial.distance as distances
import sewar

import Helper
import Task_4
import Testing_1
from Task_4 import *
import Dummy
sys.tracebacklimit = 6
width = 60
height = 30


numpy.seterr(divide='raise')
numpy.seterr(invalid='raise')


img1 = Helper.readAndResize("../testing_files/1.jpg")

img2 = Helper.readAndResize("../testing_files/3.jpg")
#
img_red = cv2.cvtColor(cv2.imread("../testing_files/red.jpg"), cv2.COLOR_BGR2RGB)
# # 0 0 0
img_black = cv2.cvtColor(cv2.imread("../testing_files/black.jpg"), cv2.COLOR_BGR2RGB)
# # 255 255 255
img_white = cv2.cvtColor(cv2.imread("../testing_files/white.jpg"), cv2.COLOR_BGR2RGB)
# # 200 200 200
img_gray = cv2.cvtColor(cv2.imread("../testing_files/gray.jpg"), cv2.COLOR_BGR2RGB)

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG, filename='test_4.log', filemode='w')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# Helper functions
def gray_cosine_sim(image1, image2):
    gsimg1 = cv2.cvtColor(image1, cv2.COLOR_RGB2GRAY)
    gsimg2 = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)
    simg1 = numpy.asarray(gsimg1, dtype=float).flatten()
    simg2 = numpy.asarray(gsimg2, dtype=float).flatten()
    cosine = numpy.dot(simg1, simg2) / (numpy.linalg.norm(simg1) * numpy.linalg.norm(simg2))
    return cosine

def cosine_sim(image1, image2):
    simg1 = numpy.asarray(image1, dtype=float).flatten()
    simg2 = numpy.asarray(image2, dtype=float).flatten()
    cosine = numpy.dot(simg1, simg2) / (numpy.linalg.norm(simg1) * numpy.linalg.norm(simg2))
    return cosine

def gray_cosine_dis(image1, image2):
    gsimg1 = cv2.cvtColor(image1, cv2.COLOR_RGB2GRAY)
    gsimg2 = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)
    simg1 = numpy.asarray(gsimg1, dtype=float).flatten()
    simg2 = numpy.asarray(gsimg2, dtype=float).flatten()
    return distances.cosine(simg1, simg2)


def cosine_dis(image1, image2):
    simg1 = numpy.asarray(image1, dtype=float).flatten()
    simg2 = numpy.asarray(image2, dtype=float).flatten()
    return distances.cosine(simg1, simg2)

def gray_rmse_sim(image1, image2):
    gsimg1 = cv2.cvtColor(image1, cv2.COLOR_RGB2GRAY)
    gsimg2 = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)
    simg1 = numpy.asarray(gsimg1, dtype=float).flatten()
    simg2 = numpy.asarray(gsimg2, dtype=float).flatten()
    return -sewar.rmse(simg1, simg2)

def rmse_sim(image1, image2):
    simg1 = numpy.asarray(image1, dtype=float).flatten()
    simg2 = numpy.asarray(image2, dtype=float).flatten()
    return -sewar.rmse(simg1, simg2)

def gray_rmse_dis(image1, image2):
    gsimg1 = cv2.cvtColor(image1, cv2.COLOR_RGB2GRAY)
    gsimg2 = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)
    simg1 = numpy.asarray(gsimg1, dtype=float).flatten()
    simg2 = numpy.asarray(gsimg2, dtype=float).flatten()
    return sewar.rmse(simg1, simg2)


def rmse_dis(image1, image2):
    simg1 = numpy.asarray(image1, dtype=float).flatten()
    simg2 = numpy.asarray(image2, dtype=float).flatten()
    return sewar.rmse(simg1, simg2)

places = 10
class Task_4_Testing(Testing_1.BaseTestCase):

    def test1_computeCosineSimilarity(self):
        measure_function = Task_4.computeCosineSimilarity
        student_output = measure_function(copy.deepcopy(img1), copy.deepcopy(img2))

        # We first check if it returns what it is supposed to, rounded to given decimal places for convenience
        expected_output = cosine_sim(copy.deepcopy(img1), copy.deepcopy(img2))
        val1 = round(float(student_output), places)
        val2 = round(float(expected_output), places)

        res = (val1 == val2)
        logger.debug(
            "student computeCosineSimilarity against staff;Correct {}; on input {}. Staff produced {} and student produced {}. Check if type corrections take place outside of measure function.".format(
                str(res) + '***********************\n',
                "img1 and img2", val2, val1))
        with self.subTest(msg = "Checking if cosine similarity is computed fine"):
            self.assertEqual(res, True,
                             "student computeCosineSimilarity against staff do not return the same value on img1 and img2")
        if not res:
            # We now check if problem is due to lack of type conversion
            student_output = measure_function(numpy.asarray(img1, dtype=float), numpy.asarray(img2, dtype=float))
            val1 = round(float(student_output), places)
            val2 = round(float(expected_output), places)

            res = (val1 == val2)
            logger.debug(
                "student computeCosineSimilarity against staff with type conversion;Correct {}; on input {}. Staff produced {} and student produced {}. Check if type corrections take place outside of measure function.".format(
                    str(res) + '***********************\n',
                    "img1 and img2", val2, val1))
            with self.subTest(msg="Checking if cosine similarity is computed fine if image type is fixed"):
                self.assertEqual(res, True,
                                 "student computeCosineSimilarity against staff do not return the same value on img1 and img2 even after type conversion")

        # We now check if it got transformed to gray scale when it shouldn't have - WARNING: more than one way to transform to grayscale!
        if not res:
            student_output = measure_function(copy.deepcopy(img1), copy.deepcopy(img2))
            expected_output = gray_cosine_sim(copy.deepcopy(img1), copy.deepcopy(img2))
            val1 = round(float(student_output), places)
            val2 = round(float(expected_output), places)

            res = (val1 == val2)
            logger.debug(
                "student computeCosineSimilarity computed with grayscale;Correct {}; on input {}. Staff produced {} and student produced {}. Check if type corrections take place outside of measure function.".format(
                    str(res) + '***********************\n',
                    "img1 and img2", val2, val1))
            with self.subTest(msg = "Checking if cosine similarity is computed with grayscale"):
                self.assertEqual(res, True,
                                 "student computeCosineSimilarity against grayscale staff do not return the same value on img1 and img2")

        # We now do the same in case similarity got confused with distance - WARNING: more than one way to transform similarity to distance!
        if not res:
            expected_output = cosine_dis(copy.deepcopy(img1), copy.deepcopy(img2))
            val1 = round(float(student_output), places)
            val2 = round(float(expected_output), places)

            res = (val1 == val2)
            logger.debug(
                "student computeCosineSimilarity confused with distance;Correct {}; on input {}. Staff produced {} and student produced {}. Check if type corrections take place outside of measure function.".format(
                    str(res) + '***********************\n',
                    "img1 and img2", val2, val1))
            with self.subTest(msg = "Checking if cosine similarity got confused with distance"):
                self.assertEqual(res, True,
                                 "student computeCosineSimilarity did not get confused with distance on img1 and img2")

        # We now do the same in case similarity got confused with grayscale distance - WARNING: more than one way to transform similarity to grayscale distance!
        if not res:
            expected_output = gray_cosine_dis(copy.deepcopy(img1), copy.deepcopy(img2))
            val1 = round(float(student_output), places)
            val2 = round(float(expected_output), places)

            res = (val1 == val2)
            logger.debug(
                "student computeCosineSimilarity confused with gray distance;Correct {}; on input {}. Staff produced {} and student produced {}. Check if type corrections take place outside of measure function.".format(
                    str(res) + '***********************\n',
                    "img1 and img2", val2, val1))
            with self.subTest(msg="Checking if cosine similarity got confused with gray distance"):
                self.assertEqual(res, True,
                                 "student computeCosineSimilarity did not get confused with gray distance on img1 and img2")



    def test2_computeCosineSimilarity_symmetry(self):
        measure_function=Task_4.computeCosineSimilarity

        logger.debug("Testing computeCosineSimilarity symmetry")
        val1 = measure_function(copy.deepcopy(img_white), copy.deepcopy(img_gray))
        val2 = measure_function(copy.deepcopy(img_gray), copy.deepcopy(img_white))
        logger.debug(
            "computeCosineSimilarity symmetry;Correct {}; Gray to white produced {} and white to gray produced {}".format(
                str(numpy.array_equal(numpy.array(val1),numpy.array(val2)))+'***********************\n', val2, val1))
        with self.subTest(msg= "Checking computeCosineSimilarity symmetry on white-gray"):
            self.assertEqual(val1, val2,
                         "computeCosineSimilarity is not symmetric. Likely numerical value misuse")
        val1 = measure_function(copy.deepcopy(img1), copy.deepcopy(img2))
        val2 = measure_function(copy.deepcopy(img2), copy.deepcopy(img1))
        logger.debug(
            "computeCosineSimilarity symmetry;Correct {}; img1 to img2 produced {} and img2 to img1 produced {}".format(
                str(numpy.array_equal(numpy.array(val1),numpy.array(val2)))+'***********************\n', val2, val1))
        with self.subTest(msg= "Checking computeCosineSimilarity symmetry on more complex image"):
            self.assertEqual(val1, val2,
                             "computeCosineSimilarity is not symmetric. Likely numerical value misuse")

    def test3_computeRMSEDistance(self):
        measure_function = Task_4.computeRMSEDistance
        student_output = measure_function(copy.deepcopy(img1), copy.deepcopy(img2))

        # We first check if it returns what it is supposed to, rounded to given decimal places for convenience
        expected_output = rmse_dis(copy.deepcopy(img1), copy.deepcopy(img2))
        val1 = round(float(student_output), places)
        val2 = round(float(expected_output), places)

        res = (val1 == val2)
        logger.debug(
            "student computeRMSEDistance against staff;Correct {}; on input {}. Staff produced {} and student produced {}. Check if type corrections take place outside of measure function.".format(
                str(res) + '***********************\n',
                "img1 and img2", val2, val1))
        with self.subTest(msg="Checking if RMSE is computed fine"):
            self.assertEqual(res, True,
                             "student computeRMSEDistance against staff do not return the same value on img1 and img2")
        if not res:
        # We now check if problem is due to lack of type conversion
            student_output = measure_function(numpy.asarray(img1, dtype=float), numpy.asarray(img2, dtype=float))
            val1 = round(float(student_output), places)
            val2 = round(float(expected_output), places)

            res = (val1 == val2)
            logger.debug(
                "student computeRMSEDistance against staff with type conversion;Correct {}; on input {}. Staff produced {} and student produced {}. Check if type corrections take place outside of measure function.".format(
                    str(res) + '***********************\n',
                    "img1 and img2", val2, val1))
            with self.subTest(msg="Checking if RMSE is computed fine if image type is fixed"):
                self.assertEqual(res, True,
                                 "student computeRMSEDistance against staff do not return the same value on img1 and img2 even after type conversion")

        # We now check if it got transformed to gray scale when it shouldn't have - WARNING: more than one way to transform to grayscale!
        if not res:
            student_output = measure_function(copy.deepcopy(img1), copy.deepcopy(img2))
            expected_output = gray_rmse_dis(copy.deepcopy(img1), copy.deepcopy(img2))
            val1 = round(float(student_output), places)
            val2 = round(float(expected_output), places)

            res = (val1 == val2)
            logger.debug(
                "student computeRMSEDistance computed with grayscale;Correct {}; on input {}. Staff produced {} and student produced {}. Check if type corrections take place outside of measure function.".format(
                    str(res) + '***********************\n',
                    "img1 and img2", val2, val1))
            with self.subTest(msg="Checking if RMSE is computed with grayscale"):
                self.assertEqual(res, True,
                                 "student computeRMSEDistance against grayscale staff do not return the same value on img1 and img2")

        # We now do the same in case similarity got confused with distance - WARNING: more than one way to transform similarity to distance!
        if not res:
            expected_output = rmse_sim(copy.deepcopy(img1), copy.deepcopy(img2))
            val1 = round(float(student_output), places)
            val2 = round(float(expected_output), places)

            res = (val1 == val2)
            logger.debug(
                "student computeRMSEDistance confused with similarity;Correct {}; on input {}. Staff produced {} and student produced {}. Check if type corrections take place outside of measure function.".format(
                    str(res) + '***********************\n',
                    "img1 and img2", val2, val1))
            with self.subTest(msg="Checking if RMSE got confused with similarity"):
                self.assertEqual(res, True,
                                 "student computeRMSEDistance did not get confused with similarity on img1 and img2")

        # We now do the same in case similarity got confused with grayscale distance - WARNING: more than one way to transform similarity to grayscale distance!
        if not res:
            expected_output = gray_rmse_sim(copy.deepcopy(img1), copy.deepcopy(img2))
            val1 = round(float(student_output), places)
            val2 = round(float(expected_output), places)

            res = (val1 == val2)
            logger.debug(
                "student computeRMSEDistance confused with gray similarity;Correct {}; on input {}. Staff produced {} and student produced {}. Check if type corrections take place outside of measure function.".format(
                    str(res) + '***********************\n',
                    "img1 and img2", val2, val1))
            with self.subTest(msg="Checking if RMSE got confused with gray similarity"):
                self.assertEqual(res, True,
                                 "student computeRMSEDistance did not get confused with gray similarity on img1 and img2")
                

    def test4_computeRMSEDistance_symmetry(self):
        measure_function = Task_4.computeRMSEDistance

        logger.debug("Testing computeRMSEDistance symmetry")
        val1 = measure_function(copy.deepcopy(img_white), copy.deepcopy(img_gray))
        val2 = measure_function(copy.deepcopy(img_gray), copy.deepcopy(img_white))
        logger.debug(
            "computeRMSEDistance symmetry;Correct {}; Gray to white produced {} and white to gray produced {}".format(
                str(numpy.array_equal(numpy.array(val1), numpy.array(val2))) + '***********************\n', val2, val1))
        with self.subTest(msg="Checking computeRMSEDistance symmetry on white-gray"):
            self.assertEqual(val1, val2,
                             "computeCosineSimilarity is not symmetric. Likely numerical value misuse")
        val1 = measure_function(copy.deepcopy(img1), copy.deepcopy(img2))
        val2 = measure_function(copy.deepcopy(img2), copy.deepcopy(img1))
        logger.debug(
            "computeRMSEDistance symmetry;Correct {}; img1 to img2 produced {} and img2 to img1 produced {}".format(
                str(numpy.array_equal(numpy.array(val1), numpy.array(val2))) + '***********************\n', val2, val1))
        with self.subTest(msg="Checking computeRMSEDistance symmetry on more complex image"):
            self.assertEqual(val1, val2,
                             "computeRMSEDistance is not symmetric. Likely numerical value misuse")



if __name__ == "__main__":
    test_classes_to_run = [Task_4_Testing]
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(test_classes_to_run)
    runner = Testing_1.LogCaptureRunner(verbosity=2)
    runner.run(suite)
