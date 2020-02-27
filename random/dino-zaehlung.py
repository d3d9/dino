#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

from DINO import Version, Line, getlinetrips, readrestrictions, readallstops, printstops, csvstops
import pandas
from csv import writer
from tqdm import tqdm
from collections import defaultdict
from datetime import timedelta


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

    versionid, testdate = 16, (2019, 12, 16)
    # versionid, testdate = 80, (2019, 12, 9)
    # todo: mehrere versions undso
    # todo: ganze woche/sa/so
    # todo: ausgabe als csv usw. inkl. ifopt, koordinaten, ...

    version = Version(set_version.loc[versionid])
    stops = readallstops(version, rec_stop, rec_stop_area, rec_stopping_points)
    restrictions = readrestrictions(service_restriction, version)

    lineids = set(map(str, rec_lin_ber.query("VERSION == @version.id").index.values))
    lines = {lineid: Line(version, lineid, rec_lin_ber, lid_course, lid_travel_time_type, stops) for lineid in lineids}

    pairs = defaultdict(int)
    for line in tqdm(lines.values()):
        print(line)
        for trip in getlinetrips(line, 0, testdate, (0, 0, 0), -1, restrictions, rec_trip, lid_course, lid_travel_time_type, stops, calendar_otc, day_type_2_day_attribute):
            for _stopi, stop in enumerate(trip.stops):
                if stop.coursestop.stopnr != len(trip.stops):
                    pairs[(stop.coursestop.stoppos.area.stop, trip.stops[_stopi+1].coursestop.stoppos.area.stop)] += 1
    
    print(f"\n{'='*20}\nAbfahrten von einer Haltestelle zur anderen\n{'='*20}\n")
    for (sf, st), dc in sorted(pairs.items(), key=lambda i: -i[1]):
        print(f"{sf.name}\t\t->\t\t{st.name}:\t{dc}")
    
    pairsbidi = {}
    for (sf, st), dc in pairs.items():
        if (sf, st) not in pairsbidi and (st, sf) not in pairsbidi:
            pairsbidi[(sf, st)] = dc
            if (st, sf) in pairs and (sf, st) != (st, sf):
                pairsbidi[(sf, st)] += pairs[(st, sf)]

    print(f"\n{'='*20}\nAbfahrten zwischen zwei Haltestellen\n{'='*20}\n")
    for (sf, st), dc in sorted(pairsbidi.items(), key=lambda i: -i[1]):
        print(f"{sf.name}\t\t<->\t\t{st.name}:\t{dc}")
    
    print(f"\n{'='*20}\nAbfahrten an einer Haltestelle\n{'='*20}\n")
    clines = []
    stopdeps = {stop: sum(dc for ((sf, st), dc) in pairs.items() if stop == sf) for (stop, _) in pairs}
    for stop, dc in sorted(stopdeps.items(), key=lambda i: -i[1]):
        print(f"{stop.name}\t\t{dc}")
        clines.append((stop.ifopt, stop.name, dc))

    with open(f"C:/tmp/zaehlung-{versionid}.csv", 'w') as f:
        writer(f, delimiter=";", lineterminator="\n").writerows(clines)
