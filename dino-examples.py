#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from DINO import Version, Line, getlinetrips, readrestrictions, readallstops, printstops, csvstops
import pandas


if __name__ == "__main__":
    with open("./dino/set_version.din", 'r') as verfile:
        set_version = pandas.read_csv(verfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'VERSION_TEXT':str,'TIMETABLE_PERIOD':str,'TT_PERIOD_NAME':str,'PERIOD_DATE_FROM':str,'PERIOD_DATE_TO':str,'NET_ID':str,'PERIOD_PRIORITY':int}, index_col=0)
    with open("./dino/rec_trip.din", 'r') as tripfile:
        rec_trip = pandas.read_csv(tripfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'DEPARTURE_TIME':int,'DEP_STOP_NR':int,'ARR_STOP_NR':int,'DAY_ATTRIBUTE_NR':int,'RESTRICTION':str,'NOTICE':str,'NOTICE_2':str,'NOTICE_3':str,'NOTICE_4':str,'NOTICE_5':str,'TIMING_GROUP_NR':int})
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
        lid_travel_time_type = pandas.read_csv(timefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_CONSEC_NR':int,'TIMING_GROUP_NR':int})
    with open("./dino/rec_stopping_points.din", 'r') as platfile:
        rec_stopping_points = pandas.read_csv(platfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'STOP_AREA_NR':int,'STOPPING_POINT_NR':int,'STOPPING_POINT_SHORTNAME':str,'STOPPING_POINT_POS_X':str,'STOPPING_POINT_POS_Y':str,'IFOPT':str})
    with open("./dino/rec_lin_ber.din", 'r') as linefile:
        rec_lin_ber = pandas.read_csv(linefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_NAME':str}, index_col=3)

    versionid = 12  # HST (DINO_VRR_20180209)

    version = Version(set_version.loc[versionid])
    stops = readallstops(version, rec_stop, rec_stop_area, rec_stopping_points)

    # list of stops/areas/positions
    #'''
    print(printstops(stops))
    csvstops(stops, "csv/stops.csv")
    #'''

    # line(s) to csv
    #'''
    inputlines = input("Linien-IDs kommagetrennt (\"K\" für Komplettexport): ")
    if inputlines == "K":
        lines = set(rec_lin_ber.query("VERSION == @version.id").index.values)
    else:
        lines = list(map(int, inputlines.split(",")))
    for lineid in lines:
        line = Line(version, lineid, rec_lin_ber, lid_course, lid_travel_time_type, stops)
        line.ascsv("csv")
    #'''

    # course texts for line
    #'''
    lineid = 50514
    line = Line(version, lineid, rec_lin_ber, lid_course, lid_travel_time_type, stops)
    print("\n".join([course.stoptext() for course in [line.courses[x] for x in line.courses]]))
    #'''

    # trip texts for line
    #'''
    lineid = 50514
    direction = 0
    testdate = (2018,2,23)
    ph = False
    testtime = (18,50,0)
    limit = -1

    line = Line(version, lineid, rec_lin_ber, lid_course, lid_travel_time_type, stops)
    restrictions = readrestrictions(service_restriction, version)
    print("\n".join([trip.stoptext() for trip in getlinetrips(line, direction, testdate, ph, testtime, limit,
                                                             restrictions, rec_trip, lid_course,
                                                             lid_travel_time_type, stops)]))
    #'''

