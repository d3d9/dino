#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DINO import Restriction, dayvalid, findstop, findplat
import pandas
from datetime import timedelta


#'''
def printtrips(betrieb, line, day, rec_trip, service_restriction, rec_stop, lid_course, \
               lid_travel_time_type, rec_stopping_points):
    #restrictions = {}
    restrictioncodes = {}
    for index, row in service_restriction.query("VERSION == @betrieb").iterrows():
    	#restrictions[row[1].strip()] = row[2].strip()
    	restrictioncodes[row[1].strip()] = [row[7].strip(),str(row[8]),str(row[9])]

    for index, row in rec_trip.query("VERSION == @betrieb & LINE_NR == @line").iterrows():
        if dayvalid(Restriction(*restrictioncodes[row["RESTRICTION"].strip()]), day, row["DAY_ATTRIBUTE_NR"]):
            variant = row["STR_LINE_VAR"]
            startzeit = row["DEPARTURE_TIME"]
            zeit = timedelta(seconds=startzeit)
            zeithin = timedelta()
            zeitwarte = timedelta()
            prevwarte = timedelta()

            print(line + " var" + str(variant) + " um " \
                  + str(startzeit//3600).zfill(2)+":"+str((startzeit//60)%60).zfill(2)+":"+str(startzeit%60).zfill(2) \
                  + " Uhr von " + findstop(rec_stop, row["DEP_STOP_NR"]) + " nach " + findstop(rec_stop, row["ARR_STOP_NR"]) + ":")

            for index, row in lid_course.query("VERSION == @betrieb & LINE_NR == @line & STR_LINE_VAR == @variant").iterrows():
                stopid = row["STOP_NR"]
                platid = row["STOPPING_POINT_NR"]
                stopnr = row["LINE_CONSEC_NR"]

                for index, row in lid_travel_time_type.query("VERSION == @betrieb & LINE_NR == @line & STR_LINE_VAR == @variant & LINE_CONSEC_NR == @stopnr").iterrows():
                    zeithin = timedelta(seconds=int(row["TT_REL"]))
                    zeitwarte = timedelta(seconds=int(row["STOPPING_TIME"]))
                    break  # ?
                zeit += zeithin
                if zeitwarte != timedelta():
                    print(str(stopnr)+":\tan "+str(zeit)+"\t"+findstop(rec_stop, stopid)+" "+findplat(rec_stopping_points, betrieb, stopid, platid))
                    zeit += zeitwarte
                    print(str(stopnr)+":\tab "+str(zeit)+"\t"+findstop(rec_stop, stopid)+" "+findplat(rec_stopping_points, betrieb, stopid, platid))
                else:
                    print(str(stopnr)+":\t   "+str(zeit)+"\t"+findstop(rec_stop, stopid)+" "+findplat(rec_stopping_points, betrieb, stopid, platid))
#'''

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
    line = "50115"
    testdate = (2018,2,16)    

    printtrips(betrieb, line, testdate, rec_trip, service_restriction, rec_stop, lid_course, \
               lid_travel_time_type, rec_stopping_points)



