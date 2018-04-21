#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from DINO import Version, Line, getlinetrips, readrestrictions, readallstops
from datetime import date, datetime, timedelta
from csv import writer
from sys import stdout
import pandas


class RTTripStop():
    def __init__(self, tripstop):
        self.tripstop = tripstop
        self.rtarrtime = None
        self.arrdelaystr = None
        self.rtdeptime = None
        self.depdelaystr = None
        self.status = None

    def __str__(self):
        return "RTTripStop " + str(self.tripstop.coursestop.stopnr) + " " \
               + str(self.tripstop.coursestop.stoppos.area.stop.stopid) + ":" \
               + str(self.tripstop.coursestop.stoppos.posid) + " " + nonestr(self.status) \
               + " arr " + nonestr(self.rtarrtime) + " (" + nonestr(self.arrdelaystr) + ")" \
               + " dep " + nonestr(self.rtdeptime) + " (" + nonestr(self.depdelaystr) + ")"


def nonestr(instr, nonestr="-"):
    return (nonestr if instr is None else str(instr))


def hms(td):
    m, s = divmod(td.seconds, 60)
    h, m = divmod(m, 60)
    return (h, m, s)


def delaystr(plantime, realtime, nonestr="-"):
    if realtime is None:
        return nonestr

    if realtime >= plantime:
        diff = realtime - plantime
        sign = "+"
    else:
        diff = plantime - realtime
        sign = "-"

    h, m, s = hms(diff)
    return (sign + str(h*60 + m).zfill(2) + ":" + str(s).zfill(2))


if __name__ == "__main__":
    with open("./dino/set_version.din", 'r') as verfile:
        set_version = pandas.read_csv(verfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'VERSION_TEXT':str,'TIMETABLE_PERIOD':str,'TT_PERIOD_NAME':str,'PERIOD_DATE_FROM':str,'PERIOD_DATE_TO':str,'NET_ID':str,'PERIOD_PRIORITY':int}, index_col=0)
    with open("./dino/rec_trip.din", 'r') as tripfile:
        rec_trip = pandas.read_csv(tripfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'DEPARTURE_TIME':int,'DEP_STOP_NR':int,'ARR_STOP_NR':int,'DAY_ATTRIBUTE_NR':int,'RESTRICTION':str,'NOTICE':str,'NOTICE_2':str,'NOTICE_3':str,'NOTICE_4':str,'NOTICE_5':str,'TIMING_GROUP_NR':int})
    with open("./dino/service_restriction.din", 'r') as restrictionfile:
        service_restriction = pandas.read_csv(restrictionfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'RESTRICTION':str,'RESTRICT_TEXT1':str,'RESTRICT_TEXT2':str,'RESTRICT_TEXT3':str,'RESTRICT_TEXT4':str,'RESTRICT_TEXT5':str,'RESTRICTION_DAYS':str})
    with open("./dino/calendar_of_the_company.din", 'r') as calendarfile:
        calendar_otc = pandas.read_csv(calendarfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'DAY':str,'DAY_TEXT':str,'DAY_TYPE_NR':int})
    with open("./dino/rec_stop.din", 'r') as stopfile:
        rec_stop = pandas.read_csv(stopfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'STOP_TYPE_NR':int,'STOP_NAME':str,'STOP_SHORTNAME':str,'STOP_POS_X':str,'STOP_POS_Y':str,'PLACE':str,'OCC':int,'IFOPT':str}, index_col=1)
    with open("./dino/rec_stop_area.din", 'r') as areafile:
        rec_stop_area = pandas.read_csv(areafile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'STOP_AREA_NR':int,'STOP_AREA_NAME':str,'IFOPT':str})
    #with open("./dino/rec_additional_stopname.din", 'r') as addnamefile:
    #     rec_additional_stopname = pandas.read_csv(addnamefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int, 'STOP_TYPE_NR':int,'ADD_STOP_NAME_WITH_LOCALITY':str,'ADD_STOP_NAME_WITHOUT_LOCALITY':str})
    with open("./dino/lid_course.din", 'r') as coursefile:
        lid_course = pandas.read_csv(coursefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_CONSEC_NR':int,'STOPPING_POINT_NR':int,'LENGTH':int})
    with open("./dino/lid_travel_time_type.din", 'r') as timefile:
        lid_travel_time_type = pandas.read_csv(timefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_CONSEC_NR':int,'TIMING_GROUP_NR':int})
    with open("./dino/rec_stopping_points.din", 'r') as platfile:
        rec_stopping_points = pandas.read_csv(platfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'STOP_AREA_NR':int,'STOPPING_POINT_NR':int,'STOPPING_POINT_SHORTNAME':str,'STOPPING_POINT_POS_X':str,'STOPPING_POINT_POS_Y':str,'IFOPT':str})
    with open("./dino/rec_lin_ber.din", 'r') as linefile:
        rec_lin_ber = pandas.read_csv(linefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_NAME':str}, index_col=3)

    versionid = 12  # HST (DINO_VRR_20180209)
    # versionid = 14  # NIAG, 929: 25929 (DINO_VRR_20180209)

    version = Version(set_version.loc[versionid])
    stops = readallstops(version, rec_stop, rec_stop_area, rec_stopping_points)
    restrictions = readrestrictions(service_restriction, version)

    #today = date.today().timetuple()[:3]
    today = (2018, 4, 2)

    line = Line(version, int(input("Linien-ID: ")), rec_lin_ber, lid_course, lid_travel_time_type, stops)
    print("geladen: ", line)

    # temporär, später via Abfahrtsmonitor oderso laden
    trips = sorted(getlinetrips(line, 0, today, (0, 0, 0), -1, restrictions, rec_trip, lid_course, lid_travel_time_type, stops, calendar_otc), key=lambda x: x.starttime)
    for ti, trip in enumerate(trips):
        print(str(ti)+":", trip)

    trip = trips[int(input("Fahrtauswahl: "))]
    print("Ausgewählte Fahrt:", trip.stoptext())

    rtstops = []
    for tripstop in trip.stops:
        rtstops.append(RTTripStop(tripstop))

    inp = "@1"
    currentstopnr = 0
    newstop = False
    while inp != "e":
        now = datetime.now()
        currenttime = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
        if inp == "a":
            rtstops[currentstopnr - 1].status = "angekommen"
            rtstops[currentstopnr - 1].rtarrtime = currenttime
            rtstops[currentstopnr - 1].arrdelaystr = delaystr(rtstops[currentstopnr - 1].tripstop.arrtime, rtstops[currentstopnr - 1].rtarrtime)
            newstop = False
        elif inp == "d":
            rtstops[currentstopnr - 1].status = "abgefahren"
            rtstops[currentstopnr - 1].rtdeptime = currenttime
            rtstops[currentstopnr - 1].depdelaystr = delaystr(rtstops[currentstopnr - 1].tripstop.deptime, rtstops[currentstopnr - 1].rtdeptime)
            newstop = True
        elif inp == "p":
            rtstops[currentstopnr - 1].status = "vorbeigefahren"
            rtstops[currentstopnr - 1].rtarrtime = currenttime
            rtstops[currentstopnr - 1].rtdeptime = currenttime
            rtstops[currentstopnr - 1].arrdelaystr = delaystr(rtstops[currentstopnr - 1].tripstop.arrtime, rtstops[currentstopnr - 1].rtarrtime)
            rtstops[currentstopnr - 1].depdelaystr = delaystr(rtstops[currentstopnr - 1].tripstop.deptime, rtstops[currentstopnr - 1].rtdeptime)
            newstop = True
        elif inp == "r":
            rtstops[currentstopnr - 1].status = None
            rtstops[currentstopnr - 1].rtarrtime = None
            rtstops[currentstopnr - 1].rtdeptime = None
            rtstops[currentstopnr - 1].arrdelaystr = None
            rtstops[currentstopnr - 1].depdelaystr = None
        elif inp.startswith("@"):
            currentstopnr = int(inp[1:])
            newstop = False
        else:
            print("Unbekannte Eingabe")
            newstop = False
        if newstop and currentstopnr < len(rtstops):
            currentstopnr += 1
        for rtts in rtstops:
            stopnr = rtts.tripstop.coursestop.stopnr
            stopname = rtts.tripstop.coursestop.stoppos.area.stop.name

            arrow = ("->" if currentstopnr == stopnr else "  ")
            print(arrow + "{:>2}".format(str(stopnr)) + "  " + "{:32}".format(stopname)
                  + "arr " + str(rtts.tripstop.arrtime) + " rtarr " + nonestr(rtts.rtarrtime)
                  + " (" + nonestr(rtts.arrdelaystr) + ")")
            print(arrow + "  " + "  " + "{:32}".format("Status: "+nonestr(rtts.status))
                  + "dep " + str(rtts.tripstop.deptime) + " rtdep " + nonestr(rtts.rtdeptime)
                  + " (" + nonestr(rtts.depdelaystr) + ")")
        print("Eingaben:\na Ankunft\nd Abfahrt\np Vorbeifahrt\nr Reset\n@{nr} Haltenummer ändern\ne Ende")
        inp = input("Eingabe: ")

    print("\nBeobachtung beendet.")
    filename = "csv/" + "fb_" + line.linesymbol + "_" + str(trip.course.variant) + "_" \
               + trip.course.stops[0].stoppos.area.stop.shortname + "-" \
               + trip.course.stops[-1].stoppos.area.stop.shortname + "_" \
               + str(today[0]) + "-" + str(today[1]).zfill(2) + "-" + str(today[2]).zfill(2) \
               + "_" + str(trip.starttime) + ".csv"

    csvrows = [("stopnr", "stopname", "ifopt",
                "status", "planarr", "rtarr", "arrdelay",
                "plandep", "rtdep", "depdelay")]
    maxfrueh = timedelta(0)
    maxfruehstr = "-"
    maxspaet = timedelta(0)
    maxspaetstr = "-"
    for rtts in rtstops:
        stoppos = rtts.tripstop.coursestop.stoppos
        if rtts.rtdeptime is not None:
            diff = rtts.rtdeptime - rtts.tripstop.deptime
            if diff < maxfrueh:
                maxfrueh = diff
                maxfruehstr = rtts.depdelaystr
            elif diff > maxspaet:
                maxspaet = diff
                maxspaetstr = rtts.depdelaystr
        csvrows.append((rtts.tripstop.coursestop.stopnr, stoppos.area.stop.name, stoppos.ifopt,
                        rtts.status, rtts.tripstop.arrtime, rtts.rtarrtime, rtts.arrdelaystr,
                        rtts.tripstop.deptime, rtts.rtdeptime, rtts.depdelaystr))

    print("Maximale Abfahrtsverfrühung:", maxfruehstr)
    print("Maximale Abfahrtsverspätung:", maxspaetstr)

    print("\nDateiname:", filename)
    writer(stdout, delimiter=';').writerows(csvrows)
    with open(filename, 'w') as tf:
        writer(tf, delimiter=';', lineterminator='\n').writerows(csvrows)

    print("\nSchreiben:\n")
    print("Hallo,\n\nich berichte über eine Fahrt der Linie " + line.linesymbol + ", Abfahrt um "
          + str(trip.starttime) + " Uhr von " + trip.course.stopfrom + " in Richtung "
          + trip.course.stopto + ".")
    print("Die größte Abfahrtsverspätung beträgt " + maxspaetstr +
          ", die verfrühteste Abfahrt war " + maxfruehstr + ".")
    print("\nHier ist eine Liste von den befahrenen Haltestellen (Im Anhang ist eine genauere csv-Datei) (Daten sind nicht unbedingt komplett erfasst):")
    print("(\"Nr. Abfahrtsverspätung Status bei Haltestellenname\")")
    for rtts in rtstops:
        if rtts.status:
            stoppos = rtts.tripstop.coursestop.stoppos
            print(str(rtts.tripstop.coursestop.stopnr).zfill(2) + ". " + nonestr(rtts.depdelaystr)
                  + " " + nonestr(rtts.status) + " bei " + stoppos.area.stop.name)
    print("\nQuelle: Verkehrsverbund Rhein-Ruhr/OpenVRR")
    print(f"Fahrplandaten: {version.periodname} ({version.text}) gültig von "
          + f"{version.validfromstr} bis {version.validtostr}")
    print("\nViele Grüße\n")

