from threading import Thread, Semaphore
from time import sleep

aArrived = Semaphore(0)
bArrived = Semaphore(0)

def aBody():
    aArrived.release()
    print('a at rendezvous')
    bArrived.acquire()
    print('a past rendezvous')

def bBody():
    bArrived.release()
    print('b at rendezvous')
    aArrived.acquire()
    print('b past rendezvous')

tA = Thread(target=aBody)
tA.start()
sleep(1) # force thread A to block
tB = Thread(target=bBody)
tB.start()