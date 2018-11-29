'''
Written by Debojit Kaushik  (Timestamp)
'''
import os
import sys
import traceback
from random import randint
import json



def gcd(x, y):
   """This function implements the Euclidian algorithm
   to find G.C.D. of two numbers"""
   
   while(y):
       x, y = y, x % y

   return x

# define lcm function
def lcm(x, y):
   """This function takes two
   integers and returns the L.C.M."""

   lcm = (x*y)//gcd(x,y)
   return lcm


def ClockGrowth(N, processes, primes, clocks, bit_length, events):
    try:
        prime = 3
        clock = 1
        i = 1
        while int(clock).bit_length() <= 32*N:
            # print("Growing", clock)
            event_type = randint(1,2)
            bit_length.append(int(clock).bit_length())
            if event_type == 1:
                # print("here")
                clock = clock * prime
            else:
                # print("LCM", int(clock), int((int(int(clock))*int(int(prime)) / int(i))))
                choice_rcv = randint(0,1)
                p_id = None
                if choice_rcv == 0:
                    p_id = randint(0, N-1)
                    processes[p_id] = processes[p_id] * primes[p_id]
                else:
                    p_id = randint(0, N-1)
                    processes[p_id] = lcm(processes[p_id], clock) * primes[p_id]
                temp = lcm(int(clock), int(processes[p_id]))
                clock = temp * prime
                # print("Here3")
            clocks.append(clock)
            events.append(i)
            i += 1
        return len(events)
    except Exception:
        print(traceback.format_exc())

if __name__ == '__main__':
    try:
        # N = int(sys.argv[len(sys.argv)-1:][0])
        ev = []
        n = []
        for N in range(10, 50, 2):
            num = 2
            events = []
            clocks = []
            bit_length = []
            processes = [1 for item in range(N)]
            primes = []
            dic = {}
            while len(primes) < N:
                prime = True
                for i in range(2,num):
                    if (num%i==0):
                        prime = False
                if prime:
                    primes.append(num)
                num += 1
            x = ClockGrowth(N, processes, primes, clocks, bit_length, events)
            ev.append(x)
            n.append(N)


        with open("data.json", "w+") as f:
            f.write(json.dumps({"n": n, "events": ev}))
    except Exception:
        print(traceback.format_exc())