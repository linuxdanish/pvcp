#! /usr/bin/python

import hashlib
import subprocess
import os

file= "/Users/kielthorlton/test_path/A002C009_190530_A3JX.mxf"
path = "/Users/kielthorlton/test_path"

files = []

for r, d, f in os.walk(path):
    for file in f:
        files.append(file)
        print(r)
        print(file)

print("Files in file")


for file in files:
    print(file)


# m = hashlib.md5()

# command = "/sbin/md5 -r " + file
# proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
# while True:
#     line = proc.stdout.readline()
#     if not line:
#         break
#     print(line)


# with open(file, "rb") as f:
#     for chunk in iter(lambda: f.read(65536), b""):
#         m.update(chunk) 


# print(f)
# print(m.hexdigest())
