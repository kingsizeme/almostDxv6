from __future__ import print_function
from threading import Semaphore, Lock, Thread
from collections import deque
import random
from time import sleep
from timeit import Timer
import itertools
import sys
import logging


#P = int(input('Total of Philosophers:'))
#M = int(input('Max Meals:'))
#tested works in cmdline
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

#-The "footman" solution---------
#counts all Ps time
def footman_solution(pid):
    global counter_foot
    global M
    global done_phils_foot
    while done_phils_foot != P:
        #if there are philosophers still need to eat, then continue
        if (counter_foot[pid] != M):
            get_forks(pid)
            counter_foot[pid] += 1
            if(counter_foot[pid] == M):
                done_phils_foot += 1
            put_forks(pid)
        else:
            pass
    
def get_forks(i):
    footman.acquire()
    fork_foot[right(i)].acquire()
    fork_foot[left(i)].acquire()
    
def put_forks(i):
    fork_foot[right(i)].release()
    fork_foot[left(i)].release()
    footman.release()

def totime_footman():
    global P
    global done_phils_foot
    ts = [Thread(target=footman_solution,args=[i]) for i in range(P)]
    for t in ts: t.start()
    for t in ts: t.join()
    print ("finished phils: ", done_phils_foot)

timer_1 = Timer(totime_footman)
print ("1. Footman solution, time elapsed: ",timer_1.timeit(1))   
#--------------------------------

#The "left-handed philosopher" solution
def left_handed_solution(pid):
    global counter_lefty
    global M
    global done_phils_lefty
    while done_phils_lefty != P:
        if(counter_lefty[pid] != M):
            if pid == P - 1: #one and only one of the philos is lefty
                get_lefti_forks(pid)
            else:
                get_righty_forks(pid)
            counter_lefty[pid] += 1
            if (counter_lefty[pid] == M):
                done_phils_lefty += 1   
            put_forks(pid)
        else:
            pass
            
def get_righty_forks(i):
    fork_lefty[right(i)].acquire()
    fork_lefty[left(i)].acquire()

def get_lefti_forks(i):
    fork_lefty[left(i)].acquire()
    fork_lefty[right(i)].acquire()

def put_forks(i): #no difference between lefty and righty...
    fork_lefty[right(i)].release()
    fork_lefty[left(i)].release()
    
def totime_left_handed():
    global P
    global done_phils_lefty
    ts = [Thread(target=left_handed_solution,args=[i]) for i in range(P)]
    for t in ts: t.start()
    for t in ts: t.join()
    print ("lefty finished phils: ", done_phils_lefty)

timer_2 = Timer(totime_left_handed)
print ("2. Left_handed solution, time elapsed: ",timer_2.timeit(1))
#--------------------------------

#--The Tanenbaum solution--------
def tanenbaum_solution(pid):
    global counter_Tanenbaums
    global M
    global done_phils_Tanenbaums
    global state
    while done_phils_Tanenbaums != P:
        if (counter_Tanenbaums[pid] == M):
            pass
        else:
            get_Tane_fork(pid)
            if (state[pid] == "eating"):
                if (counter_Tanenbaums[pid] == M):
                    done_phils_Tanenbaums += 1  
                put_Tane_fork(pid)

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
        counter_Tanenbaums[i] += 1
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

while True:
    sleep(1)