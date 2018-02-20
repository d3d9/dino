#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import sys
import os
import xml.etree.ElementTree as ET
from urllib.request import urlopen

def getnameifopt(type, ref, root):
    name = ""
    ifopt = ""
    for element in root.findall(type):
        if element.attrib['id'] == ref:
            for tag in element.findall('tag'):
                k = tag.attrib['k']
                v = tag.attrib['v']
                if k == "name":
                    name = v
                elif k == "ref:IFOPT":
                    ifopt = v
    return (name, ifopt)

# todo: mehrere eingaben moeglich machen
relationid = input("Relation id (route or route_master): ").strip()
initialdata = urlopen("https://www.openstreetmap.org/api/0.6/relation/" + relationid)
initialroot = ET.fromstring(initialdata.read())

# erst einmal type={route,route_master,*} herausfinden
type = ""
for relation in initialroot.iter('relation'):
    if relation.attrib['id'] == relationid:
        for tag in relation.iter('tag'):
            if tag.attrib['k'] == "type":
                type = tag.attrib['v']

routeroots = []
# todo: non-ptv2 wegschmeissen
# todo: network auch moeglich machen -> komplettexport betrieb wie bei DINO
if type == "route_master":
    # alle routen mit /full herunterladen
    for member in initialroot.iter('member'):
        if member.attrib['type'] == "relation":
            id = member.attrib['ref']
            routedata = urlopen("https://www.openstreetmap.org/api/0.6/relation/" + id + "/full")
            routeroot = ET.fromstring(routedata.read())
            routeroots.append((id,routeroot))
elif type == "route":
    # dieselbe relation nochmal mit full herunterladen
    routedata = urlopen("https://www.openstreetmap.org/api/0.6/relation/" + relationid + "/full")
    routeroot = ET.fromstring(routedata.read())
    routeroots.append((relationid,routeroot))
else:
    print("relation "+relationid+" is no route or route_master")
    sys.exit(1)

routes = []
for id, root in routeroots:
    stopnr = 1
    route = []
    previousifopt = "" # wird erstmal nicht benutzt, gleicher >name< ist bei PTv2 wichtig
    previousname = ""
    linefrom = ""
    lineto = ""
    linevia = ""

    try:
        for relation in root.iter('relation'):
            if relation.attrib['id'] == id:
                # erst einmal Liniennummer usw. heraussuchen
                for tag in relation.findall('tag'):
                    k = tag.attrib['k']
                    v = tag.attrib['v']
                    if k == "ref":
                        line = v
                    elif k == "from":
                        linefrom = v
                    elif k == "to":
                        lineto = v
                    elif k == "via":
                        linevia = v
                print(line,linefrom,"=",linevia,">",lineto,end="\n\n")
                # member der Route durchgehen
                for member in relation.findall('member'):
                    if member.attrib['role']:
                        name, ifopt = getnameifopt(member.attrib['type'],member.attrib['ref'],root)
                        if name != previousname:
                            print(str(stopnr)+"\t"+ifopt+"\t"+name)
                            route.append((stopnr, ifopt, name))
                            stopnr += 1
                        previousname = name
                        previousifopt = ifopt
    except Exception as e:
        print("Unexpected error:\n",e)
    else:
        routes.append((line, linefrom, lineto, id, route))
        print("\n")

for line, linefrom, lineto, id, route in routes:
    filenamefrom = linefrom
    if not filenamefrom:
        filenamefrom = route[0][2]
    filenameto = lineto
    if not filenameto:
        filenameto = route[-1][2]
        
    try:
        filenamefrom = filenamefrom.split(" ")[1].replace("/","").replace(".","")
    except:
        filenamefrom = filenamefrom.replace("/","").replace(".","")
    try:
        filenameto = filenameto.split(" ")[1].replace("/","").replace(".","")
    except:
        filenameto = filenameto.replace("/","").replace(".","")
    
    filename = os.path.join(os.getcwd(),"csv","osm_"+line+"_"+id+"_"+filenamefrom+"_"+filenameto+".csv")
    
    try:
        with open(filename, 'w') as outfile:
            outwriter = csv.writer(outfile, delimiter=";", lineterminator='\n')
            outwriter.writerows(route)
        print("File " + filename + " written")
    except Exception as e:
        print("Error writing file",e)
'''
    stdoutwriter = csv.writer(sys.stdout)
    for route in routes:
        #print(route)
        stdoutwriter.writerows(route)
'''
