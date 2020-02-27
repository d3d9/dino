#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from DINO import Restriction, Version, Line, dayvalid, getlinetrips, readrestrictions, readallstops, printstops, csvstops
#from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Pool, Manager
import pandas
from tqdm import tqdm
from datetime import timedelta, date
dwt = __import__("dino-wikitable")

def single_rdt(rid, day_attr, ns):
    print(rid, day_attr)
    daycount = 0
    c = Restriction(*ns.restrictions[rid])
    daydate = date(c.startyear, c.firstmonth, c.firstday)
    enddate = date(c.endyear, c.lastmonth, c.lastday)

    while daydate <= enddate:
        if dayvalid(c, ns.version, daydate.timetuple()[:3], ns.calendar_otc, day_attr, day_type_2_day_attribute):
            daycount += 1
        daydate += timedelta(days=1)

    return daycount

def single_line(lineid, ns):
    print(lineid)
    line = Line(ns.version, lineid, ns.rec_lin_ber, ns.lid_course, ns.lid_travel_time_type, ns.stops)
    ldf = ns.rec_trip.query("VERSION == @versionid & LINE_NR == @lineid")
    linedistance = 0
    for index, row in ldf.iterrows():
        day_attr = row["DAY_ATTRIBUTE_NR"]
        rid = row["RESTRICTION"].strip()
        distance = line.courses[int(row["STR_LINE_VAR"])].distance
        linedistance += distance*ns.rdts[(rid, day_attr)]
        
    return linedistance

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


    versionid = 16
    version = Version(set_version.loc[versionid])
    stops = readallstops(version, rec_stop, rec_stop_area, rec_stopping_points)
    restrictions = readrestrictions(service_restriction, version)

    lineids = []
    lines = {}
    linekm = {}
    rdtlist = []
    rdts = {}
    qdf = rec_trip.query("VERSION == @versionid")
    print(qdf.shape[0])
    
    for index, row in tqdm(qdf.iterrows(), total=qdf.shape[0]):
        lineid = str(int(row["LINE_NR"]))
        if lineid not in lineids:
            lineids.append(lineid)

        day_attr = row["DAY_ATTRIBUTE_NR"]
        rid = row["RESTRICTION"].strip()
        if (rid, day_attr) not in rdtlist:
            rdtlist.append((rid, day_attr))    

    mgr = Manager()
    ns = mgr.Namespace()
    ns.restrictions = restrictions
    ns.version = version
    ns.calendar_otc = calendar_otc

    with Pool(8) as pool:
        '''
        fs = {ppe.submit(single_rdt, *x): x
                for x in rdtlist}
        for f in as_completed(fs):
            _result = f.result()
            rid, day_attr = fs[f]
            print(f"{rid}, {day_attr}: {_result}")
            rdts[(rid, day_attr)] = _result
        '''
        for x, _r in zip(rdtlist, pool.starmap(single_rdt, [(*x, ns) for x in rdtlist])):
            rid, day_attr = x
            print(f"{rid}, {day_attr}: {_r}")
            rdts[x] = _r        
    
    mgr = Manager()
    ns = mgr.Namespace()
    ns.rdts = rdts
    ns.rec_trip = rec_trip
    ns.version = version
    ns.rec_lin_ber = rec_lin_ber
    ns.lid_course = lid_course
    ns.lid_travel_time_type = lid_travel_time_type
    ns.stops = stops
    
    with Pool(8) as pool:
        '''
        fs = {ppe.submit(single_line, lineid): lineid
                for lineid in lineids}
        for f in as_completed(fs):
            _result = f.result()
            lineid = fs[f]
            print(f"{lineid}: {_result}")
            linekm[lineid] = _result
        '''
        for lineid, _r in zip(lineids, pool.starmap(single_line, [(lineid, ns) for lineid in lineids])):
            print(f"{lineid}: {_r}")
            linekm[lineid] = _r       
        
    '''
    for index, row in tqdm(qdf.iterrows(), total=qdf.shape[0]):
        lineid = str(int(row["LINE_NR"]))
        if lineid not in lines:
            linekm[lineid] = 0.0
            lines[lineid] = Line(version, lineid, rec_lin_ber, lid_course, lid_travel_time_type, stops)

        day_attr = row["DAY_ATTRIBUTE_NR"]
        rid = row["RESTRICTION"].strip()
        if (rid, day_attr) not in rdts:
            daycount = 0
            c = Restriction(*restrictions[rid])
            daydate = date(c.startyear, c.firstmonth, c.firstday)
            enddate = date(c.endyear, c.lastmonth, c.lastday)

            while daydate <= enddate:
                if dayvalid(c, version, daydate.timetuple()[:3], calendar_otc, day_attr, day_type_2_day_attribute):
                    daycount += 1
                daydate += timedelta(days=1)

            rdts[(rid, day_attr)] = daycount

        distance = lines[lineid].courses[int(row["STR_LINE_VAR"])].distance
        linekm[lineid] += distance*rdts[(rid, day_attr)]
    '''

    '''
    for lineid in lines:
        line = lines[lineid]
        print("\n- "+str(line))
        for courseid in line.courses:
            course = line.courses[courseid]
            print("\n-- "+str(course))
            querystring = "VERSION == @line.version.id & LINE_NR == @line.lineid & STR_LINE_VAR == @courseid"
            trips = dict((date, list()) for date in dates)
            for index, row in rec_trip.query(querystring).iterrows():
                rrow = row["RESTRICTION"]
                if rrow:
                    restriction = Restriction(*restrictions[line.version.id][rrow.strip()])
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
    '''