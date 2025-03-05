#!/usr/bin/env python3
# -*- coding: ascii -*-

import sys, os, time, datetime, signal

"""
The configuration file for runner.py will contain one line for each program that is to be run.   Each line has the following parts: 

timespec program-path parameters

where program-path is a full path name of a program to run and the specified time(s), parameters are the parameters for the program,
timespec is the specification of the time that the program should be run.

The timespec has the following format:

[every|on day[,day...]] at HHMM[,HHMM] run

Square brackets mean the term is optional, vertical bar means alternative, three dots means repeated.

Examples:

every Tuesday at 1100 run /bin/echo hello
	every tuesday at 11am run "echo hello"
on Tuesday at 1100 run /bin/echo hello
	on the next tuesday only, at 11am run "echo hello"
every Monday,Wednesday,Friday at 0900,1200,1500 run /home/bob/myscript.sh
	every monday, wednesday and friday at 9am, noon and 3pm run myscript.sh
at 0900,1200 run /home/bob/myprog
	runs /home/bob/myprog once  at 9am and noon


"""

#Function convert weekday and time to actual date
def get_next_weekday(date, next_weekday, h, m):     
    new_date = date.replace(hour=h, minute=m, second=0, microsecond=0)
    time_difference = (new_date - date).total_seconds()

    #If schedule weekday same as today and have not pass the schedule time.
    if new_date.strftime("%A") == next_weekday and time_difference>0:
        return new_date

    #Convert date to next schedule weekday.
    new_date += datetime.timedelta(1)
    while new_date.strftime('%A') != next_weekday:
        new_date+= datetime.timedelta(1)

    return new_date


#Function divide hour and minute from schedule time
def get_hour_minute(clock, inst):
    clock_ls = list(clock)
    hour = int(clock_ls[0]+clock_ls[1])     #eg. 1124 > hour = 11 ; minute = 24
    minute = int(clock_ls[2]+clock_ls[3])
    if inst == "hour":
        return hour
    elif inst == "minute":
        return minute


#Function check ".runner.conf" file syntax
def check_conf(line):
    line = line.strip()
    line = line.split(" ")
    if len(line)<4:
        return False

    frequency = line[0]
    #Check valid keyword
    if frequency != "every" and frequency != "on" and frequency != "at":
        return False
    
    #Error checking for line with keyword "every" or "on"
    if frequency == "every" or frequency == "on":
        if len(line)<6:
            return False
        
        weekday_ls = line[1].split(",")
        correct_weekday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        #Check valid weekday name
        for w in weekday_ls:
            correct = False
            i = 0
            while len(correct_weekday)>i:
                if w == correct_weekday[i]:
                    correct = True
                    break
                i += 1
            if not correct:
                return False
        
        #Check syntax
        if line[2] != "at" or line[4] != "run":
            return False

        clock_ls = line[3].split(",")
    #Error checking for line with keyword "at"
    else:
        if line[2] != "run":
            return False
        clock_ls = line[1].split(",")

    #Check valid time syntax
    for clock in clock_ls:
        sub_clock_ls = list(clock)
        if len(sub_clock_ls) != 4:
            return False

        for d in sub_clock_ls:
            if not d.isdigit():
                return False
        hour = int(sub_clock_ls[0] + sub_clock_ls[1])
        minute = int(sub_clock_ls[2] + sub_clock_ls[3])
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            return False

    return True


#Function construct instruction from conf to a process dictionary with key information
def construct_program_dictionary(instruction):
    i=0
    while i<len(instruction):
        parameter = []
        frequency = instruction[i][0]

        #Construct process dictionary with keyword "at"
        if frequency == "at":
            x=4
            while x<len(instruction[i]):
                parameter.append(instruction[i][x])     #Defined parameter for the process
                x+=1
            path = instruction[i][3]

            clock_ls = instruction[i][1].split(',')
            weekday_ls = []
            for clock in clock_ls:
                #Convert time to actual date
                h = get_hour_minute(clock, "hour")
                m = get_hour_minute(clock, "minute")
                current_date = datetime.datetime.today()
                planing_date = datetime.datetime.today().replace(hour=h, minute=m, second=0, microsecond=0)
                time_difference = (planing_date - current_date).total_seconds()

                if time_difference < 0:
                    planing_date += datetime.timedelta(1)
                
                day = planing_date.strftime("%A")
                #Construct Dictionary
                program = {
                    "Frequency": frequency,
                    "Weekday": day,
                    "Clock": clock,
                    "Path": path,
                    "Parameter": parameter,
                    "Date": planing_date,
                    "Statu": "will run"}
                program_ls.append(program)

        #Construct process dictionary with keyword "on" or "every"   
        else:
            weekday_ls = instruction[i][1].split(',')
            clock_ls = instruction[i][3].split(',')
            path = instruction[i][5]

            x=6
            while x<len(instruction[i]):
                parameter.append(instruction[i][x])
                x+=1
        
            for day in weekday_ls:
                for clock in clock_ls:
                    h = get_hour_minute(clock, "hour")
                    m = get_hour_minute(clock, "minute")
                    current_date = datetime.datetime.today()
                    planing_date = get_next_weekday(current_date, day, h, m)
                    
                    program = {
                        "Frequency": frequency,
                        "Weekday": day,
                        "Clock": clock,
                        "Path": path,
                        "Parameter": parameter,
                        "Date": planing_date,
                        "Statu": "will run"}
                    program_ls.append(program)

        i+=1
    
    return program_ls


#Function check duplicate run time error in conf
def check_duplicate_run_time(instruction):
    #Covert instruction from conf to list of program dictionary
    check_program_ls = construct_program_dictionary(instruction)

    #Check every process have unique schedule date
    i=0
    while i<len(check_program_ls):
        x=0
        while x<len(check_program_ls):
            if x == i:
                x+=1
                continue
            elif check_program_ls[x]["Date"] == check_program_ls[i]["Date"]:
                return False
            x+=1
        i+=1
    return True


#Function add last ran process to error process
def error_handler(signum, frame):
    error_program = ran_program_ls[-1].copy()
    ran_program_ls.pop(-1)
    error_program_ls.append(error_program)
    error_program_ls[-1]["Statu"]="error"


#Function send status information to ".runner.status" file
def status_handler(signum, frame):
    total_program_ls = ran_program_ls + program_ls + error_program_ls

    if len(total_program_ls)==0:
        return

    #Sort process with different status by date
    total_program_ls = sorted(total_program_ls, key=lambda k: k['Date'])

    #Open ".runner.status" file in write mode
    try:
        f = open(".runner.status", "w")
    except Exception:
        print('file ".runner.status" FileNotFoundError: fail to open in write mode ')
        exit(2)

    num_program = 0
    for program in total_program_ls:
        num_program += 1
        message = ""
        date_time = program["Date"].ctime()

        #Write statu infor correspond to each process's statu
        if program["Statu"] == "ran":
            message = "ran" + " " + date_time + " " + program["Path"]
        elif program["Statu"] == "will run":
            message = "will run at" + " " + date_time + " " + program["Path"]
        elif program["Statu"] == "error":
            message = "error" + " " + date_time + " " + program["Path"]
        
        if len(program["Parameter"])>0:
            for p in program["Parameter"]:
                message = message + " " + p
        
        if num_program != len(total_program_ls):
            message = message + "\n"
        
        f.write(message)
    
    f.close()



# ~ MAIN PROCESS ~

#Created three process list for processes with different status
program_ls = []
ran_program_ls = []
error_program_ls = []

#Signal Receiver
signal.signal(signal.SIGUSR2, error_handler)
signal.signal(signal.SIGUSR1, status_handler)

#Get runner.py process id and write to ".runner.pid" file
pid = str(os.getpid())
try:
    with open(".runner.pid", "w") as f:
        f.write(pid)
except Exception:
    print('file ".runner.pid" Error: fail to open in write mode')
    exit(1)

#Created ".runner.status" file, if not exist
if not os.path.isfile(".runner.status"):
    try:
        f = open(".runner.status", 'x')
        f.close()
    except FileExistsError:
        print('file ".runner.status" FileExistsError: file alread exists')
        exit(2)
    except Exception:
        print('file ".runner.status" Error: fail to open in create mode')
        exit(2)

#Read from ".runner.conf" file
try:
    f = open(".runner.conf", 'r')
except Exception:
    print('configuration file not found')
    exit(3)

#Check file not empty
if not os.path.getsize(".runner.conf") > 0:
    print('configuration file empty')
    f.close()
    exit(4)

instruction = []
while True:
    l = f.readline()
    if l == '':
        break
    check_syntax_result = check_conf(l)     #Check conf file syntax
    if check_syntax_result == False:
        print("error in configuration: " + l.strip())
        f.close()
        exit(4)
    
    line = l.split()
    instruction.append(line)

    #Check duplicate run time error
    check_run_time_result = check_duplicate_run_time(instruction)
    program_ls = []
    if check_run_time_result == False:
        print("error in configuration: " + l.strip())
        f.close()
        exit(4)
f.close()


#Construct will run process list and sort by its schedule date
program_ls = construct_program_dictionary(instruction)
program_ls = sorted(program_ls, key=lambda k: k['Date'])

#Run process in will run process list
while len(program_ls)>0:
    #Wait until schedule date of the process reach
    current_date = datetime.datetime.today()
    time_difference = (program_ls[0]["Date"] - current_date).total_seconds()
    time.sleep(time_difference)
    
    #Construct path and parameter for running the process
    path = program_ls[0]["Path"]
    argument = [program_ls[0]["Path"]]
    if len(program_ls[0]["Parameter"])>0:
        argument = argument + program_ls[0]["Parameter"]

    #Add the prcess to ran process list
    ran_program = program_ls[0].copy()
    ran_program_ls.append(ran_program)
    ran_program_ls[-1]["Statu"]="ran"

    #Construct a new date for process with keyword "every"
    if program_ls[0]["Frequency"] == "every":
        program_ls[0]["Date"] += datetime.timedelta(1)
        h = get_hour_minute(program_ls[0]["Clock"], "hour")
        m = get_hour_minute(program_ls[0]["Clock"], "minute")
        program_ls[0]["Date"] = get_next_weekday(program_ls[0]["Date"], program_ls[0]["Weekday"], h, m)
        #Change the position of the process be the last one in will run process list
        program_ls.append(program_ls[0])
        program_ls.pop(0)
    #Delete process with keyword "on" or "at" from will run process list 
    else:
        program_ls.pop(0)

    #Run process by fork and exec
    new_pid = os.fork()
    if new_pid == 0:
        try:
            os.execvp(path, argument)   #Process running
        except Exception:
            #Sent signal to parent runner.py to handle error occurs during process running
            pid = int(pid)
            os.kill(pid, signal.SIGUSR2)
            exit(5)
    else:
        os.wait()


print("nothing left to run")
exit()
