import os
from datetime import datetime
from collections import defaultdict


# First element for time, second element for msg, delete \n and split with white space
# return a dict with {time: [data]}, if file not exists, use default greeting.
def read_file(filepath):
    msg = defaultdict(list)
    print("Loading greeting msg from file!")
    if file_availability(filepath):
        with open(filepath, "r", encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip("\n")
                data = line.split(" ")
                msg[data[0]].append(data[1])
    return msg


def file_availability(filepath):
    if not os.path.exists(filepath):
        print("File", filepath, "not exists!")
        return False
    return True


def load_timetable():
    msg = {}
    with open("timetable", "r", encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip("\n")
            data = line.split(" ")
            msg[data[0]] = data[1]
    return msg


# Load timetable from file and select current time
def choose_current_time_dur():
    current = datetime.now().hour
    table = load_timetable()
    keys = table.keys()
    dur = ""
    if current < int(list(table)[0]):
        return table[list(table)[0]]
    for key in keys:
        if current >= int(key):
            dur = table[key]
    return dur


# Choose greeting list from time_table
def choose_greeting_list(filepath):
    return read_file(filepath)[choose_current_time_dur()]
