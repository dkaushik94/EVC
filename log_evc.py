'''
    Written by Debojit Kaushik  (Timestamp)
'''
import os
import sys
import traceback
import simplejson as json
import math

from multiprocessing import Queue, Process, Lock
from threading import Thread
from random import randint
from time import sleep
from decimal import *


def EVC(t_id, q, prime, max_size, prec, V):
    try:
        def gcd(x, y):
            while(y):
                x, y = y, x % y
            return x

        def LCM(x, y):
            lcm = (x*y)//math.gcd(x,y)
            return lcm

        def receive(q, t_id, prime, prec, V):
            try:
                evc = 1
                log_clock = Decimal('0')
                events = {
                    'int': 0,
                    'rcv': 0, 
                    'send': 0,
                    'evc': [], 
                    'log_clock': []
                }
                evt_count = 0
                while evt_count < V:
                    event = q[t_id].get()
                    if event['type'] == "INT":

                        evc = evc * prime
                        log_clock = log_clock + (Decimal(prime).log10() / Decimal(2).log10()) 

                        events['evc'].append(evc)
                        events['log_clock'].append(log_clock)
                        
                        events['int'] += 1
                        evt_count += 1
                    
                    elif event['type'] == "SEND":
                        
                        log_clock = log_clock + (Decimal(prime).log10() / Decimal(2).log10())
                        evc = evc * prime

                        events['evc'].append(evc)
                        events['log_clock'].append(log_clock)

                        recv_id = randint(0, max_size-1)
                        while recv_id == t_id:
                            recv_id = randint(0, max_size-1)
                        assert recv_id != t_id
                        q[recv_id].put({
                            'type': "RECV",
                            'log_clock': log_clock,
                            'evc': evc
                        })

                        events['send'] += 1
                        evt_count += 1

                    elif event['type'] == "RECV":

                        s = Decimal(event['log_clock'])
                        log_clock = s + log_clock - Decimal(gcd(int(evc), int(event['evc']))).log10() / Decimal(2).log10()
                        log_clock = log_clock + (Decimal(prime).log10() / Decimal(2).log10())

                        evc = LCM(int(event['evc']), int(evc))
                        evc = evc * prime

                        events['log_clock'].append(log_clock)
                        events['evc'].append(evc)

                        events['rcv'] += 1
                        evt_count += 1
                events['id'] = t_id
                print(events)
                with open('part2/data_'+str(t_id)+'.json', 'w+') as f:
                    f.write(json.dumps(events))
                
            except Exception:
                print(traceback.format_exc())
        
        def send(q, t_id):
            try:
                sleep(4)
                mode = 0
                while True:
                    sleep(0.05)
                    if mode%2 == 0:
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

        th = Thread(target = send, args=(q, t_id))
        th.daemon = True
        th.start()
        receive(q, t_id, prime, prec, V)
    except Exception:
        print(traceback.format_exc())


if __name__ == '__main__':
    try:
        N, precision, V = int(sys.argv[1]), int(sys.argv[2]) + 1, int(sys.argv[3])
        qu = [Queue() for _ in range(N)]
        primes = []
        num = 2
        print(precision)
        getcontext().prec = precision
        while len(primes) < N:
            prime = True
            for i in range(2,num):
                if (num%i==0):
                    prime = False
            if prime:
                primes.append(num)
            num += 1
        for _ in range(N):
            p = Process(target = EVC, args = ((_, qu, primes[_], N, precision, V)))
            p.start()
    except Exception:
        print(traceback.format_exc())






# for it, x in enumerate(evc):
#     for it2, y in enumerate(evc[it+1:]):
#         if (causality(x, y) is True and log_causality(log_clock[it2], log_clock[it]) is True) or (causality(y, x) is True and log_causality(log_clock[it], log_clock[it2) is True):
#             stats_dict['TP'] += 1
#         elif (causality(x, y) is True and log_causality(log_clock[it2], log_clock[it]) is False) or (causality(y, x) is True and log_causality(log_clock[it], log_clock[it2]) is False):
#             states_dict['FN'] += 1
#         elif (causality(x, y) is False and log_causality(log_clock[it2], log_clock[it]) is False) and (causality(y, x) is False and log_causality(log_clock[it], log_clock[it2]) is False):
#             stats_dict['TN'] += 1
#         elif (causality(x, y) is False and causality(y, x) is False) and (log_causality(log_clock[it2], log_clock[it]) is True or log_causality(log_clock[it], log_clock[it2]) is True):
#             stats_dict['FP'] += 1