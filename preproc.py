import os, json

files = []
for item in os.listdir():
    if item.split(".")[-1] == 'json' and item.split("_")[0] == 'data':
        files.append(item)

data = []
for item in files:
    with open(item, "r+") as f:
        data.append(json.loads(f.read()))


# for item in data:
#     print(item.keys())
l = 1000000
for item in data:
    if len(item['bit_length']) < l:
        l = len(item['bit_length'])
    
d = []
for item in data:
    d = d + item['bit_length'][:l+1]

with open("x.json", 'w+') as f:
    f.write(json.dumps({"clock":sorted(d)}))

