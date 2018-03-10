#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas
import csv
from urllib.request import urlopen

overpassurl = "http://overpass-api.de/api/interpreter?data=%5Bout%3Acsv%28%3A%3Alat%2C%3A%3Alon%2C%3A%3Aid%2C%3A%3Atype%2C%22ref%3AIFOPT%22%2C%22name%22%2C%22public_transport%22%3Btrue%3B%22%5E%22%29%5D%5Btimeout%3A200%5D%3B%0Aarea%283601800297%29-%3E.searchArea%3B%0A%28%0A%20%20node%5B%22ref%3AIFOPT%22%5D%28area.searchArea%29%3B%0A%20%20way%5B%22ref%3AIFOPT%22%5D%28area.searchArea%29%3B%0A%29%3B%0Aout%20center%3B"

vrr = pandas.read_csv("./csv/stops.csv", sep=";", encoding="utf-8", dtype=str)
osm = pandas.read_csv(urlopen(overpassurl), sep="^", encoding="utf-8", dtype=str)

merged = pandas.merge(vrr, osm, left_on='posifopt', right_on='ref:IFOPT', how="outer", indicator=True)

treffer = []
zuwenig = []
zuviel = []
for index, row in merged.iterrows():
    if row['_merge'] == "both":
        treffer.append((row["X"], row["Y"], row["@lat"], row["@lon"], row["posifopt"],
                        row["stopid"],row["posname"], row["stopname"], row["name"],
                        row["@type"][0]+row["@id"], row["public_transport"]))
    elif row['_merge'] == "left_only":
        zuwenig.append((row["X"], row["Y"], row["posifopt"], row["stopid"],
                        row["posname"], row["stopname"]))
    elif row['_merge'] == "right_only":
        zuviel.append((row["@lat"], row["@lon"], row["ref:IFOPT"], row["name"],
                       row["@type"][0]+row["@id"], row["public_transport"]))

trefferfn = "./csv/stops-treffer.csv"
with open(trefferfn, 'w', newline='') as f:
    writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(("X", "Y", "lat_osm", "lon_osm", "ifopt", "stopid", "posname", "stopname", "osm_name", "full_id", "public_transport"))
    writer.writerows(treffer)
print("Datei " + trefferfn + " geschrieben")

zuwenigfn = "./csv/stops-zuwenig.csv"
with open(zuwenigfn, 'w', newline='') as f:
    writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(("X", "Y", "ifopt", "stopid", "posname", "stopname"))
    writer.writerows(zuwenig)
print("Datei " + zuwenigfn + " geschrieben")

zuvielfn = "./csv/stops-zuviel.csv"
with open(zuvielfn, 'w', newline='') as f:
    writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(("lat_osm", "lon_osm", "ifopt", "osm_name", "full_id", "public_transport"))
    writer.writerows(zuviel)
print("Datei " + zuvielfn + " geschrieben")

