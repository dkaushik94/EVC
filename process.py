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


class Process(Thread):

    def __init__(self, args, t_id, prime):
        Thread.__init__(self)
        self.args = args
        self.t_id = t_id
        self.prime = prime
        self.clock = self.prime


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


    def onRecieve(self, ch, method, properties, body):
        try:
            data = json.loads(body)
            ext_clock = data["clock"]
            self.clock = self.LCM(self.clock, ext_clock)
            self.clock = self.clock * self.prime
            print("Message recieved by thread", self.t_id, "clock increased", self.clock)
        except Exception:
            print(traceback.format_exc())


    def run(self):
        try:
            self.initiate_send_events()
            print("Thread %s Starting to listen.." %(self.t_id))
            connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
            channel = connection.channel()
            channel.queue_declare(str(self.t_id))
            channel.basic_consume(self.onRecieve, queue = str(self.t_id), no_ack = True)
            print("Thread %s Starting to listen.." %(self.t_id))
            channel.start_consuming()
        except Exception:
            print(traceback.format_exc())


    def send_message(self):
        try:
            while True:
                self.clock = self.clock * self.prime
                print("Message sent by process", self.t_id, "Clock increased: ", self.clock)
                connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
                channel = connection.channel()
                queue =channel.queue_declare(str(randint(1,5)))
                channel.basic_publish(body = json.dumps({"clock": self.clock}), routing_key = str(self.t_id), exchange = '')
                connection.close()
                sleep(randint(1,2))
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
        t1 = Process("Thread 1", 1, 2)
        t2 = Process("Thread 2", 2, 3)
        t3 = Process("Thread 3", 3, 5)
        t4 = Process("Thread 4", 4, 7)
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t2.join()
        t1.join()
        t4.join()
        t3.join()
        print("Finished!")
    except Exception:
        print(traceback.format_exc())