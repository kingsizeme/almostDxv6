from __future__ import print_function
from threading import Semaphore, Lock, Thread
from collections import deque
from random import random, randint
from time import sleep
from timeit import Timer
import sys
import logging

L = int(input('Number of Leaders:'))
F = int(input('Number of Followers:'))

leaders = deque[]

def bandleader():
    for music in cycle(['waltz', 'tango', 'foxtrot']):
        start_music(music)
        end_music(music)   

def leader():
    while True:
        enter_floor()
        dance()
        line_up()    

def follower():
    while True:
        enter_floor()
        dance()
        line_up()    