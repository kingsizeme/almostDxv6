from __future__ import print_function
from threading import Semaphore, Lock, Thread
from collections import deque
import random
from time import sleep
import time
from timeit import Timer
import itertools
import sys
import logging


#L = int(input('Number of Leaders:'))
#F = int(input('Number of Followers:'))
L = int(sys.argv[1])
F = int(sys.argv[2])
#-----Global Variables-----------
#append right and pop left, FIFO
leaders_line = deque()
followers_line = deque()
dancing = deque([0,0]) #pair of all current dancing couples
leaders_on_floor = deque()
followers_on_floor = deque()

for i in range(0,L):
    leaders_line.append(i)
for i in range(0,F):
    followers_line.append(i)

floor_counter = 0

can_dance = False
can_enter = False
changing = False
bandwaiting = False
music_lockby_end = False
init = True

rng = random.Random()
rng.seed(100)
#--------------------------------

mutex = Semaphore(1)
Leaders_lock = Semaphore(0)
Follower_lock = Semaphore(0)
leader_wait = [Semaphore(0)]*L
follower_wait = [Semaphore(0)]*F

#------Bandleaders---------------

def startmusic(music):
    global can_enter
    global can_dance
    global leader_wait
    global follower_wait
    can_enter = True
    can_dance = True
    print ("** Band leader started playing ",music," **")
        #while there are players locked, release them
        #don't need to go through this hussle for the first time
        #need release for later
    if (init == False):
            #not first time enter, means there are players whose locked
            #by can_enter condition, need to release them before starting new round
        for i in range(0,L):
            leader_wait[i] = Semaphore(0)
        for i in range(0,F):
            follower_wait[i] = Semaphore(0)    

def end_music(music):
    global can_enter
    print ("** Band leader stopped playing ",music," **")

def band_leader():
    global can_enter
    global init
    global can_dance
    for music in itertools.cycle(['waltz', 'tango', 'foxtrot']):
        mutex.acquire()
        startmusic(music)
        start = time.time()
        mutex.release()
        while (time.time()-start) <= 5:
            if len(followers_on_floor) != 0 and len(leaders_on_floor) != 0:
                mutex.acquire()
                if(len(followers_on_floor) != 0):
                    can_dance = True
                    lid = leaders_on_floor.popleft()
                    leader_wait[lid].release()
                mutex.release()
        #mutex.acquire()
        can_enter = False
        can_dance = False
        #print ("stop")
        #mutex.release()
        while len(followers_line) != F or len(leaders_line) != L: #wait for everyone; also mark that no one can enter during this time
            if (len(leaders_on_floor) == 0 and len(followers_on_floor) != 0):
                if(can_enter == False):
                    mutex.acquire()
                    can_dance = False
                    fid = followers_on_floor.popleft()
                    follower_wait[fid].release()
                    mutex.release()
                    
            if (len(leaders_on_floor) != 0 and len(followers_on_floor) == 0):
                if(can_enter == False):
                    can_dance = False
                    if(len(leaders_on_floor)!=0):
                        mutex.acquire()
                        lid = leaders_on_floor.popleft()
                        leader_wait[lid].release()
                        mutex.release()
            pass
            #It's guarranteed that at this point, there is no one on the field.
        end_music(music)
        init = False #set init to false after 1st time
#--------------------------------
                
#------players-------------------
def leader():
    global can_dance
    global can_enter
    while True:
        if(can_enter == True):
            mutex.acquire()
            lid = leaders_line.popleft()
            #print ("Leader ",lid," leftline")
            print ("Leader ",lid," entering floor")
            leaders_on_floor.append(lid)
            mutex.release()
            
            leader_wait[lid].acquire()
            
            if(can_dance == True):
                mutex.acquire()
                fid = followers_on_floor.popleft() #appears that append and popleft are thread safe. might not need this sema for protection...
                print("Leader ",lid," and Follower ",fid," are dancing.") 
                follower_wait[fid].release()
                mutex.release()
                
                    # if not returned due to poor luck, then dance
                sleep(rng.random())
                    #-------
            mutex.acquire()
            print ("Leader ",lid," getting back in line.")
            leaders_line.append(lid)  
            mutex.release()

def follower():
    global can_enter
    global followers_on_floor
    global mutex
    global rng    
    while True:
        if (can_enter == True):
            mutex.acquire()
            fid = followers_line.popleft()
            #print ("Follower ",fid," leftline")
            print ("Follower ",fid," entering floor")
            followers_on_floor.append(fid)
            #print ("Follower ",fid," entered floor")
            mutex.release()
            
            follower_wait[fid].acquire()
      
            if (can_dance == True):# if not returned due to poor luck, then dance
                sleep(rng.random())
                #-------
            mutex.acquire()
            print ("Follower ",fid," getting back in line.") 
            followers_line.append(fid)  
            mutex.release()

#--------------------------------

if __name__ == '__main__':
    #everyone enters the ballroom
    #init all leaders and followers
    #no one can dance unless music starts
    #Like a formal dance
    #where music will not start until everyone has entered the ballroom
    init_band = Thread(target = band_leader)
    init_band.start()
    
    for i in range(0,L):
        lead = Thread(target=leader)
        lead.start()    
    for i in range(0,F):
        follow = Thread(target=follower)
        follow.start() 
    
    init_band.join()
    lead.join()
    follow.join()
    #start first music for everyone to dance