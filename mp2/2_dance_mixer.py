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

#-----Semaphores-----------------
music_on = Semaphore(0)
#only one couple can pair at any given time
#once some guy is pairing, the sema turns 0 and subsequent guys have to wait
leader_line_lock = Semaphore(1)
follower_line_lock = Semaphore(1)
leader_returning = Semaphore(1)
follower_returning = Semaphore(1)
got_one = Semaphore(0)
leader_wait = [Semaphore(0)]*L
follower_wait = [Semaphore(0)]*F
leader_poor_check = [0]*L
follower_poor_check = [0]*F
#--------------------------------

#------Bandleaders---------------
def start_music(music):
    global can_enter
    global leader_wait
    global follower_wait
    global init
    global got_one
    can_enter = True
    print ("** Band leader started playing ",music," **")
    #while there are players locked, release them
    #don't need to go through this hussle for the first time
    #need release for later
    if (init == False):
        #not first time enter, means there are players whose locked
        #by can_enter condition, need to release them before starting new round
        for i in range(0,L):
            leader_wait[i] = Semaphore(0)
            leader_poor_check[i] = 0
        for i in range(0,F):
            follower_wait[i] = Semaphore(0)
            follower_poor_check[i] = 0
        got_one = Semaphore(0)
    #music_on.release()
    start_time = time.time()
    while (time.time() - start_time) <= 5:
        if (len(leaders_on_floor) != 0):
            got_one.acquire()
            popleader = leaders_on_floor.popleft()
            leader_poor_check[popleader] = 0          
            leader_wait[popleader].release()
    #sleep(5)
    
def end_music(music):
    global can_enter
    print ("** Band leader stopped playing ",music," **")
    #can only be released by next start_music
    
def band_leader():
    global can_enter
    global init
    for music in itertools.cycle(['waltz', 'tango', 'foxtrot']):
        start_music(music)
        #end_music cannot be evoked unless everyone is back in line
        can_enter = False
        #can_return
        #print ("now stop")
        while len(followers_line) != F or len(leaders_line) != L: #wait for everyone; also mark that no one can enter during this time
            if (len(leaders_on_floor) == 0 and len(followers_on_floor) != 0):
                if(can_enter == False):
                    #means leaders are all gone, only poor followers left behind
                    #they need to be popped & go back in line
                    fid = followers_on_floor.popleft()
                    #mark this poor guy is going back line because there is no one to dance with
                    follower_poor_check[fid] = 1
                    follower_wait[fid].release()
                    
            if (len(leaders_on_floor) != 0 and len(followers_on_floor) == 0):
                if(can_enter == False):
                    #means followers are all gone, only leaders are left behind
                    #they need to be popped & go back in line
                    lid = leaders_on_floor.popleft()
                    leader_poor_check[lid] = 1
                    leader_wait[lid].release()        
            pass
            #It's guarranteed that at this point, there is no one on the field.
        end_music(music)
        init = False #set init to false after 1st time
    
#--------------------------------
                
#------players-------------------
def leader():
    global can_enter
    while True:
        #leaders can enter, but they cannot dance on their own, have to wait for return from enter floor
        #before 
        if (len(leaders_line) != 0 and can_enter == True): #make sure there are people who are in line before calling enter, same below
            lid = leaders_line.popleft()
            #print ("Leader ",lid," leftline")
            print ("Leader ",lid," entering floor")
            leaders_on_floor.append(lid)
            #print ("Leader ",lid," entered floor")
            #block
            leader_wait[lid].acquire()
            #print ("Leader ",lid," released")
            #if found someone
            if (leader_poor_check[lid] != 1):
                follower_returning.acquire()
                fid = followers_on_floor.popleft() #appears that append and popleft are thread safe. might not need this sema for protection...
                print("Leader ",lid," and Follower ",fid," are dancing.") 
                follower_poor_check[fid] = 0                
                follower_returning.release()
                
                follower_wait[fid].release()
                
                # if not returned due to poor luck, then dance
                sleep(rng.random())
                #-------
                print ("Leader ",lid," getting back in line.")
                leaders_line.append(lid)
            #if cannot enter, then leader should stay in line   
            else:
                print ("Leader ",lid," getting back in line.")  
                leaders_line.append(lid)
                             
def follower():
    while True:
        if (len(followers_line) != 0 and can_enter == True):
            fid = followers_line.popleft()
            #print ("Follower ",fid," leftline")
            print ("Follower ",fid," entering floor")
            followers_on_floor.append(fid)
            #print ("Follower ",fid," entered floor")
            #block
            got_one.release()
            follower_wait[fid].acquire()
            #dance--
            #only leader got to say who they are dancing with
            if (follower_poor_check[fid] != 1):# if not returned due to poor luck, then dance
                sleep(rng.random())
                #-------
                print ("Follower ",fid," getting back in line.") 
                followers_line.append(fid)
            else:
                #going back without a dance
                print ("Follower ",fid," getting back in line.") 
                followers_line.append(fid)

#--------------------------------

if __name__ == '__main__':
    #everyone enters the ballroom
    #init all leaders and followers
    #no one can dance unless music starts
    #Like a formal dance
    #where music will not start until everyone has entered the ballroom
    init_band = Thread(target = band_leader)
    init_band.start()
    
    lead = Thread(target=leader)
    lead.start()    
    
    follow = Thread(target=follower)
    follow.start() 
    
    init_band.join()
    lead.join()
    follow.join()
    #start first music for everyone to dance