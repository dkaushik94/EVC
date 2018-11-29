'''
    Written by Debojit Kaushik  (5th November 2019)
'''
import os
import sys
import traceback
import json
import math

from multiprocessing import Process, Queue
from threading import Thread
from time import sleep
from random import randint


NUM_PROC, PROCESSES, SENDERS, KILLED_NODES = None, [], [], 0
SENDERS2 = []
class Proc(Process):

    def __init__(self, t_id, prime):
        Process.__init__(self)
        self.events = {
            "INT_EVNT": 0, 
            "SND_EVNT": 0,
            "RCV_EVNT": 0
        }
        self.clock_growth = {"event":[], "clock_val": [], "no_of_bits": []}
        self.t_id = t_id
        self.prime = prime
        self.clock = 1
        self.channel = None
        self.consumer_tag = None
        self.i = 0
        self.queue = Queue()
        self.kill_self = False
        self.ev_no = 0


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


    def update_clock(self, mode, ext_clock = None):
        global NUM_PROC
        if int(self.clock).bit_length() <= 32*NUM_PROC:
            self.ev_no += 1
            if mode == "RCV":
                temp = self.LCM(self.clock, ext_clock)
                self.clock = temp*self.prime
            elif mode == "SND" or mode == "INT":
                self.clock = self.clock * self.prime
            self.clock_growth["event"].append(self.ev_no)
            self.clock_growth["clock_val"].append(self.clock)
            self.clock_growth["no_of_bits"].append(int(self.clock).bit_length())
            return False
        else:
            return True
 

    def onReceive(self, ext_clock):
        try:
            self.events['RCV_EVNT'] += 1
            kill_self = self.update_clock("RCV", int(ext_clock))
            if kill_self:
                self.kill()
                return True
            else:
                return False
        except Exception:
            print(traceback.format_exc())


    def run(self):
        try:
            while True:
                if self.queue.empty() is False:
                    event = self.queue.get()
                    flag = self.onReceive(event)
                    if flag:
                        global KILLED_NODES
                        KILLED_NODES += 1
                        global SENDERS
                        SENDERS[self.t_id] = True
                        break
            print("Killed")
        except Exception:
            print(traceback.format_exc())


    def kill(self):
        try:
            print(self.events)
            filename = "_".join(["Process", str(self.t_id), "data"]) + ".json"
            with open(filename, "w+") as f:
                f.write(json.dumps({"growth":self.clock_growth, "events": self.events}))
            return
        except Exception:
            print(traceback.format_exc())



def send_message(K, t_id):
    try:
        global KILLED_NODES
        i = 0
        kill_self = False
        global SENDERS
        while SENDERS[t_id] is False:
            choice = randint(0,1)
            p_id, ext_process = PROCESSES[randint(0, len(PROCESSES)-1)].t_id, PROCESSES[randint(0, len(PROCESSES)-1)]

            own_proc = None
            for item in PROCESSES:
                if item.t_id == t_id:
                    own_proc = item
                    break
            if choice == 0:
                own_proc.events['INT_EVNT'] += 1
                own_proc.update_clock("INT")
            elif choice > 0:
                own_proc.events['SND_EVNT'] += 1
                own_proc.update_clock("SND")
                ext_process.queue.put(int(own_proc.clock))
            i += 1
        print(t_id, "sender killed.") 
    except Exception:
        print('\n',traceback.format_exc())


if __name__ == '__main__':
    try:
        NUM_PROC = int(sys.argv[len(sys.argv)-1:][0])
        primes = []
        num = 2
        while len(primes) < NUM_PROC:
            prime = True
            for i in range(2,num):
                if (num%i==0):
                    prime = False
            if prime:
                primes.append(num)
            num += 1

        for item in range(NUM_PROC):
            thread = Proc(item, primes[item])
            PROCESSES.append(thread)
            thread = Process(target = send_message, args = (4,item))
            SENDERS2.append(thread)
            SENDERS.append(False)
        
        for it ,item in enumerate(PROCESSES):
            item.start()
            SENDERS2[it].start()
    except Exception:
        print(traceback.format_exc())