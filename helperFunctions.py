# import pygame as pg
from colours import BLACK, WHITE, GREEN, RED, YELLOW
import os
import pickle
from datetime import datetime, timedelta

# timezone = "PST"
timezone = "EST"


def getDuedateBackground(assignment):
    #checks if an assignment is due soon
    #Black > week
    #green > 3 days
    #yellow > 1 day
    #red < 1 day
    #flashing red < 1 hr
    due_date = assignment.due_date
    now = datetime.now()
    diff = due_date - now
    assignment.time_left = str(diff)[:-7]
    if diff > timedelta(weeks=1):
        # print('due_date:', due_date)
        background = BLACK
    elif diff > timedelta(days=3):
        background = GREEN
    elif diff > timedelta(days=1):
        background = YELLOW
    elif timedelta(0) <= diff < timedelta(days=1):
        background = RED
    else:
        background = WHITE
    return background


def new_line(text):
    if len(text) > 40:
        line_0 = text[:39]+"-$_$"
        line_1 = text[39:]
        return line_0 + new_line(line_1)
    return text


def string2date(date):
    #an error will be raised if the date was formatted incorrectly
    try:
        # due date format 2019-06-05T25:53
        #remove spaces in the date
        if " " in date:
            date.replace(" ","")
        #if only the date was given, default to a time fo 23:55 EST
        ### MAKESHIFT SOLUTION ###
        if "T" not in date:
            if timezone == "PST":
                t = ['20','55']
            else:
                t = ['23','55']
            d = date.split('-')
        else:
            d_t = date.split('T')
            t = d_t[1].split(':')
            d = d_t[0].split('-')
        due = datetime(int(d[0]),int(d[1]),int(d[2]),int(t[0]),int(t[1]))
        # #checks if the datetime given is prior to the current datetime
        # if due < datetime.now():
        #     #This will be processed as an error
        #     return 0
        return due
    except:
        return False


def date2string(date):
    return date.strftime("%Y-%m-%dT%H:%M")


def rect2start_pos(rect):
    #(left, top, width, height) => (x1,y1),(x2,y2)
    x1 = rect[0]
    y1 = rect[1]
    return (x1,y1)


def rect2end_pos(rect):
    #(left, top, width, height) => (x1,y1),(x2,y2)
    x2 = rect[0] + rect[2]
    y2 = rect[1] + rect[3]
    return (x2,y2)


def pair2rect():
    #(x1,y1),(x2,y2) => (left, top, width, height)
    pass


def loadSort(filename):
    #loads the assignmets
    assignments = [i for i in loadall(filename)]
    #sorts the assignements
    sortKey = lambda ans : ans.due_date  # noqa: E731
    assignments.sort(key=sortKey)
    return assignments


def save_object(obj, filename):
    with open(filename, 'a+b') as output:  # Appends to the file
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def loadall(filename):
    if not os.path.exists(filename):
        open(filename, 'a').close()
    if os.path.getsize(filename) > 0:
        #display assignmets 1-8
        with open(filename, "rb") as f:
            while True:
                try:
                    yield pickle.load(f)
                except EOFError:
                    break


def delete_assignment(asn_num, filename):
    #deletes the specified assignment from the pickle file
    # asn_num corresponds to the index of the assignment in the
    # full list of assignments
    pkl_assignments = loadSort(filename)
    pkl_assignments.pop(asn_num)
    os.remove(filename)
    for i in range(len(pkl_assignments)):
        save_object(pkl_assignments[i], filename)  #wow no real database management


def delete_specific_assignment(asn, pkl_assignments, filename):
    #deletes the specified assignment from the pickle file
    pkl_assignments.remove(asn)
    os.remove(filename)
    for i in range(len(pkl_assignments)):
        save_object(pkl_assignments[i], filename)  #wow no real database management
