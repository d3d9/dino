#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

class Restriction():
    def __init__(self, restrictionstr, datefrom, dateuntil):
        self.restrictionstr = restrictionstr
        self.firstday = int(datefrom[6:8])
        self.firstmonth = int(datefrom[4:6])
        self.startyear = int(datefrom[0:4])

        self.lastday = int(dateuntil[6:8])
        self.lastmonth = int(dateuntil[4:6])
        self.endyear = int(dateuntil[0:4])
        self.bd = self.booldictcalendar()

    def __str__(self):
        return "Restriction " + self.restrictionstr + "\n" \
                + str(self.firstday).zfill(2) + "." + str(self.firstmonth).zfill(2) \
                + "." + str(self.startyear) + " - " + str(self.lastday).zfill(2) \
                + "." + str(self.lastmonth).zfill(2) + "." + str(self.endyear)

    def strdictcalendar(self):
        currentnumber = 0
        currentyear = self.startyear
        currentmonth = self.firstmonth
        calendar = {currentyear: {}}

        for o in range(0,len(self.restrictionstr),8):
            bits = bin(int(self.restrictionstr[o:o+8],16))[2:].zfill(32)[1:][::-1]

            if currentmonth == 13:
                currentmonth = 1
                currentyear += 1
                calendar[currentyear] = {}

            daysinmonth = daysin(currentmonth, currentyear)

            if not o:
                bits = "."*(self.firstday-1) + bits[self.firstday-1:]
            elif o == len(self.restrictionstr) - 8:
                bits = bits[:self.lastday] + "."*(daysinmonth-self.lastday+1)

            bits = bits[:daysinmonth] + "_"*(31-daysinmonth)

            calendar[currentyear][currentmonth] = bits
            currentmonth += 1

        return calendar

    def booldictcalendar(self):
        currentnumber = 0
        currentyear = self.startyear
        currentmonth = self.firstmonth
        calendar = {currentyear: {}}

        for o in range(0,len(self.restrictionstr),8):
            bits = bin(int(self.restrictionstr[o:o+8],16))[2:].zfill(32)[1:][::-1]

            if currentmonth == 13:
                currentmonth = 1
                currentyear += 1
                calendar[currentyear] = {}

            daysinmonth = daysin(currentmonth, currentyear)
            calendar[currentyear][currentmonth] = []

            for x in range(daysinmonth):
                if (not o) and x < self.firstday - 1:
                    calendar[currentyear][currentmonth].append(False)
                elif o == len(self.restrictionstr) - 8 and x > self.lastday - 1:
                    calendar[currentyear][currentmonth].append(False)
                else:
                    calendar[currentyear][currentmonth].append(bool(int(bits[x])))

            currentmonth += 1

        return calendar

    def textcalendar(self):
        months = {1: "Januar", 2: "Februar", 3: "März",
                  4: "April", 5: "Mai", 6: "Juni",
                  7: "Juli", 8: "August", 9: "September",
                 10: "Oktober", 11: "November", 12: "Dezember"}

        text = "\t\t0        1         2         3\n" \
               "\t\t1234567890123456789012345678901\n" \
               "\t\t|||||||||||||||||||||||||||||||\n"

        calendar = self.strdictcalendar()

        for year in sorted(calendar):
            for month in sorted(calendar[year]):
                text += months[month] + " " + str(year) + "\t" + calendar[year][month] + "\n"

        return text

    def dayresvalid(self, year, month, day):
        return self.bd[year][month][day-1]


def daysin(month, year):
    days = 31

    if month in [4, 6, 9, 11]:
        days = 30
    elif month == 2:
        days = 28
        if ((not year % 4) and year % 100) or (not year % 400):
            days = 29

    return days


# day von 0 - 6
def daytypevalid(weekday, daytype):
    assert 0 <= weekday <= 6
    return bool(int(bin(daytype)[2:].zfill(7)[weekday]))


def dayvalid(r, day, daytype):
    return daytypevalid(datetime(*day).weekday(), daytype) and r.dayresvalid(*day)


def findstop(rec_stop, stopid):
	#todo: beim laden das mit duplicate weg und hier etwas machen
	return rec_stop.loc[stopid]['STOP_NAME'].strip()


def findplat(rec_stopping_points, betrieb, stopid, plat):
    # verbessern
    for index, row in rec_stopping_points.query("VERSION == @betrieb & STOP_NR == @stopid & STOPPING_POINT_NR == @plat").iterrows():
        return row["STOPPING_POINT_SHORTNAME"]

'''
r = Restriction(restrictionstr="3e7cb9e34f9f3e7c79f3e7cf1f3e7cf967cf9f3a3cf9f3e61c3e7cf973e7cf9e0e7cf9f31e7cf9f327cf9f3c39e3e5ce1f3e7cf9",
                datefrom="20170611",
                dateuntil="20180617")
print(str(r)+"\n")
print(r.textcalendar(), end='')
print('')
bc = r.booldictcalendar()
print(bc)
for x in bc:
    for y in bc[x]:
        print(str(x)+" "+str(y)+"\t\t", end='')
        for z in bc[x][y]:
            if z:
                print("1", end='')
            else:
                print("0", end='')
        print('')
'''

