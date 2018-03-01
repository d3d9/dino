#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from geojson import LineString
import xml.etree.ElementTree as ET
from recordclass import recordclass
from urllib.request import urlopen


def sliceways(ways, slice_from, slice_to):
    coords = []
    firstfound = False
    for way in ways:
        for index, node in enumerate(way.nodes):
            if not firstfound and node.id == slice_from:
                firstfound = True
            if firstfound:
                coords.append((float(node.lon), float(node.lat)))
                if node.id == slice_to:
                    return coords


Way = recordclass('Way', 'id nodes')
Node = recordclass('Node', 'id lat lon')


'''
todo:
* aufräumen
* exceptions
* funktionen machen
* doppelungen, insbesondere am anfang, vermeiden
* attribute (liniennummer, ziel, ..) ans linestring
* abfragen von slice

mögliche erweiterungen:
* featurecollection mit stops dabei
* als abrufbaren dienst
* daten lokal statt osm api
'''


'''
tree = ET.parse("e104.xml")
root = tree.getroot()
relationid = "4644873"
'''
relationid = input("osm route relation id: ").strip()
data = urlopen("https://www.openstreetmap.org/api/0.6/relation/" + relationid + "/full")
root = ET.fromstring(data.read())
# '''

slice_from = input("slice from node id: ")
slice_to = input("slice to node id: ")

allways = []
for relation in root.iter('relation'):
    if relation.attrib['id'] == relationid:
        # for tag in relation.iter('tag'):
        #     k = tag.attrib['k']
        #     v = tag.attrib['v']
        #     print(k, v)
        for member in relation.iter('member'):
            if member.attrib['type'] == "way" and not member.attrib['role']:
                for rel_way in root.iter('way'):
                    if rel_way.attrib['id'] == member.attrib['ref']:
                        # print("way",member.attrib['ref'])
                        nodes = []
                        for way_node in rel_way.iter('nd'):
                            for node in root.iter('node'):
                                if way_node.attrib['ref'] == node.attrib['id']:
                                    # print("node",node.attrib['id'])
                                    nodes.append(Node(node.attrib['id'], node.attrib['lat'], node.attrib['lon']))
                        allways.append(Way(member.attrib['ref'], nodes))

roundabout_following = False
if len(allways) == 0 or len(allways) == 1:
    pass
else:
    if allways[0].nodes[-1] == allways[1].nodes[0]:
        pass
    elif allways[0].nodes[-1] == allways[1].nodes[-1]:
        allways[1].nodes = allways[1].nodes[::-1]
    elif allways[0].nodes[0] == allways[1].nodes[0]:
        allways[0].nodes = allways[0].nodes[::-1]
    elif allways[0].nodes[0] == allways[1].nodes[-1]:
        allways[0].nodes = allways[0].nodes[::-1]
        allways[1].nodes = allways[1].nodes[::-1]
    elif allways[1].nodes[0] == allways[1].nodes[-1]:
        print("start roundabout following")
        roundabout_following = True
        for st, node in enumerate(allways[1].nodes):
            if node.id == allways[0].nodes[-1].id:
                startfound = True
                allways[1].nodes = allways[1].nodes[st:] + allways[1].nodes[:st]
                break
        if not startfound:
            print("start roundabout start gap?")
    elif allways[0].nodes[0] == allways[0].nodes[-1]:
        print("start roundabout")
        for st, node in enumerate(allways[0].nodes):
            if node.id == allways[1].nodes[0].id:
                endfound = True
                allways[0].nodes = allways[0].nodes[:st]
                break
            elif node.id == allways[1].nodes[-1].id:
                endfound = True
                allways[1].nodes = allways[1].nodes[::-1]
                allways[0].nodes = allways[0].nodes[:st]
                break
        if not endfound:
            print("start roundabout end gap?")
    else:
        print("gap")

    for index, way in enumerate(allways):
        startfound = False
        endfound = False
        if index < 1:  # oder 2?
            continue
        elif index == len(allways) - 1:
            break

        if way.nodes[-1] == allways[index+1].nodes[0]:
            pass
        elif way.nodes[-1] == allways[index+1].nodes[-1]:
            allways[index+1].nodes = allways[index+1].nodes[::-1]
        elif allways[index+1].nodes[0] == allways[index+1].nodes[-1]:
            print("roundabout following")
            roundabout_following = True
            # start finden, rotieren
            for st, node in enumerate(allways[index+1].nodes):
                if node.id == way.nodes[-1].id:
                    startfound = True
                    allways[index+1].nodes = allways[index+1].nodes[st:] + allways[index+1].nodes[:st]
                    break
            if not startfound:
                print("roundabout start gap?")
        elif roundabout_following:
            print("inside roundabout")
            roundabout_following = False
            # ende finden, abschneiden
            for st, node in enumerate(way.nodes):
                if node.id == allways[index+1].nodes[0].id:
                    endfound = True
                    way.nodes = way.nodes[:st]
                    break
                elif node.id == allways[index+1].nodes[-1].id:
                    endfound = True
                    allways[index+1].nodes = allways[index+1].nodes[::-1]
                    way.nodes = way.nodes[:st]
                    break
            if not endfound:
                print("roundabout end gap?")
        else:
            print("gap")

print("full:")
fullcoords = []
for wi, way in enumerate(allways):
    print(way.id)
    for ni, node in enumerate(way.nodes):
        print(node)
        # doppelte nodes vermeiden durch weglassen des letzten (ausser beim letzten way)
        if (ni < len(way.nodes) - 1) or wi == len(allways) - 1:
            fullcoords.append((float(node.lon), float(node.lat)))

print("\nfull geojson\n")
print(LineString(fullcoords))

print("\nsliced geojson\n")
print(LineString(sliceways(allways, slice_from, slice_to)))


