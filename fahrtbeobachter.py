#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from DINO import Version, Line, getlinetrips, readrestrictions, readallstops
from pandas import read_csv
from datetime import date, datetime, timedelta
from csv import writer
from sys import stdout


class RTTripStop():
    def __init__(self, tripstop):
        self.tripstop = tripstop
        self.rtarrtime = None
        self.arrdelaystr = None
        self.rtdeptime = None
        self.depdelaystr = None
        self.status = None
        self.comment = None

    def __str__(self):
        return "RTTripStop " + str(self.tripstop.coursestop.stopnr) + " " \
               + str(self.tripstop.coursestop.stoppos.area.stop.stopid) + ":" \
               + str(self.tripstop.coursestop.stoppos.posid) + " " + nonestr(self.status) \
               + " arr " + nonestr(self.rtarrtime) + " (" + nonestr(self.arrdelaystr) + ")" \
               + " dep " + nonestr(self.rtdeptime) + " (" + nonestr(self.depdelaystr) + ")" \
               + ((" comment \"" + self.comment + "\"") if self.comment else "")


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
        set_version = read_csv(verfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'VERSION_TEXT':str,'TIMETABLE_PERIOD':str,'TT_PERIOD_NAME':str,'PERIOD_DATE_FROM':str,'PERIOD_DATE_TO':str,'NET_ID':str,'PERIOD_PRIORITY':int}, index_col=0)
    with open("./dino/rec_trip.din", 'r') as tripfile:
        rec_trip = read_csv(tripfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'DEPARTURE_TIME':int,'DEP_STOP_NR':int,'ARR_STOP_NR':int,'DAY_ATTRIBUTE_NR':int,'RESTRICTION':str,'NOTICE':str,'NOTICE_2':str,'NOTICE_3':str,'NOTICE_4':str,'NOTICE_5':str,'TIMING_GROUP_NR':int})
    with open("./dino/service_restriction.din", 'r') as restrictionfile:
        service_restriction = read_csv(restrictionfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'RESTRICTION':str,'RESTRICT_TEXT1':str,'RESTRICT_TEXT2':str,'RESTRICT_TEXT3':str,'RESTRICT_TEXT4':str,'RESTRICT_TEXT5':str,'RESTRICTION_DAYS':str})
    with open("./dino/calendar_of_the_company.din", 'r') as calendarfile:
        calendar_otc = read_csv(calendarfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'DAY':str,'DAY_TEXT':str,'DAY_TYPE_NR':int})
    with open("./dino/day_type_2_day_attribute.din", 'r') as dt2dafile:
        day_type_2_day_attribute = read_csv(dt2dafile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'DAY_TYPE_NR':int,'DAY_ATTRIBUTE_NR':int})
    with open("./dino/rec_stop.din", 'r') as stopfile:
        rec_stop = read_csv(stopfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'STOP_TYPE_NR':int,'STOP_NAME':str,'STOP_SHORTNAME':str,'STOP_POS_X':str,'STOP_POS_Y':str,'PLACE':str,'OCC':int,'IFOPT':str}, index_col=1)
    with open("./dino/rec_stop_area.din", 'r') as areafile:
        rec_stop_area = read_csv(areafile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'STOP_AREA_NR':int,'STOP_AREA_NAME':str,'IFOPT':str})
    #with open("./dino/rec_additional_stopname.din", 'r') as addnamefile:
    #     rec_additional_stopname = read_csv(addnamefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int, 'STOP_TYPE_NR':int,'ADD_STOP_NAME_WITH_LOCALITY':str,'ADD_STOP_NAME_WITHOUT_LOCALITY':str})
    with open("./dino/lid_course.din", 'r') as coursefile:
        lid_course = read_csv(coursefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_CONSEC_NR':int,'STOPPING_POINT_NR':int,'LENGTH':int})
    with open("./dino/lid_travel_time_type.din", 'r') as timefile:
        lid_travel_time_type = read_csv(timefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_CONSEC_NR':int,'TIMING_GROUP_NR':int})
    with open("./dino/rec_stopping_points.din", 'r') as platfile:
        rec_stopping_points = read_csv(platfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'STOP_AREA_NR':int,'STOPPING_POINT_NR':int,'STOPPING_POINT_SHORTNAME':str,'STOPPING_POINT_POS_X':str,'STOPPING_POINT_POS_Y':str,'IFOPT':str})
    with open("./dino/rec_lin_ber.din", 'r') as linefile:
        rec_lin_ber = read_csv(linefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_NAME':str}, index_col=3)

    versionid = 13

    version = Version(set_version.loc[versionid])
    stops = readallstops(version, rec_stop, rec_stop_area, rec_stopping_points)
    restrictions = readrestrictions(service_restriction, version)

    today = date.today().timetuple()[:3]

    line = Line(version, int(input("Linien-ID: ")), rec_lin_ber, lid_course, lid_travel_time_type, stops)
    print("geladen: ", line)

    # temporär, später via Abfahrtsmonitor oderso laden
    trips = sorted(getlinetrips(line, 0, today, (0, 0, 0), -1, restrictions, rec_trip, lid_course, lid_travel_time_type, stops, calendar_otc, day_type_2_day_attribute), key=lambda x: x.starttime)
    for ti, trip in enumerate(trips):
        print(str(ti)+":", trip)

    trip = trips[int(input("Fahrtauswahl: "))]
    print("Ausgewählte Fahrt:", trip.stoptext())

    rtstops = []
    for tripstop in trip.stops:
        rtstops.append(RTTripStop(tripstop))

    save = True
    inp = "@1"
    currentstopnr = 0
    message = ""
    newstop = False
    while inp != "e":
        message = ""
        now = datetime.now()
        currenttime = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
        currentstop = rtstops[currentstopnr - 1]
        if inp == "a":
            currentstop.status = "angekommen"
            currentstop.rtarrtime = currenttime
            currentstop.arrdelaystr = delaystr(currentstop.tripstop.arrtime, currentstop.rtarrtime)
            newstop = False
        elif inp == "d":
            currentstop.status = "abgefahren"
            currentstop.rtdeptime = currenttime
            currentstop.depdelaystr = delaystr(currentstop.tripstop.deptime, currentstop.rtdeptime)
            newstop = True
        elif inp == "p":
            currentstop.status = "vorbeigefahren"
            currentstop.rtarrtime = currenttime
            currentstop.rtdeptime = currenttime
            currentstop.arrdelaystr = delaystr(currentstop.tripstop.arrtime, currentstop.rtarrtime)
            currentstop.depdelaystr = delaystr(currentstop.tripstop.deptime, currentstop.rtdeptime)
            newstop = True
        elif inp == "r":
            currentstop.status = None
            currentstop.rtarrtime = None
            currentstop.rtdeptime = None
            currentstop.arrdelaystr = None
            currentstop.depdelaystr = None
            currentstop.comment = None
            newstop = False
        elif inp == "k":
            currentstop.comment = input("Kommentar: ")
            newstop = False
        elif inp.startswith("@"):
            afterat = inp[1:]
            if afterat == "+":
                if currentstopnr < len(rtstops):
                    currentstopnr += 1
                else:
                    message = "Bereits am Fahrtende"
            elif afterat == "-":
                if currentstopnr > 1:
                    currentstopnr -= 1
                else:
                    message = "Bereits am Fahrtanfang"
            else:
                try:
                    if (0 < int(afterat) <= len(rtstops)):
                        currentstopnr = int(afterat)
                    else:
                        message = f"Ungültige Haltestellennummer {afterat}"
                except:
                    message = "@-Eingabe nicht verstanden. Erwartet wird \"@+\", \"@-\", @{zahl} (z.B. \"@5\")"
            newstop = False
        elif inp == "qQq":
            save = False
            break
        else:
            message = "Unbekannte Eingabe"
            newstop = False
        if newstop and currentstopnr < len(rtstops):
            currentstopnr += 1
        for rtts in rtstops:
            stopnr = rtts.tripstop.coursestop.stopnr
            stopname = rtts.tripstop.coursestop.stoppos.area.stop.name

            arrow = ("->" if currentstopnr == stopnr else "  ")
            print(arrow + "{:>2}".format(str(stopnr)) + "  " + "{:32}".format(stopname)
                  + "arr " + str(rtts.tripstop.arrtime) + " rtarr " + nonestr(rtts.rtarrtime)
                  + " (" + nonestr(rtts.arrdelaystr) + ")"
                  + (("  Kommentar: " + rtts.comment) if rtts.comment else ""))
            print(arrow + "  " + "  " + "{:32}".format("Status: "+nonestr(rtts.status))
                  + "dep " + str(rtts.tripstop.deptime) + " rtdep " + nonestr(rtts.rtdeptime)
                  + " (" + nonestr(rtts.depdelaystr) + ")")
        print(message)
        print("Eingaben:\na Ankunft\nd Abfahrt\np Vorbeifahrt\nk Kommentar\nr Reset\n@nr, @+, @- Halt ändern\ne Ende\nqQq Beenden ohne Speichern")
        inp = input("Eingabe: ")

    print("\nBeobachtung beendet.")
    filename = "./csv/" + "fb_" + line.linesymbol + "_" + str(trip.course.variant) + "_" \
               + trip.course.stops[0].stoppos.area.stop.shortname + "-" \
               + trip.course.stops[-1].stoppos.area.stop.shortname + "_" \
               + str(today[0]) + "-" + str(today[1]).zfill(2) + "-" + str(today[2]).zfill(2) \
               + "_" + str(trip.starttime) + ".csv"

    csvrows = [("stopnr", "stopname", "ifopt",
                "status", "planarr", "rtarr", "arrdelay",
                "plandep", "rtdep", "depdelay", "comment")]
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
                        rtts.tripstop.deptime, rtts.rtdeptime, rtts.depdelaystr, rtts.comment))

    print("Maximale Abfahrtsverfrühung:", maxfruehstr)
    print("Maximale Abfahrtsverspätung:", maxspaetstr)
    print("")

    if save:
        print("Dateiname:", filename)
        with open(filename, 'w') as tf:
            writer(tf, delimiter=';', lineterminator='\n').writerows(csvrows)
    writer(stdout, delimiter=';').writerows(csvrows)

    print("\nSchreiben:\n")
    print("Hallo,\n\nich berichte über eine Fahrt der Linie " + line.linesymbol + ", Abfahrt um "
          + str(trip.starttime) + " Uhr von " + trip.course.stopfrom + " in Richtung "
          + trip.course.stopto + ".")
    print("Die größte Abfahrtsverspätung beträgt " + maxspaetstr +
          ", die verfrühteste Abfahrt war " + maxfruehstr + ".")
    print("\nHier ist eine Liste von den befahrenen Haltestellen (Daten sind nicht unbedingt komplett erfasst):")
    print("(\"Nr. Abfahrtsverspätung Status bei Haltestellenname (ggf. Kommentar)\")")
    for rtts in rtstops:
        if rtts.status or rtts.comment:
            stoppos = rtts.tripstop.coursestop.stoppos
            print(str(rtts.tripstop.coursestop.stopnr).zfill(2) + ". " + nonestr(rtts.depdelaystr)
                  + " " + nonestr(rtts.status) + " bei " + stoppos.area.stop.name
                  + ((" (" + rtts.comment + ")") if rtts.comment else ""))
    print("\nOriginaldatenquelle: Verkehrsverbund Rhein-Ruhr/OpenVRR")
    print(f"Fahrplandaten: {version.periodname} ({version.text}) gültig von "
          + f"{version.validfromstr} bis {version.validtostr}")
    print("\nViele Grüße\n")

