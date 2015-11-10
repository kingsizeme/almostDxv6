from __future__ import print_function
from threading import Semaphore, Lock, Thread
from collections import deque
import random
from time import sleep
import sys
import logging

#-----Semaphores-----------------
can_throw = Semaphore(0)
cart_go = Semaphore(0)
in_call = Semaphore(1)
#--------------------------------

#-----Global Variables-----------
stash = int(input('Initial Stash Size:'))
#print 'stash: %d' % stash
N = int(input('Number of disc per bucket:'))
frolfers = int(input('Number of frolfers:'))
disc_on_field = 0
started_cnt = 0;
stopped_cnt = 0;
flag = False;
mylist = [0]*frolfers
myfrolfercall = [0]*frolfers
rng = random.Random()
rng.seed(100)
#--------------------------------


def frolfer(seq):
    global stash
    global N
    global disc_on_field
    global flag
    global stopped_cnt
    global mylist
    global myfrolfercall
    global rng
    #sleep(1)
    while True:
        #sleep(1)
        N_got = 0
        in_call.acquire()
        if(myfrolfercall[seq]==0):
            print ("Frolfer ",seq, " calling for bucket")
            myfrolfercall[seq] = 1
            if(stash < N):
                if(flag!=True):
                    #print ("trying to get cart")
                    flag = True #marks that cart is in
                    stopped_cnt += 1
                    cart_go.release()
                    can_throw.acquire()
            if(stash >= N):
                stash -= N
                N_got = N
                mylist[seq] = N
                myfrolfercall[seq] = 0
                print ("Frolfer ",seq," got ",N," discs; Stash = ",stash)
        #calling.release()
        in_call.release()
        sleep(rng.random())
        for i in range(0,N_got):

            if(flag): #if cart is in, stops immediately
                stopped_cnt += 1
                can_throw.acquire()             
            if(stopped_cnt != 0):
                stopped_cnt -= 1
                can_throw.release()
            if(flag!=True):
                print ("Frolfer ",seq," threw disc ",i)
                disc_on_field += 1;
                mylist[seq] = N-i-1               

        

def cart():
    global stash
    global disc_on_field
    global flag
    global stopped_cnt
    global total_disc
    global mylist
    while True:
        cart_go.acquire()#locks the cart in the beginning
        #can_throw.acquire()
        total_disc = stash + disc_on_field
        #for i in range(frolfers):
        #print ("Total Discs: ",total_disc + mylist[0]+mylist[1]+mylist[2])
        print ("################################################################################")
        print ("Stash = ",stash,"; Cart entering field")
        #cart_on_field.acquire()
        stash += disc_on_field
        print ("Cart done, gathered ",disc_on_field," discs; Stash = ",stash)
        print ("################################################################################")
        disc_on_field = 0
        flag = False
        stopped_cnt -= 1
        can_throw.release()

if __name__ == '__main__':
#init cart first
    global total_disc
    total_disc = stash
    frolfer_seq = 0
    cr = Thread(target = cart)
    cr.start()
    while frolfer_seq < frolfers:
        fr = Thread(target = frolfer, args =(frolfer_seq,))
        fr.start()
        frolfer_seq += 1
    #fr.join()

