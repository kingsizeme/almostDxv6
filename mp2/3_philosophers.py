from __future__ import print_function
from threading import Semaphore, Lock, Thread
from collections import deque
import random
from time import sleep
from timeit import Timer
import itertools
import sys
import logging


#P = int(input('pid of Philosophers:'))
#M = int(input('pid of Max Meals:'))
P = int(sys.argv[1])
M = int(sys.argv[2])
print ("Running dining philosophers simulation: ",P," philosophers, ",M," meals each")

#-----Global Variables-----------
counter_foot = [0]*P #check for each philosopher
counter_lefty = [0]*P
counter_Tanenbaums = [0]*P
state = ['thinking']*P
done_phils_foot = 0
done_phils_lefty = 0
done_phils_Tanenbaums = 0
#if one has reached target meal, then he shall never pick forks up after put them down ...

rng = random.Random()
rng.seed(100)
#--------------------------------


#-----Semaphores-----------------

#-----Footman&left hand----------
footman = Semaphore(P - 1)
fork_foot = [Semaphore(1) for i in range(P)]
fork_lefty = [Semaphore(1) for i in range(P)]

#-------Tanenbaums---------------
mutex = Semaphore(1)
state = ['thinking'] * P
sem = [Semaphore(0) for i in range(P)]
#--------------------------------

#-general functions--------------
def left(i):
    return i

def right(i):
    global P
    return (i+1) % P
#--------------------------------



#--The Tanenbaum solution--------
def tanenbaum_solution(pid):
    global counter_Tanenbaums
    global M
    global done_phils_Tanenbaums
    global state
    while done_phils_Tanenbaums != P:
        if(counter_Tanenbaums[pid] != M):
            get_Tane_fork(pid)
            if state[pid] == "eating" :
                counter_Tanenbaums[pid] += 1
                if (counter_Tanenbaums[pid] == M):
                    done_phils_Tanenbaums += 1  
                put_Tane_fork(pid)
        else:
            pass

def get_Tane_fork(i):
    mutex.acquire()
    state[i] = "hungry"
    test(i) # check neighbors states
    mutex.release()
    sem[i].acquire() # wait on my own semaphore
    
def put_Tane_fork(i):
    mutex.acquire()
    state[i] = "thinking"
    test(right(i)) # signal neighbors if they can eat
    test(left(i))
    mutex.release() 

# Check state : check if the philosopher can eat
def test(i):
    global state
    if (state[i] == "hungry" and state[left(i)] != "eating" and state[right(i)] != "eating"):
        state[i] = "eating"
        sem[i].release()     # this signals me OR a neighbor
        
def totime_tanenbaum():
    global P
    ts = [Thread(target=tanenbaum_solution,args=[i]) for i in range(P)]
    for t in ts: t.start()
    for t in ts: t.join()
    print ("tanenbaum finished phils: ", done_phils_Tanenbaums)

timer_3 = Timer(totime_tanenbaum)
print("3. Tanenbaum's solution, time elapsed: ", timer_3.timeit(1))
#--------------------------------
    