##########################################################################################
# Task 2 [6 points out of 30] Basic evaluation
# Evaluate your classifier. On your own, implement a method that will create a confusion matrix based on the provided
# classified data. Then implement methods that will return TPs, FPs and FNs based on the confusion matrix.
# From these, implement binary precision, recall and f-measure, and their macro counterparts.
# Finally, implement the multiclass version of accuracy.
# Remember to be mindful of edge cases (the approach for handling them is explained in lecture slides).
# The template contains a range of functions you must implement and use appropriately for this task.
# The template also uses a range of functions implemented by the module leader to support you in this task,
# particularly relating to reading images and csv files accompanying this portfolio.
# You can start working on this task immediately. Please consult at the very least Week 3 materials.
##########################################################################################

from Task_1 import classification_scheme
import Helper
import Dummy
import numpy


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

def confusionMatrix(classified_data: numpy.typing.NDArray) -> numpy.typing.NDArray:
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


def computeTPs(confusion_matrix: numpy.typing.NDArray) -> list[int]:
    num = len(classification_scheme)
    tps = []
    for i in range(0, num):
        tps.append(confusion_matrix[i][i])
    return tps


def computeFPs(confusion_matrix: numpy.typing.NDArray) -> list[int]:
    num = len(classification_scheme)
    fps = []
    for i in range(0, num):
        sum = 0
        for j in range(0, num):
            if i != j:
                sum += confusion_matrix[i, j]
        fps.append(sum)
    return fps


def computeFNs(confusion_matrix: numpy.typing.NDArray) -> list[int]:
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

def computeBinaryPrecision(tp: int, fp: int, fn: int) -> float:
    precision = float(0)
    bot = tp + fp
    if bot > 0:
        precision += tp / bot
    return precision


def computeBinaryRecall(tp: int, fp: int, fn: int) -> float:
    recall = float(0)
    bot = tp + fn
    if bot > 0:
        recall += tp / bot
    return recall


def computeBinaryFMeasure(tp: int, fp: int, fn: int) -> float:
    f_measure = float(0)
    recall = computeBinaryRecall(tp,fp,fn)
    precision = computeBinaryPrecision(tp,fp,fn)
    if recall + precision == 0:
        return f_measure
    f = 2 * precision * recall / (recall + precision)
    f_measure += f
    return f_measure


# These functions compute the evaluation measures based on the provided values - macro precision, macro recall,
# macro f-measure, and accuracy (multiclass version). Not all measures use of all the values.
# You are expected to use appropriate binary counterparts when needed (binary recall for macro recall, binary precision
# for macro precision, binary f-measure for macro f-measure).
#
# INPUT: tps, fps, fns, data_size
#                       : the per-class true positives, false positive and negatives, and number of classified entries
#                         in the classified data (aka, don't count the header!)
# OUTPUT: appropriate evaluation measures created using the macro-average approach.

def computeMacroPrecision(tps: list[int], fps: list[int], fns: list[int], data_size: int) -> float:
    precision = float(0)
    num = len(classification_scheme)
    for i in range(0, num):
        precision += computeBinaryPrecision(tps[i], fps[i], fns[i])
    return precision / num


def computeMacroRecall(tps: list[int], fps: list[int], fns: list[int], data_size: int) -> float:
    num = len(classification_scheme)
    recall = float(0)
    for i in range(0, num):
        recall += computeBinaryRecall(tps[i], fps[i], fns[i])
    return recall / num


def computeMacroFMeasure(tps: list[int], fps: list[int], fns: list[int], data_size: int) -> float:
    num = len(classification_scheme)
    f_measure = float(0)
    for i in range(0, num):
        f_measure += computeBinaryFMeasure(tps[i], fps[i], fns[i])
    return f_measure / num


def computeAccuracy(tps: list[int], fps: list[int], fns: list[int], data_size: int) -> float:
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
def evaluateKNN(classified_data: numpy.typing.NDArray, confusion_func=confusionMatrix) \
        -> tuple[float, float, float, float]:
    # Have fun with the computations!
    confusion_matrix = confusion_func(classified_data)
    # Remove the header to count the number of predictions
    data_size = len(classified_data[1:])
    tps = computeTPs(confusion_matrix)
    fps = computeFPs(confusion_matrix)
    fns = computeFNs(confusion_matrix)
    precision = computeMacroPrecision(tps, fps, fns, data_size)
    recall = computeMacroRecall(tps, fps, fns, data_size)
    f_measure = computeMacroFMeasure(tps, fps, fns, data_size)
    accuracy = computeAccuracy(tps, fps, fns, data_size)
    # once ready, we return the values
    return precision, recall, f_measure, accuracy


##########################################################################################
# You should not need to modify things below this line - it's mostly reading and writing #
# Be aware that error handling below is...limited.                                       #
##########################################################################################


# This function reads the necessary arguments (see parse_arguments function in Task_1_5),
# and based on them evaluates the kNN classifier.
def main():
    opts = Helper.parseArguments()
    if not opts:
        print("Missing input. Read the README file.")
        exit(1)
    print(f'Reading data from {opts["classified_data"]}')
    classified_data = Helper.readCSVFile(opts['classified_data'])
    if classified_data.size == 0:
        print("Classified data is empty, cannot run evaluation. Exiting Task 2.")
        return
    print('Evaluating kNN')
    result = evaluateKNN(classified_data)
    print('Result: precision {}; recall {}; f-measure {}; accuracy {}'.format(*result))


if __name__ == '__main__':
    main()
