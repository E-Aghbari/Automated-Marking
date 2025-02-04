# https://gist.github.com/clayg/3787160
import unittest
import sys
import cv2
from io import StringIO
import copy
import logging
from Task_1 import *
import Dummy

sys.tracebacklimit = 6
width = 60
height = 30

numpy.seterr(divide='raise')
numpy.seterr(invalid='raise')

def readTXTFile(filename):
    mylist = []
    try:
        with open(filename) as f:
            mylist = f.read().splitlines()
    except FileNotFoundError as ferror:
        print(ferror)
    for i in range(0, len(mylist)):
        mylist[i] = mylist[i].upper()
    return mylist


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

training_data = Helper.readCSVFile("../training_data4.csv")
testing_data = Helper.readCSVFile("../testing_data2.csv")
training_data2 = Helper.readCSVFile("../training_data3.csv")

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG, filename='test_1.log', filemode='w')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


class LogCaptureResult(unittest.TextTestResult):

    def _exc_info_to_string(self, err, test):
        # jack into the bit that writes the tracebacks, and add captured log
        tb = super(LogCaptureResult, self)._exc_info_to_string(err, test)
        captured_log = test.stream.getvalue()
        return '***********************\n'.join([tb, 'CAPTURED LOG', '=' * 70, captured_log])


class LogCaptureRunner(unittest.TextTestRunner):

    def _makeResult(self):
        # be nice if TextTestRunner just had a class attr for defaultResultClass
        return LogCaptureResult(self.stream, self.descriptions, self.verbosity)


class BaseTestCase(unittest.TestCase):

    def setUp(self, *args, **kwargs):
        super(BaseTestCase, self).setUp(*args, **kwargs)
        # create a in memory stream
        self.stream = StringIO()
        # add handler to logger
        self.handler = logging.StreamHandler(self.stream)
        logger.addHandler(self.handler)

    def tearDown(self, *args, **kwargs):
        super(BaseTestCase, self).tearDown(*args, **kwargs)
        # we're done with the caputre handler
        logger.removeHandler(self.handler)

    def badImports(self):
        logger.debug("Testing for naughty functions. The following things from naughty list are present: ")
        classes = dir()
        naughty = ["Counter", "sklearn", "confusionMatrix", "train_test_split", "cross_val_score", "cross_validate",
                   "KNeighborsClassifier", "RepeatedKFold", "LeaveOneOut", "ShuffleSplit", "StratifiedKFold", "KFold",
                   "array_split"]
        present = [value for value in classes if value in naughty]
        logger.debug(present)


class Task_1_Testing(BaseTestCase):
    #
    # This function contains unit testing for getClassesOfKNearestNeighbours.
    # We first check if behaviour is as expected on distance measures. If the basic test fails,
    # there are typically two causes for this - one is input flag getting mishandled, other is incompleteness
    # of the produced diary (e.g. it contains only classes from the input, not all classes from the scheme).
    #
    def test1_getClassesOfKNearestNeighbours_distance_behaviour(self):
        logger.debug("Testing getting classes of k nearest neighbours, distance mode")
        # Setting up the variables - value of k, the input measure_classes, and the output we expect depending on
        # if distance or similarity measure was used
        k = 3
        measure_classes = [(0.0, 'Female'), (0.0, 'Male'), (1.0, 'Female'), (1.5, 'Female'), (2.0, 'Female')]
        outputIfDist = {'Female': 2, 'Male': 1, 'Primate': 0, 'Rodent': 0, 'Food': 0}
        res = False

        # ---------------------------------First test: simple case, distance mode
        with self.subTest(msg="Testing behaviour on clear input and distance measure"):
            student_res = getClassesOfKNearestNeighbours(copy.deepcopy(measure_classes), k, False)
            res = student_res == outputIfDist
            logger.debug(
                "getClassesOfKNearestNeighbours Dist;Correct {}; on input {} and similarity {}. Expected {} and got {}".format(
                    str(res) + '***********************\n', measure_classes, str(False), outputIfDist, student_res))
            self.assertEqual(res, True, 'Produced output is not equal to the expected one')
        # if test crapped out, we follow with backup tests
        if not res:
            # ------Backup test: simple case, distance mode - checking if the
            # student dictionary agrees with expected one on non-zero classes, happens when students produce incomplete
            # dictionaries only for classes appearing in input and not for all classes
            with self.subTest(msg="Backup testing behaviour on clear input and distance measure - key classes test"):
                student_res = getClassesOfKNearestNeighbours(copy.deepcopy(measure_classes), k, False)
                res = student_res.items() == {z: v for (z, v) in outputIfDist.items() if v > 0}.items()
                logger.debug(
                    "getClassesOfKNearestNeighbours Dist on key classes;Correct {}; on input {} and similarity {}. "
                    "Expected {} and got {}".format(
                        str(res) + '***********************\n', measure_classes, str(False), outputIfDist, student_res))
                self.assertEqual(res, True,
                                 "Produced output does not agree on key classes either")

        # -----------------------------Second test: this is in case sim flag got flipped/misused in student code
        # and key classes don't match up either, in this case we would expect distances to produce similarity behaviours
        if not res:
            with self.subTest(msg="Backup testing behaviour on clear input and distance measure - confused sim flag"):
                student_res = getClassesOfKNearestNeighbours(copy.deepcopy(measure_classes), k, True)
                res = student_res == outputIfDist
                logger.debug(
                    "getClassesOfKNearestNeighbours Dist confused flag;Correct {}; on input {} and similarity {}. "
                    "Expected {} and got {}".format(
                        str(res) + '***********************\n', measure_classes, str(True), outputIfDist, student_res))
                self.assertEqual(res, True, 'Produced output is not equal to the expected one for confused flag')
            if not res:
                # ------Backup second test: this is in case sim flag got flipped/misused in student code and
                # dictionary is also incomplete
                with self.subTest(
                        msg="Backup testing behaviour on clear input and distance measure - confused sim flag and key "
                            "classes test"):
                    student_res = getClassesOfKNearestNeighbours(copy.deepcopy(measure_classes), k, True)
                    res = student_res.items() == {z: v for (z, v) in outputIfDist.items() if v > 0}.items()
                    logger.debug(
                        "getClassesOfKNearestNeighbours Dist on confused flag and key classes;Correct {}; on input {} "
                        "and similarity {}. Expected {} and got {}".format(
                            str(res) + '***********************\n', measure_classes, str(True), outputIfDist,
                            student_res))
                    self.assertEqual(res, True,
                                     "Produced output does not agree on confused flag and key classes either")

    def test2_getClassesOfKNearestNeighbours_similarity_behaviour(self):
        logger.debug("Testing getting classes of k nearest neighbours, similarity mode")
        # Setting up the variables - value of k, the input measure_classes, and the output we expect depending on
        # if distance or similarity measure was used
        k = 3
        measure_classes = [(0.0, 'Female'), (0.0, 'Male'), (1.0, 'Female'), (1.5, 'Female'), (2.0, 'Female')]
        outputIfSim = {'Female': 3, 'Male': 0, 'Primate': 0, 'Rodent': 0, 'Food': 0}
        res = False

        # --------------------------------First test: simple case, distance mode
        with self.subTest(msg="Testing behaviour on clear input and similarity measure"):
            student_res = getClassesOfKNearestNeighbours(copy.deepcopy(measure_classes), k, True)
            res = student_res == outputIfSim
            logger.debug("getClassesOfKNearestNeighbours Sim;Correct {}; on input {} and "
                         "similarity {}. Expected {} and got {}".format(str(res) + '***********************\n',
                                                                        measure_classes, str(True), outputIfSim,
                                                                        student_res))
            self.assertEqual(res, True, 'Produced output is not equal to the expected one')
        # if test crapped out, we follow with backup tests
        if not res:
            # ------Backup test: simple case, similarity mode - checking if the
            # student dictionary agrees with expected one on non-zero classes, happens when students produce incomplete
            # dictionaries only for classes appearing in input and not for all classes
            with self.subTest(msg="Backup testing behaviour on clear input and similarity measure - key classes test"):
                student_res = getClassesOfKNearestNeighbours(copy.deepcopy(measure_classes), k, True)
                res = student_res.items() == {z: v for (z, v) in outputIfSim.items() if v > 0}.items()
                logger.debug(
                    "getClassesOfKNearestNeighbours Sim on key classes;Correct {}; on input {} and similarity {}. "
                    "Expected {} and got {}".format(
                        str(res) + '***********************\n', measure_classes, str(True), outputIfSim, student_res))
                self.assertEqual(res, True,
                                 "Produced output does not agree on key classes either")

        # --------------------------------Second test: this is in case sim flag got flipped/misused in student code
        # and key classes don't match up either, in this case we would expect distances to produce similarity behaviours
        if not res:
            with self.subTest(msg="Backup testing behaviour on clear input and similarity measure - confused sim flag"):
                student_res = getClassesOfKNearestNeighbours(copy.deepcopy(measure_classes), k, False)
                res = student_res == outputIfSim
                logger.debug(
                    "getClassesOfKNearestNeighbours Sim confused flag;Correct {}; on input {} and similarity {}. "
                    "Expected {} and got {}".format(
                        str(res) + '***********************\n', measure_classes, str(False), outputIfSim, student_res))
                self.assertEqual(res, True, 'Produced output is not equal to the expected one for confused flag')
            if not res:
                # ------Backup second test: this is in case sim flag got flipped/misused in student code and
                # dictionary is also incomplete
                with self.subTest(
                        msg="Backup testing behaviour on clear input and distance measure - confused sim flag and key "
                            "classes test"):
                    student_res = getClassesOfKNearestNeighbours(copy.deepcopy(measure_classes), k, False)
                    res = student_res.items() == {z: v for (z, v) in outputIfSim.items() if v > 0}.items()
                    logger.debug(
                        "getClassesOfKNearestNeighbours Sim on confused flag and key classes;Correct {}; on input {} "
                        "and similarity {}. Expected {} and got {}".format(
                            str(res) + '***********************\n', measure_classes, str(False), outputIfSim,
                            student_res))
                    self.assertEqual(res, True,
                                     "Produced output does not agree on confused flag and key classes either")

    def test3_getClassesOfKNearestNeighbours_excessive(self):
        # Setting up the variables - value of k, the input measure_classes, and the output we expect if k larger
        # than the size of input data is provided
        res=False
        k = 10
        measure_classes = [(0.0, 'Female'), (0.0, 'Male'), (1.0, 'Female'), (1.5, 'Female'), (2.0, 'Female')]
        outputAll = {'Female': 4, 'Male': 1, 'Primate': 0, 'Rodent': 0, 'Food': 0}
        # ----------------------------------Third test: testing if excessive k is handled
        with self.subTest(msg="Checking if case of k exceeding size of data is handled"):
            try:
                student_res = getClassesOfKNearestNeighbours(copy.deepcopy(measure_classes), k, True)
            except ValueError as ve:
                logger.debug(
                    "getClassesOfKNearestNeighbours;Correct False; Bugged out probably due to excessive k being 10, "
                    "that's not handled!".format(
                        str(ve)))
            res = student_res == outputAll
            logger.debug("getClassesOfKNearestNeighbours;Correct {}; on input {} and similarity {}. Expected {} and "
                         "got {}".format(str(res) + '***********************\n', measure_classes, str(True),
                                         outputAll, student_res))
            self.assertEqual(res, True, 'Produced output is not equal to the expected one on excessive k')
        if not res:
            # ----------------------------------Backup test: testing if excessive k is handled, but focusing on k
            # classes in case student output is incomplete
            with self.subTest(msg="Backup checking if case of k exceeding size of data is handled, key classes"):
                student_res = getClassesOfKNearestNeighbours(copy.deepcopy(measure_classes), k, True)
                res = student_res.items() == {z: v for (z, v) in outputAll.items() if v > 0}.items()
                logger.debug(
                    "getClassesOfKNearestNeighbours on key classes;Correct {}; on input {} and similarity {}. "
                    "Expected {} and got {}".format(
                        str(res) + '***********************\n', measure_classes, str(True), outputAll, student_res))
                self.assertEqual(res, True,
                                 "Produced output does not agree on key classes either for excessive k")

    def test4_getMostCommonClass(self):
        logger.debug("Testing getting most common class of k neighbours")
        # Setting up the variables - different inputs and expected outputs

        input1 = {'Female': 1, 'Male': 2, 'Primate': 0, 'Rodent': 0, 'Food': 0}
        input2 = {'Female': 0, 'Male': 2, 'Primate': 2, 'Rodent': 0, 'Food': 2}
        input3 = {'Female': 0, 'Male': 0, 'Primate': 0, 'Rodent': 0, 'Food': 0}
        input4 = {'Female': 0, 'Primate': 2, 'Rodent': 0, 'Food': 2,'Male': 2}
        answer1 = 'Male'
        answer2 = 'Male'
        answer3 = ''

        res = False
        #------First test: if correct most common class is returned when only one winner is present
        with self.subTest(msg="Testing most common class with simple unique candidate"):
            student_res = getMostCommonClass(copy.deepcopy(input1))
            res = student_res == answer1
            logger.debug(
                "getMostCommonClass;Correct {}; on input {}. Expected {} and got {}".format(
                    str(res) + '***********************\n',
                    input1, answer1, student_res))
            self.assertEqual(res, True, "Wrong most common class picked with unique candidate")

        #------Second test: if correct most common class is returned when when several candidates are there - this
        # essentially checks if order of the scheme is followed
        with self.subTest(msg="Testing most common class with three candidates"):
            student_res = getMostCommonClass(copy.deepcopy(input2))
            res = student_res == answer2
            logger.debug(
                "getMostCommonClass;Correct {}; on input {}. Expected {} and got {}".format(
                    str(res) + '***********************\n',
                    input2, answer2, student_res))
            self.assertEqual(res, True,
                             "Wrong most common class picked with more than one candidate")
        #------Third test: if correct most common class is returned when no candidate is there, should be empty
        #  string but students sometimes offer "Female"
        with self.subTest(msg="Testing most common class with no candidates"):
            student_res = getMostCommonClass(copy.deepcopy(input3))
            res = student_res == answer3
            logger.debug(
                "getMostCommonClass;Correct {}; on input {}. Expected {} and got {}".format(
                    str(res) + '***********************\n',
                    input3, answer3, student_res))
            self.assertEqual(res, True,
                             "Wrong most common class picked when no candidates present")
        #------Fourth test: if correct most common class is returned when when several candidates are there, but the
        # input is not sorted
        with self.subTest(msg="Testing most common class with three candidates and no order in dict"):
            student_res = getMostCommonClass(copy.deepcopy(input4))
            res = student_res == answer2
            logger.debug(
                "getMostCommonClass;Correct {}; on input {}. Expected {} and got {}".format(
                    str(res) + '***********************\n',
                    input2, answer2, student_res))
            self.assertEqual(res, True,
                             "Wrong most common class picked with more than one candidate")

    def test5_kNN(self):
        self.badImports()
        logger.debug("Testing knn")
        # --------- First test: student functions are replaced with staff functions to see if code logic is fine
        # CAVEAT: make sure students use the input functions and not hardcode it with their own
        #
        # First we check staff version of kNN vs student version of kNN supplied with staff functions
        expected = Dummy.T1staff_kNN(copy.deepcopy(training_data), copy.deepcopy(testing_data), 3,
                                   Dummy.T4staff_computeRMSEDistance, False,
                                   most_common_class_func=Dummy.T1staff_getMostCommonClass,
                                   get_neighbour_classes_func=Dummy.T1staff_getClassesOfKNearestNeighbours,
                                   read_func=Helper.readAndResize)
        output = kNN(copy.deepcopy(training_data), copy.deepcopy(testing_data), 3, Dummy.T4staff_computeRMSEDistance,
                     False,
                     most_common_class_func=Dummy.T1staff_getMostCommonClass,
                     get_neighbour_classes_func=Dummy.T1staff_getClassesOfKNearestNeighbours,
                     read_func=Helper.readAndResize)
        res = numpy.array_equal(numpy.array(output), numpy.array(expected))
        logger.debug(
            "kNN with all staff functions;Correct {}; Expected {} and got {}".format(
                str(res) + '***********************\n', str(expected), str(output)))
        with self.subTest(msg="Checking if student kNN with staff subfunctions works 1"):
            self.assertEqual(res, True,
                             "Wrong kNN output even with staff functions, possible knn logic violation")
        # --------- Second test: student kNN vs staff kNN
        #
        # We check staff version of kNN vs student version of kNN using only student functions
        # If this works but first test doesn't, it's a sign that e.g. some logic that was meant to be in subfunctions
        # got moved to kNN, or e.g. input-output patterns have changed, etc
        output = kNN(copy.deepcopy(training_data), copy.deepcopy(testing_data), 3, Dummy.T4staff_computeRMSEDistance,
                     False)
        res = numpy.array_equal(numpy.array(output), numpy.array(expected))
        logger.debug(
            "kNN with staff vs student functions;Correct {}; Expected {} and got {}".format(
                str(res) + '***********************\n', str(expected), str(output)))
        with self.subTest(msg="Checking if student kNN with student subfunctions works 1"):
            self.assertEqual(res, True,
                             "Wrong kNN output with staff vs student functions")
        # ---------Third test: student functions are replaced with staff functions to see if code logic is fine
        # CAVEAT: make sure students use the input functions and not hardcode it with their own
        #
        # First we check staff version of kNN vs student version of kNN supplied with staff functions
        # just on a different training data

        expected = Dummy.T1staff_kNN(copy.deepcopy(training_data2), copy.deepcopy(testing_data), 3,
                                   Dummy.T4staff_computeRMSEDistance, False,
                                   most_common_class_func=Dummy.T1staff_getMostCommonClass,
                                   get_neighbour_classes_func=Dummy.T1staff_getClassesOfKNearestNeighbours,
                                   read_func=Helper.readAndResize)
        output = kNN(copy.deepcopy(training_data2), copy.deepcopy(testing_data), 3, Dummy.T4staff_computeRMSEDistance,
                     False,
                     most_common_class_func=Dummy.T1staff_getMostCommonClass,
                     get_neighbour_classes_func=Dummy.T1staff_getClassesOfKNearestNeighbours,
                     read_func=Helper.readAndResize)
        res = numpy.array_equal(numpy.array(output), numpy.array(expected))
        logger.debug(
            "kNN with all staff functions 2;Correct {}; Expected {} and got {}".format(
                str(res) + '***********************\n', str(expected), str(output)))
        with self.subTest(msg="Checking if student kNN with staff subfunctions works 2"):
            self.assertEqual(res, True,
                             "Wrong kNN output even with staff functions, possible knn logic violation")
        # --------- Second test: student kNN vs staff kNN
        #
        # We check staff version of kNN vs student version of kNN using only student functions
        # If this works but first test doesn't, it's a sign that e.g. some logic that was meant to be in subfunctions
        # got moved to kNN, or e.g. input-output patterns have changed, etc
        output = kNN(copy.deepcopy(training_data2), copy.deepcopy(testing_data), 3, Dummy.T4staff_computeRMSEDistance,
                     False)
        res = numpy.array_equal(numpy.array(output), numpy.array(expected))
        logger.debug(
            "kNN with staff vs student functions 2;Correct {}; Expected {} and got {}".format(
                str(res) + '***********************\n', str(expected), str(output)))
        with self.subTest(msg="Checking if student kNN with student subfunctions works 2"):
            self.assertEqual(res, True,
                             "Wrong kNN output with staff vs student functions")



if __name__ == "__main__":
    test_classes_to_run = [Task_1_Testing]
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(test_classes_to_run)
    runner = LogCaptureRunner(verbosity=2)
    runner.run(suite)
