#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from DINO import Version, Line, Restriction, getlinetrips, readrestrictions, readallstops, printstops, csvstops
import pandas
from datetime import date, timedelta


if __name__ == "__main__":
    with open("./dino/set_version.din", 'r') as verfile:
        set_version = pandas.read_csv(verfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'VERSION_TEXT':str,'TIMETABLE_PERIOD':str,'TT_PERIOD_NAME':str,'PERIOD_DATE_FROM':str,'PERIOD_DATE_TO':str,'NET_ID':str,'PERIOD_PRIORITY':int}, index_col=0)
    with open("./dino/rec_trip.din", 'r') as tripfile:
        rec_trip = pandas.read_csv(tripfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'DEPARTURE_TIME':int,'DEP_STOP_NR':int,'ARR_STOP_NR':int,'DAY_ATTRIBUTE_NR':int,'NOTICE':str,'NOTICE_2':str,'NOTICE_3':str,'NOTICE_4':str,'NOTICE_5':str,'TIMING_GROUP_NR':int}, converters = {'RESTRICTION': lambda x: x.strip()})
    with open("./dino/service_restriction.din", 'r') as restrictionfile:
        service_restriction = pandas.read_csv(restrictionfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'RESTRICTION':str,'RESTRICT_TEXT1':str,'RESTRICT_TEXT2':str,'RESTRICT_TEXT3':str,'RESTRICT_TEXT4':str,'RESTRICT_TEXT5':str,'RESTRICTION_DAYS':str})
    with open("./dino/calendar_of_the_company.din", 'r') as calendarfile:
        calendar_otc = pandas.read_csv(calendarfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'DAY':str,'DAY_TEXT':str,'DAY_TYPE_NR':int})
#    with open("./dino/rec_stop.din", 'r') as stopfile:
#        rec_stop = pandas.read_csv(stopfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'STOP_TYPE_NR':int,'STOP_NAME':str,'STOP_SHORTNAME':str,'STOP_POS_X':str,'STOP_POS_Y':str,'PLACE':str,'OCC':int,'IFOPT':str}, index_col=1)
#    with open("./dino/rec_stop_area.din", 'r') as areafile:
#        rec_stop_area = pandas.read_csv(areafile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'STOP_AREA_NR':int,'STOP_AREA_NAME':str,'IFOPT':str})
    #with open("./dino/rec_additional_stopname.din", 'r') as addnamefile:
    #     rec_additional_stopname = pandas.read_csv(addnamefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int, 'STOP_TYPE_NR':int,'ADD_STOP_NAME_WITH_LOCALITY':str,'ADD_STOP_NAME_WITHOUT_LOCALITY':str})
#    with open("./dino/lid_course.din", 'r') as coursefile:
#        lid_course = pandas.read_csv(coursefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_CONSEC_NR':int,'STOPPING_POINT_NR':int,'LENGTH':int})
#    with open("./dino/lid_travel_time_type.din", 'r') as timefile:
#        lid_travel_time_type = pandas.read_csv(timefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_CONSEC_NR':int,'TIMING_GROUP_NR':int})
#    with open("./dino/rec_stopping_points.din", 'r') as platfile:
#        rec_stopping_points = pandas.read_csv(platfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'STOP_AREA_NR':int,'STOPPING_POINT_NR':int,'STOPPING_POINT_SHORTNAME':str,'STOPPING_POINT_POS_X':str,'STOPPING_POINT_POS_Y':str,'IFOPT':str})
#    with open("./dino/rec_lin_ber.din", 'r') as linefile:
#        rec_lin_ber = pandas.read_csv(linefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_NAME':str}, index_col=3)

    versionid = 11  # HST (DINO_VRR_20180418)

    version = Version(set_version.loc[versionid])
    #stops = readallstops(version, rec_stop, rec_stop_area, rec_stopping_points)
    restrictions = readrestrictions(service_restriction, version)

    #daytype = 124
    #rid = "#0029"
    #c = Restriction(*restrictions[rid])

    #  8;d5   (DINO_VRR_20180209)
    #daytype = 119
    #rid = "test"
    #c = Restriction("060c182000c1830640c183062c183060230e0d183060c1830c1830604183060c183060c1460c183220c1830658b060c102040818",
    #                "20180107", "20190105",
    #                "nur samstags, auch 12.1.18, 19.1., 26.1., 2.2., 9.2., 16.2.,;23.2., 2.3., 9.3., 16.3., 23.3., 6.4., 13.4., 20.4., 27.4., ;30.4., 4.5., 9.5., 11.5., 18.5., 20.5., 25.5., 30.5., 1.6., ;8.6., 15.6., 22.6., 29.6., 6.7., 13.7., 20.7., 27.7., 3.8., ;10.8., 17.8., 24.8., 31.8., 7.9., 14.9., 21.9., 28.9., 2.10 ;")

    #daytype = 1
    #rid = "hst18" # DINO_VRR_20180418
    #c = ("00000000000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000",
    #     "20170611", "20180609",
    #     "Fährt nur am 11.02.2018")
    #restrictions = {rid: c}

    crows = {}
    cdrows = []

    for rid in restrictions:
        c = Restriction(*restrictions[rid])
        bc = c.booldictcalendar()
        #'''
        print(rid)
        print(c)
        print(c.textcalendar())
        print(bc)
        print("")
        #'''
        for index, row in rec_trip.query("VERSION == @version.id & RESTRICTION == @rid").iterrows():
            daytype = row["DAY_ATTRIBUTE_NR"]
            sid = str(versionid) + "-" + rid + "-" + str(daytype)
            if sid in crows:
                continue
            daytypebits = bin(daytype)[2:].zfill(7)
            crows[sid] = sid + "," + ",".join(x for x in daytypebits) + "," + c.datefrom + "," + c.dateuntil

            daydate = date(c.startyear, c.firstmonth, c.firstday)
            enddate = date(c.endyear, c.lastmonth, c.lastday)
            exception_type = 0

            while daydate <= enddate:
                weekday = daydate.weekday()
                daystr = daydate.strftime("%Y%m%d")

                #print(daydate, weekday, daystr)

                daytypevalid = bool(int(daytypebits[weekday]))
                restrictionvalid = bc[daydate.year][daydate.month][daydate.day-1]

                if daytypevalid and restrictionvalid:
                    #print("ok")
                    exception_type = 0
                elif daytypevalid and not restrictionvalid:
                    #print("e: 2 (removed)")
                    exception_type = 2
                elif (not daytypevalid) and restrictionvalid:
                    # ???
                    #print("grrgrgrgrgrgr")
                    #exception_type = 1
                    exception_type = 0
                else:
                    #print("off")
                    exception_type = 0

                if exception_type:
                    cdrows.append(sid + "," + daystr + "," + str(exception_type))

                daydate += timedelta(days=1)

    print("calendar.txt")
    print("service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date")
    print('\n'.join(crows[sid] for sid in crows))

    print("")
    print("calendar_dates.txt")
    print("service_id,day,exception_type")
    print('\n'.join(cdrows))


