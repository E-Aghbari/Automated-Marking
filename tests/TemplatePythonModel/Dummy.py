# If for some reason you have not completed Task 1 or Task 2 but can completed Task 3, feel free to use the following
# dummy functions.
import numpy
import sewar

import Helper
from typing import Callable

classification_scheme = ['Female', 'Male', 'Primate', 'Rodent', 'Food']

def dummyKNN(training_data, data_to_classify, k, measure_func, similarity_flag,  most_common_class_func,
             get_neighbour_classes_func, read_func, validate_format_func):
    classified_data = [['Path', 'ActualClass', 'PredictedClass']]
    for i in range(1, len(data_to_classify)):
        # this is only a dummy function, we default classification to Food
        classified_data.append(data_to_classify[i] + ['Food'])
    print("Running dummyKNN")
    return classified_data


def dummyEvaluateKNN(classified_data, confusion_func):
    precision = float(2)
    recall = float(2)
    f_measure = float(2)
    accuracy = float(2)
    return precision, recall, f_measure, accuracy

#########################
#########################
#### DELETE FOR STUDENSTS

def T1staff_getMostCommonClass(nearest_neighbours_classes: dict[str, int]) -> str:
    winner = ''
    maxv: int = 0
    for key in classification_scheme:
        if nearest_neighbours_classes.get(key, -1) > maxv:
            maxv = nearest_neighbours_classes[key]
            winner = key
    return winner


# The function finds the k nearest neighbours from measures_classes, and returns a dictionary made of classes
# and their occurrences based on these k nearest neighbours.
#
# INPUT:  measure_classes   : a list of tuples that contain two elements each - a distance/similarity value
#                             and class from scheme (in that order)
#         k                 : the value of k neighbours, greater than 0, not guaranteed to be smaller than data size.
#         similarity_flag   : a boolean value stating that the measure used to produce the values above is a distance
#                             (False) or a similarity (True)
# OUTPUT: nearest_neighbours_classes
#                           : a dictionary that, for each class in the scheme, states how often this class
#                             was in the k nearest neighbours
#
def T1staff_getClassesOfKNearestNeighbours(measures_classes: list[tuple[float, str]], k: int, similarity_flag: bool) -> (
        dict)[str, int]:
    nearest_neighbours_classes = {'Female': 0, 'Male': 0, 'Primate': 0, 'Rodent': 0, 'Food': 0}
    if similarity_flag:
        sorted_measures = sorted(measures_classes, key=lambda x: x[0], reverse=True)
    else:
        sorted_measures = sorted(measures_classes, key=lambda x: x[0])
    stop = k
    if k > len(measures_classes):
        stop = len(measures_classes)
    for i in range(stop):
        if sorted_measures[i][1] in nearest_neighbours_classes:
            nearest_neighbours_classes[sorted_measures[i][1]] += 1
    return nearest_neighbours_classes


# In this function I expect you to implement the kNN classifier. You are free to define any number of helper functions
# you need for this! You need to use all the other functions in the part of the template above.
#
# INPUT:  training_data       : a numpy array that was read from the training data csv
#         data_to_classify    : a numpy array  that was read from the data to classify csv;
#                             this data is NOT be used for training the classifier, but for running and testing it
#                             (see parse_arguments function)
#         k                   : the value of k neighbours, greater than 0, not guaranteed to be smaller than data size.
#         measure_func        : the function to be invoked to calculate similarity/distance (see Task 4 for
#                               some teacher-defined ones)
#         similarity_flag     : a boolean value stating that the measure above used to produce the values is a distance
#                             (False) or a similarity (True)
#     most_common_class_func  : the function to be invoked to find the most common class among the neighbours
#                             (by default, it is the one from above)
# get_neighbour_classes_func  : the function to be invoked to find the classes of nearest neighbours
#                             (by default, it is the one from above)
#         read_func           : the function to be invoked to find to read and resize images
#                             (by default, it is the Helper function)
#  OUTPUT: classified_data    : a numpy array which expands the data_to_classify with the results on how your
#                             classifier has classified a given image.

def T1staff_kNN(training_data: numpy.typing.NDArray, data_to_classify: numpy.typing.NDArray, k: int, measure_func: Callable,
        similarity_flag: bool, most_common_class_func=T1staff_getMostCommonClass,
        get_neighbour_classes_func=T1staff_getClassesOfKNearestNeighbours,
        read_func=Helper.readAndResize) -> numpy.typing.NDArray:
    # This sets the header list
    classified_data = numpy.array([['Path', 'ActualClass', 'PredictedClass']])
    # Have fun!
    train_data = []
    for row in training_data[1:]:
        t_class = row[1]
        img = read_func(row[0])
        train_data.append([img, t_class])

    for row in data_to_classify[1:]:
        test_img = read_func(row[0])
        measures_classes: list[tuple[float, str]] = []
        for train in train_data:
            measures_classes.append((measure_func(train[0], test_img), train[1]))
        neighbours = get_neighbour_classes_func(measures_classes, k, similarity_flag)
        winner = most_common_class_func(neighbours)
        classified_data = numpy.append(classified_data, [[row[0], row[1], winner]], axis=0)
    return classified_data




# This function computes the confusion matrix based on the provided data.
#
# INPUT: classified_data   : a numpy array containing paths to images, actual classes and predicted classes.
#                            Please refer to Task 1 for precise format description. Remember, this data contains
#                            header row!
# OUTPUT: confusion_matrix : a numpy array representing the confusion matrix computed based on the classified_data.
#                            The order of elements MUST be the same as in the classification scheme.
#                            The columns correspond to actual classes and rows to predicted classes.
#                            In other words, confusion_matrix[0] should be understood
#                            as the row of values predicted as Female, and [row[0] for row in confusion_matrix] as the
#                            column of values that were actually Female (independently of if the classified data
#                            contained Female entries or not).

def T2staff_confusionMatrix(classified_data: numpy.typing.NDArray) -> numpy.typing.NDArray:
    num = len(classification_scheme)
    confusion_matrix = numpy.zeros((num, num))
    for row in classified_data[1:]:
        actual_class = row[1]
        predicted_class = row[2]
        a_ind = classification_scheme.index(actual_class)
        p_ind = classification_scheme.index(predicted_class)
        confusion_matrix[p_ind, a_ind] += 1
    return confusion_matrix


# These functions compute per-class true positives and false positives/negatives based on the provided confusion matrix.
#
# INPUT: confusion_matrix : the numpy array representing the confusion matrix computed based on the classified_data.
#                           The order of elements is the same as  in the classification scheme.
#                           The columns correspond to actual classes and rows to predicted classes.
# OUTPUT: a list of ints representing appropriate true positive, false positive or false
#         negative values per a given class, in the same order as in the classification scheme. For example, tps[1]
#         corresponds to TPs for Male class.


def T2staff_computeTPs(confusion_matrix: numpy.typing.NDArray) -> list[int]:
    num = len(classification_scheme)
    tps = []
    for i in range(0, num):
        tps.append(confusion_matrix[i][i])
    return tps


def T2staff_computeFPs(confusion_matrix: numpy.typing.NDArray) -> list[int]:
    num = len(classification_scheme)
    fps = []
    for i in range(0, num):
        sum = 0
        for j in range(0, num):
            if i != j:
                sum += confusion_matrix[i, j]
        fps.append(sum)
    return fps


def T2staff_computeFNs(confusion_matrix: numpy.typing.NDArray) -> list[int]:
    num = len(classification_scheme)
    fns = []
    for i in range(0, num):
        sum = 0
        for j in range(0, num):
            if i != j:
                sum += confusion_matrix[j, i]
        fns.append(sum)
    return fns


# These functions compute the binary measures based on the provided values. Not all measures use all of the values.
#
# INPUT: tp, fp, fn : the values of true positives, false positive and negatives
# OUTPUT: appropriate evaluation measure created using the binary approach.

def T2staff_computeBinaryPrecision(tp: int, fp: int, fn: int) -> float:
    precision = float(0)
    bot = tp + fp
    if bot > 0:
        precision += tp / bot
    return precision


def T2staff_computeBinaryRecall(tp: int, fp: int, fn: int) -> float:
    recall = float(0)
    bot = tp + fn
    if bot > 0:
        recall += tp / bot
    return recall


def T2staff_computeBinaryFMeasure(tp: int, fp: int, fn: int) -> float:
    f_measure = float(0)
    recall = T2staff_computeBinaryRecall(tp,fp,fn)
    precision = T2staff_computeBinaryPrecision(tp,fp,fn)
    if recall + precision == 0:
        return f_measure
    f = 2 * precision * recall / (recall + precision)
    f_measure += f
    return f_measure


# These functions compute the evaluation measures based on the provided values. Not all measures use of all the values.
# You are expected to use appropriate binary counterparts when needed (binary recall for macro recall, binary precision
# for macro precision, binary f-measure for macro f-measure).
#
# INPUT: tps, fps, fns, data_size
#                       : the per-class true positives, false positive and negatives, and number of classified entries
#                         in the classified data (aka, don't count the header!)
# OUTPUT: appropriate evaluation measures created using the macro-average approach.

def T2staff_computeMacroPrecision(tps: list[int], fps: list[int], fns: list[int], data_size: int) -> float:
    precision = float(0)
    num = len(classification_scheme)
    for i in range(0, num):
        precision += T2staff_computeBinaryPrecision(tps[i], fps[i], fns[i])
    return precision / num


def T2staff_computeMacroRecall(tps: list[int], fps: list[int], fns: list[int], data_size: int) -> float:
    num = len(classification_scheme)
    recall = float(0)
    for i in range(0, num):
        recall += T2staff_computeBinaryRecall(tps[i], fps[i], fns[i])
    return recall / num


def T2staff_computeMacroFMeasure(tps: list[int], fps: list[int], fns: list[int], data_size: int) -> float:
    num = len(classification_scheme)
    f_measure = float(0)
    for i in range(0, num):
        f_measure += T2staff_computeBinaryFMeasure(tps[i], fps[i], fns[i])
    return f_measure / num


def T2staff_computeAccuracy(tps: list[int], fps: list[int], fns: list[int], data_size: int) -> float:
    if data_size == 0:
        return 0
    accuracy = sum(tps) / data_size
    return accuracy


# In this function you are expected to compute precision, recall, f-measure and accuracy of your classifier using
# the macro average approach.

# INPUT: classified_data   : a numpy array containing paths to images, actual classes and predicted classes.
#                            Please refer to Task 1 for precise format description.
#       confusion_func     : function to be invoked to compute the confusion matrix
#
# OUTPUT: computed measures
def T2staff_evaluateKNN(classified_data: numpy.typing.NDArray, confusion_func=T2staff_confusionMatrix) \
        -> tuple[float, float, float, float]:
    # Have fun with the computations!
    confusion_matrix = confusion_func(classified_data)
    # Remove the header to count the number of predictions
    data_size = len(classified_data[1:])
    tps = T2staff_computeTPs(confusion_matrix)
    fps = T2staff_computeFPs(confusion_matrix)
    fns = T2staff_computeFNs(confusion_matrix)
    precision = T2staff_computeMacroPrecision(tps, fps, fns, data_size)
    recall = T2staff_computeMacroRecall(tps, fps, fns, data_size)
    f_measure = T2staff_computeMacroFMeasure(tps, fps, fns, data_size)
    accuracy = T2staff_computeAccuracy(tps, fps, fns, data_size)
    # once ready, we return the values
    return precision, recall, f_measure, accuracy

def T3staff_partitionData(training_data: numpy.typing.NDArray, f: int) -> list[numpy.typing.NDArray]:
    if training_data.size == 0:
        return []
    if training_data[0, 0] == "Path":
        part = training_data[1:]
    else:
        part = training_data

    base_size = len(part) // f
    remainder = len(part) % f

    partition_list = []
    start = 0
    for i in range(0, f):
        chunk_size = base_size
        if remainder > 0:
            chunk_size += 1
            remainder -= 1
        end = start + chunk_size
        partition = part[start:end]
        start = end
        partition_list.append(partition)
    return partition_list


# This function transforms partitions into training and testing data for each cross-validation round (there are
# as many rounds as there are partitions); in other words, we prepare the folds.
# Please remember that the training and testing data for each round must include a header at this point.

# INPUT: partition_list     : a list of numpy arrays, where each array represents a partition (see partitionData function)
#        f                  : the number of folds to use in cross-validation, which is the same as the number of
#                             partitions the data was supposed to be split to, and the number of rounds in cross-validation.
#                             Value is greater than 0.
# OUTPUT: folds             : a list of 3-tuple s.t. the first element is the round number, second is the numpy array
#                             representing the training data for that round, and third is the numpy array representing
#                             the testing data for that round
#                             The round numbers START WITH 0
#                             You must make sure that the training and testing data are ready for use
#                             (e.g. contain the right headers already)


def T3staff_preparingDataForCrossValidation(partition_list: list[numpy.typing.NDArray], f: int) \
        -> list[tuple[int, numpy.typing.NDArray, numpy.typing.NDArray]]:
    # This is just for error handling, if for some magical reason f and number of partitions are not the same,
    # then something must have gone wrong in the other functions and you should investigate it
    if len(partition_list) != f:
        print("Something went really wrong! Why is the number of partitions different from f??")
        return []
    # Defining the header here for your convenience
    header = numpy.array([["Path", "ActualClass"]])

    folds = []
    # Implement your code here
    for i in range(0, f):

        new_test = numpy.array(partition_list[i])
        new_train = []
        for j in range(0, f):
            if i != j:
                new_train.extend(partition_list[j])

        new_train = numpy.insert(numpy.array(new_train), 0, header, axis=0)
        new_test = numpy.insert(new_test, 0, header, axis=0)

        folds.append((i, numpy.array(new_train), numpy.array(new_test)))
    return folds


# This function takes the classified data from each cross validation round and calculates the average precision, recall,
# accuracy and f-measure for them.
# Invoke either the Task 2 evaluation function or the dummy function here, do not code from scratch!
#
# INPUT: classified_data_list
#                           : a list of numpy arrays representing classified data computed for each cross validation round
#        evaluation_func    : the function to be invoked for the evaluation (by default, it is the one from
#                             Task_2, but you can use dummy)
# OUTPUT: avg_precision, avg_recall, avg_f_measure, avg_accuracy
#                           : average evaluation measures. You are expected to evaluate every classified data in the
#                             list and average out these values in the usual way.

def T3staff_evaluateResults(classified_data_list: list[numpy.typing.NDArray], evaluation_func=T2staff_evaluateKNN) \
        -> tuple[float, float, float, float]:
    avg_precision = float(0)
    avg_recall = float(0)
    avg_f_measure = float(0)
    avg_accuracy = float(0)
    # There are multiple ways to count average measures during cross-validation. For the purpose of this portfolio,
    # it's fine to just compute the values for each round and average them out in the usual way.

    for c in classified_data_list:
        precision, recall, f_measure, accuracy = evaluation_func(c)
        #  print(precision,recall,f_measure,accuracy)
        avg_precision += precision
        avg_recall += recall
        avg_f_measure += f_measure
        avg_accuracy += accuracy
    return avg_precision / len(classified_data_list), avg_recall / len(classified_data_list), avg_f_measure / len(
        classified_data_list), avg_accuracy / len(classified_data_list)

# In this task you are expected to perform and evaluate cross-validation on a given dataset.
# You are expected to partition the input dataset into f partitions, then arrange them into training and testing
# data for each cross validation round, and then run kNN for each round using this data and k, measure_func, and
# similarity_flag that are provided at input (see Task 1 for kNN input for more details).
# The results for each round are collected into a list and then evaluated.
#
# You are then asked to produce an output dataset which extends the original input training_data by adding
# "PredictedClass" and "FoldNumber" columns, which for each entry state what class it got predicted when it
# landed in a testing fold and what the number of that fold was (everything is in string format).
# This output dataset is then extended by two extra rows which add the average measures at the end.
#
# You are expected to invoke the Task 1 kNN classifier or the Dummy classifier here, do not implement these things
# from scratch! You must use the other relevant function defined in this file.
#
# INPUT: training_data      : a numpy array that was read from the training data csv (see parse_arguments function)
#        f                  : the value of k neighbours, greater than 0, not guaranteed to be smaller than data size.
#        k                  : the value of k neighbours, greater than 0, not guaranteed to be smaller than data size.
#        measure_func       : the function to be invoked to calculate similarity/distance (see Task 4 for
#                               some teacher-defined ones)
#        similarity_flag    : a boolean value stating that the measure above used to produce the values is a distance
#                             (False) or a similarity (True)
#        knn_func           : the function to be invoked for the classification (by default, it is the one from
#                             Task_1, but you can use dummy)
#        partition_func     : the function used to partition the input dataset (by default, it is the one above)
#        prep_func          : the function used to transform the partitions into appropriate folds
#                            (by default, it is the one above)
#        eval_func          : the function used to evaluate cross validation (by default, it is the one above)
# OUTPUT: output_dataset    : a numpy array which extends the original input training_data by adding "PredictedClass"
#                             and "FoldNumber" columns, which for each entry state what class it got predicted when it
#                             landed in a testing fold and what the number of that fold was (everything is in string
#                             format). This output dataset is then extended by two extra rows which add the average
#                             measures at the end (see the h and v variables).
def T3staff_crossEvaluateKNN(training_data: numpy.typing.NDArray, f: int, k: int, measure_func: Callable,
                     similarity_flag: bool, knn_func=T1staff_kNN,
                     partition_func=T3staff_partitionData, prep_func=T3staff_preparingDataForCrossValidation,
                     eval_func=T3staff_evaluateResults) -> numpy.typing.NDArray:
    # This adds the header
    output_dataset = numpy.array([['Path', 'ActualClass', 'PredictedClass', 'FoldNumber']])
    avg_precision = -1.0;
    avg_recall = -1.0;
    avg_fMeasure = -1.0;
    avg_accuracy = -1.0;
    classified_list = []

    # Have fun with the computations!
    partitions = partition_func(training_data, f)

    folds = prep_func(partitions, f)
    for i in range(0, len(folds)):
        result = knn_func(folds[i][1], folds[i][2], k, measure_func, similarity_flag)
        r = numpy.insert(result[1:], 3, folds[i][0], axis=1)
        output_dataset = numpy.vstack((output_dataset, r))
        classified_list.append(result)

    avg_precision, avg_recall, avg_fMeasure, avg_accuracy = eval_func(classified_list)

    # The measures are now added to the end. You should invoke validation BEFORE this step.
    h = ['avg_precision', 'avg_recall', 'avg_f_measure', 'avg_accuracy']
    v = [avg_precision, avg_recall, avg_fMeasure, avg_accuracy]

    output_dataset = numpy.append(output_dataset, [h], axis=0)
    output_dataset = numpy.append(output_dataset, [v], axis=0)

    return output_dataset
def T4staff_computeRMSEDistance(image1: numpy.typing.NDArray, image2: numpy.typing.NDArray) -> float:
    return sewar.rmse(image1, image2)