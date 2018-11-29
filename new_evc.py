'''
    Written by Debojit Kaushik  (Timestamp)
'''
import os
import sys
import traceback
import json

from multiprocessing import Queue, Process, Lock
from threading import Thread
from random import randint
from time import sleep
from numpy.random import choice


def EVC(t_id, q, prime, max_size, p1, p2):
    try:
        def gcd(x, y):
            """This function implements the Euclidian algorithm
            to find G.C.D. of two numbers"""
            while(y):
                x, y = y, x % y
            return x

        def LCM(x, y):
            """This function takes two
            integers and returns the L.C.M."""
            lcm = (x*y)//gcd(x,y)
            return lcm

        def receive(q, t_id, prime, p1):
            try:
                clock = 1
                events = {
                    'int': 0,
                    'rcv': 0, 
                    'send': 0,
                    'bit_length': [],
                    'clock': []
                }
                
                while True:
                    event = q[t_id].get()
                    if int(clock).bit_length() > max_size*32 or event["type"] == 'STOP':
                        for item in q:
                            item.put({
                                "type": "STOP"
                            })
                        break

                    if event['type'] == "INT":
                        clock = clock * prime
                        events['clock'].append(clock)
                        events['bit_length'].append(int(clock).bit_length())
                        events['int'] += 1
                    elif event['type'] == "SEND":
                        events['send'] += 1
                        clock = clock * prime
                        events['bit_length'].append(int(clock).bit_length())
                        events['clock'].append(clock)
                        recv_id = randint(0, max_size-1)
                        while recv_id == t_id:
                            recv_id = randint(0, max_size-1)
                        assert recv_id != t_id
                        q[recv_id].put({
                            'type': "RECV", 
                            'clock': clock
                        })
                    elif event['type'] == "RECV":
                        events['rcv'] += 1
                        temp = LCM(int(event["clock"]), int(clock))
                        clock = temp * prime
                        events['bit_length'].append(int(clock).bit_length())
                        events['clock'].append(clock)
                # print(events)
                events['id'] = t_id
                with open('part1/part3/data_' + str(N) + '_' + str(p1) + '_' + str(t_id) +'.json', 'w+') as f:
                    f.write(json.dumps(events))
                
            except Exception:
                print(traceback.format_exc())
        
        def send(q, t_id, p1, p2):
            try:
                sleep(4)
                mode = 0
                while True:
                    sleep(0.05)
                    mode = choice([0,1], p=[p1, p2])
                    if mode == 0:
                        q[t_id].put({
                            'type': "INT"
                        })
                    else:
                        q[t_id].put({
                            'type': "SEND"
                        })
                    mode += 1
            except Exception:
                print(traceback.format_exc())

        th = Thread(target = send, args=(q, t_id, p1, p2))
        th.daemon = True
        th.start()
        receive(q, t_id, prime, p1)
    except Exception:
        print(traceback.format_exc())


if __name__ == '__main__':
    try:
        # N = int(sys.argv[1])
        for N in range(28, 31, 4):
            print("N", N)
            qu = [Queue() for _ in range(N)]
            primes = []
            num = 2
            while len(primes) < N:
                prime = True
                for i in range(2,num):
                    if (num%i==0):
                        prime = False
                if prime:
                    primes.append(num)
                num += 1
            # p = [0, 0.25, 0.5, 0.75, 1]
            i = 1
            for _ in range(N):
                p = Process(target = EVC, args = ((_, qu, primes[_], N, i, 1-i)))
                p.start()
            sleep(10)
    except Exception:
        print(traceback.format_exc())