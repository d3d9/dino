#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

import pandas

vorher = pandas.read_csv("C:/tmp/zaehlung-80.csv", header=None, names=["ifopt", "name", "count"], sep=";", encoding="cp1252", dtype=str)
nachher = pandas.read_csv("C:/tmp/zaehlung-16.csv", header=None, names=["ifopt", "name", "count"], sep=";", encoding="cp1252", dtype=str)

merged = pandas.merge(vorher, nachher, on="ifopt", how="outer")

merged.to_csv("C:/tmp/zaehlung-merged.csv", sep=";", encoding="utf-8")
