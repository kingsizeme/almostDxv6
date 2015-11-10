from __future__ import print_function
from threading import Semaphore, Lock, Thread
from collections import deque
import random
from time import sleep
from timeit import Timer
import itertools
import sys
import logging

L = int(input('Number of Leaders:'))
F = int(input('Number of Followers:'))
#-----Global Variables-----------
#append right and pop left, FIFO
leaders_line = deque()
followers_line = deque()
dancing = deque([0,0]) #pair of all current dancing couples
leaders_on_floor = deque()
followers_on_floor = deque()

for i in range(L):
    leaders_line.append(i)
for i in range(F):
    followers_line.append(i)

floor_counter = 0

can_dance = False
can_enter = False
bandwaiting = False
music_lockby_end = False
init = True

rng = random.Random()
rng.seed(100)
#--------------------------------

#-----Semaphores-----------------
music_on = Semaphore(0)
#can_change = Semaphore(0)
#follower_ready = Semaphore(0)
#leader_enter = Semaphore(0)
#follower_wait = Semaphore(0)
#pairing = Semaphore(1)

#only one couple can pair at any given time
#once some guy is pairing, the sema turns 0 and subsequent guys have to wait
leader_line_pair = Semaphore(1)
follower_line_pair = Semaphore(1)

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
    can_enter = True
    print ("** Band leader started playing ",music," **")
    #while there are players locked, release them
    #don't need to go through this hussle for the first time
    #need release for later
    if (init == False):
        #not first time enter, means there are players whose locked
        #by can_enter condition, need to release them before starting new round
        for i in range(0,L):
            leader_wait.release()
            leader_poor_check[i] = 0
        for i in range(0,F):
            follower_wait.release()
            follower_poor_check[i] = 0
    #music_on.release()
    sleep(5)

def end_music(music):
    global can_enter
    print ("** Band leader stopped playing ",music," **")
    #can only be released by next start_music
    
def band_leader():
    global can_enter
    for music in itertools.cycle(['waltz', 'tango', 'foxtrot']):
        start_music(music)
        #end_music cannot be evoked unless everyone is back in line
        init = False #set init to false after 1st time
        print ("now stop")
        can_enter = False
        while floor_counter != 0: #wait for everyone; also mark that no one can enter during this time
            if (len(leaders_on_floor)==0 and len(followers_on_floor)!=0):
                #means leaders are all gone, only poor followers left behind
                #they need to be popped & go back in line
                fid = followers_on_floor.popleft()
                #mark this poor guy is going back line because there is no one to dance with
                follower_poor_check[fid] += 1
                follower_wait[fid].release()
            if (len(leaders_on_floor)!=0 and len(followers_on_floor)==0):
                #means followers are all gone, only leaders are left behind
                #they need to be popped & go back in line
                lid = leaders_on_floor.popleft()
                leader_poor_check[fid] += 1
                leader_wait[lid].release()            
            pass
        #It's guarranteed that at this point, there is no one on the field.
        end_music(music)
#--------------------------------
                
#------players-------------------
def leader_enter_floor():
    global leaders_line
    global floor_counter
    global followers_on_floor
    global followers_line
    global follower_wait
    id = leaders_line.popleft()
    print ("Leader ",id," entering floor")
    leaders_on_floor.append(id)
    floor_counter += 1
    #waits if no one on field
    while len(followers_on_floor)==0: #will not cause deadlock, as followers will constantly bump in;
        pass
    #if found someone
    follower_line_pair.acquire()
    fid = followers_on_floor.popleft() #appears that append and popleft are thread safe. might not need this sema for protection...
    follower_line_pair.release()
    follower_wait[fid].release()
    #print("Leader ",id," and Follower ",fid," are dancing.")   
    return (id,fid)

def leader_line_up(id):
    global can_enter
    global floor_counter
    global leader_wait  
    print ("Leader ",id," getting back in line.")
    leaders_on_floor.remove(id)
    leaders_line.append(id)
    floor_counter -= 1

def follower_enter_floor():
    global followers_line
    global floor_counter
    global follower_wait
    fid = followers_line.popleft()
    print ("Follower ",fid," entering floor")
    followers_on_floor.append(fid) #enters and waits for leader
    floor_counter += 1
    follower_wait[fid].acquire()
    return fid

def follower_line_up(fid):
    global floor_counter
    global followers_line
    global can_enter
    global follower_wait
    print ("Follower ",fid," getting back in line.")
    #followers_on_floor.remove(id)
    followers_line.append(fid)
    floor_counter -= 1
    #if cannot enter, then leader should stay in line

def dance():
    global rng
    sleep(rng.random())

#the enter should work in the following way:
#if leader enters:
#    if no follower on field, then wait
#    if found one, then popfollower and release that particular follower
#for followers-----
#if follower enters:
#    jump on the floor
#    wait for a leader to release
#
#eg. if leader releases follower one, then both can proceed to dance 
#which is basically sleep for random sec (0-1)
#**logic should work...
def leader():
    while True:
        #leaders can enter, but they cannot dance on their own, have to wait for return from enter floor
        #before 
        if (len(leaders_line)!=0): #make sure there are people who are in line before calling enter, same below
            mytup = leader_enter_floor()
            #dance--
            print("Leader ",mytup[0]," and Follower ",mytup[1]," are dancing.") 
            if (leader_poor_check[mytup[0]] != 1):# if not returned due to poor luck, then dance
                dance()
            #-------
            leader_line_up(mytup[0])
            #if cannot enter, then leader should stay in line
            if(can_enter == False):
                leader_wait[mytup[0]].acquire()            

def follower():
    while True:
        if (len(followers_line)!=0):
            fid = follower_enter_floor()
            #dance--
            #only leader got to say who they are dancing with
            if (follower_poor_check[fid] != 1):# if not returned due to poor luck, then dance
                dance()
            #-------
            follower_line_up(fid)
            if(can_enter == False):
                follower_wait[fid].acquire()            

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