#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import os
import sys
import pandas
from datetime import date, datetime, time, timedelta

betrieb = 12 #HST

with open("./dino/rec_lin_ber.din", 'r') as linefile:
    rec_lin_ber = pandas.read_csv(linefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_NAME':str}, index_col=3)
with open("./dino/rec_stop.din", 'r') as stopfile:
    rec_stop = pandas.read_csv(stopfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int}, index_col=1)
    rec_stop = rec_stop[~rec_stop.index.duplicated(keep='first')] # weg hiermit, betrieb bevorzugen
with open("./dino/rec_stopping_points.din", 'r') as platfile:
    rec_stopping_points = pandas.read_csv(platfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'STOPPING_POINT_NR':int,'IFOPT':str})
with open("./dino/service_restriction.din", 'r') as restrictionfile:
    service_restriction = pandas.read_csv(restrictionfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'RESTRICTION':str,'RESTRICT_TEXT1':str,'RESTRICTION_DAYS':str})
with open("./dino/rec_trip.din", 'r') as tripfile:
    rec_trip = pandas.read_csv(tripfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'DEPARTURE_TIME':int,'DEP_STOP_NR':int,'ARR_STOP_NR':int,'DAY_ATTRIBUTE_NR':int,'RESTRICTION':str})
with open("./dino/lid_course.din", 'r') as coursefile:
    lid_course = pandas.read_csv(coursefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_CONSEC_NR':int,'STOPPING_POINT_NR':int})
with open("./dino/lid_travel_time_type.din", 'r') as timefile:
    lid_travel_time_type = pandas.read_csv(timefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_CONSEC_NR':int})

zeit = timedelta()
prevwarte = timedelta()
prevvariant = -1
route = []
departures = []

eingabe = ""
restrictions = {}
restrictioncodes = {}
#lines = {}

for index, row in service_restriction.query("VERSION == @betrieb").iterrows():
    restrictions[row[1].strip()] = row[2].strip()
    restrictioncodes[row[1].strip()] = [row[7].strip(),row[8],row[9]]

'''
#blabla
lines[row[3]] = row[5].strip()

for row in rec_lin_ber:
    if row[0] == betrieb:
        lines[row[3]] = row[5].strip()

# erstmal auskommentierte dinge:
#* linienvarianten anzeigen
try:
    if sys.argv[1] == "L":
        #linefile.seek(0)
        print("\nLinienvarianten, Betrieb " + betrieb + ":\n")
        for row in rec_lin_ber:
            if(row[0] == betrieb):
                print (row[3] + ":" + row[4] + ":" + row[6])
        sys.exit(0)
except:
    pass
'''

def findstop(stopid):
    #todo: oben das mit duplicate weg und hier etwas machen
    return rec_stop.loc[stopid]['STOP_NAME'].strip()

def findline(line):
    tmp = rec_lin_ber.loc[line]['LINE_NAME']
    # das geht bestimmt besser..
    if type(tmp) == str:
        return tmp.strip()
    elif type(tmp) == pandas.Series:
        return tmp.iloc[0].strip()
    else:
        return line

def printdeps(auswahl,prevvariant):
    global departures
    print("\nAbfahrtszeiten")
    for index, row in rec_trip.query("VERSION == @betrieb & LINE_NR == @auswahl & STR_LINE_VAR == @prevvariant").iterrows():
        #fahrtzeit = str(timedelta(seconds=int(row[9])))
        fahrtzeit = str(row[9]//3600).zfill(2)+":"+str((row[9]//60)%60).zfill(2)+":"+str(row[9]%60).zfill(2)
        restriction = restrictions[row[18].strip()]
        start = findstop(row[10])
        end = findstop(row[13])
        # todo: notice_1, _2 undso alle zusammen nehmen
        print(fahrtzeit + "\t(" + restriction + ")\t" + start + " => " + end)
        departures.append([prevvariant,start,end,fahrtzeit,row[9],row[17],restriction,restrictioncodes[row[18].strip()][0],restrictioncodes[row[18].strip()][1],restrictioncodes[row[18].strip()][2]])

def findifopt(stopid,plat):
    try:
        for index, row in rec_stopping_points.query("VERSION == @betrieb & STOP_NR == @stopid & STOPPING_POINT_NR == @plat").iterrows():
            if row[16].strip() != "":
                return(row[16].strip())
    except:
        return("de:xxxxx:"+str(stopid)+":x:"+str(plat))
    return("de:xxxxx:"+str(stopid)+":x:"+str(plat))

def writeroutecsv(line,prevvariant):
    global route
    try:
        try:
            firststop = route[0][2].split(" ")[1].replace("/","").replace(".","")
        except:
            firststop = route[0][2].replace("/","").replace(".","")
        try:
            laststop = route[-1][2].split(" ")[1].replace("/","").replace(".","")
        except:
            laststop = route[-1][2].replace("/","").replace(".","")
        
        filename = os.path.join(os.getcwd(),"csv", "vrr_"+findline(line)+"_"+str(prevvariant)+"_"+firststop+"_"+laststop+".csv")
        with open(filename, 'w') as routefile:
            outwriter = csv.writer(routefile,delimiter=";",lineterminator = '\n')
            outwriter.writerows(route)
        print("\nroute file " + filename + " written")
    except Exception as e:
        print("\nError writing route file, continuing",e)
    route.clear()
    filename = ""

def writedepcsv(line, departures):
    try:
        filename = os.path.join(os.getcwd(),"csv", "vrr_"+findline(line)+"_departures.csv")
        with open(filename, 'w') as depfile:
            outwriter = csv.writer(depfile,delimiter=";",lineterminator = '\n')
            outwriter.writerows(departures)
        print("\ndeparture file " + filename + " written")
    except Exception as e:
        print("\nError writing departure file, continuing", e)
    departures.clear()
    filename = ""

def newvariant(line,prevvariant,variant,richtung):
    global zeit
    zeit = timedelta()
    print("\nLinie " + str(line) + ", Variante " + str(variant) + ", Richtung " + str(richtung))

def printstop(line,variant,stopnr,stopid,plat):
    global zeit
    global prevwarte
    for index, row in lid_travel_time_type.query("VERSION == @betrieb & LINE_NR == @line & STR_LINE_VAR == @variant & LINE_CONSEC_NR == @stopnr").iterrows():
        zeithin = timedelta(seconds=int(row[6]))
        zeitwarte = timedelta(seconds=int(row[7]))
        break
    zeit = zeit + zeithin + prevwarte
    ifopt = findifopt(stopid,plat)
    print(str(stopnr) + ": " + str(zeit) + "\t" + ifopt + " " + findstop(stopid))
    route.append([stopnr,ifopt,findstop(stopid),str(int(int(row[6])+prevwarte.total_seconds())),int(zeit.total_seconds())])
    prevwarte = timedelta()
    if zeitwarte != timedelta():
        prevwarte = zeitwarte

################################################

if __name__ == "__main__":
    eingabe = input("Interne Linien-ID(s) kommagetrennt (\"K\"=alle vom Betrieb): ")
    if eingabe.upper() == "K":
        print("\nKomplettexport, Betrieb " + str(betrieb) + ":\n")
        eingabe = ""
        for line in set(rec_lin_ber.query("VERSION == @betrieb").index.values):
            eingabe += str(line)
            eingabe += ","
        eingabe = eingabe[:-1]
    
    for auswahl in list(map(int,eingabe.split(","))):
        for index, row in lid_course.query("VERSION == @betrieb & LINE_NR == @auswahl").iterrows():
            currvariant = int(row[2])
            if prevvariant == -1: # erste variante der linie
                newvariant(auswahl,prevvariant,currvariant,int(row[3]))
                printstop(auswahl,currvariant,int(row[4]),int(row[5]),int(row[7]))
                prevvariant = currvariant
            elif currvariant == prevvariant: # gleiche variante wie im letzten schritt
                printstop(auswahl,currvariant,int(row[4]),int(row[5]),int(row[7]))
            else: # wechselnde variante
                printdeps(auswahl,prevvariant)
                writeroutecsv(auswahl,prevvariant)
                newvariant(auswahl,prevvariant,currvariant,int(row[3]))
                printstop(auswahl,currvariant,int(row[4]),int(row[5]),int(row[7]))
                prevvariant = currvariant
        # alle varianten durch, ende der linie
        printdeps(auswahl, prevvariant)
        writeroutecsv(auswahl,prevvariant)
        writedepcsv(auswahl, departures)
        prevvariant = -1
