#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas
from urllib.request import urlopen

overpassurl = "http://overpass-api.de/api/interpreter?data=%5Bout%3Acsv%28%3A%3Alat%2C%3A%3Alon%2C%3A%3Aid%2C%3A%3Atype%2C%22ref%3AIFOPT%22%2C%22name%22%2C%22public_transport%22%3Btrue%3B%22%5E%22%29%5D%5Btimeout%3A200%5D%3B%0Aarea%283601800297%29-%3E.searchArea%3B%0A%28%0A%20%20node%5B%22ref%3AIFOPT%22%5D%28area.searchArea%29%3B%0A%20%20way%5B%22ref%3AIFOPT%22%5D%28area.searchArea%29%3B%0A%29%3B%0Aout%20center%3B"

vrr = pandas.read_csv("./csv/stops.csv", sep=";", encoding="utf-8", dtype=str)
osm = pandas.read_csv(urlopen(overpassurl), sep="^", encoding="utf-8", dtype=str)

merged = pandas.merge(vrr, osm, left_on='posifopt', right_on='ref:IFOPT', how="outer", indicator=True)

for index, row in merged.iterrows():
    if row['_merge'] == "both":
        print("b : " + str(row['posifopt']) + " (" + str(row['stopname']) + ")")
    elif row['_merge'] == "left_only":
        print("lo: " + str(row['posifopt']) + " (" + str(row['stopname']) + ")")
    elif row['_merge'] == "right_only":
        print("ro: " + str(row['ref:IFOPT']) + " (" + str(row['name']) + ") " + str(row['public_transport']))

