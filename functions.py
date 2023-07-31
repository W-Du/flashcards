from datetime import datetime, date
import math

today = date.today()
# print(today.strftime("%Y/%m/%d"))


def elaspedTime(day1, day2):
    if not isinstance(day1, str):
        day1 = day1.strftime("%Y/%m/%d")
    if not isinstance(day2, str):
        day2 = day2.strftime("%Y/%m/%d")
    res = (datetime.strptime(day2, "%Y/%m/%d") - datetime.strptime(day1, "%Y/%m/%d")).days
    return res

def priorityChange(last_visit, mode=None, cur_priority = None):
    if not isinstance(last_visit, str):
        last_visit = last_visit.strftime('%Y/%m/%d')
    if not mode and not cur_priority:
        daydiff = elaspedTime(last_visit, today)
        return priorityFunction(daydiff)
    elif mode == 'review' and cur_priority:
        daydiff = elaspedTime(today,last_visit)
        if daydiff >= -1:
            return -1
        pdiff = priorityFunction(daydiff)
        if pdiff + cur_priority < 0:
            pdiff = int(pdiff / 2)
        return pdiff
    else:
        raise Exception('wrong parameters for pritoryChange function')

    

def priorityFunction(daydiff):
    if daydiff > 0:
        return int(math.log(abs(daydiff))) * 2
    else:
        return int(math.log(abs(daydiff))) * (-2)
    

# print(elaspedTime('2021/02/11', today))


    