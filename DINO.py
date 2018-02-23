#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pandas import isnull
from datetime import datetime, timedelta
from copy import deepcopy


class Restriction():
    def __init__(self, restrictionstr, datefrom, dateuntil, text=""):
        self.restrictionstr = restrictionstr
        self.firstday = int(datefrom[6:8])
        self.firstmonth = int(datefrom[4:6])
        self.startyear = int(datefrom[0:4])

        self.lastday = int(dateuntil[6:8])
        self.lastmonth = int(dateuntil[4:6])
        self.endyear = int(dateuntil[0:4])

        self.text = text
        self.bd = self.booldictcalendar()

    def __str__(self):
        return "Restriction " + self.restrictionstr + "\n" \
                + str(self.firstday).zfill(2) + "." + str(self.firstmonth).zfill(2) \
                + "." + str(self.startyear) + " - " + str(self.lastday).zfill(2) \
                + "." + str(self.lastmonth).zfill(2) + "." + str(self.endyear) \
                + (("\nText: " + self.text) if self.text else "")

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


class CourseStop():
    def __init__(self, stopnr, ifopt, stopid, stopname, platid, platname, time, dep, different_arrdep=False):
        self.stopnr = stopnr
        self.ifopt = ifopt
        self.stopid = stopid
        self.stopname = stopname
        # self.areaid = areaid
        self.platid = platid
        self.platname = platname
        self.time = time
        self.dep = dep
        # geht das besser?
        self.different_arrdep = different_arrdep

    def __str__(self):
        return "CourseStop " + str(self.stopnr) + " " + ("dep" if self.dep else "arr") + " " \
                + str(self.time) + " " + str(self.stopid) + ":" + str(self.platid) \
                + " (" + self.stopname + " " + self.platname + ", "+ self.ifopt +")"


class Line():
    def __init__(self, timetable, lineid, rec_lin_ber, rec_stop, lid_course, lid_travel_time_type, rec_stopping_points):
        self.timetable = timetable
        self.lineid = lineid
        self.linesymbol = findlinesymbol(rec_lin_ber, self.timetable, self.lineid)
        self.courses = {}
        getlinecourses(self, rec_lin_ber, rec_stop, lid_course, lid_travel_time_type, rec_stopping_points)

    def __str__(self):
        return "Line " + self.linesymbol + " (" + self.timetable + ":" + str(self.lineid) + ")"

# class Variant?

class Course():
    # todo: sind die erwarteten angaben str, int, ?
    def __init__(self, line, variant, linedir, stops):
        self.line = line
        self.variant = variant
        self.linedir = linedir
        self.stops = stops
        self.time = stops[0].time
        self.endtime = stops[-1].time
        self.stopfrom = stops[0].stopname
        self.stopto = stops[-1].stopname
        self.duration = self.endtime - self.time
        # + daytype und restriction hier nochmal angeben

    def __str__(self):
        return "Course " + self.line.timetable + ":" + self.line.lineid + ":" + str(self.linedir) + ":" + str(self.variant) \
                + " from " + self.stopfrom + " to " + self.stopto \
                + " (" + str(self.duration) + ")"

    def stoptext(self):
        text = str(self) + "\n"
        prevnr = 0
        for stop in self.stops:
            if stop.different_arrdep or prevnr != stop.stopnr:
                text += str(stop.stopnr)+":\t"
                if stop.different_arrdep:
                    text += "dep" if stop.dep else "arr"
                else:
                    text += "   "
                text += " "+str(stop.time)+"\t"+stop.stopname+" "+stop.platname+"\n"
                prevnr = stop.stopnr

        return text


class Trip(Course):
    def __init__(self, course, restriction, daytype, starttime):
        super().__init__(course.line, course.variant, course.linedir, course.stops)
        self.restriction = restriction
        self.daytype = daytype
        self.starttime = starttime
        self.time += self.starttime
        self.endtime += self.starttime
        self.stops = deepcopy(self.stops)

        for stop in self.stops:
            stop.time += starttime

    def __str__(self):
        # was ist für time besser? mit:
        # str(startzeit//3600).zfill(2)+":"+str((startzeit//60)%60).zfill(2)+":"+str(startzeit%60).zfill(2)
        # kriegt man als stunde auch 24, 25 usw., mit str(timedelta(..)) kriegt man "1 day, .."
        return "Trip " + self.line.timetable + ":" + self.line.lineid + ":" + str(self.linedir) + ":" + str(self.variant) \
                + " at " + str(self.time) + " from " + self.stopfrom + " to " + self.stopto \
                + " (" + str(self.duration) + "), restriction \"" + self.restriction.text \
                + "\", daytype " + str(self.daytype)

#    def tripgraph(self):
#        raise NotImplementedError()

    # todo: sind areaids notwendig?
    # todo: was tun, wenn ein stop mehrmals vorkommt? wie macht man es angenehm nutzbar?

##    def timeforstop(self, stopid, areaid, platid, dep):
#    def timeforstop(self, stopid, platid, dep):
#        raise NotImplementedError()

##    def slice(self, stopid1, areaid1, platid1, stopid2, areaid2, platid2):
#    def slice(self, stopid1, platid1, stopid2, platid2):
#        raise NotImplementedError()


def daysin(month, year):
    days = 31

    if month in [4, 6, 9, 11]:
        days = 30
    elif month == 2:
        days = 28
        if ((not year % 4) and year % 100) or (not year % 400):
            days = 29

    return days


def daytypevalid(weekday, daytype):
    assert 0 <= weekday <= 6
    return bool(int(bin(daytype)[2:].zfill(7)[weekday]))


def dayvalid(r, day, daytype):
    return daytypevalid(datetime(*day).weekday(), daytype) and r.dayresvalid(*day)


def findstop(rec_stop, stopid):
    #todo: beim laden das mit duplicate weg und hier etwas machen
    return rec_stop.loc[stopid]['STOP_NAME'].strip()


def findplat(rec_stopping_points, timetable, stopid, plat):
    # verbessern
    for index, row in rec_stopping_points.query("VERSION == @timetable & STOP_NR == @stopid & STOPPING_POINT_NR == @plat").iterrows():
        return str(row["IFOPT"]).strip(), str(row["STOPPING_POINT_SHORTNAME"]).strip()


def findlinesymbol(rec_lin_ber, timetable, lineid):
    for index, row in rec_lin_ber.query("VERSION == @timetable & LINE_NR == @lineid").iterrows():
        return str(row["LINE_NAME"]).strip()


def getcourse(line, variant, rec_stop, lid_course, lid_travel_time_type, rec_stopping_points):
            zeit = timedelta()
            zeithin = timedelta()
            zeitwarte = timedelta()
            prevwarte = timedelta()
            stops = []

            for index, row in lid_course.query("VERSION == @line.timetable & LINE_NR == @line.lineid & STR_LINE_VAR == @variant").iterrows():
                stopid = int(row["STOP_NR"])
                platid = int(row["STOPPING_POINT_NR"])
                stopnr = int(row["LINE_CONSEC_NR"])
                # verschieben
                linedir = int(row["LINE_DIR_NR"])

                for index, row in lid_travel_time_type.query("VERSION == @line.timetable & LINE_NR == @line.lineid & STR_LINE_VAR == @variant & LINE_CONSEC_NR == @stopnr").iterrows():
                    zeithin = timedelta(seconds=int(row["TT_REL"]))
                    zeitwarte = timedelta(seconds=int(row["STOPPING_TIME"]))
                    break
                zeit += zeithin
                stopname = findstop(rec_stop, stopid)
                ifopt, platname = findplat(rec_stopping_points, line.timetable, stopid, platid)
                if zeitwarte != timedelta():
                    stops.append(CourseStop(stopnr = stopnr, ifopt = ifopt, stopid = stopid,
                                            stopname = stopname, platid = platid, platname = platname,
                                            time = zeit, dep = False, different_arrdep = True))
                    zeit += zeitwarte
                    stops.append(CourseStop(stopnr = stopnr, ifopt = ifopt, stopid = stopid,
                                            stopname = stopname, platid = platid, platname = platname,
                                            time = zeit, dep = True, different_arrdep = True))
                else:
                    stops.append(CourseStop(stopnr = stopnr, ifopt = ifopt, stopid = stopid,
                                            stopname = stopname, platid = platid, platname = platname,
                                            time = zeit, dep = False))
                    stops.append(CourseStop(stopnr = stopnr, ifopt = ifopt, stopid = stopid,
                                            stopname = stopname, platid = platid, platname = platname,
                                            time = zeit, dep = True))
            # stops[1:-1] damit der erste stop keine ankunft und der letzte keine abfahrt hat
            return Course(line, variant, linedir, stops[1:-1])


def getlinecourses(line, rec_lin_ber, rec_stop, lid_course, lid_travel_time_type, rec_stopping_points):
    for index, row in rec_lin_ber.query("VERSION == @line.timetable & LINE_NR == @line.lineid").iterrows():
        variant = int(row["STR_LINE_VAR"])
        line.courses[variant] = getcourse(line, variant, rec_stop, lid_course, \
                                          lid_travel_time_type, rec_stopping_points)


def getlinetrips(line, direction, day, fromtime, limit, restrictions, rec_trip, \
                 rec_stop, lid_course, lid_travel_time_type, rec_stopping_points):
    timeseconds = fromtime[0]*60*60 + fromtime[1]*60 + fromtime[2]
    querystring = "VERSION == @line.timetable & LINE_NR == @line.lineid & DEPARTURE_TIME >= @timeseconds"
    # hoffentlich gibt es keine echte LINE_DIR_NR=0
    if direction:
        querystring += " & LINE_DIR_NR == @direction"

    trips = []
    for index, row in rec_trip.query(querystring).iterrows():
        if not limit:
            break
        else:
            limit -= 1

        restriction = Restriction(*restrictions[row["RESTRICTION"].strip()])
        daytype = row["DAY_ATTRIBUTE_NR"]
        if dayvalid(restriction, day, daytype):
            trips.append(Trip(line.courses[row["STR_LINE_VAR"]], restriction, \
                              daytype, timedelta(seconds=row["DEPARTURE_TIME"])))

    return trips


def readrestrictions(service_restriction, timetable):
    restrictions = {}
    for index, row in service_restriction.query("VERSION == @timetable").iterrows():
        text = ""
        for n in range(1,6):
            rt = row["RESTRICT_TEXT"+str(n)]
            if isnull(rt):
                rt = ""
            else:
                rt = rt.strip()
            text += rt

        restrictions[row["RESTRICTION"].strip()] = (row["RESTRICTION_DAYS"].strip(), \
                                                    str(row["DATE_FROM"]), str(row["DATE_UNTIL"]), \
                                                    text)
    return restrictions


'''
r = Restriction(restrictionstr="3e7cb9e34f9f3e7c79f3e7cf1f3e7cf967cf9f3a3cf9f3e61c3e7cf973e7cf9e0e7cf9f31e7cf9f327cf9f3c39e3e5ce1f3e7cf9",
                datefrom="20170611",
                dateuntil="20180617",
                text="Mo-Fr ohne Feiertage")
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

