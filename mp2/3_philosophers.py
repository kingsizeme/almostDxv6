from __future__ import print_function
from threading import Semaphore, Lock, Thread
from time import sleep
from random import random

NUM_PHILOSOPHERS = 5

# possible philosopher states
( THINKING, EATING ) = (0, 1)

def left_fork(id):  return id

def right_fork(id): return (id + 1) % NUM_PHILOSOPHERS

def philosophize(id):
    state = THINKING
    while True:
        sleep(random())
        if state is THINKING:
            print('Philosopher', id, 'is thinking')
            forks[left_fork(id)].acquire()
            forks[right_fork(id)].acquire()
            state = EATING
        else:
            print('Philosopher', id, 'is eating')
            forks[left_fork(id)].release()
            forks[right_fork(id)].release()
            state = THINKING

if __name__ == '__main__':
    forks = [Semaphore(1) for _ in range(NUM_PHILOSOPHERS)]
    for i in range(NUM_PHILOSOPHERS):
        phil = Thread(target=philosophize, args=[i])
        phil.start()
    phil.join()
    