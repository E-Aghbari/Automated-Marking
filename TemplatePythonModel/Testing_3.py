# https://gist.github.com/clayg/3787160
import unittest
import numpy
import sys
import cv2
from io import StringIO

import logging
import Dummy
import Task_3
import Testing_1
from Task_2 import *
from Task_1 import *
from Task_3 import *
import Task_3 as StuTask_3
import copy
from threading import Thread

numpy.seterr(divide='raise')
numpy.seterr(invalid='raise')

training_data = Helper.readCSVFile("../training_data4.csv")
training_data2 = training_data[:-1]
fold_num = 3
sys.tracebacklimit = 6
is_unique = True

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG, filename='test_3.log', filemode='w')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

eval_data = numpy.asarray(Helper.readCSVFile("../testing_files/evaluation_T3.csv"))
eval_data_res = numpy.asarray(Helper.readCSVFile("../testing_files/evaluation_res_T3.csv"))
header_p = ["Path", "ActualClass", "PredictedClass", "FoldNumber"]


class Task_3_Testing(Testing_1.BaseTestCase):
    # Most errors in this function do not go well into automatic testing, sadly.
    # So this is a generic tickety-boo test
    #
    def test1_crossEvaluateKNN(self):
        logger.debug("Testing crossEvaluateKNN")
        # Checking student code when invoking staff functions
        #
        try:
            output = crossEvaluateKNN(copy.deepcopy(training_data), fold_num, 3, Dummy.T4staff_computeRMSEDistance,
                                      False, Dummy.T1staff_kNN, Dummy.T3staff_partitionData,
                                      Dummy.T3staff_preparingDataForCrossValidation, Dummy.T3staff_evaluateResults)

            expected = Dummy.T3staff_crossEvaluateKNN(copy.deepcopy(training_data), fold_num, 3,
                                                      Dummy.T4staff_computeRMSEDistance,
                                                      False, Dummy.T1staff_kNN, Dummy.T3staff_partitionData,
                                                      Dummy.T3staff_preparingDataForCrossValidation,
                                                      Dummy.T3staff_evaluateResults)
            res = numpy.array_equal(output.astype('str'), expected.astype('str'))
            logger.debug(
                "crossEvaluateKNN with all staff functions (BE WARY OF SHUFFLE);Correct {}; Expected {} and got {}".format(
                    str(res) + '***********************\n', str(expected), str(output)))
            with self.subTest(msg="Checking if crossEvaluateKNN works out with all staff function"):
                self.assertEqual(res, True,
                                 "Wrong crossEvaluateKNN output even with staff functions, possible logic issue or shuffle")
        except Exception as e:
            print(e)
            logger.debug(
                "crossEvaluateKNN with all staff functions (BE WARY OF SHUFFLE);Correct False; Things crashed")
            with self.subTest(msg="Code crashed with staff functions"):
                self.assertEqual(False, True,
                                 "crossEvaluateKNN with all staff functions crashed")
        # Checking student code works on its own
        #

        try:
            output = crossEvaluateKNN(copy.deepcopy(training_data), fold_num, 3, Dummy.T4staff_computeRMSEDistance,
                                      False)

            expected = Dummy.T3staff_crossEvaluateKNN(copy.deepcopy(training_data), fold_num, 3,
                                                      Dummy.T4staff_computeRMSEDistance,
                                                      False, Dummy.T1staff_kNN, Dummy.T3staff_partitionData,
                                                      Dummy.T3staff_preparingDataForCrossValidation,
                                                      Dummy.T3staff_evaluateResults)
            res = numpy.array_equal(output.astype('str'), expected.astype('str'))
            logger.debug(
                "crossEvaluateKNN student vs staff;Correct {}; Expected {} and got {}".format(
                    str(res) + '***********************\n', str(expected), str(output)))
            with self.subTest(msg="Checking if student vs staff is the same"):
                self.assertEqual(res, True,
                                 "Wrong crossEvaluateKNN staff vs student is wrong, possible logic issue or shuffle")

        except Exception as e:
            print(e)
            logger.debug(
                "crossEvaluateKNN with all student functions (BE WARY OF SHUFFLE);Correct False; Things crashed")
            with self.subTest(msg="Code crashed with student functions"):
                self.assertEqual(False, True,
                                 "crossEvaluateKNN with all student functions crashed")

    # This is testing the partitioning function.
    # Typical errors are:
    # 0. Producing wrong number of partitions
    # 1. The header is not flushed and ends up randomly there
    # 2. The partitions are not of roughly equal size (they can differ by at most 1)
    # 3. The partitions overlap
    # 4. The partitions do not add up to the whole initial data set
    # 5. Crashes on excessive k
    def test2_partitionData(self):

        # We set up the data to check
        data = copy.deepcopy(training_data)
        student_output = Task_3.partitionData(data, fold_num)
        # We check if number of partitions is as desired
        res = len(student_output)==fold_num
        logger.debug(
            "partitionData partition number check;Correct {}; requested {} folds and got {}".format(str(res), str(fold_num),
                                                                               str(len(student_output)) + '***********************\n'))
        with self.subTest(msg="Checking if the number of partitions is as requested"):
            self.assertEqual(res, True,
                             "the number of partitions is not as requested, requested " + str(
                                 fold_num) + " and got " + str(len(student_output)))

        # We check if header is present. If no, we continue. If yes, we have a problem, and we rerun the partition function
        # minus the header in the initial data
        header_present = partition_header_present(student_output)

        logger.debug("checking if header got purged from partitions;Correct {};".format(
            str(not header_present) + '***********************\n'))
        with self.subTest(msg="Checking if header got deleted from partitions"):
            self.assertEqual(header_present, False, "header was not purged before partitioning")
        if header_present:
            data = copy.deepcopy(training_data)
            student_output = Task_3.partitionData(data[1:], fold_num)

        # We now check if partitions are of roughly same size
        res, min_val, max_val = partition_balance_check(student_output)
        logger.debug(
            "partitionData balance check;Correct {}; min {} and max {}".format(str(res), str(min_val),
                                                                               str(max_val) + '***********************\n'))
        with self.subTest(msg="Checking if partitions have balanced sizes"):
            self.assertEqual(res, True,
                             "partitionData is not balanced, min is " + str(
                                 min_val) + " and max is " + str(max_val))

        # We now check if partitions add up to the whole dataset
        res = partition_completeness_check(student_output, data)
        logger.debug(
            "partitionData completeness check;Correct {};".format(str(res) + '***********************\n'))
        with self.subTest(msg="Checking if partitions add up to the whole dataset"):
            self.assertEqual(res, True,
                             "partitionData does is incomplete")

        # We now check for overlaps - if there are any, frequency goes above 1
        res, entry_frequency = partition_overlap_check(student_output)
        logger.debug(
            "partitionData overlap check;Correct {}; min {} and max {}".format(
                str(res), str(min(entry_frequency.values())),
                str(max(entry_frequency.values())) + '***********************\n'))
        with self.subTest(msg="Checking if partitions overlap"):
            self.assertEqual(res, True,
                             "partitionData overlap check failed;  min {} and max {}".format(
                                 str(min(entry_frequency.values())), str(max(entry_frequency.values()))))

        # Checking if excessive f is not crashing stuff
        try:
            t = Thread(target=Task_3.partitionData, args=(data, len(data) + 10))
            t.daemon = True
            t.start()
            t.join(5)
            if t.is_alive():
                raise Exception("Timeout!")
            #student_output = Task_3.partitionData(data, len(data) + 10)
        except Exception as error:
            print(error)
            res = False
        logger.debug(
            "partitionData excessive f did not crash or timeout;Correct {};".format(
                str(res) + '***********************\n'))
        with self.subTest(msg="Checking if partitionData survives excessive f"):
            self.assertEqual(res, True,
                             "partitionData crashed or timed out on excessive f")

    # Same as before, just diff data set
    def test3_partitionData2(self):

        # We set up the data to check
        data = copy.deepcopy(training_data2)
        student_output = Task_3.partitionData(data, fold_num)

        # We check if number of partitions is as desired
        res = len(student_output)==fold_num
        logger.debug(
            "partitionData partition number check;Correct {}; requested {} folds and got {}".format(str(res), str(fold_num),
                                                                               str(len(student_output)) + '***********************\n'))
        with self.subTest(msg="Checking if the number of partitions is as requested"):
            self.assertEqual(res, True,
                             "the number of partitions is not as requested, requested " + str(
                                 fold_num) + " and got " + str(len(student_output)))
        # We check if header is present. If no, we continue. If yes, we have a problem, and we rerun the partition function
        # minus the header in the initial data
        header_present = partition_header_present(student_output)

        logger.debug("checking if header got purged from partitions;Correct {};".format(
            str(not header_present) + '***********************\n'))
        with self.subTest(msg="Checking if header got deleted from partitions"):
            self.assertEqual(header_present, False, "header was not purged before partitioning")
        if header_present:
            data = copy.deepcopy(training_data2)
            student_output = Task_3.partitionData(data[1:], fold_num)

        # We now check if partitions are of roughly same size
        res, min_val, max_val = partition_balance_check(student_output)
        logger.debug(
            "partitionData balance check;Correct {}; min {} and max {}".format(str(res), str(min_val),
                                                                               str(max_val) + '***********************\n'))
        with self.subTest(msg="Checking if partitions have balanced sizes"):
            self.assertEqual(res, True,
                             "partitionData is not balanced, min is " + str(
                                 min_val) + " and max is " + str(max_val))

        # We now check if partitions add up to the whole dataset
        res = partition_completeness_check(student_output, data)
        logger.debug(
            "partitionData completeness check;Correct {};".format(str(res) + '***********************\n'))
        with self.subTest(msg="Checking if partitions add up to the whole dataset"):
            self.assertEqual(res, True,
                             "partitionData does is incomplete")

        # We now check for overlaps - if there are any, frequency goes above 1
        res, entry_frequency = partition_overlap_check(student_output)
        logger.debug(
            "partitionData overlap check;Correct {}; min {} and max {}".format(
                str(res), str(min(entry_frequency.values())),
                str(max(entry_frequency.values())) + '***********************\n'))
        with self.subTest(msg="Checking if partitions overlap"):
            self.assertEqual(res, True,
                             "partitionData overlap check failed;  min {} and max {}".format(
                                 str(min(entry_frequency.values())), str(max(entry_frequency.values()))))

        # Checking if excessive f is not crashing stuff
        try:
            t = Thread(target=Task_3.partitionData, args=(data, len(data) + 10))
            t.daemon = True
            t.start()
            t.join(5)
            if t.is_alive():
                raise Exception("Timeout!")
            #student_output = Task_3.partitionData(data, len(data) + 10)
        except Exception as error:
            print(error)
            res = False
        logger.debug(
            "partitionData2 excessive f did not crash or timeout;Correct {};".format(
                str(res) + '***********************\n'))
        with self.subTest(msg="Checking if partitionData2 survives excessive f"):
            self.assertEqual(res, True,
                             "partitionData2 crashed or timed out on excessive f")

    # Things to look for:
    # 1. Fold number
    # 2. Training and testing data having headers
    # 3. Testing and training data not overlapping
    # 4. Testing and training data adding up to full data

    def test4_preparingDataForCrossValidation(self):
        data = copy.deepcopy(training_data)
        partitions = Dummy.T3staff_partitionData(data, fold_num)

        student_output = preparingDataForCrossValidation(partitions, fold_num)

        # the expected order of elements is fold number - training data - testing - data, this checks if fold vals are ok
        # fold indexing from 0 is expected
        res, val_list, expected_val_list = check_fold_index(0, fold_num, student_output)
        logger.debug("preparingDataForCrossValidation index check from 0;Correct {}; got {} and expected {}".format(
            str(res) + '***********************\n', str(val_list),
            str(expected_val_list)))
        with self.subTest(msg="Checking if indexing starts from 0"):
            self.assertEqual(res, True, "preparingDataForCrossValidation indexing from 0 failed")
        if not res:
            res2, val_list, expected_val_list2 = check_fold_index(1, fold_num + 1, student_output)
            logger.debug(
                "preparingDataForCrossValidation index check from 1;Correct {}; got {} and expected {}".format(
                    str(res2), str(val_list),
                    str(expected_val_list2)))
            with self.subTest(msg="Checking if indexing starts from 1"):
                self.assertEqual(res2, True, "preparingDataForCrossValidation indexing from 1 failed")

        # Making sure folds do not intersect
        purged_folds, headers_consistency = header_purge(student_output)
        overlaps = fold_overlap_check(purged_folds)
        logger.debug(
            "preparingDataForCrossValidation empty intersection check;Correct {}; got overlaps on {}".format(
                str(len(overlaps)==0) + '***********************\n',
                str(overlaps)))
        with self.subTest(
                msg="Checking that training and testing data do not intersect on folds"):
            self.assertEqual(len(overlaps), 0, "test and train data intersected: " + str(overlaps))

        failed_completeness_folds = fold_completeness_check(purged_folds,data)
        res = len(failed_completeness_folds)==0
        logger.debug(
            "preparingDataForCrossValidation size checks;Correct {}; failed on {}".format(str(res) + '***********************\n',str(failed_completeness_folds)))
        with self.subTest(
                msg="Checking that training and testing data add up to whole data on all folds"):
            self.assertEqual(res, True, "preparingDataForCrossValidation size check failed on folds " + str (failed_completeness_folds))

        if fold_num > 2:
            fails = size_check(student_output)
            logger.debug(
                "preparingDataForCrossValidation test train size checks on non-purged data;Correct {}; failed folds".format(
                    str(len(fails) == 0), str(fails) + '***********************\n'))
            with self.subTest(msg="Checking that training data is greater than testing data on non-purged"):
                self.assertEqual(len(fails) == 0, True,
                                 "preparingDataForCrossValidation on non-purged data test is greater than train on folds " + str(
                                     fails))
            fails = size_check(purged_folds)
            logger.debug(
                "preparingDataForCrossValidation test train size checks on purged data;Correct {}; failed folds".format(
                    str(len(fails) == 0), str(fails) + '***********************\n'))
            with self.subTest(msg="Checking that training data is greater than testing data on purged"):
                self.assertEqual(len(fails) == 0, True,
                                 "preparingDataForCrossValidation on purged data test is greater than train on folds " + str(
                                     fails))

        res, min_val, max_val = balance_check(student_output)
        logger.debug(
            "preparingDataForCrossValidation balanced on non-purged data;Correct {}; min {} and max {}".format(str(res),
                                                                                                               str(min_val),
                                                                                                               str(max_val) + '***********************\n'))
        with self.subTest(msg="Checking that things are balanced on non-purged data"):
            self.assertEqual(res, True,
                             "preparingDataForCrossValidation is not balanced on non-purged data, min is " + str(
                                 min_val) + " and max is " + str(
                                 max_val))

        res, min_val, max_val = balance_check(purged_folds)
        logger.debug(
            "preparingDataForCrossValidation balanced on purged data;Correct {}; min {} and max {}".format(str(res),
                                                                                                           str(min_val),
                                                                                                           str(max_val) + '***********************\n'))
        with self.subTest(msg="Checking that things are balanced on purged data"):
            self.assertEqual(res, True,
                             "preparingDataForCrossValidation is not balanced on purged data, min is " + str(
                                 min_val) + " and max is " + str(
                                 max_val))

        res, train_frequency, test_frequency = check_frequency(data, student_output)
        logger.debug(
            "preparingDataForCrossValidation equal occurrence;Correct {}; min train {} and max train {} min test {} and max test {}".format(
                str(res), str(min(train_frequency.values())), str(max(train_frequency.values())),
                str(min(test_frequency.values())), str(max(test_frequency.values())) + '***********************\n'))
        with self.subTest(msg="Checking equal occurrence between testing adn training data"):
            self.assertEqual(res, True,
                             "preparingDataForCrossValidation equal occurrence failed; min train {} and max train {} min test {} and max test {}".format(
                                 str(min(train_frequency.values())), str(max(train_frequency.values())),
                                 str(min(test_frequency.values())), str(max(test_frequency.values()))))
        head_check1 = (sum(headers_consistency) == len(headers_consistency))
        logger.debug(
            "headers present at all times; Correct {}".format(
                str(head_check1) + '***********************\n'))
        with self.subTest(msg="Checking if headers are all present"):
            self.assertEqual(head_check1, True,
                             "headers not present at all times")

    def test5_evaluateResults(self):
        logger.debug("Testing evaluateResults")
        folds = [e[3] for e in eval_data[1:]]
        folds = set(folds)

        classified_data_list = []
        for fs in folds:
            classified_data = numpy.array(eval_data[(fs == eval_data[:, 3])])
            classified_data = numpy.insert(classified_data, 0, header_p, 0)
            classified_data_list.append(classified_data)

        try:
            output = evaluateResults(copy.deepcopy(classified_data_list))
            expected_output = eval_data_res[1, 1:]

            res = roundEqual(output, expected_output)
            logger.debug(
                "evaluateResults with student func; Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n', str(output), str(expected_output)))
            with self.subTest(msg="Checking if evaluating results with student function worked"):
                self.assertEqual(res, True, "evaluateResults with student func failed")
        except Exception as e:
            print(e)
            logger.debug(
                "evaluateResults with student func; Correct False; Things crashed")
            with self.subTest(msg="Code crashed with student functions"):
                self.assertEqual(res, True, "evaluateResults with student func crashed")
        try:
            output = evaluateResults(copy.deepcopy(classified_data_list), evaluation_func=Dummy.T2staff_evaluateKNN)
            expected_output = eval_data_res[1, 1:]
            res = roundEqual(output, expected_output)
            logger.debug(
                "evaluateResults with staff func; Correct {}; got {} and expected {}".format(
                    str(res) + '***********************\n',
                    str(output), str(
                        expected_output)))
            with self.subTest(msg="Checking if evaluating results with staff function worked"):
                self.assertEqual(res, True, "evaluateResults with staff func failed")
        except Exception as e:
            print(e)
            logger.debug(
                "evaluateResults with staff func; Correct False; Things crashed")
            with self.subTest(msg="Code crashed with staff functions"):
                self.assertEqual(res, True, "evaluateResults with staff func crashed")


def size_check(fold_data):
    fails = []
    for fold in fold_data:
        res = len(fold[2]) < len(fold[1])
        if not res:
            fails.append(fold[0])
    return fails


# this is checking that the size of training data folds is different by at most 1
def balance_check(fold_data):
    min_val = min([len(r[1]) for r in fold_data])
    max_val = max([len(r[1]) for r in fold_data])
    res = abs(max_val - min_val) <= 1
    return res, min_val, max_val


# this is to handle situations where students forget the !@$#%^ headers in splits
def header_purge(fold_data):
    purged_folds = []
    headers_consistency = []

    # this is to check if folds consistently start (or not start) with the header - they should all have the header nicely
    for fold in fold_data:
        train = fold[1]
        test = fold[2]
        if test[0][0] == 'Path':
            headers_consistency.append(1)
        else:
            headers_consistency.append(0)
        if train[0][0] == 'Path':
            headers_consistency.append(1)
        else:
            headers_consistency.append(0)
    # we are now doing the header purge
    for fold in fold_data:
        index = fold[0]
        train = fold[1]
        test = fold[2]
        purged_train = []
        purged_test = []
        for t in train:
            if t[0] == 'Path':
                continue
            else:
                purged_train.append(t)
        for t in test:
            if t[0] == 'Path':
                continue
            else:
                purged_test.append(t)
        purged_folds.append([index, numpy.array(purged_train), numpy.array(purged_test)])

    return purged_folds, headers_consistency


# start inclusive, end exclusive
def check_fold_index(start_val, end_val, fold_data):
    fold_col = [row[0] for row in fold_data]
    val_list = fold_col
    val_list.sort()
    expected_val_list = list(range(start_val, end_val))
    expected_val_list.sort()
    res = val_list == expected_val_list
    return res, val_list, expected_val_list


# train_data is the training data on which the test is being ran, fold_data is the students output from splitting function
def check_frequency(train_data, fold_data):
    test_frequency = {}
    train_frequency = {}
    # we will use this to make sure that every image path shows up in test data exactly once and in training data f-1 times
    for row in train_data:
        if (row[0] == 'Path'):
            continue
        test_frequency[row[0]] = 0
        train_frequency[row[0]] = 0
    for fold in fold_data:
        test = fold[2]
        train = fold[1]
        for t in train:
            if (t[0] != 'Path'):
                train_frequency[t[0]] += 1
        for t in test:
            if (t[0] != 'Path'):
                test_frequency[t[0]] += 1
    res = all(val == (fold_num - 1) for val in train_frequency.values()) and all(
        val == 1 for val in test_frequency.values())
    return res, train_frequency, test_frequency

# This checks whether training and testing data do not overlap per fold - folds are purged of headers
def fold_overlap_check(purged_folds):
    overlaps = {}
    for fold in purged_folds:
        test = fold[2]
        train = fold[1]

        # this is under the assumption that training_data info was unique
        intersection = [x for x in train[:, 0] if x in test[:, 0]]
        res = len(intersection) == 0
        if not res:
            overlaps[fold[0]] = intersection
    return overlaps

def fold_completeness_check(purged_folds, data):
    failed_folds = []
    for fold in purged_folds:
        test = fold[2]
        train = fold[1]
        cover = [x for x in numpy.vstack((test, train))[:, 0] if x in data[:, 0]]
        res = len(cover) == len(data[1:])
        if not res:
            failed_folds.append(fold[0])
    return failed_folds

# This assumes no headers are present here!
def partition_overlap_check(data_list):
    entry_frequency = {}
    for data in data_list:
        for row in data:
            entry_frequency[row[0]] = entry_frequency.get(row[0], 0) + 1

    res = all(val == 1 for val in entry_frequency.values())
    return res, entry_frequency


# This assumes the header is not in partitions anymore
def partition_completeness_check(data_list, original_data):
    total = numpy.vstack(data_list)
    data = copy.deepcopy(original_data)
    if original_data[0, 0] == 'Path':
        data = original_data[1:]
    intersection = [x for x in data if x in total]
    intersection2 = [x for x in total if x in data]
    if numpy.array_equal(intersection, data) and numpy.array_equal(intersection2, total):
        return True
    return False


def partition_header_present(data_list):
    for data in data_list:
        for row in data:
            if row[0] == 'Path':
                return True
    return False


def partition_balance_check(data_list: list[numpy.typing.NDArray]):
    min_val = min([len(r) for r in data_list])
    max_val = max([len(r) for r in data_list])
    res = abs(max_val - min_val) <= 1
    return res, min_val, max_val


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
            return False;
    return True


if __name__ == "__main__":
    test_classes_to_run = [Task_3_Testing]
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(test_classes_to_run)
    runner = Testing_1.LogCaptureRunner(verbosity=2)
    runner.run(suite)
