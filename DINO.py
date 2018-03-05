#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pandas import isnull
from datetime import datetime, timedelta
from copy import deepcopy
from csv import writer


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

        for o in range(0, len(self.restrictionstr), 8):
            bits = bin(int(self.restrictionstr[o:o+8], 16))[2:].zfill(32)[1:][::-1]

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

        for o in range(0, len(self.restrictionstr), 8):
            bits = bin(int(self.restrictionstr[o:o+8], 16))[2:].zfill(32)[1:][::-1]

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


class Stop():
    def __init__(self, stopid, timetable, stoptype, name, shortname, \
                 # addname, addname_noloc, \
                 pos_x, pos_y, placename, placeocc, farezones, ifopt):
        self.stopid = stopid
        self.timetable = timetable
        # REF_STOP_NR/NAME ?
        self.stoptype = stoptype
        self.name = name
        self.shortname = shortname
#        self.addname = addname # ADD_STOP_NAME_WITH_LOCALITY (rec_additional_stopname.din)
#        self.addname_noloc = addname_noloc # ADD_STOP_NAME_WITHOUT_LOCALITY (rec_additional_stopname.din)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.placename = placename
        self.placeocc = placeocc
        self.farezones = farezones
        self.ifopt = ifopt
        self.areas = {}

    def __str__(self):
        return "Stop " + str(self.stopid) + ", Name \"" + self.name + "\" (" + self.shortname \
               + "), IFOPT " + self.ifopt + ", Place \"" + self.placename \
               + "\" (" + str(self.placeocc) + "), fare zone" + ("s " if len(self.farezones) > 1 else " ") \
               + ",".join(str(fz) for fz in self.farezones) + ", Location " + self.pos_x + "," + self.pos_y

    def readareas(self, rec_stop_area):
        for index, row in rec_stop_area.query("VERSION == @self.timetable & STOP_NR == @self.stopid").iterrows():
            areaid = row["STOP_AREA_NR"]
            self.areas[areaid] = StopArea(self, areaid, nullorstrip(row["STOP_AREA_NAME"]), nullorstrip(row["IFOPT"]))


class StopArea():
    def __init__(self, stop, areaid, name, ifopt):
        self.stop = stop
        self.areaid = areaid
        self.name = name
        self.ifopt = ifopt
        self.positions = {}
        # self.pos_x, self.pos_y berechnen?

    def __str__(self):
        return "StopArea " + str(self.stop.stopid) + " " + str(self.areaid) + ", Name \"" + self.name \
               + "\", IFOPT " + (self.ifopt if self.ifopt else "-")

    def readpoints(self, rec_stopping_points):
        for index, row in rec_stopping_points.query("VERSION == @self.stop.timetable & STOP_NR == @self.stop.stopid & STOP_AREA_NR == @self.areaid").iterrows():
            posid = row["STOPPING_POINT_NR"]
            self.positions[posid] = \
                StopPosition(self, posid, nullorstrip(row["STOPPING_POINT_POS_X"]),
                             nullorstrip(row["STOPPING_POINT_POS_Y"]), nullorstrip(row["STOPPING_POINT_SHORTNAME"]), nullorstrip(row["IFOPT"]))


class StopPosition():
    def __init__(self, area, posid, pos_x, pos_y, name, ifopt):
        self.area = area
        self.posid = posid
        self.pos_x = pos_x
        self.pos_y = pos_y
        # STOP_RBL_NR ?
        # PURPOSE* ?
        self.name = name
        self.ifopt = ifopt

    def __str__(self):
        return "StopPosition " + str(self.area.stop.stopid) + " " + str(self.area.areaid) + " " \
                               + str(self.posid) + ", Name \"" + self.name + "\", IFOPT " \
                               + (self.ifopt if self.ifopt else "-") + ", Location " + self.pos_x + "," + self.pos_y


class CourseStop():
    def __init__(self, stopnr, stoppos, time, dep, different_arrdep=False):
        self.stopnr = stopnr
        self.stoppos = stoppos
        self.time = time
        self.dep = dep
        # geht das besser?
        self.different_arrdep = different_arrdep

    def __str__(self):
        return "CourseStop " + str(self.stopnr) + " " + ("dep" if self.dep else "arr") + " " \
                + str(self.time) + " " + str(self.stoppos.area.stop.stopid) + ":" + str(self.stoppos.posid) \
                + " (" + self.stoppos.area.stop.name + " " + self.stoppos.name + ", " + self.stoppos.ifopt + ")"


class Line():
    def __init__(self, timetable, lineid, rec_lin_ber, lid_course, lid_travel_time_type, stops):
        self.timetable = timetable
        self.lineid = str(lineid)
        self.linesymbol = findlinesymbol(rec_lin_ber, self.timetable, self.lineid)
        self.courses = {}
        getlinecourses(self, rec_lin_ber, lid_course, lid_travel_time_type, stops)

    def __str__(self):
        return "Line " + self.linesymbol + " (" + self.timetable + ":" + self.lineid + ")"

    def ascsv(self, directory):
        for courseid in self.courses:
            course = self.courses[courseid]
            try:
                try:
                    firststop = course.stopfrom.split(" ")[1].replace("/","").replace(".","")
                except:
                    firststop = course.stopfrom.replace("/","").replace(".","")
                try:
                    laststop = course.stopto.split(" ")[1].replace("/","").replace(".","")
                except:
                    laststop = course.stopto.replace("/","").replace(".","")

                filename = os.path.join(os.getcwd(), directory, "vrr_"+self.linesymbol+"_"+str(courseid)+"_"+firststop+"_"+laststop+".csv")
                with open(filename, 'w') as cf:
                    outwriter = writer(cf, delimiter=";", lineterminator='\n')
                    outwriter.writerows([(stop.stopnr, stop.stoppos.ifopt,
                                          stop.stoppos.area.stop.name,
                                          int(stop.time.total_seconds())) \
                                         for stop in singlestops(course)])
                print(f"route file \"{filename}\" written")
            except Exception as e:
                print(f"error writing route file: {e}")


class Course():
    # todo: sind die erwarteten angaben str, int, ?
    def __init__(self, line, variant, linedir, stops):
        self.line = line
        self.variant = variant
        self.linedir = linedir
        self.stops = stops
        self.time = stops[0].time
        self.endtime = stops[-1].time
        self.stopfrom = stops[0].stoppos.area.stop.name
        self.stopto = stops[-1].stoppos.area.stop.name
        self.duration = self.endtime - self.time
        # + daytype und restriction hier nochmal angeben

    def __str__(self):
        return "Course " + self.line.timetable + ":" + self.line.lineid + ":" + str(self.linedir) + ":" + str(self.variant) \
                + " from " + self.stopfrom + " to " + self.stopto \
                + " (" + str(self.duration) + ")"


class Trip():
    def __init__(self, course, restriction, daytype, starttime):
        self.course = course
        self.restriction = restriction
        # NOTICE ?
        self.daytype = daytype
        self.starttime = starttime
        self.time = course.time + self.starttime
        self.endtime = course.endtime + self.starttime
        self.stops = deepcopy(self.course.stops)

        for stop in self.stops:
            stop.time += starttime

    def __str__(self):
        # was ist für time besser? mit:
        # str(startzeit//3600).zfill(2)+":"+str((startzeit//60)%60).zfill(2)+":"+str(startzeit%60).zfill(2)
        # kriegt man als stunde auch 24, 25 usw., mit str(timedelta(..)) kriegt man "1 day, .."
        return "Trip " + self.course.line.timetable + ":" + self.course.line.lineid + ":" + str(self.course.linedir) + ":" + str(self.course.variant) \
                + " at " + str(self.time) + " from " + self.course.stopfrom + " to " + self.course.stopto \
                + " (" + str(self.course.duration) + "), restriction \"" + self.restriction.text \
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


# todo: nochmal woanders hin verschieben
def stoptext(thing):
    text = str(thing) + "\n"
    prevnr = 0
    for stop in thing.stops:
        if stop.different_arrdep or prevnr != stop.stopnr:
            text += str(stop.stopnr)+":\t"
            if stop.different_arrdep:
                text += "dep" if stop.dep else "arr"
            else:
                text += "   "
            text += " "+str(stop.time)+"\t"+stop.stoppos.area.stop.name+" "+stop.stoppos.name+"\n"
            prevnr = stop.stopnr

    return text


def singlestops(thing):
    stops = []
    for si, stop in enumerate(thing.stops):
        if (not si) or (si == (len(thing.stops) - 1)) or stop.dep:
            stops.append(stop)
    return stops


def nullorstrip(inp):
    return ("" if isnull(inp) else inp.strip())


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


def findlinesymbol(rec_lin_ber, timetable, lineid):
    for index, row in rec_lin_ber.query("VERSION == @timetable & LINE_NR == @lineid").iterrows():
        return str(row["LINE_NAME"]).strip()


def getcourse(line, variant, lid_course, lid_travel_time_type, stops):
    zeit = timedelta()
    zeithin = timedelta()
    zeitwarte = timedelta()
    prevwarte = timedelta()
    coursestops = []

    for index, row in lid_course.query("VERSION == @line.timetable & LINE_NR == @line.lineid & STR_LINE_VAR == @variant").iterrows():
        stopid = int(row["STOP_NR"])
        posid = int(row["STOPPING_POINT_NR"])
        stopnr = int(row["LINE_CONSEC_NR"])
        # verschieben
        linedir = int(row["LINE_DIR_NR"])

        for index, row in lid_travel_time_type.query("VERSION == @line.timetable & LINE_NR == @line.lineid & STR_LINE_VAR == @variant & LINE_CONSEC_NR == @stopnr").iterrows():
            zeithin = timedelta(seconds=int(row["TT_REL"]))
            zeitwarte = timedelta(seconds=int(row["STOPPING_TIME"]))
            break
        zeit += zeithin

        stoppos = None
        for areaid in stops[stopid].areas:
            if posid in stops[stopid].areas[areaid].positions:
                stoppos = stops[stopid].areas[areaid].positions[posid]
                break
        if zeitwarte != timedelta():
            coursestops.append(CourseStop(stopnr, stoppos, zeit,
                                          dep=False, different_arrdep=True))
            zeit += zeitwarte
            coursestops.append(CourseStop(stopnr, stoppos, zeit,
                                          dep=True, different_arrdep=True))
        else:
            coursestops.append(CourseStop(stopnr, stoppos, zeit, dep=False))
            coursestops.append(CourseStop(stopnr, stoppos, zeit, dep=True))
    # coursestops[1:-1] damit der erste stop keine ankunft und der letzte keine abfahrt hat
    return Course(line, variant, linedir, coursestops[1:-1])


def getlinecourses(line, rec_lin_ber, lid_course, lid_travel_time_type, stops):
    for index, row in rec_lin_ber.query("VERSION == @line.timetable & LINE_NR == @line.lineid").iterrows():
        variant = int(row["STR_LINE_VAR"])
        line.courses[variant] = getcourse(line, variant, lid_course, lid_travel_time_type, stops)


def getlinetrips(line, direction, day, fromtime, limit, restrictions, rec_trip,
                 lid_course, lid_travel_time_type, stops):
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
            trips.append(Trip(line.courses[row["STR_LINE_VAR"]], restriction,
                              daytype, timedelta(seconds=row["DEPARTURE_TIME"])))

    return trips


def readrestrictions(service_restriction, timetable):
    restrictions = {}
    for index, row in service_restriction.query("VERSION == @timetable").iterrows():
        text = ""
        for n in range(1, 6):
            rt = row["RESTRICT_TEXT"+str(n)]
            rt = nullorstrip(rt)
            text += rt

        restrictions[row["RESTRICTION"].strip()] = (row["RESTRICTION_DAYS"].strip(), str(row["DATE_FROM"]),
                                                    str(row["DATE_UNTIL"]), text)
    return restrictions


def readallstops(timetable, rec_stop, rec_stop_area, rec_stopping_points):
    stops = {}
    for index, row in rec_stop.query("VERSION == @timetable").iterrows():
        farezones = [int(row["FARE_ZONE"])]
        for x in range(2, 7):
            farezone = int(row["FARE_ZONE"+str(x)])
            if farezone != -1:
                farezones.append(farezone)
        stops[index] = Stop(index, timetable, row["STOP_TYPE_NR"], row["STOP_NAME"].strip(), row["STOP_SHORTNAME"].strip(), \
                            # addnamerow["ADD_STOP_NAME_WITH_LOCALITY"].strip(), addnamerow["ADD_STOP_NAME_WITHOUT_LOCALITY"].strip(), \
                            row["STOP_POS_X"].strip(), row["STOP_POS_Y"].strip(), row["PLACE"].strip(), \
                            row["OCC"], tuple(farezones), row["IFOPT"].strip())
        stops[index].readareas(rec_stop_area)
        for areaid in stops[index].areas:
            stops[index].areas[areaid].readpoints(rec_stopping_points)
    return stops


def printstops(stopdict):
    stopc = 0
    areac = 0
    pointc = 0
    text = ""
    for stop in stopdict:
        stopc += 1
        text += str(stopdict[stop]) + "\n"
        for area in stopdict[stop].areas:
            areac += 1
            text += "-"+str(stopdict[stop].areas[area]) + "\n"
            for pos in stopdict[stop].areas[area].positions:
                pointc += 1
                text += "--"+str(stopdict[stop].areas[area].positions[pos]) + "\n"
        text += "\n"

    text += f"Stops: {stopc}\nAreas: {areac}\nPoints: {pointc}"
    return text


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

