##########################################################################################
# Task 1 [7 points out of 30] My first not-so-pretty image classifier
# Your first task is to implement the kNN classifier on your own. The template contains a range of functions
# you must implement and use appropriately for this task. The template also uses a range of functions implemented
# by the module leader to support you in this task, particularly relating to reading images and csv files accompanying
# this portfolio.
# You can start working on this task immediately. Please consult at the very least Week 2 materials.
##########################################################################################

import os
import Dummy
import Helper
import numpy
from typing import Callable
import Task_4

# Please replace with your student id, including the "c" at the beginning!!!
student_id = 'Test4'

# This is the classification scheme you should use for kNN
classification_scheme = ['Female', 'Male', 'Primate', 'Rodent', 'Food']


# Given a dictionary of classes and their occurrences, returns a class from the scheme that is most common in that
# dictionary. In case there are multiple candidates, it follows the order of classes in the scheme.
# The function returns empty string if the input dictionary is empty, does not contain any classes from the scheme,
# or if all classes in the scheme have occurrence of 0.
#
# INPUT: nearest_neighbours_classes
#                           : a dictionary that, for each and every class in the scheme, states the occurrence number
#                             of this class (this particular value is calculated elsewhere)
#
# OUTPUT: winner            : a class from classification scheme that is most common in the input variable.
#                             In case there are multiple candidates, it follows the order of classes in the scheme.
#                             Returns empty string if the input dictionary is empty, does not contain any classes
#                             from the scheme, or if all classes in the scheme have occurrence of 0
#

def getMostCommonClass(nearest_neighbours_classes, classification_scheme):
    winner = ''
    if nearest_neighbours_classes == {}:
        return winner

    for class_occurance in classification_scheme:
        if class_occurance in nearest_neighbours_classes:
            if nearest_neighbours_classes[class_occurance] > 0:
                winner = class_occurance
                break

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
def getClassesOfKNearestNeighbours(measures_classes: list[tuple[float, str]], k: int, similarity_flag: bool) -> (
        dict)[str, int]:
    nearest_neighbours_classes = {'Female': 0, 'Male': 0, 'Primate': 0, 'Rodent': 0, 'Food': 0}
    if similarity_flag:
        sorted_measures = sorted(measures_classes, key=lambda x: x[1], reverse=True)
    else:
        sorted_measures = sorted(measures_classes, key=lambda x: x[1])
    stop = k
    if k > len(measures_classes):
        stop = len(measures_classes)
    for i in range(stop):
        if sorted_measures[i][0] in nearest_neighbours_classes:
            nearest_neighbours_classes[sorted_measures[i][0]] += 1
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

def kNN(training_data: numpy.typing.NDArray, data_to_classify: numpy.typing.NDArray, k: int, measure_func: Callable,
        similarity_flag: bool, most_common_class_func=getMostCommonClass,
        get_neighbour_classes_func=getClassesOfKNearestNeighbours,
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
            measures_classes.append((train[1],measure_func(train[0], test_img)))
        neighbours = getClassesOfKNearestNeighbours(measures_classes, k, similarity_flag)
        winner = getMostCommonClass(neighbours)
        classified_data = numpy.append(classified_data, [[row[0], row[1], winner]], axis=0)
    return classified_data


##########################################################################################
# Do not modify things below this line - it's mostly reading and writing #
# Be aware that error handling below is...limited.                                       #
##########################################################################################


# This function reads the necessary arguments from input (see parse_arguments function in Helper file),
# and based on them executes
# the kNN classifier. If the "unseen" mode is on, the results are written to a file.

def main():
    opts = Helper.parseArguments()
    if not opts:
        print("Missing input. Read the README file.")
        exit(1)
    print(f'Reading data from {opts["training_data"]} and {opts["data_to_classify"]}')
    training_data = Helper.readCSVFile(opts['training_data'])
    data_to_classify = Helper.readCSVFile(opts['data_to_classify'])
    unseen = opts['mode']
    if training_data.size == 0 or data_to_classify.size == 0:
        print("Not all of the input data is present, cannot run kNN. Exiting Task 1.")
        return
    if opts['k'] is None or opts['k']<1:
        print("Value of k is missing from input or too small, cannot run kNN. Exiting Task 1.")
        return
    if opts['simflag'] is None:
        print("Similarity flag is missing from input, cannot run kNN. Exiting Task 1.")
        return
    print('Running kNN')
    try:
        result = kNN(training_data, data_to_classify, opts['k'], eval(opts['measure']), opts['simflag'])
    except NameError as nerror:
        print(nerror)
        print("Wrong measure function name was passed to the function, please double check the function name. "
              "For example, try 'Task_4.computePSNRSimilarity' and make sure you have not deleted any imports "
              "from the template.")
        return
    if unseen:
        path = os.path.dirname(os.path.realpath(opts['data_to_classify']))
        out = f'{path}/{student_id}_classified_data.csv'
        print(f'Writing data to {out}')
        Helper.writeCSVFile(out, result)


if __name__ == '__main__':
    main()
