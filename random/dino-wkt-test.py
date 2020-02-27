#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from DINO import Version, Line, getlinetrips, readrestrictions, readallstops, printstops, csvstops
from csv import writer
from datetime import datetime
import pandas


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

    # !!!!!
    versionid = 22

    version = Version(set_version.loc[versionid])
    stops = readallstops(version, rec_stop, rec_stop_area, rec_stopping_points)
    restrictions = readrestrictions(service_restriction, version)

    # !!!!!

    lineids_hstne10 = {50901, 50902, 50903, 50904, 50905, 50906, 50907, 50908,
                       50910, 50911, 50912, 50919, 50921, 50922, 50931, 50932}
    lineids_hst544n = {50544}
                       
    lineids_bvr591n = {88591, 88909}
    
    lineids_ver511n = {45511}
                     
    lineids_hstne11 = {50901, 50902, 50903, 50904, 50905, 50906, 50907,
                       50919, 50922, 50931, 50932}

    lineids_hst = set(rec_lin_ber.query("VERSION == @version.id").index.values)

    # !!!!!
    lineids = lineids_ver511n

    lines = {lineid: Line(version, lineid, rec_lin_ber, lid_course, lid_travel_time_type, stops)
                     for lineid in lineids}
    
    direction = 0
    
    # !!!!!
    # testdate = (2019,6,5)
    testdate = (2019,6,12)
    
    testdatetime = datetime(*testdate)
    ph = False  # ...
    testtime = (0,0,0)
    limit = -1
    
    m = 0.000001
    
    trips = {lineid: getlinetrips(line, direction, testdate, testtime, limit,
                                  restrictions, rec_trip, lid_course,
                                  lid_travel_time_type, stops, calendar_otc,
                                  day_type_2_day_attribute) for lineid, line in lines.items()}
    
    # print("\n\n".join((str(lines[lineid])+"\n"+("\n".join(trip.stoptext() for trip in trips[lineid]))) for lineid in lines))
    
    with open("./csv/testwkt.csv", 'w') as cf:
        w = writer(cf, delimiter=";", lineterminator='\n')
        w.writerow(["lineid", "linedir", "variant", "timinggroup", "day_attr", "restrictionstr", "linesymbol", "from", "to", "startt", "endt", "ids", "wkt"])
        for trip in (trip for triplist in trips.values() for trip in triplist):
            _row = list(map(str, [trip.course.line.lineid, trip.course.linedir, trip.course.variant,
                                  trip.timing_group_nr, trip.day_attr, (trip.restriction.restrictionstr if trip.restriction else ""),  # tmp..
                                  trip.course.line.linesymbol, trip.course.stopfrom, trip.course.stopto,
                                  int((testdatetime + trip.starttime).timestamp()),
                                  int((testdatetime + trip.endtime).timestamp())]))
            _row.append("|".join(_row[:6]))
            _wkt = "LINESTRING M ("
            _xym = ""
            for tripstop in trip.stops:
                _s = tripstop.coursestop.stoppos
                if _s.pos_x is None or _s.pos_y is None: continue
                _xym += f"{round(float(_s.pos_x)*m, 6)} {round(float(_s.pos_y)*m, 6)} {int((testdatetime + (tripstop.deptime or tripstop.arrtime)).timestamp())}, "
            _wkt += _xym[:-2] + ")"
            _row.append(_wkt)
            w.writerow(_row)
            '''
            for tripstop in trip.stops:
                _c = tripstop.coursestop
                writer.writerow(_row + [_c.stopnr,
                                        _c.stoppos.area.stop.name,
                                        _c.stoppos.ifopt,
                                        ...,
                                        testdatetime + tripstop.arrtime,
                                        testdatetime + tripstop.deptime])
            '''
    
    #'''

