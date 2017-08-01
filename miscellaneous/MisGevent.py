#! -*- coding: utf-8 -*-

import gevent
from gevent import select
import time

start = time.time()

def func1():
    print('func1  Starting Polling: %1.3f' %(time.time() - start))
    select.select([], [], [], 2)
    print('func1 Ended Polling: %1.3f' %(time.time() - start))

def func2():
    print('func2 Starting Polling: %1.3f' %(time.time() - start))
    select.select([], [], [], 2)
    print('func2 Ended Polling: %1.3f' %(time.time() - start))

def func3():
    print('func3 Now Sleep start....%1.3f' %(time.time() - start))
    gevent.sleep(5)
    print('func3 End ALL %s' %(time.time() - start))


gevent.joinall([gevent.spawn(func1), gevent.spawn(func2), gevent.spawn(func3)])




import gevent
from gevent.event import Event

'''
Illustrates the use of events
'''

evt = Event()

def setter():
    '''After 3 seconds, wake all threads waiting on the value of evt'''
    print('A: Hey wait for me, I have to do something at %1.1f' %(time.time() - start ))
    gevent.sleep(3)
    print("Ok, I'm done at %1.1f" %(time.time()  - start))
    evt.set()

def waiter():
    '''After 3 seconds the get call will unblock'''
    print("I'll wait for you at %1.1f" %(time.time() - start))
    evt.wait()  # blocking
    print("It's about time at %1.1f" %(time.time() - start))

def main():
    gevent.joinall([
        gevent.spawn(setter),
        gevent.spawn(waiter),
        gevent.spawn(waiter),
        gevent.spawn(waiter),
        gevent.spawn(waiter),
        gevent.spawn(waiter)
    ])

import gevent
from gevent import Timeout

seconds = 10

timeout = Timeout(seconds)
timeout.start()

def wait():
    gevent.sleep(3)
    print('KKKKKKKKKKK')

try:
    gevent.spawn(wait).join()
except Timeout:
    print('Could not complete')


import collections