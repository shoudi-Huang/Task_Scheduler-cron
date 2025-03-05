#!/usr/bin/env python3
# -*- coding: ascii -*-

import os, signal, time

#Function read status information from ".runner.status" file
def read_status():
    try:
        with open (".runner.status", "r") as f:
            line = f.read()
    except FileNotFoundError:
        print('file ".runner.status" FileNotFoundError: file not found')
        exit(2)
    except Exception:
        print('file ".runner.status" Error: fail to open in read mode')
        exit(2)
    
    return line

#Open ".runner.pid" file in read mode and read runner.py pid
try:
    with open (".runner.pid", "r") as f:
        pid = int(f.readline())
except FileNotFoundError:
    print('flie ".runner.pid" FileNotFoundError: file not found')
    exit(1)
except Exception:
    print('flie ".runner.pid" Error: fail to open in read mode')
    exit(1)

#Sent signal to runner.py for construct status information
os.kill(pid, signal.SIGUSR1)

#Read status information from ".runner.status" file
time.sleep(1)
line = read_status()

#Redo the read status information, if ".runner.status" file is empty
if line == "":
    time.sleep(4)
    line = read_status()
    if line == "":
        print("status timeout")
        exit(0)

#Output status information
print(line)

#Overwrite ".runner.status" file
try:
    f = open(".runner.status", "w")
    f.close()
except FileNotFoundError:
    print('file ".runner.status" FileNotFoundError: file not found')
    exit(2)
except Exception:
    print('file ".runner.status" Error: fail to open in write mode ')
    exit(2)
