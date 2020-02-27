#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from DINO import Restriction, Version, Line, dayvalid, getlinetrips, readrestrictions, readallstops, printstops, csvstops
import pandas
from datetime import timedelta
dwt = __import__("dino-wikitable")


if __name__ == "__main__":
    with open("./dino/set_version.din", 'r') as verfile:
        set_version = pandas.read_csv(verfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'VERSION_TEXT':str,'TIMETABLE_PERIOD':str,'TT_PERIOD_NAME':str,'PERIOD_DATE_FROM':str,'PERIOD_DATE_TO':str,'NET_ID':str,'PERIOD_PRIORITY':int}, index_col=0)
    with open("./dino/rec_trip.din", 'r') as tripfile:
        rec_trip = pandas.read_csv(tripfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'DEPARTURE_TIME':int,'DEP_STOP_NR':int,'ARR_STOP_NR':int,'DAY_ATTRIBUTE_NR':int,'RESTRICTION':str,'NOTICE':str,'NOTICE_2':str,'NOTICE_3':str,'NOTICE_4':str,'NOTICE_5':str,'TIMING_GROUP_NR':int})
    with open("./dino/service_restriction.din", 'r') as restrictionfile:
        service_restriction = pandas.read_csv(restrictionfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'RESTRICTION':str,'RESTRICT_TEXT1':str,'RESTRICT_TEXT2':str,'RESTRICT_TEXT3':str,'RESTRICT_TEXT4':str,'RESTRICT_TEXT5':str,'RESTRICTION_DAYS':str})
    with open("./dino/calendar_of_the_company.din", 'r') as calendarfile:
        calendar_otc = pandas.read_csv(calendarfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'DAY':str,'DAY_TEXT':str,'DAY_TYPE_NR':int})
    with open("./dino/day_type_2_day_attribute.din", 'r') as dt2dafile:
        day_type_2_day_attribute = pandas.read_csv(dt2dafile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'DAY_TYPE_NR':int,'DAY_ATTRIBUTE_NR':int})
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

    # dates = [(2018, 11, 5), (2018, 11, 6), (2018, 11, 7), (2018, 11, 8), (2018, 11, 9), (2018, 11, 10), (2018, 11, 11)]
    # dates = [(2018, 11, 8)]
    dates = [ #(2019, 3, 11), (2019, 3, 12), (2019, 3, 13), (2019, 3, 14), (2019, 3, 15), (2019, 3, 16), (2019, 3, 17),
             (2019, 5, 6), (2019, 5, 7), (2019, 5, 8), (2019, 5, 9), (2019, 5, 10), (2019, 5, 11), (2019, 5, 12)]
    versionidHST = 9
    versionHST = Version(set_version.loc[versionidHST])
    stopsHST = readallstops(versionHST, rec_stop, rec_stop_area, rec_stopping_points)
    restrictions = {versionidHST: readrestrictions(service_restriction, versionHST)}

    _lineids = (50510, 50521, 50542, 50903, 50931, 50932, 50047)
    lines = {_lineid: Line(versionHST, _lineid, rec_lin_ber, lid_course, lid_travel_time_type, stopsHST)
             for _lineid in _lineids}

    linedatekm = {}
    for lineid in lines:
        line = lines[lineid]
        linedatekm[lineid] = {}
        print("\n- "+str(line))
        for courseid in line.courses:
            course = line.courses[courseid]
            print("\n-- "+str(course))
            querystring = "VERSION == @line.version.id & LINE_NR == @line.lineid & STR_LINE_VAR == @courseid"
            trips = dict((date, list()) for date in dates)
            for index, row in rec_trip.query(querystring).iterrows():
                rrow = row["RESTRICTION"]
                restriction = Restriction(*restrictions[line.version.id][rrow.strip()]) if rrow else None
                day_attr = row["DAY_ATTRIBUTE_NR"]
                starttime = timedelta(seconds=row["DEPARTURE_TIME"])
                for cdate in dates:
                    # print(cdate)
                    if dayvalid(restriction, line.version, cdate, calendar_otc, day_attr, day_type_2_day_attribute):
                        # print(f"valid trip: da {day_attr}, st {starttime}")
                        trips[cdate].append(starttime)
                    else:
                        # print(f"invalid trip: da {day_attr}, st {starttime}")
                        pass
            for cdate in dates:
                dts = len(trips[cdate])
                print(f"--- {cdate[2]}.{cdate[1]}.: {dts} deps ({dwt.takt(sorted(trips[cdate]))})")
                print(f"--~> {round((dts*course.distance)/1000, 1)} km")
                if cdate not in linedatekm[lineid]:
                    linedatekm[lineid][cdate] = 0
                linedatekm[lineid][cdate] += (dts*course.distance)/1000
                
    for lineid, datedict in linedatekm.items():
        print(lines[lineid].linesymbol)
        for d, km in datedict.items():
            print(f"{d[0]}-{d[1]:02}-{d[2]:02}", round(km, 1))
