from threading import Thread
from threading import Semaphore
from time import sleep

s1 = input('SemaphoreA:')

aArrived = Semaphore(s1)
bArrived = Semaphore(0)

def aBody():
    aArrived.release()
    print('a at rendezvous\n')
    bArrived.acquire()
    print('a past rendezvous\n')

def bBody():
    bArrived.release()
    print('b at rendezvous\n')
    aArrived.acquire()
    print('b past rendezvous\n')

tA = Thread(target=aBody)
tA.start()
sleep(1) # force thread A to block
tB = Thread(target=bBody)
tB.start()

#stash = input('Initial Stash Size:')
#N = input('Number of disc per bucket:')
#frolfers = input('Number of frolfers:')

def frolfer():
    while True:
        stash -= N

def cart():
    while True:
        stash += N