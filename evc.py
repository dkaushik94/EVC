'''
Written by Debojit Kaushik  (Timestamp)
'''
import os
import sys
import traceback
from multiprocessing import Process, Queue
from random import randint
import json
from time import sleep
import numpy as np


class receiver(Process):
    def __init__(self, n, prime, t_id, q_list):
        Process.__init__(self)
        self.prime = prime
        self.n = n
        self.q = q_list
        self.clock = 1
        self.t_id = t_id
        self.kill = False
        self.events = {
            "INT": 0, 
            "SND": 0,
            "RCV": 0
        }
        self.bit_length = []
        self.ev_no = [0]
    
    def gcd(self, x, y):
        """This function implements the Euclidian algorithm
        to find G.C.D. of two numbers"""
        while(y):
            x, y = y, x % y
        return x


    def LCM(self, x, y):
        """This function takes two
        integers and returns the L.C.M."""
        lcm = (x*y)//self.gcd(x,y)
        return lcm

    def run(self):
        try:
            # global REC
            while int(self.clock).bit_length() <= 32*self.n:
                msg = self.q[self.t_id].get()
                self.events[msg["type"]] += 1
                self.ev_no.append(self.ev_no[-1] + 1)

                if msg["type"] == "INT":
                    self.clock = self.clock * self.prime
                    self.bit_length.append(int(self.clock).bit_length())
                elif msg["type"] == "SND":
                    self.clock = self.clock * self.prime
                    self.bit_length.append(int(self.clock).bit_length())
                    index = self.t_id
                    while index == self.t_id:   
                        index = randint(0, len(self.q)-1)
                    self.q[index].put({"type": "RCV", "clock": self.clock})     
                elif msg["type"] == "RCV":
                    print("Receiving...")
                    temp = self.LCM(self.clock, msg["clock"])
                    self.clock = self.clock * temp
                    self.bit_length.append(int(self.clock).bit_length())
            # self.kill = True
            if self.kill:
                print("Killed")
                filename = "_".join(["data", str(self.t_id), ".json"])
                with open("test_"+filename, "w+") as f:
                    f.write(json.dumps({
                        "bit_length": self.bit_length,
                        "events": self.ev_no,
                        "ev_types": self.events 
                        }))
        except Exception:
            print(traceback.format_exc())


def sender(t_id, worker_q):
    try:
        # rev_thr = list(filter(lambda x: x.t_id == t_id, REC))[0]
        i = 0
        sleep(4)
        while True:
            sleep(0.01)
            mode = i%2
            if mode == 0:
                worker_q[t_id].put({"type": "INT"})
            elif mode == 1:
                worker_q[t_id].put({"type": "SND"})
            i += 1
    except Exception:
        print(traceback.format_exc())



if __name__ == '__main__':
    try:
        n = int(sys.argv[1])
        primes = []
        num = 2
        while len(primes) < n:
            prime = True
            for i in range(2,num):
                if (num%i==0):
                    prime = False
            if prime:
                primes.append(num)
            num += 1

        work_q = [Queue() for _ in range(n)]

        for item in range(0, n):
            thread = receiver(n, primes[item], item, work_q)
            # REC.append(thread)
            thread.daemon = True
            thread.start()

        for item in range(0, n):
            thread = Process(target=sender, args= ((item,work_q)))
            thread.daemon = True
            thread.start()
        sleep(100)
    except Exception:
        print(traceback.format_exc())