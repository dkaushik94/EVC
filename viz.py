'''
Written by Debojit Kaushik  (Timestamp)
'''
import os
import sys
import traceback
import json
import matplotlib.pyplot as plt

# f = open("Process_6_data.json", "r")
# data = json.loads(f.read())
# x, y = data["growth"]["event"], data["growth"]["no_of_bits"]
# plt.xlabel("Number of events")
# plt.ylabel("No of Bits")
# plt.title("Growth of Bit Length vs Number of Events, n = 30")

# plt.plot(x, y)
# plt.savefig("Growth3")
# plt.show()
# for it, item in enumerate(y):
#     if item < len(y)-1:
#         print(y[it+1] - item)

f = open("x.json", "r")
data = json.loads(f.read())
# x, y = [i for i in range(len(data['bit_length']))], data["bit_length"]
x,y = [i for i in range(len(data['clock']))], data["clock"]
# print(len(x), len(y))

plt.xlabel("Events")
plt.ylabel("bit size of clock")
plt.title("Events vs Growth of bit length of clock at a process")

plt.plot(x, y)
plt.savefig("Proesses")
plt.show()