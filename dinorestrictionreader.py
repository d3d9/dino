#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from DINO import getlinetrips
import pandas
from datetime import timedelta


if __name__ == "__main__":
    with open("./dino/rec_trip.din", 'r') as tripfile:
        rec_trip = pandas.read_csv(tripfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'DEPARTURE_TIME':int,'DEP_STOP_NR':int,'ARR_STOP_NR':int,'DAY_ATTRIBUTE_NR':int,'RESTRICTION':str})
    with open("./dino/service_restriction.din", 'r') as restrictionfile:
        service_restriction = pandas.read_csv(restrictionfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'RESTRICTION':str,'RESTRICT_TEXT1':str,'RESTRICTION_DAYS':str})
    with open("./dino/rec_stop.din", 'r') as stopfile:
        rec_stop = pandas.read_csv(stopfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int}, index_col=1)
        rec_stop = rec_stop[~rec_stop.index.duplicated(keep='first')] # weg hiermit, betrieb bevorzugen
    with open("./dino/lid_course.din", 'r') as coursefile:
        lid_course = pandas.read_csv(coursefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_CONSEC_NR':int,'STOPPING_POINT_NR':int})
    with open("./dino/lid_travel_time_type.din", 'r') as timefile:
        lid_travel_time_type = pandas.read_csv(timefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_CONSEC_NR':int})
    with open("./dino/rec_stopping_points.din", 'r') as platfile:
        rec_stopping_points = pandas.read_csv(platfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'STOPPING_POINT_NR':int,'STOPPING_POINT_SHORTNAME':str,'IFOPT':str})

    betrieb = "12"
    line = "50543"
    direction = 0
    testdate = (2018,2,17)    
    testtime = (12,15,0)
    limit = -1

    print("\n".join([trip.triptext() for trip in getlinetrips(betrieb, line, direction, testdate, testtime, limit, \
    rec_trip, service_restriction, rec_stop, lid_course, lid_travel_time_type, rec_stopping_points)]))




