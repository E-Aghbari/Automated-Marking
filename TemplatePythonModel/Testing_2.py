# https://gist.github.com/clayg/3787160
import unittest
import numpy
import sys
import copy
import Dummy
import logging

import Task_2
import Testing_1
from Task_2 import *
from Task_1 import *

numpy.seterr(divide='raise')
numpy.seterr(invalid='raise')
#sys.tracebacklimit = 0

classified_nice = numpy.asarray(Helper.readCSVFile("../testing_files/class_data_no_nulls.csv"))
classified_edge = numpy.asarray(Helper.readCSVFile("../testing_files/class_data_nulls.csv"))
classified_edge2 = numpy.asarray(Helper.readCSVFile("../testing_files/class_data_nulls_2.csv"))

conf_nice = numpy.asarray(Helper.readCSVFile("../testing_files/confusion_no_nulls.csv")).astype(float)
conf_edge = numpy.asarray(Helper.readCSVFile("../testing_files/confusion_nulls.csv")).astype(float)
conf_edge2 = numpy.asarray(Helper.readCSVFile("../testing_files/confusion_nulls_2.csv")).astype(float)

eval_nice = numpy.asarray(Helper.readCSVFile("../testing_files/eval_no_nulls.csv"))
eval_edge = numpy.asarray(Helper.readCSVFile("../testing_files/eval_nulls.csv"))
eval_edge2 = numpy.asarray(Helper.readCSVFile("../testing_files/eval_nulls_2.csv"))

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG, filename='test_2.log', filemode='w')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


class Task_2_Testing(Testing_1.BaseTestCase):

    # General idea: I have several files and corresponding evaluations, some are pretty, some contain edge cases
    # (so division by 0 issues), and I replace student functions with my own functions to see if issues are with
    # logic or sub_functions

    # This is the general function, typical errors include:
    # 1. Calculating stuff from scratch instead of using the template functions (this is checked manually)
    # 2. Miscalculating data_size (they do not remove the header when counting entries, or pass the number of classes)
    # 3. Swapping output order
    # 4. Wrong computations in the underlying functions (which is not penalized in evaluateKNN itself though)
    # The tests below don't check for all of that, really, they are more a sign to look into things
    #
    # WARNING: please ensure first that functions are invoked through param names in student code
    # (e.g. confusion_func not confusionMatrix)
    def test1_evaluateKNN(self):
        self.badImports()
        logger.debug("Testing evaluateKNN with student confusionMatrix function")
        student_output = Task_2.evaluateKNN(classified_nice, Task_2.confusionMatrix)

        # This is what we would expect if things were tickety-boo
        expected = [float(x) for x in eval_nice[1, 4:8]]

        # This is what we would expect if the underlying f-measure function used bad harmonic mean of macro precision and recall
        # formula instead of the right one
        expected_harmonic_f = copy.deepcopy(expected)
        expected_harmonic_f[2] = float(eval_nice[1, 8])

        # This is what we would expect if the underlying f-measure function used micro approach
        expected_micro_f = copy.deepcopy(expected)
        expected_micro_f[2] = float(eval_nice[1, 9])

        # This is what we would expect if someone mishandled data size (forgetting the header)
        expected_ds_accuracy = copy.deepcopy(expected)
        expected_ds_accuracy[3] = float(eval_nice[1, 10])

        # Combo of f-measure and accuracy
        expected_harmonic_f_ds = copy.deepcopy(expected)
        expected_harmonic_f_ds[2] = float(eval_nice[1, 8])
        expected_harmonic_f_ds[3] = float(eval_nice[1, 10])

        # Another combo
        expected_micro_f_ds = copy.deepcopy(expected)
        expected_micro_f_ds[2] = float(eval_nice[1, 9])
        expected_micro_f_ds[3] = float(eval_nice[1, 10])

        # We first check student code against the correct output and the one with malformed f-measure
        res = roundEqual(student_output, expected)
        res2 = False
        logger.debug(
            "evaluatekNN with student confusionMatrix and normal f formula;Correct {}; got {} and expected {}".format(
                str(res) + '***********************\n', str(student_output),
                str(expected)))
        with self.subTest(msg="Checking evaluatekNN with student confusion matrix and correct measure values"):
            self.assertEqual(res, True,
                             "EvaluateKNN does not return proper answer with student confusionMatrix with good fmeasure formula")

        # And then we go through possible f-up cases of f-measure and accuracy
        if not res:
            res2 = roundEqual(student_output, expected_harmonic_f)
            logger.debug(
                "evaluatekNN with student confusionMatrix and backup f formula;Correct {}; got {} and expected {}".format(
                    str(res2) + '***********************\n', str(student_output),
                    str(expected_harmonic_f)))
            with self.subTest(msg="Checking evaluatekNN with student confusion matrix and a miscalculated f-measure"):
                self.assertEqual(res2, True,
                                 "EvaluateKNN does not return proper answer with student confusionMatrix with backup fmeasure formulas")
        if not res:
            res2 = roundEqual(student_output, expected_micro_f)
            logger.debug(
                "evaluatekNN with student confusionMatrix and micro f formula;Correct {}; got {} and expected {}".format(
                    str(res2) + '***********************\n', str(student_output),
                    str(expected_micro_f)))
            with self.subTest(msg="Checking evaluatekNN with student confusion matrix and a miscalculated micro f-measure"):
                self.assertEqual(res2, True,
                                 "EvaluateKNN does not return proper answer with student confusionMatrix with micro fmeasure formulas")

        if not res:
            res2 = roundEqual(student_output,expected_ds_accuracy)
            logger.debug(
                "evaluatekNN with student confusionMatrix and ds accuracy;Correct {}; got {} and expected {}".format(
                    str(res2) + '***********************\n', str(student_output),
                    str(expected_ds_accuracy)))
            with self.subTest(
                    msg="Checking evaluatekNN with student confusion matrix and ds accuracy"):
                self.assertEqual(res2, True,
                                 "EvaluateKNN does not return proper answer with student confusionMatrix and ds accuracy")

        if not res:
            res2 = roundEqual(student_output, expected_harmonic_f_ds)
            logger.debug(
                "evaluatekNN with student confusionMatrix and backup f formula and ds accuracy;Correct {}; got {} and expected {}".format(
                    str(res2) + '***********************\n', str(student_output),
                    str(expected_harmonic_f_ds)))
            with self.subTest(msg="Checking evaluatekNN with student confusion matrix and a miscalculated f-measure and ds accuracy"):
                self.assertEqual(res2, True,
                                 "EvaluateKNN does not return proper answer with student confusionMatrix with backup fmeasure formulas and ds accuracy")
        if not res:
            res2 = roundEqual(student_output, expected_micro_f_ds)
            logger.debug(
                "evaluatekNN with student confusionMatrix and micro f formula and ds accuracy;Correct {}; got {} and expected {}".format(
                    str(res2) + '***********************\n', str(student_output),
                    str(expected_micro_f_ds)))
            with self.subTest(msg="Checking evaluatekNN with student confusion matrix and a miscalculated micro f-measure and ds accuracy"):
                self.assertEqual(res2, True,
                                 "EvaluateKNN does not return proper answer with student confusionMatrix with micro fmeasure formulas and ds accuracy")

        # We then check student output against evaluatekNN ran with staff confusion matrix and against correct
        # output and one with malformed f-measure
        logger.debug("Testing evaluateKNN with staff confusionMatrix function")
        student_output = evaluateKNN(classified_nice, Dummy.T2staff_confusionMatrix)
        # We first check staff code against the correct output and the one with malformed f-measure
        res = roundEqual(student_output, expected)
        res2 = False
        logger.debug(
            "evaluatekNN with staff confusionMatrix and normal f formula;Correct {}; got {} and expected {}".format(
                str(res) + '***********************\n', str(student_output),
                str(expected)))
        with self.subTest(msg="Checking evaluatekNN with staff confusion matrix and correct measure values"):
            self.assertEqual(res, True,
                             "EvaluateKNN does not return proper answer with staff confusionMatrix with good fmeasure formula")

        # And then we go through possible f-up cases of f-measure and accuracy
        if not res:
            res2 = roundEqual(student_output, expected_harmonic_f)
            logger.debug(
                "evaluatekNN with staff confusionMatrix and backup f formula;Correct {}; got {} and expected {}".format(
                    str(res2) + '***********************\n', str(student_output),
                    str(expected_harmonic_f)))
            with self.subTest(msg="Checking evaluatekNN with staff confusion matrix and a miscalculated f-measure"):
                self.assertEqual(res2, True,
                                 "EvaluateKNN does not return proper answer with staff confusionMatrix with backup fmeasure formulas")
        if not res:
            res2 = roundEqual(student_output, expected_micro_f)
            logger.debug(
                "evaluatekNN with staff confusionMatrix and micro f formula;Correct {}; got {} and expected {}".format(
                    str(res2) + '***********************\n', str(student_output),
                    str(expected_micro_f)))
            with self.subTest(
                    msg="Checking evaluatekNN with staff confusion matrix and a miscalculated micro f-measure"):
                self.assertEqual(res2, True,
                                 "EvaluateKNN does not return proper answer with staff confusionMatrix with micro fmeasure formulas")

        if not res:
            res2 = roundEqual(student_output, expected_ds_accuracy)
            logger.debug(
                "evaluatekNN with staff confusionMatrix and ds accuracy;Correct {}; got {} and expected {}".format(
                    str(res2) + '***********************\n', str(student_output),
                    str(expected_ds_accuracy)))
            with self.subTest(
                    msg="Checking evaluatekNN with staff confusion matrix and ds accuracy"):
                self.assertEqual(res2, True,
                                 "EvaluateKNN does not return proper answer with staff confusionMatrix and ds accuracy")

        if not res:
            res2 = roundEqual(student_output, expected_harmonic_f_ds)
            logger.debug(
                "evaluatekNN with staff confusionMatrix and backup f formula and ds accuracy;Correct {}; got {} and expected {}".format(
                    str(res2) + '***********************\n', str(student_output),
                    str(expected_harmonic_f_ds)))
            with self.subTest(
                    msg="Checking evaluatekNN with staff confusion matrix and a miscalculated f-measure and ds accuracy"):
                self.assertEqual(res2, True,
                                 "EvaluateKNN does not return proper answer with staff confusionMatrix with backup fmeasure formulas and ds accuracy")
        if not res:
            res2 = roundEqual(student_output, expected_micro_f_ds)
            logger.debug(
                "evaluatekNN with student confusionMatrix and micro f formula and ds accuracy;Correct {}; got {} and expected {}".format(
                    str(res2) + '***********************\n', str(student_output),
                    str(expected_micro_f_ds)))
            with self.subTest(
                    msg="Checking evaluatekNN with student confusion matrix and a miscalculated micro f-measure and ds accuracy"):
                self.assertEqual(res2, True,
                                 "EvaluateKNN does not return proper answer with student confusionMatrix with micro fmeasure formulas and ds accuracy")

    # Typical errors in confusion matrix are
    # 1. data transposition (so actual and predicted class swapped places)
    # 2. including the header row and creating weird stuff
    # 3. not following the order in the classification scheme, but order in the data
    # (be it through actual class, predicted class, mix, alphabetical, blah)
    # 4. including only the classes present in the data, not all classes from the scheme

    # We first check if the confusion matrix produced by the student is the same as the expected one on a case
    # where the data - either in actual or predicted classes - contains all classes from the scheme
    def test2_confusionMatrix_basic(self):
        logger.debug("Testing confusionMatrix on basic nice case")
        correct_data = copy.deepcopy(conf_nice)
        student_matrix = Task_2.confusionMatrix(copy.deepcopy(classified_nice))
        # Using a helper function for equality checking, given some funky data formats sometimes
        res = arrayEqual(student_matrix, correct_data)
        logger.debug(
            "confusionMatrix;Correct {}; got {} and expected {}".format(str(res) + '***********************\n',
                                                                        str(student_matrix),
                                                                        str(correct_data)))
        # Testing if student matrix is the same as expected matrix (held in pre-read conf_nice)
        with self.subTest(msg="Checking if student matrix equals expected matrix"):
            self.assertEqual(res, True, "confusionMatrix construction failed")

        # If that fails, we check if the confusion matrix is perhaps transposed
        if not res:
            student_matrix = numpy.transpose(student_matrix)
            res = arrayEqual(student_matrix, correct_data)
            logger.debug(
                "checking transposed confusionMatrix;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_matrix),
                    str(correct_data)))
            with self.subTest(msg="Checking if student matrix equals transposed expected matrix"):
                self.assertEqual(res, True, "Even transposed confusionMatrix construction failed")

        # If that fails, we check if removing the header row would lead to correct result
        if not res:
            no_header_data = copy.deepcopy(classified_nice)
            no_header_data = no_header_data[1:]
            student_matrix = Task_2.confusionMatrix(copy.deepcopy(no_header_data))
            res = arrayEqual(student_matrix, correct_data)
            logger.debug(
                "confusionMatrix after header row removal;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n',
                    str(student_matrix),
                    str(correct_data)))
            # Testing if student matrix is the same as expected matrix (held in pre-read conf_nice)
            with self.subTest(msg="Checking if student matrix equals expected matrix after header removal"):
                self.assertEqual(res, True, "confusionMatrix construction failed")

        # If that fails, we again check if the confusion matrix is perhaps transposed
        if not res:
            student_matrix = numpy.transpose(student_matrix)
            res = arrayEqual(student_matrix, correct_data)
            logger.debug(
                "checking transposed confusionMatrix after header removal;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_matrix),
                    str(correct_data)))
            with self.subTest(msg="Checking if student matrix equals transposed expected matrix after header removal"):
                self.assertEqual(res, True, "Even transposed header removal confusionMatrix construction failed")
        # Shuffled order is tricky to check - please investigate manually

    # We now first check if the confusion matrix produced by the student is the same as the expected one on a case
    # where the data is missing a class
    def test3_confusionMatrix_edge(self):
        logger.debug("Testing confusionMatrix on edge case")
        correct_data = copy.deepcopy(conf_edge)
        student_matrix = Task_2.confusionMatrix(copy.deepcopy(classified_edge))
        # Using a helper function for equality checking, given some funky data formats sometimes
        res = arrayEqual(student_matrix, correct_data)
        logger.debug(
            "confusionMatrix edge;Correct {}; got {} and expected {}".format(str(res) + '***********************\n',
                                                                             str(student_matrix),
                                                                             str(correct_data)))
        # Testing if student matrix is the same as expected matrix (held in pre-read conf_nice)
        with self.subTest(msg="Checking if student matrix equals expected matrix"):
            self.assertEqual(res, True, "confusionMatrix construction failed")

        # If that fails, we check if the confusion matrix is perhaps transposed
        if not res:
            student_matrix = numpy.transpose(student_matrix)
            res = arrayEqual(student_matrix, correct_data)
            logger.debug(
                "checking transposed confusionMatrix edge;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_matrix),
                    str(correct_data)))
            with self.subTest(msg="Checking if student matrix equals transposed expected matrix"):
                self.assertEqual(res, True, "Even transposed confusionMatrix construction failed")

        # If that fails, we check if removing the header row would lead to correct result
        if not res:
            no_header_data = copy.deepcopy(classified_nice)
            no_header_data = no_header_data[1:]
            student_matrix = Task_2.confusionMatrix(copy.deepcopy(no_header_data))
            res = arrayEqual(student_matrix, correct_data)
            logger.debug(
                "confusionMatrix after header row removal;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n',
                    str(student_matrix),
                    str(correct_data)))
            # Testing if student matrix is the same as expected matrix (held in pre-read conf_nice)
            with self.subTest(msg="Checking if student matrix equals expected matrix after header removal"):
                self.assertEqual(res, True, "confusionMatrix construction failed")

        # If that fails, we again check if the confusion matrix is perhaps transposed
        if not res:
            student_matrix = numpy.transpose(student_matrix)
            res = arrayEqual(student_matrix, correct_data)
            logger.debug(
                "checking transposed confusionMatrix after header removal;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_matrix),
                    str(correct_data)))
            with self.subTest(msg="Checking if student matrix equals transposed expected matrix after header removal"):
                self.assertEqual(res, True, "Even transposed header removal confusionMatrix construction failed")
        # Shuffled order or missing classes are tricky to check - please investigate manually

    # Here we check if TPs are calculated well
    # This task is typically done well, so no need to fight much
    def test4_computeTPs(self):
        logger.debug("Testing computeTPs")
        student_result = Task_2.computeTPs(copy.deepcopy(conf_nice))
        expected = eval_nice[1:, 1]
        #We check with roundEqual since students should be using ints but don't always do ><
        res = roundEqual(student_result, expected)
        logger.debug(
            "computeTPs;Correct {}; got {} and expected {}".format(str(res) + '***********************\n',
                                                                   str(student_result),
                                                                   str(expected)))
        with self.subTest(msg="Checking if TPs are calculated well on nice case"):
            self.assertEqual(res, True, "computeTPS on nice failed")
        student_result = Task_2.computeTPs(copy.deepcopy(conf_edge))
        expected = eval_edge[1:, 1]
        res = roundEqual(student_result, expected)
        logger.debug(
            "computeTPs;Correct {}; got {} and expected {}".format(str(res) + '***********************\n',
                                                                   str(student_result), str(expected)))
        with self.subTest(msg="Checking if TPs are calculated well on edge case"):
            self.assertEqual(res, True, "computeTPS on edge failed")

    # Here we check if FPs are calculated well
    # Common error in this task relates to FPs swapping places with FNs
    def test5_computeFPs(self):
        logger.debug("Testing computeFPs")
        #### BASIC TEST
        student_result = computeFPs(copy.deepcopy(conf_nice))
        expected = eval_nice[1:, 2]
        res = roundEqual(student_result, expected)
        logger.debug(
            "computeFPs;Correct {}; got {} and expected {}".format(str(res) + '***********************\n', str(student_result),
                                                                   str(expected)))
        # First checking if FPs are calculated well on a case of confusion matrix that has no full-zero rows/columns
        with self.subTest(msg="Checking if FPs are calculated well on nice case"):
            self.assertEqual(res, True, "computeFPS on nice failed")
        # If FPs are wrong, we check if they swapped places with FNs
        if not res:
            expected = eval_nice[1:, 3]
            res = roundEqual(student_result, expected)
            logger.debug(
                "checking if FPs got confused with FNs;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_result),
                    str(expected)))
            with self.subTest(msg="Checking if FPs got swapped with FNs on nice case"):
                self.assertEqual(res, True, "FPs not equal to FNs on nice either")
        # EDGE TEST
        student_result = computeFPs(copy.deepcopy(conf_edge))
        expected = eval_edge[1:, 2]
        res = roundEqual(student_result, expected)
        logger.debug(
            "computeFPs;Correct {}; got {} and expected {}".format(str(res) + '***********************\n', str(student_result),
                                                                   str(expected)))
        # Now checking if FPs are calculated well on a case of confusion matrix that has as full-zero row and column
        with self.subTest(msg="Checking if FPs are calculated well on edge case"):
            self.assertEqual(res, True, "computeFPS on edge failed")
        # If FPs are wrong, we check if they swapped places with FNs
        if not res:
            expected = eval_edge[1:, 3]
            res = roundEqual(student_result, expected)
            logger.debug(
                "checking if FPs got confused with FNs;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_result),
                    str(expected)))
            with self.subTest(msg="Checking if FPs got swapped with FNs on edge case"):
                self.assertEqual(res, True, "FPs not equal to FNs on edge either")

    # Here we check if FPs are calculated well
    # Common error in this task relates to FPs swapping places with FNs

    def test6_computeFNs(self):
        #### BASIC TEST
        logger.debug("Testing computeFNs")
        student_result = computeFNs(copy.deepcopy(conf_nice))
        expected = eval_nice[1:, 3]
        res = roundEqual(student_result, expected)
        logger.debug(
            "computeFNs;Correct {}; got {} and expected {}".format(str(res) + '***********************\n', str(student_result),
                                                                   str(expected)))
        # First checking if FNs are calculated well on a case of confusion matrix that has no full-zero rows/columns
        with self.subTest(msg="Checking if FNs are calculated well on nice case"):
            self.assertEqual(res, True, "computeFNS on nice failed")
        # If FPs are wrong, we check if they swapped places with FNs
        if not res:
            expected = eval_nice[1:, 2]
            res = roundEqual(student_result, expected)
            logger.debug(
                "checking if FPs got confused with FNs;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_result),
                    str(expected)))
            with self.subTest(msg="Checking if FPs got swapped with FNs on nice case"):
                self.assertEqual(res, True, "FPs not equal to FNs on nice either")
        #### EDGE TEST
        student_result = computeFNs(copy.deepcopy(conf_edge))
        expected = eval_edge[1:, 3]
        res = roundEqual(student_result, expected)
        logger.debug(
            "computeFNs;Correct {}; got {} and expected {}".format(str(res) + '***********************\n', str(student_result),
                                                                   str(expected)))
        with self.subTest(msg="Checking if FNs are calculated well on edge case"):
            self.assertEqual(res, True, "computeFNS on edge failed")
        if not res:
            expected = eval_edge[1:, 2]
            res = roundEqual(student_result, expected)
            logger.debug(
                "checking if FPs got confused with FNs;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_result),
                    str(expected)))
            with self.subTest(msg="Checking if FPs got swapped with FNs on edge case"):
                self.assertEqual(res, True, "FPs not equal to FNs on edge either")

    def test7_computeBinaryPrecision(self):
        logger.debug("Testing binary precision")
        # First checking basic precision calculation
        student_result = Task_2.computeBinaryPrecision(1,3,0)
        expected = 0.25
        res = roundEqual([student_result],[expected])
        logger.debug(
            "computeBinaryPrecision nice;Correct {}; got {} and expected {}".format(
                str(res) + '***********************\n', str(student_result), str(expected)))
        with self.subTest(msg = "Checking binary precision on a nice case"):
            self.assertEqual(res, True, "computeBinaryPrecision on nice failed")

        # Now checking division by 0 calculation

        try:
            student_result = Task_2.computeBinaryPrecision(0,0,1)
        except Exception as ze:
            logger.debug("Error during edge calculation on binary precision!")
            with self.subTest(msg="Edge case crash occurred"):
                self.assertEqual(False, True, "computeBinaryPrecision on edge caused exception!")
            return
        expected = 0
        res = roundEqual([student_result], [expected])
        logger.debug(
            "computeBinaryPrecision edge;Correct {}; got {} and expected {}".format(
                str(res) + '***********************\n', str(student_result), str(expected)))
        with self.subTest(msg = "Checking binary precision on an edge case"):
            self.assertEqual(res, True, "computeBinaryPrecision on edge failed")

    def test8_computeBinaryRecall(self):
        logger.debug("Testing binary recall")
        # First checking basic recall calculation
        student_result = Task_2.computeBinaryRecall(1, 0, 3)
        expected = 0.25
        res = roundEqual([student_result], [expected])
        logger.debug(
            "computeBinaryRecall nice;Correct {}; got {} and expected {}".format(
                str(res) + '***********************\n', str(student_result), str(expected)))
        with self.subTest(msg="Checking binary recall on a nice case"):
            self.assertEqual(res, True, "computeBinaryRecall on nice failed")

        # Now checking division by 0 calculation

        try:
            student_result = Task_2.computeBinaryRecall(0, 1, 0)
        except Exception as ze:
            logger.debug("Error during edge calculation on binary recall!")
            with self.subTest(msg="Edge case crash occurred"):
                self.assertEqual(False, True, "computeBinaryRecall on edge caused exception!")
            return
        expected = 0
        res = roundEqual([student_result], [expected])
        logger.debug(
            "computeBinaryRecall edge;Correct {}; got {} and expected {}".format(
                str(res) + '***********************\n', str(student_result), str(expected)))
        with self.subTest(msg="Checking binary recall on an edge case"):
            self.assertEqual(res, True, "computeBinaryRecall on edge failed")

    def test9_computeBinaryFMeasure(self):
        logger.debug("Testing binary f-measure")
        # First checking basic recall calculation
        student_result = Task_2.computeBinaryFMeasure(1, 7, 3)
        expected = 0.16666666666
        res = roundEqual([student_result], [expected])
        logger.debug(
            "computeBinaryFMeasure nice;Correct {}; got {} and expected {}".format(
                str(res) + '***********************\n', str(student_result), str(expected)))
        with self.subTest(msg="Checking f-measure recall on a nice case"):
            self.assertEqual(res, True, "computeBinaryFMeasure on nice failed")

        # Now checking edge calculation, where one measure is 0 while other is not (because students sometimes
        # write silly conditions for edge cases)
        try:
            student_result = Task_2.computeBinaryFMeasure(0, 1, 0)
        except Exception as ze:
            logger.debug("Error during edge calculation on binary f-measure!")
            with self.subTest(msg="Edge case crash occurred on f-measure with recall"):
                self.assertEqual(False, True, "computeBinaryFMeasure on edge caused exception!")
            return
        expected = 0
        res = roundEqual([student_result], [expected])
        logger.debug(
            "computeBinaryFMeasure edge;Correct {}; got {} and expected {}".format(
                str(res) + '***********************\n', str(student_result), str(expected)))
        with self.subTest(msg="Checking binary f-measure on a recall edge case"):
            self.assertEqual(res, True, "computeBinaryFMeasure on edge failed")
        # Same again, just other measure (because students sometimes
        # write silly conditions for edge cases)
        try:
            student_result = Task_2.computeBinaryFMeasure(0, 0, 1)
        except Exception as ze:
            logger.debug("Error during edge calculation on binary f-measure!")
            with self.subTest(msg="Edge case crash occurred on f-measure with precision"):
                self.assertEqual(False, True, "computeBinaryFMeasure on edge caused exception!")
            return
        expected = 0
        res = roundEqual([student_result], [expected])
        logger.debug(
            "computeBinaryFMeasure edge;Correct {}; got {} and expected {}".format(
                str(res) + '***********************\n', str(student_result), str(expected)))
        with self.subTest(msg="Checking binary f-measure on a precision edge case"):
            self.assertEqual(res, True, "computeBinaryFMeasure on edge failed")

        # Now total 0 edge case
        try:
            student_result = Task_2.computeBinaryFMeasure(0, 0, 0)
        except Exception as ze:
            logger.debug("Error during edge calculation on binary f-measure!")
            with self.subTest(msg="Edge case crash occurred on f-measure with both recall and precision"):
                self.assertEqual(False, True, "computeBinaryFMeasure on edge caused exception!")
            return
        expected = 0
        res = roundEqual([student_result], [expected])
        logger.debug(
            "computeBinaryFMeasure edge;Correct {}; got {} and expected {}".format(
                str(res) + '***********************\n', str(student_result), str(expected)))
        with self.subTest(msg="Checking binary f-measure on a total edge case"):
            self.assertEqual(res, True, "computeBinaryFMeasure on edge failed")


    # Typical errors that happen here is confusing precision with recall
    # Students are expected to use binary precision in these calculations, but in case they do things from scratch,
    # not handling edge cases is also an issue

    def testx10_computeMacroPrecision(self):
        logger.debug("Testing macro precision")
        # We get tps, fps, etc from a confusion matrix
        # We start with a nice cases where each class occurs
        tps = Dummy.T2staff_computeTPs(copy.deepcopy(conf_nice))
        fps = Dummy.T2staff_computeFPs(copy.deepcopy(conf_nice))
        fns = Dummy.T2staff_computeFNs(copy.deepcopy(conf_nice))
        data_size = sum(sum(copy.deepcopy(conf_nice)))

        # We get student result, expected result is pulled from pre-read file, and we
        # compare them (roundEqual is used to bypass number format problems
        student_result = computeMacroPrecision(tps, fps, fns, data_size)
        expected = eval_nice[1, 4]
        res = roundEqual([student_result], [expected])

        logger.debug(
            "computeMacroPrecision nice;Correct {}; got {} and expected {}".format(
                str(res) + '***********************\n', str(student_result), str(expected)))
        with self.subTest(msg="Checking if macro precision is calculated well on nice case"):
            self.assertEqual(res, True, "computeMacroPrecision on nice failed")

        # If macro precision is calculated wrong, we see if it got swapped with macro recall
        if not res:
            # Pulling expected macro recall results from pre-read files, and comparing
            expected = eval_nice[1, 5]
            res = roundEqual([student_result], [expected])
            logger.debug(
                "checking of macro precision swapped with recall;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_result), str(expected)))
            with self.subTest(msg="Checking if macro precision swapped with recall on nice case"):
                self.assertEqual(res, True, "computeMacroPrecision not swapped with recall on nice either")

        # Checking if perhaps student divided by data size instead of class count
        if not res:
            student_result = computeMacroPrecision(tps, fps, fns, 5)
            expected = eval_nice[1, 4]
            res = roundEqual([student_result], [expected])
            logger.debug(
                "checking if macro precision misused data_size;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_result), str(expected)))
            with self.subTest(msg="Checking if macro precision misused data size"):
                self.assertEqual(res, True, "computeMacroPrecision did not use data size instead of class count either")

        # We get tps, fps, etc from a confusion matrix
        # We do a nasty case where zero rows/columns happen
        tps = Dummy.T2staff_computeTPs(copy.deepcopy(conf_edge))
        fps = Dummy.T2staff_computeFPs(copy.deepcopy(conf_edge))
        fns = Dummy.T2staff_computeFNs(copy.deepcopy(conf_edge))
        data_size = sum(sum(copy.deepcopy(conf_edge)))
        try:
            student_result = computeMacroPrecision(tps, fps, fns, data_size)
        except Exception:
            student_result = -1
            logger.debug("Error during edge calculation!")
            with self.subTest(msg="Macro precision on edge case crashed"):
                self.assertEqual(False, True, "computeMacroPrecision on edge failed caused exception!")
        expected = eval_edge[1, 4]
        res = roundEqual([student_result], [expected])
        logger.debug(
            "computeMacroPrecision edge;Correct {}; got {} and expected {}".format(
                str(res) + '***********************\n', str(student_result), str(expected)))
        with self.subTest(msg="Checking if macro precision is calculated well on edge case"):
            self.assertEqual(res, True, "computeMacroPrecision on edge failed")

        # We get tps, fps, etc from a confusion matrix
        # We do another nasty case where zero rows/columns happen
        tps = Dummy.T2staff_computeTPs(copy.deepcopy(conf_edge2))
        fps = Dummy.T2staff_computeFPs(copy.deepcopy(conf_edge2))
        fns = Dummy.T2staff_computeFNs(copy.deepcopy(conf_edge2))
        data_size = sum(sum(copy.deepcopy(conf_edge2)))
        try:
            student_result = computeMacroPrecision(tps, fps, fns, data_size)
        except Exception:
            student_result = -1
            logger.debug("Error during edge calculation!")
            with self.subTest(msg="Macro precision on 2nd edge case crashed"):
                self.assertEqual(False, True, "computeMacroPrecision on 2nd edge failed caused exception!")
        expected = eval_edge2[1, 4]
        res = roundEqual([student_result], [expected])
        logger.debug(
            "computeMacroPrecision edge2;Correct {}; got {} and expected {}".format(
                str(res) + '***********************\n', str(student_result), str(expected)))
        with self.subTest(msg="Checking if macro precision is calculated well on 2nd edge case"):
            self.assertEqual(res, True, "computeMacroPrecision on edge2 failed")

    def testx11_computeMacroRecall(self):
        # We get tps, fps, etc from a confusion matrix
        # We start with a nice cases where each class occurs
        logger.debug("Testing macro recall")
        tps = Dummy.T2staff_computeTPs(copy.deepcopy(conf_nice))
        fps = Dummy.T2staff_computeFPs(copy.deepcopy(conf_nice))
        fns = Dummy.T2staff_computeFNs(copy.deepcopy(conf_nice))
        data_size = sum(sum(copy.deepcopy(conf_nice)))

        student_result = computeMacroRecall(tps, fps, fns, data_size)
        expected = eval_nice[1, 5]
        res = roundEqual([student_result], [expected])
        logger.debug(
            "computeMacroRecall nice;Correct {}; got {} and expected {}".format(str(res) + '***********************\n',
                                                                                str(student_result), str(expected)))
        with self.subTest(msg="Checking if macro recall is calculated well on nice case"):
            self.assertEqual(res, True, "computeMacroRecall on nice failed")

        # If that fails, we check if perhaps precision got swapped with recall
        if not res:
            expected = eval_nice[1, 4]
            res = roundEqual([student_result], [expected])
            logger.debug(
                "checking of macro recall swapped with precision;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_result), str(expected)))
            with self.subTest(msg="Checking if macro recall swapped with precision nice case"):
                self.assertEqual(res, True, "computeMacroRecall not swapped with precision on nice either")
        # Checking if perhaps data size got misused
        if not res:
            student_result = computeMacroRecall(tps, fps, fns, 5)
            expected = eval_nice[1, 5]
            res = roundEqual([student_result], [expected])
            logger.debug(
                "checking of macro recall misused data_size;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_result), str(expected)))
            with self.subTest(msg="Checking if macro recall misused data size"):
                self.assertEqual(res, True, "computeMacroRecall did not use data size instead of class count either")

        # We get tps, fps, etc from a confusion matrix
        # We do a nasty case where zero rows/columns happen
        tps = Dummy.T2staff_computeTPs(copy.deepcopy(conf_edge))
        fps = Dummy.T2staff_computeFPs(copy.deepcopy(conf_edge))
        fns = Dummy.T2staff_computeFNs(copy.deepcopy(conf_edge))
        data_size = sum(sum(copy.deepcopy(conf_edge)))
        try:
            student_result = computeMacroRecall(tps, fps, fns, data_size)
        except Exception:
            student_result = -1
            logger.debug("Error during edge calculation!")
            with self.subTest(msg="Macro recall crashed on edge case"):
                self.assertEqual(False, True, "computeMacroRecall on edge failed caused exception!")
        expected = eval_edge[1, 5]
        res = roundEqual([student_result], [expected])
        logger.debug(
            "computeMacroRecall edge;Correct {}; got {} and expected {}".format(str(res) + '***********************\n',
                                                                                str(student_result), str(expected)))
        with self.subTest(msg="Checking if macro recall is calculated well on edge case"):
            self.assertEqual(res, True, "computeMacroRecall on edge failed")

        # We get tps, fps, etc from a confusion matrix
        # We do another nasty case where zero rows/columns happen

        tps = Dummy.T2staff_computeTPs(copy.deepcopy(conf_edge2))
        fps = Dummy.T2staff_computeFPs(copy.deepcopy(conf_edge2))
        fns = Dummy.T2staff_computeFNs(copy.deepcopy(conf_edge2))
        data_size = sum(sum(copy.deepcopy(conf_edge2)))
        try:
            student_result = computeMacroRecall(tps, fps, fns, data_size)
        except Exception:
            student_result = -1
            logger.debug("Error during edge calculation!")
            with self.subTest(msg = "Macro recall crashed on 2nd edge case"):
                self.assertEqual(False, True, "computeMacroRecall on edge failed caused exception!")
        expected = eval_edge2[1, 5]
        res = roundEqual([student_result], [expected])
        logger.debug(
            "computeMacroRecall edge2;Correct {}; got {} and expected {}".format(str(res) + '***********************\n',
                                                                                 str(student_result), str(expected)))
        with self.subTest(msg="Checking if macro recall is calculated well on 2nd edge case"):
            self.assertEqual(res, True, "computeMacroRecall on edge2 failed")

    # Typical errors that happen here is:
    # 1. Not handling edge cases
    # 2. Using micro not macro average
    # 3. Using harmonic mean of macro precision and recall, not macro average

    def testx12_computeMacroFMeasure(self):
        logger.debug("Testing macro fmeasure")

        # We are first testing on a nice confusion matrix, no edge cases
        tps = Dummy.T2staff_computeTPs(copy.deepcopy(conf_nice))
        fps = Dummy.T2staff_computeFPs(copy.deepcopy(conf_nice))
        fns = Dummy.T2staff_computeFNs(copy.deepcopy(conf_nice))
        data_size = sum(sum(copy.deepcopy(conf_nice)))

        # We get student results and compare it to expected ones that were pre-read
        student_result = Task_2.computeMacroFMeasure(tps, fps, fns, data_size)
        expected = eval_nice[1, 6]
        res = roundEqual([student_result], [expected])
        logger.debug(
            "computeMacroFMeasure nice;Correct {}; got {} and expected {}".format(
                str(res) + '***********************\n', str(student_result), str(expected)))
        with self.subTest(msg="Checking if macro f-measure is calculated well on nice case"):
            self.assertEqual(res, True, "computeMacroFMeasure on nice failed on good formula")

        # If proper formula failed, we check if it is miscalculated as harmonic mean of macro precision and recall
        if not res:
            expected = eval_nice[1, 7]
            res = roundEqual([student_result], [expected])
            logger.debug(
                "computeMacroFMeasure backup formula nice;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_result), str(expected)))

            with self.subTest(msg="Checking if macro f-measure is calculated using bad harmonic formula on nice case"):
                self.assertEqual(res, True, "computeMacroFMeasure on nice failed on bad harmonic formula")

        # If that failed too, we check if it is miscalculated as micro f-measure
        if not res:
            expected = eval_nice[1, 8]
            res = roundEqual([student_result], [expected])
            logger.debug(
                "computeMacroFMeasure micro formula nice;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_result), str(expected)))

            with self.subTest(msg="Checking if macro f-measure is calculated using bad micro formula on nice case"):
                self.assertEqual(res, True, "computeMacroFMeasure on nice failed on micro formula")

         # Checking if perhaps data size got misused
        if not res:
            student_result = computeMacroFMeasure(tps, fps, fns, 5)
            expected = eval_nice[1, 6]
            res = roundEqual([student_result], [expected])
            logger.debug(
                "checking if macro f-measure misused data_size;Correct {}; got {} and expected {}".format(
                       str(res) + '***********************\n', str(student_result), str(expected)))
            with self.subTest(msg="Checking if macro f-measure misused data size"):
                self.assertEqual(res, True,
                                    "computeMacroFMeasure did not use data size instead of class count either")

        # We now do the same on an edge case
        tps = Dummy.T2staff_computeTPs(copy.deepcopy(conf_edge))
        fps = Dummy.T2staff_computeFPs(copy.deepcopy(conf_edge))
        fns = Dummy.T2staff_computeFNs(copy.deepcopy(conf_edge))
        data_size = sum(sum(copy.deepcopy(conf_edge)))

        try:
            student_result = computeMacroFMeasure(tps, fps, fns, data_size)
        except Exception:
            student_result = -1
            logger.debug("Error during edge calculation!")
            with self.subTest(msg="F-measure crashed on edge case"):
                self.assertEqual(False, True, "computeMacroFMeasure on edge failed caused exception!")

        expected = eval_edge[1, 6]
        res = roundEqual([student_result], [expected])
        logger.debug(
            "computeMacroFMeasure edge;Correct {}; got {} and expected {}".format(
                str(res) + '***********************\n', str(student_result), str(expected)))

        with self.subTest(msg="Checking if macro f-measure is calculated well on edge case"):
            self.assertEqual(res, True, "computeMacroFMeasure on edge failed on good formula")

        # If proper formula failed, we check if it is miscalculated as harmonic mean of macro precision and recall
        if not res:
            expected = eval_edge[1, 7]
            res = roundEqual([student_result], [expected])
            logger.debug(
                "computeMacroFMeasure backup formula edge;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_result), str(expected)))

            with self.subTest(msg="Checking if macro f-measure is calculated using bad harmonic formula on edge case"):
                self.assertEqual(res, True, "computeMacroFMeasure on edge failed on backup formula")

        # If that failed too, we check if it is miscalculated as micro f-measure
        if not res:
            expected = eval_edge[1, 8]
            res = roundEqual([student_result], [expected])
            logger.debug(
                "computeMacroFMeasure micro formula edge;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_result), str(expected)))

            with self.subTest(
                    msg="Checking if macro f-measure is calculated using bad micro formula on edge case"):
                self.assertEqual(res, True, "computeMacroFMeasure on edge failed on micro formula")

        # Checking if perhaps data size got misused
        if not res:
            student_result = computeMacroFMeasure(tps, fps, fns, 5)
            expected = eval_edge[1, 6]
            res = roundEqual([student_result], [expected])
            logger.debug(
                "checking of macro f-measure misused data_size edge case ;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_result), str(expected)))
            with self.subTest(msg="Checking if macro f-measure misused data size edge case"):
                self.assertEqual(res, True,
                                 "computeMacroFMeasure did not use data size instead of class count either edge case")

        # We now do the same on another edge case
        tps = Dummy.T2staff_computeTPs(copy.deepcopy(conf_edge2))
        fps = Dummy.T2staff_computeFPs(copy.deepcopy(conf_edge2))
        fns = Dummy.T2staff_computeFNs(copy.deepcopy(conf_edge2))
        data_size = sum(sum(copy.deepcopy(conf_edge2)))

        try:
            student_result = computeMacroFMeasure(tps, fps, fns, data_size)
        except Exception:
            student_result = -1
            logger.debug("Error during edge calculation!")
            with self.subTest(msg="F-measure crashed on edge case2"):
                self.assertEqual(False, True, "computeMacroFMeasure on edge failed caused exception!")

        expected = eval_edge2[1, 6]
        res = roundEqual([student_result], [expected])
        logger.debug(
            "computeMacroFMeasure edge2;Correct {}; got {} and expected {}".format(
                str(res) + '***********************\n', str(student_result), str(expected)))

        with self.subTest(msg="Checking if macro f-measure is calculated well on edge case 2"):
            self.assertEqual(res, True, "computeMacroFMeasure on edge 2 failed on good formula")

        # If proper formula failed, we check if it is miscalculated as harmonic mean of macro precision and recall
        if not res:
            expected = eval_edge2[1, 7]
            res = roundEqual([student_result], [expected])
            logger.debug(
                "computeMacroFMeasure backup formula edge2;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_result), str(expected)))

            with self.subTest(msg="Checking if macro f-measure is calculated using bad harmonic formula on edge case 2"):
                self.assertEqual(res, True, "computeMacroFMeasure on edge 2 failed on backup formula")

        # If that failed too, we check if it is miscalculated as micro f-measure
        if not res:
            expected = eval_edge2[1, 8]
            res = roundEqual([student_result], [expected])
            logger.debug(
                "computeMacroFMeasure micro formula edge2;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_result), str(expected)))

            with self.subTest(
                    msg="Checking if macro f-measure is calculated using bad micro formula on edge case 2"):
                self.assertEqual(res, True, "computeMacroFMeasure on edge 2 failed on micro formula")

        # Checking if perhaps data size got misused
        if not res:
            student_result = computeMacroFMeasure(tps, fps, fns, 5)
            expected = eval_edge2[1, 6]
            res = roundEqual([student_result], [expected])
            logger.debug(
                "checking of macro f-measure misused data_size edge case 2;Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(student_result), str(expected)))
            with self.subTest(msg="Checking if macro f-measure misused data size edge case 2"):
                self.assertEqual(res, True,
                                 "computeMacroFMeasure did not use data size instead of class count either edge case 2")

    # Testing accuracy. Typical errors include:
    # 1. Using some completely garbled formula
    # 2. Handling data_size wrong
    # This is something more handled manually, so this is just a yes/no thing really
    def testx13_computeAccuracy(self):
        logger.debug("Testing macro accuracy nice")
        tps = Dummy.T2staff_computeTPs(copy.deepcopy(conf_nice))
        fps = Dummy.T2staff_computeFPs(copy.deepcopy(conf_nice))
        fns = Dummy.T2staff_computeFNs(copy.deepcopy(conf_nice))
        data_size = sum(sum(copy.deepcopy(conf_nice)))

        student_result = computeAccuracy(tps, fps, fns, data_size)
        expected = eval_nice[1, 7]
        res = roundEqual([student_result], [expected])
        logger.debug(
            "computeAccuracy nice;Correct {}; got {} and expected {}".format(str(res) + '***********************\n',
                                                                             str(student_result), str(expected)))
        with self.subTest(msg="Checking if accuracy is calculated well on nice case"):
            self.assertEqual(res, True, "computeAccuracy on nice failed")

        tps = Dummy.T2staff_computeTPs(copy.deepcopy(conf_edge))
        fps = Dummy.T2staff_computeFPs(copy.deepcopy(conf_edge))
        fns = Dummy.T2staff_computeFNs(copy.deepcopy(conf_edge))
        data_size = sum(sum(copy.deepcopy(conf_edge)))
        student_result = computeAccuracy(tps, fps, fns, data_size)
        expected = eval_edge[1, 7]
        res = roundEqual([student_result], [expected])
        logger.debug(
            "computeAccuracy edge;Correct {}; got {} and expected {}".format(str(res) + '***********************\n',
                                                                             str(student_result), str(expected)))
        with self.subTest(msg="Checking if accuracy is calculated well on edge case"):
            self.assertEqual(res, True, "computeAccuracy on edge failed")

        tps = Dummy.T2staff_computeTPs(copy.deepcopy(conf_edge2))
        fps = Dummy.T2staff_computeFPs(copy.deepcopy(conf_edge2))
        fns = Dummy.T2staff_computeFNs(copy.deepcopy(conf_edge2))
        data_size = sum(sum(copy.deepcopy(conf_edge2)))
        student_result = computeAccuracy(tps, fps, fns, data_size)
        expected = eval_edge2[1, 7]
        res = roundEqual([student_result], [expected])
        logger.debug(
            "computeAccuracy edge2;Correct {}; got {} and expected {}".format(str(res) + '***********************\n',
                                                                              str(student_result), str(expected)))
        with self.subTest(msg="Checking if accuracy is calculated well on edge case 2"):
            self.assertEqual(res, True, "computeAccuracy on edge2 failed")


def arrayEqual(data1, data2):
    nums1 = numpy.array(data1).flatten()
    nums2 = numpy.array(data2).flatten()
    return roundEqual(nums1, nums2)


def roundEqual(nums1, nums2):
    if len(nums1) != len(nums2):
        return False
    for i in range(0, len(nums1)):
        v1 = round(float(nums1[i]), 4)
        v2 = round(float(nums2[i]), 4)
        if v1 != v2:
            return False
    return True


if __name__ == "__main__":
    test_classes_to_run = [Task_2_Testing]
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(test_classes_to_run)
    runner = Testing_1.LogCaptureRunner(verbosity=2)
    runner.run(suite)
