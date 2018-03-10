#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from DINO import Version, Line, getlinetrips, readrestrictions, stoptext, readallstops, printstops, csvstops
import pandas
from datetime import timedelta


def departures():
    raise NotImplementedError


if __name__ == "__main__":
    with open("./dino/set_version.din", 'r') as verfile:
        set_version = pandas.read_csv(verfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'VERSION_TEXT':str,'TIMETABLE_PERIOD':str,'TT_PERIOD_NAME':str,'PERIOD_DATE_FROM':str,'PERIOD_DATE_TO':str,'NET_ID':str,'PERIOD_PRIORITY':int}, index_col=0)
    with open("./dino/rec_trip.din", 'r') as tripfile:
        rec_trip = pandas.read_csv(tripfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'DEPARTURE_TIME':int,'DEP_STOP_NR':int,'ARR_STOP_NR':int,'DAY_ATTRIBUTE_NR':int,'RESTRICTION':str,'NOTICE':str,'NOTICE_2':str,'NOTICE_3':str,'NOTICE_4':str,'NOTICE_5':str})
    with open("./dino/service_restriction.din", 'r') as restrictionfile:
        service_restriction = pandas.read_csv(restrictionfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'RESTRICTION':str,'RESTRICT_TEXT1':str,'RESTRICT_TEXT2':str,'RESTRICT_TEXT3':str,'RESTRICT_TEXT4':str,'RESTRICT_TEXT5':str,'RESTRICTION_DAYS':str})
    with open("./dino/rec_stop.din", 'r') as stopfile:
        rec_stop = pandas.read_csv(stopfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'STOP_TYPE_NR':int,'STOP_NAME':str,'STOP_SHORTNAME':str,'STOP_POS_X':str,'STOP_POS_Y':str,'PLACE':str,'OCC':int,'IFOPT':str}, index_col=1)
    with open("./dino/rec_stop_area.din", 'r') as areafile:
        rec_stop_area = pandas.read_csv(areafile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'STOP_AREA_NR':int,'STOP_AREA_NAME':str,'IFOPT':str})
    #with open("./dino/rec_additional_stopname.din", 'r') as addnamefile:
    #     rec_additional_stopname = pandas.read_csv(addnamefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int, 'STOP_TYPE_NR':int,'ADD_STOP_NAME_WITH_LOCALITY':str,'ADD_STOP_NAME_WITHOUT_LOCALITY':str})
    with open("./dino/lid_course.din", 'r') as coursefile:
        lid_course = pandas.read_csv(coursefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_CONSEC_NR':int,'STOPPING_POINT_NR':int,'LENGTH':int})
    with open("./dino/lid_travel_time_type.din", 'r') as timefile:
        lid_travel_time_type = pandas.read_csv(timefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_CONSEC_NR':int})
    with open("./dino/rec_stopping_points.din", 'r') as platfile:
        rec_stopping_points = pandas.read_csv(platfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'STOP_AREA_NR':int,'STOPPING_POINT_NR':int,'STOPPING_POINT_SHORTNAME':str,'STOPPING_POINT_POS_X':str,'STOPPING_POINT_POS_Y':str,'IFOPT':str})
    with open("./dino/rec_lin_ber.din", 'r') as linefile:
        rec_lin_ber = pandas.read_csv(linefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_NAME':str}, index_col=3)

    versionid = 12  # HST (DINO_VRR_20180209)
    teststopid = 2020
    # plat
    testdate = (2018, 3, 10)
    testtime = (16, 20, 0)
    # limit = -1

    version = Version(set_version.loc[versionid])
    stops = readallstops(version, rec_stop, rec_stop_area, rec_stopping_points)
    restrictions = readrestrictions(service_restriction, version)

    # lineids = set(map(str, rec_lin_ber.query("VERSION == @version.id").index.values))
    servinglines = {}
    for index, row in lid_course.query("VERSION == @version.id & STOP_NR == @teststopid").iterrows():
        lineid = str(int(row["LINE_NR"]))
        if lineid not in servinglines:
            servinglines[lineid] = Line(version, lineid, rec_lin_ber, lid_course, lid_travel_time_type, stops)

    departures = []
    for lineid in servinglines:
        line = servinglines[lineid]
        print(line)
        for trip in getlinetrips(line, 0, testdate, (0, 0, 0), -1, restrictions, rec_trip, lid_course, lid_travel_time_type, stops):
            for stop in trip.stops:
                if stop.stopnr != len(trip.stops) \
                   and stop.stoppos.area.stop.stopid == teststopid \
                   and stop.deptime >= timedelta(hours=testtime[0], minutes=testtime[1], seconds=testtime[2]):
                    departures.append((stop, trip))

    departures.sort(key=lambda dep: dep[0].deptime)
    for dep in departures:
        print(dep[0].deptime, dep[0].stoppos.name, dep[1].course.line.linesymbol, dep[1].course.stopto)


