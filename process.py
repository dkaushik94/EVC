'''
    Written by Debojit Kaushik  (5th November 2019)
'''
import os
import sys
import traceback
import json
import pika
from threading import Thread
from time import sleep
from random import randint


NUM_PROC, PROCESSES = None, []

class Process(Thread):

    def __init__(self, t_id, prime):
        Thread.__init__(self)
        self.events = {
            "INT_EVNT": 0, 
            "SND_EVNT": 0,
            "RCV_EVNT": 0
        }
        self.clock_growth = {"event":[], "clock_val": []}
        self.t_id = t_id
        self.prime = prime
        self.clock = self.prime
        self.channel = None
        self.consumer_tag = None


    def LCM(self, x, y):
        try:
            lcm, greater = None, None    
            if x > y:  
                greater = x  
            else:
                greater = y

            while True:  
                if((greater % x == 0) and (greater % y == 0)):  
                    lcm = greater
                    break
                greater += 1
            return lcm
        except Exception:
            print(traceback.format_exc())


    def update_clock(self, mode, ext_clock = None):
        if mode == "RCV":
            self.clock = int(self.LCM(self.clock, ext_clock))
            self.clock = int(self.clock) * int(self.prime)
        elif mode == "SND" or mode == "INT":
            self.clock = self.clock * self.prime

        if int(self.clock).bit_length() <= 32*NUM_PROC:
            self.clock_growth["event"].append(sum(self.events.values()))
            self.clock_growth["clock_val"].append(self.clock)
            return False
        else:
            return True


    def onRecieve(self, ch, method, properties, body):
        try:
            data = json.loads(body)
            ext_clock = data["clock"]
            self.events['RCV_EVNT'] += 1
            self.update_clock("RCV", ext_clock)
            # print("Message recieved by thread", self.t_id, "clock increased", self.clock)
        except Exception:
            print(traceback.format_exc())


    def run(self):
        try:
            print("Thread %s Starting to listen.." %(self.t_id))
            self.initiate_send_events()
            connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
            self.channel = connection.channel()
            self.channel.queue_declare(str(self.t_id))
            self.consumer_tag = self.channel.basic_consume(self.onRecieve, queue = str(self.t_id), no_ack = True)
            self.channel.start_consuming()
            connection.close()
            print(self.t_id, "stopped consuming!")
        except Exception:
            self.kill()
            print(self.t_id, "Crashed.")


    def send_message(self):
        try:
            kill_self = False
            while True and not kill_self:
                choice = randint(0,1)
                if choice == 0:
                    self.events['INT_EVNT'] += 1
                    kill_self = self.update_clock("INT")
                elif choice == 1:
                    self.events['SND_EVNT'] += 1
                    kill_self = self.update_clock("SND")
                    # print("Message sent by process", self.t_id, "Clock increased: ", self.clock)
                    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
                    channel = connection.channel()
                    p_id = self.t_id
                    while p_id == self.t_id:
                        if PROCESSES:
                            p_id = PROCESSES[randint(0, len(PROCESSES)-1)].t_id
                        elif len(PROCESSES) <= 1:
                            self.kill()
                    queue = channel.queue_declare(str(randint(1,NUM_PROC)))
                    channel.basic_publish(body = json.dumps({"clock": self.clock}), routing_key = str(self.t_id), exchange = '')
                    connection.close()
                # sleep(randint(1, 4)/10)
            self.kill()
        except Exception:
            self.kill()
            print(self.t_id, "Crashed.")
            # print(traceback.format_exc())

    def kill(self):
        try:
            self.channel.basic_cancel(self.consumer_tag)
            del PROCESSES[PROCESSES.index(self)]
            filename = "_".join(["Process", str(self.t_id), "data"]) + ".json"
            with open(filename, "w+") as f:
                f.write(json.dumps({"growth":self.clock_growth, "events": self.events}))
        except Exception:
            print(traceback.format_exc())


    def initiate_send_events(self):
        try:
            thread = Thread(target=self.send_message)
            thread.start()
        except Exception:
            print(traceback.format_exc())


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
            thread = Process(item, primes[item])
            PROCESSES.append(thread)
            thread.start()
    except Exception:
        print(traceback.format_exc())