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


# def overlap(a, b):
#     for i in a:
#         if i in b:
#             return True
#     return False
def partition(G, nodes):
    return nx.subgraph(G, nodes), _

def checkrowdy(b, new, constraints):
    newb = b[:]
    newb.append(new)
    newb = set(newb)
    rowdies =[]
    for i in constraints:
        if i.issubset(newb):
            rowdies.extend(i)
    rowdies = set(rowdies)
    return len(rowdies)>0
    
def gain(b, new, constraints, G):
    newb = b[:]
    newb.append(new)
    newb = set(newb)
    rowdies =[]
    for i in constraints:
        if i.issubset(newb):
            rowdies.extend(i)
    rowdies = set(rowdies)
    V = set(G.nodes)
    if len(rowdies)>0:
        xGo, _ = partition(G, list(newb))
        xGn, _ = partition(G, list(newb - rowdies))
        oldedges = len(xGo.edges())
        newedges = len(xGn.edges())
        del xGo
        del xGn
        _, t = partition(G, b[:])
        y = t.degree[new]
        loss = newedges - oldedges
        return (loss - y , loss)
    else:
        return None
        

def solve(G, k, c, constraints, w):
    #TODO: Write this method as you like. We'd recommend changing the arguments here as well
    
    # conflicts = nx.Graph()
    # for i in constraints:
    #     temp = []
    #     for student in i:
    #         for another_student in i[i.index(student) + 1:]:
    #             temp.append((student, another_student))
    #         conflicts.add_edges_from(temp)
            
    origraph = copy.deepcopy(G)
    constraints = [set(i) for i in constraints]
    n = len(G)
    buses = []
    assigned = 0

    if k*c<n:
        raise Exception('Passanger exceeds capacity')
    else:
        #search for how many garbage bus
        for i in range(0, k+1):
            if math.ceil((n - i)/c) + i == k:
                g = i
                break
        
        pq = MaxPQ()
        for i in G.nodes():
            pq.insert(i, (-G.degree[i]*w, 0))
            
        for i in range(k - g):
            buses.append([])
        for i in range(g):
            b = []
            rm = pq.pop().obj
            b.append(rm)
            G.remove_node(rm)
            # if rm in conflicts.nodes:
            #     conflicts.remove_node(rm)
            buses.append(b)
        for nbus in range(k):
            b = buses[nbus]
            if nbus>= k-g and nbus*c>assigned and pq.length()>0:
                for i in range(nbus):
                    if len(buses[i])<c and not checkrowdy(buses[i], b[0], constraints):
                        buses[i].append(b.pop())
                        break
            
            while (len(b)<c) and pq.length()>0:
                temp = pq.pop()
                new = temp.obj
                #===========
                while checkrowdy(b, new, constraints) and pq.length()>0:
                    temp = pq.pop()
                    new = temp.obj
                #===========
                b.append(new)
                assigned+=1
                for j in G.neighbors(new):
                    if j not in b:
                        pq.change(j, (1+w, 1))
                # if new in conflicts.nodes:
                #     for j in conflicts.neighbors(new):
                #         if j not in b:
                #             r = gain(b, j, constraints, G)
                #             if r != None:
                #                 pq.insert(j, (r[0]*w, r[1]))
                            
            G.remove_nodes_from(b)
            # for i in b:
            #     if i in conflicts.nodes:
            #         conflicts.remove_node(i)
                    
            pq = MaxPQ()
            for i in G.nodes():
                pq.insert(i, (-G.degree[i]*w, 0))

        rest = list(G.nodes)
        newrest = []
        if len(constraints)<=1000 and len(rest)<=50:
            if rest:
                for r in rest:
                    m = -n
                    recordi = -1
                    for i in range(0, k):
                        b = buses[i]
                        if len(b)==c and not checkrowdy(b, r, constraints):
                            for cand in b:
                                before = len(origraph.subgraph(b).edges())
                                hypo = b[:]
                                hypo.remove(cand)
                                hypo.append(r)
                                after = len(origraph.subgraph(hypo).edges())
                                dif = after - before
                                if dif>m:
                                    m = dif
                                    record = cand
                                    recordi = i
                    if recordi>=0:          
                        buses[recordi].remove(record)
                        buses[recordi].append(r)
                        rest.remove(r)
                        newrest.append(record)
        rest.extend(newrest)
        

        
        for i in range(1, k+1):
            if len(rest)==0:
                break
            temp = min(c - len(buses[-i]), len(rest))
            buses[-i].extend(rest[:temp])
            rest = rest[temp:]
        return buses


def solvewrapper(G, k, c, constraints, rw, graphcpy):
    up = (rw+1)*10
    low = (rw-1)*10
    bestscore = -1.0
    for i in range(low, up, 2):
        G = copy.deepcopy(graphcpy)
        w = i/100
        plan = solve(G, k, c, constraints, w)
        del G
        score = score_output(graphcpy, k, c, constraints, plan)[0]
        if score>bestscore:
            bestscore = score
            bestplan = plan
            bestw = w
    return bestplan, bestw

def main():
    '''
        Main method which iterates over all inputs and calls `solve` on each.
        The student should modify `solve` to return their solution and modify
        the portion which writes it to a file to make sure their output is
        formatted correctly.
    '''
    # ws = [1, 2, 2, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ws = [0.02, 0.18, 0.14, 0.52, 0.14, 0.1, 0.1, 0.1, 0.24, 0.1, 0.1, 0.16, 0.26, 0.1, 0.1, 0.1, 0.1, 0.22, 0.1, 0.1, 0.22, 0.18, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.22, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1, 0.26, 0.26, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.24, 0.1, 0.1, 0.1, 0.1, 0.1, 0.22, 0.26, 0.16, 0.1, 0.14, 0.1, 0.1, 0.12, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1, -0.1, 0.0, 0.0, 0.0, -0.1, 0.02, -0.1, 0.02, 0.0, 0.0, -0.1, 0.02, 0.02, 0.0, 0.02, 0.02, -0.1, 0.0, 0.0, 0.0, 0.02, 0.02, -0.1, -0.1, 0.02, -0.1, 0.02, 0.02, 0.02, -0.1, 0.0, 0.0, 0.0, -0.1, 0.0, 0.02, 0.02, -0.1, -0.1, -0.1, 0.02, 0.0, 0.02, 0.06, 0.0, -0.1, -0.1, 0.0, 0.02, -0.1, 0.02, 0.0, 0.0, 0.02, 0.0, 0.0, -0.1, 0.02, 0.02, 0.0, -0.1, 0.02, 0.0, 0.02, 0.02, 0.0, 0.0, 0.0, 0.02, -0.1, -0.1, 0.02, -0.1, 0.0, 0.0, 0.02, 0.0, -0.1, -0.1, 0.0, 0.02, 0.02, 0.02, -0.1, 0.02, 0.0, -0.1, -0.1, 0.02, -0.1, 0.0, 0.06, 0.02, 0.0, 0.02, 0.02, 0.0, 0.0, 0.02, 0.0, -0.1, 0.02, 0.02, -0.1, 0.02, 0.2, -0.1, 0.22, 0.2, 0.2, 0.34, 0.2, 0.26, 0.26, 0.34, 0.2, 0.1, 0.16, 0.1, 0.22, 0.1, 0.1, 0.1, 0.1, 0.1, 0.22, 0.1, 0.26, 0.2, 0.2, 0.26, 0.22, 0.34, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.22, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.12, 0.1, 0.18, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 0.26, 0.1, 0.1, 0.1, 0.1, 0.26, 0.12, 0.1, 0.26, 0.1, 0.1, 0.1, 0.22, 0.1, 0.26, 0.18, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.14, 0.1, 0.1, 0.1, 0.14, 0.1, 0.1, 0.1, 0.1, 0.18, 0.1, 0.1, 0.1, 0.12, 0.1, 0.1, 0.26, 0.1, 0.16, 0.18, 0.1, 0.1, 0.26, 0.1, 0.1, 0.2, 0.1, 0.22, 0.1, 0.26, 0.1, 0.26, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.22, 0.1, 0.1, 0.22, 0.14, 0.2, 0.2, 0.1, 0.22, 0.1, 0.12, 0.0, 0.0, 0.02, 0.08, 0.0, 0.1, 0.02, 0.1, 0.0, 0.14, 0.0, 0.0, 0.14, 0.16, 0.02, 0.0, 0.02, 0.0, 0.0, 0.02, 0.02, 0.12, 0.02, 0.02, 0.14, 0.02, 0.04, 0.02, 0.02, 0.02, 0.0, 0.02, 0.1, 0.02, 0.02, 0.0, 0.04, 0.0, 0.0, 0.16, 0.18, 0.0, 0.02, 0.02, 0.02, 0.0, 0.18, 0.0, 0.02, 0.0, 0.0, 0.0, 0.12, 0.06, 0.0, 0.0, 0.02, 0.02, 0.1, 0.0, 0.08, 0.02, 0.18, 0.06, 0.1, 0.02, 0.0, 0.04, 0.0, 0.0, 0.02, 0.0, 0.02, 0.0, 0.1, 0.04, 0.06, 0.18, 0.02, 0.0, 0.0, 0.12, 0.08, 0.16, 0.02, 0.0, 0.0, 0.08, 0.14, 0.04, 0.08, 0.08, 0.02, 0.0, 0.0, 0.0, 0.06, 0.02, 0.1, 0.0, 0.12, 0.0, 0.04, 0.02, 0.0, 0.02, 0.02, 0.08, 0.0, 0.0, 0.0, 0.18, 0.16, 0.02, 0.0, 0.18, 0.02, 0.0, 0.02, 0.04, 0.0, 0.0, 0.0, 0.0, 0.08, 0.0, 0.02, 0.02, 0.14, 0.02, 0.06, 0.12, 0.0, 0.02, 0.12, 0.0, 0.0, 0.02, 0.04, 0.02, 0.06, 0.0, 0.0, 0.02, 0.02, 0.02, 0.0, 0.04, 0.18, 0.0, 0.02, 0.16, 0.14, 0.1, 0.0, 0.18, 0.14, 0.08, 0.06, 0.02, 0.1, 0.02, 0.02, 0.0, 0.18, 0.0, 0.02, 0.12, 0.02, 0.02, 0.12, 0.0, 0.1, 0.06, 0.08, 0.18, 0.0, 0.02, 0.0, 0.1, 0.0, 0.02, 0.1, 0.08, 0.02, 0.02, 0.18, 0.02, 0.08, 0.02, 0.04, 0.18, 0.14, 0.18, 0.02, 0.06, 0.0, 0.1, 0.02, 0.16, 0.0, 0.0, 0.0, 0.0, 0.04, 0.06, 0.16, 0.04, 0.18, 0.0, 0.0, 0.08, 0.0, 0.1, 0.02, 0.02, 0.0, 0.02, 0.0, 0.02, 0.02, 0.02, 0.02, 0.0, 0.1, 0.02, 0.0, 0.12, 0.18, 0.02, 0.0, 0.02, 0.02, 0.02, 0.02, 0.08, 0.02, 0.16, 0.0, 0.14, 0.02, 0.0, 0.02, 0.02, 0.16, 0.02, 0.08, 0.18, 0.0, 0.0, 0.0, 0.14, 0.16, 0.02, 0.06, 0.0, 0.0, 0.02, 0.1, 0.14, 0.0, 0.18, 0.0, 0.02, 0.02, 0.16, 0.0, 0.0, 0.0, 0.0, 0.06, 0.06, 0.06, 0.02, 0.02, 0.04, 0.02, 0.02, 0.02, 0.02, 0.1, 0.16, 0.0, 0.14, 0.0, 0.06, 0.16, 0.02, 0.12, 0.02, 0.16, 0.02, 0.0, 0.06, 0.16, 0.02, 0.02, 0.06, 0.14, 0.0, 0.0, 0.0, 0.02, 0.0, 0.02, 0.06, 0.0, 0.12, 0.02, 0.08, 0.02, 0.0, 0.0, 0.02, 0.14, 0.12, 0.02, 0.0, 0.02, 0.02, 0.0, 0.0, 0.0, 0.02, 0.0, 0.02, 0.02, 0.02, 0.02, 0.04, 0.06, 0.02, 0.12, 0.18, 0.02, 0.12, 0.0, 0.0, 0.08, 0.18, 0.02, 0.02, 0.02, 0.04, 0.18, 0.02, 0.02, 0.02, 0.0, 0.0, 0.02, 0.08, 0.06, 0.02, 0.04, 0.04, 0.02, 0.02, 0.18, 0.12, 0.0, 0.0, 0.02, 0.02, 0.02, 0.0, 0.0, 0.04, 0.02, 0.04, 0.0, 0.02, 0.0, 0.02, 0.0, 0.04, 0.06, 0.06, 0.1, 0.02, 0.0, 0.14, 0.08, 0.02, 0.18, 0.02, 0.06, 0.0, 0.04, 0.0, 0.08, 0.0, 0.02, 0.0, 0.0, 0.02, 0.02, 0.0, 0.14, 0.02, 0.0, 0.02, 0.06]
    size_categories = ["small", "medium", "large"]
    if not os.path.isdir(path_to_outputs):
        os.mkdir(path_to_outputs)

    print('=========reading data=======')
    if os.path.exists('./sml.pkl'):
        cache = open('./sml.pkl', 'rb')
        work = pickle.load(cache)
        cache.close()


    else:
        work=[]
        count = 0
        for size in size_categories:
            category_path = path_to_inputs + "/" + size
            output_category_path = path_to_outputs + "/" + size
            category_dir = os.fsencode(category_path)
            
            if not os.path.isdir(output_category_path):
                os.mkdir(output_category_path)

            for input_folder in os.listdir(category_dir):
                input_name = os.fsdecode(input_folder)
                print('reading', category_path, input_name)
                pack = parse_input(category_path + "/" + input_name)
                work.extend([(pack, ws[count], category_path, output_category_path, input_name)])
                count += 1

        cache = open('sml.pkl', 'wb')
        pickle.dump(work, cache)
        cache.close()
        print('saving done')

    print('============done reading')

    # work = itertools.permutations(work)
    start_time = time.time()
    p = Pool()
    towrite = p.map(threadwork, work)
    elapsed_time = time.time() - start_time

    print('saving result ====================')

    avg = 0.0

    # newws = []
    for f, sol, score in towrite:
        avg += score
        # newws.append(bestw)
        print(f, score)
        output_file = open(f, "w")
        output_file.write(sol)
        output_file.close()
    # print(newws)
    print(elapsed_time, 's for computing')
    print('avg score', avg/len(towrite))
        
            
def threadwork(data):
    pack, w, category_path, output_category_path, input_name = data
    # w/=10
    print('doing', category_path, input_name)
    graph, num_buses, size_bus, constraints = pack
    graphcpy = copy.deepcopy(graph)
#             draw_graph(graph, graph_layout='spring')
#             print(num_buses, size_bus)

    # raw, bestw = solvewrapper(graph, num_buses, size_bus, constraints, w, graphcpy)
    raw = solve(graph, num_buses, size_bus, constraints, w)
    solution = formatlst(raw)
    filename = output_category_path + "/" + input_name + ".out"
    score = score_output(graphcpy, num_buses, size_bus, constraints, raw)[0]

    return filename, solution, score

    #TODO: modify this to write your solution to your 
    #      file properly as it might not be correct to 
    #      just write the variable solution to a file
#             print(solution)
            
if __name__ == '__main__':
    main()

