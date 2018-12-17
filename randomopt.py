from __future__ import division
from pylab import *
import random as rnd
import networkx as nx
import os
import math
from maxpq import MaxPQ
from multiprocessing import Pool
from random import shuffle
import pickle
import time
import os.path
from score_function import score_output 
import copy
import itertools
import random


def swap(graph, num_buses, size_bus, constraints, result):
    prev_score = score_output(graph, num_buses, size_bus, constraints, result)
    for i in range(len(result)-1):
        for j in range(i+1, len(result)):
            for x in range(len(result[i])):
                for y in range(len(result[j])):
                    temp = result[i][x]
                    result[i][x] = result[j][y]
                    result[j][y] = temp
                    if score_output(graph, num_buses, size_bus, constraints, result) > prev_score:
                        swap(result)
                    if i==len(result)-2 and x == len(result[i])-1 and y == len(result[i+1])-1:
                        return
                    result[j][y] = result[i][x]
                    result[i][x] = temp


def random_swap(graph, num_buses, size_bus, constraints, result):
    #result is a 2d array containing student assignment:
    prev_score = score_output(graph, num_buses, size_bus, constraints, result)
    x1 = random.randint(0, len(result) - 1)
    x2 = random.randint(0, len(result) - 1)

    #prevent two buses are the same
    while x1 == x2:
        x2 = random.randint(0, len(result) - 1)

    bus1 = result[x1]
    bus2 = result[x2]

    #get index of random student
    y1 = random.randint(0, len(bus1) - 1)
    y2 = random.randint(0, len(bus2) - 1)

    #choose random student from buses and swap them
    student1 = bus1[y1]
    student2 = bus2[y2]

    #swap them
    temp = result[x1][y1]
    result[x1][y1] = result[x2][y2]
    result[x2][y2] = temp

    if score_output(graph, num_buses, size_bus, constraints, result) <= prev_score:
        result[x2][y2] = result[x1][y1]
        result[x1][y1] = temp


def random_two_swap(graph, num_buses, size_bus, constraints, result):
    #result is a 2d array containing student assignment:
    prev_score = score_output(graph, num_buses, size_bus, constraints, result)
    x1 = random.randint(0, len(result) - 1)
    x2 = random.randint(0, len(result) - 1)

    #prevent there's only one student in the bus
    while len(result[x1]) == 1:
        x1 = random.randint(0, len(result) - 1)

    #if all other buses except x1 only has one student, return
    if all_one(x1, result):
        return

    #prevent two buses are the same
    while x1 == x2 or len(result[x2]) == 1:
        x2 = random.randint(0, len(result) - 1)



    bus1 = result[x1]
    bus2 = result[x2]

    #get index of random student
    y1 = random.randint(0, len(bus1) - 1)
    z1 = random.randint(0, len(bus1) - 1)

    while y1 == z1:
        z1 = random.randint(0, len(bus1) - 1)
    y2 = random.randint(0, len(bus2) - 1)
    z2 = random.randint(0, len(bus2) - 1)

    while y2 == z2:
        z2 = random.randint(0, len(bus2) - 1)

    #choose random student from buses and swap them
    student1 = bus1[y1]
    student2 = bus2[y2]

    another_student1 = bus1[z1]
    another_student2 = bus2[z2]

    #swap them
    temp1 = result[x1][y1]
    result[x1][y1] = result[x2][y2]
    result[x2][y2] = temp1

    temp2 = result[x1][z1]
    result[x1][z1] = result[x2][z2]
    result[x2][z2] = temp2

    if score_output(graph, num_buses, size_bus, constraints, result) <= prev_score:
        result[x2][y2] = result[x1][y1]
        result[x1][y1] = temp1

        result[x2][z2] = result[x1][z1]
        result[x1][z1] = temp2

def random_move(graph, num_buses, size_bus, constraints, result):
    #result is a 2d array containing student assignment:

    #prevent no place to move.
    if size_bus * num_buses == len(graph.nodes):
        return

    prev_score = score_output(graph, num_buses, size_bus, constraints, result)

    s = random.randint(0, len(result) - 1)
    t = random.randint(0, len(result) - 1)

    while len(result[s]) == 1 or all_full(s, result, size_bus):
        s = random.randint(0, len(result) - 1)

    #prevent two buses are the same
    while t == s or t >= size_bus:
        t = random.randint(0, len(result) - 1)

    source_bus = result[s]
    target_bus = result[t]

    #choose random student from t
    student_index = random.randint(0, len(source_bus)- 1)
    student = source_bus[student_index]

    result[t].append(student)
    del result[s][student_index]

    #check for scoure improvement
    if score_output(graph, num_buses, size_bus, constraints, result) <= prev_score:
        del result[t][-1]
        result[s].append(student)

def all_full(t, result, size_bus):
    #check if all buses except t is full
    all_full = []
    for bus in range(len(result)):
        if bus != t:
            all_full.append(len(result[bus]) == size_bus)
    return all(all_full)

def all_one(t, result):
    #check if all buses except t is full
    all_one = []
    for bus in range(len(result)):
        if bus != t:
            all_one.append(len(result[bus]) == 1)
    return all(all_one)


def get_assignment(output_file):
    output = open(output_file)
    assignments = []
    for line in output:
        line = line[1: -2]
        curr_assignment = [node.replace("'","") for node in line.split(", ")]
        assignments.append(curr_assignment)

    return assignments

def formatlst(l):
    s = ''
    for i in l:
        s+= str(i) +'\n'
    return s

def flatten(l):
    return [item for sublist in l for item in sublist]


path_to_inputs = "./all_inputs"

###########################################
# Change this variable if you want
# your outputs to be put in a 
# different folder
###########################################
path_to_outputs = "./outputs"

def parse_input(folder_name):
    '''
        Parses an input and returns the corresponding graph and parameters

        Inputs:
            folder_name - a string representing the path to the input folder

        Outputs:
            (graph, num_buses, size_bus, constraints)
            graph - the graph as a NetworkX object
            num_buses - an integer representing the number of buses you can allocate to
            size_buses - an integer representing the number of students that can fit on a bus
            constraints - a list where each element is a list vertices which represents a single rowdy group
    '''
    graph = nx.read_gml(folder_name + "/graph.gml")
    parameters = open(folder_name + "/parameters.txt")
    num_buses = int(parameters.readline())
    size_bus = int(parameters.readline())
    constraints = []
    
    for line in parameters:
        line = line[1: -2]
        curr_constraint = [num.replace("'", "") for num in line.split(", ")]
        constraints.append(curr_constraint)

    return graph, num_buses, size_bus, constraints

def main():

    size_categories = ["small"]
    if not os.path.isdir(path_to_outputs):
        os.mkdir(path_to_outputs)

    print('=========reading data=======')
    if os.path.exists('./sml.pkl'):
        cache = open('./sml.pkl', 'rb')
        work = pickle.load(cache)
        cache.close()
    else:
        print("error, pickle not found")
        return 
    
    work = work[:311]
    work.reverse()
    data = []
    for i in range(311):
        a, b, c, output_category_path, input_name = work.pop()
        output_file = output_category_path + "/" + input_name + ".out"
        output = open(output_file)
        assignments = []
        for line in output:
            line = line[1: -2]
            curr_assignment = [node.replace("'","") for node in line.split(", ")]
            assignments.append(curr_assignment)
        # doing = [36]
        # # 
        # doing = [str(j) for j in doing]
        # if input_name in doing:
        data.append((a, b, c, output_category_path, input_name, assignments))

    print('============done reading')

    # work = itertools.permutations(work)
    start_time = time.time()
    p = Pool()
    towrite = p.map(threadwork, data)
    elapsed_time = time.time() - start_time

    print('saving result ====================')

    avg = 0.0

    # newws = []
    for f, sol, score in towrite:
        avg += score
        # newws.append(bestw)
        print(f, score)
        # output_file = open(f, "w")
        # output_file.write(sol)
        # output_file.close()
    # print(newws)
    print(elapsed_time, 's for computing')
    print('avg score', avg/722)
        
            
def threadwork(data):

    pack, _, category_path, output_category_path, input_name, result = data
    print('doing', category_path, input_name)
    filename = output_category_path + "/" + input_name + ".out"

    graph, num_buses, size_bus, constraints = pack
    
    optimal_result = result

    oriscore = score_output(graph, num_buses, size_bus, constraints, result)[0]
    max_score = oriscore

    direction = 5
    trynum = 16000
    # begin = time.time()
    if len(result) == 1:
        return filename, formatlst(result), 0
    else:
        for j in range(direction):
            result_copy = copy.deepcopy(result)

            for i in range(trynum):
                action = random.randint(0, 2)
                if action == 0:
                    random_two_swap(graph, num_buses, size_bus, constraints, result_copy)
                elif action == 1:
                    random_move(graph, num_buses, size_bus, constraints, result_copy)
                else:
                    random_swap(graph, num_buses, size_bus, constraints, result_copy)

                current_score = score_output(graph, num_buses, size_bus, constraints, result_copy)
                if (current_score[0] > max_score):
                    max_score = current_score[0]
                    optimal_result = result_copy
                    print(input_name, 'improved by',max_score-oriscore, 'at', int((j*trynum+i)*100/(direction*trynum)), '%')
                
                if (j*trynum+i) % 1000 ==0:
                    print(input_name, int((j*trynum+i)*100/(direction*trynum)), '%')
                    # if time.time()- begin> 30:
                    #     print(input_name, 'time_out')
                    #     return filename, optimal_result, max_score-oriscore
    output_file = open(filename, "w")
    output_file.write(formatlst(optimal_result))
    output_file.close()
    print('done', input_name)
    return filename, formatlst(optimal_result), max_score-oriscore
            
if __name__ == '__main__':
    main()

