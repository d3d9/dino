#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas
from json import dumps
from DINO import Version, Line, getlinetrips, readrestrictions, readallstops, printstops, csvstops
from datetime import timedelta


# todo: ersetzen, es sollte kontext verstehen
def stopclean(name, placelist, ignoreif=["Hauptbahnhof", "Hbf", "Bahnhof", "Bf"]):
    for s in ignoreif:
        if s in name:
            return name
    for place in placelist:
        name = name.replace(place, "", 1)
    return name


def timestr(secs):
    return (str(secs//3600).zfill(2)+":"+str((secs//60) % 60).zfill(2)+":"+str(secs % 60).zfill(2)).rstrip("00").rstrip(":")


def mins(td):
    return ("%f" % (td.total_seconds()/60)).rstrip("0").rstrip(".")


def rowspan(e):
    return (1 if not e else sum(rowspan(x[1]) for x in e))


# todo: "Mo-Fr" statt "Mo, Di, .." oderso?
def daytypetext(dt, days=["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]):
    tage = []
    for i, day in enumerate(bin(dt)[2:].zfill(7)):
        if bool(int(day)):
            tage.append(days[i])
    return (", ".join(tage) if tage else "keine")


def takt(a, min_alle=3):
    r = []
    nexttime = timedelta(seconds=-9999)
    nexttd = timedelta(seconds=-9999)
    takt = timedelta(seconds=0)
    taktc = 0

    for i, s in enumerate(a):
        td = s if type(s) == timedelta else timedelta(seconds=s)
        if i < len(a) - 1:
            n = a[i+1]
            nexttime = n if type(n) == timedelta else timedelta(seconds=n)
        else:
            nexttime = timedelta(seconds=-9999)
        tdiff = nexttime - td

        if tdiff == nexttd:
            takt = tdiff
            taktc += 1
        else:
            if taktc:
                if not takt:
                    for _ in range(taktc):
                        r.append(timestr(int(td.total_seconds())))
                elif taktc < min_alle:
                    for t in range(taktc, 0, -1):
                        r.append(timestr(int((td-t*takt).total_seconds())))
                else:
                    r.append("alle " + mins(takt) + " min")
            takt = timedelta(0)
            taktc = 0
            r.append(timestr(int(td.total_seconds())))
        nexttd = tdiff
        nexttime = td

    rtext = ""
    for ri, re in enumerate(r):
        rtext += re
        if re.startswith("alle"):
            sep = " --"
        elif ri < len(r) - 1 and r[ri+1].startswith("alle"):
            sep = "-- "
        else:
            sep = ", "
        if ri < len(r) - 1:
            rtext += sep

    return rtext


def fahrplanarray(lineids, placelist):
    a = []
    for lineid in lineids:
        line = Line(version, lineid, rec_lin_ber, lid_course, lid_travel_time_type, stops)
        # print(line)
        a_l = [["'''" + line.linesymbol + "'''"], []]
        for course in sorted(line.courses.values(), key=lambda c: (c.linedir, stopclean(c.stopfrom, placelist), -len(c.stops), -c.distance)):
            courseid = course.variant
            # print(course)
            a_c = [["'''" + stopclean(course.stopfrom, placelist) + "'''&nbsp;→ '''" + stopclean(course.stopto, placelist) + "'''", len(course.stops), str(round(course.distance/1000, 1)).replace(".", ",").rstrip("0").rstrip(",") + " km"], []]
            fahrzeiten = {}
            for timing_group_nr in course.timing_groups:
                tg = course.timing_groups[timing_group_nr]
                fahrzeit = mins(tg[course.stops[-1].stopnr][0]) + " min"
                if fahrzeit not in fahrzeiten:
                    fahrzeiten[fahrzeit] = [timing_group_nr]
                else:
                    # zeiten, die insgesamt gleich sind werden zusammengetan
                    fahrzeiten[fahrzeit].append(timing_group_nr)
            for fahrzeit in fahrzeiten:
                a_fz = [[fahrzeit], []]
                restrictions = {}
                for index, row in rec_trip.query("VERSION == @versionid & LINE_NR == @lineid & STR_LINE_VAR == @courseid & (" + " | ".join(("TIMING_GROUP_NR == " + str(tg)) for tg in fahrzeiten[fahrzeit]) + ")").iterrows():
                    restrictionid = row["RESTRICTION"].strip()
                    restrictiontext = allrestrictions[restrictionid][3]
                    daytype = row["DAY_ATTRIBUTE_NR"]
                    starttime = row["DEPARTURE_TIME"]
                    # todo: auch schauen ob die kalender an sich gleich sind, nicht nur der text!
                    if restrictiontext not in restrictions:
                        restrictions[restrictiontext] = {daytype: [starttime]}
                    elif daytype not in restrictions[restrictiontext]:
                        restrictions[restrictiontext][daytype] = [starttime]
                    elif starttime not in restrictions[restrictiontext][daytype]:
                        restrictions[restrictiontext][daytype].append(starttime)
                    else:
                        restrictions[restrictiontext][daytype].append(starttime)
                        print("Warnung, gleichzeitige gleiche Abfahrt:", course, fahrzeit, restrictiontext, daytype, timestr(starttime))
                for restrictiontext in restrictions:
                    a_r = [[restrictiontext], []]
                    # print("Restriction " + restrictiontext)
                    for daytype in restrictions[restrictiontext]:
                        dttext = daytypetext(daytype)
                        # print("Daytype " + str(daytype) + " (" + dttext + ")")
                        takttext = takt(sorted(restrictions[restrictiontext][daytype]))
                        # print("Takttext " + takttext)
                        a_r[1].append([[dttext, takttext], []])
                    a_r[1].sort(key=lambda dt: dt[0][0])
                    a_fz[1].append(a_r)
                a_fz[1].sort(key=lambda r: r[0][0])
                a_c[1].append(a_fz)
            a_c[1].sort(reverse=True, key=lambda fz: fz[0][0])
            a_l[1].append(a_c)
        a.append(a_l)
    return a


def stoparray(stopdict):
    a = []
    m = 0.000001
    # coords = lambda x, y: ((str(round(float(y)*m, 6))+","+str(round(float(x)*m, 6))) if (x and y) else "")
    vocoords = lambda x, y, name, dim: (("{{Coordinate|NS="+str(round(float(y)*m, 6))+"|EW="+str(round(float(x)*m, 6))+"|dim="+dim+"|type=landmark|region=DE-NW|simple=y|name="+name+"}}") if (x and y) else "")
    sortf = lambda e: (e.name, e.ifopt)
    for stop in sorted(stopdict.values(), key=sortf):
        a_s = [["'''" + stop.name + "'''", stop.ifopt, vocoords(stop.pos_x, stop.pos_y, stop.name, "120"), ", ".join(str(fz) for fz in stop.farezones), stop.shortname], []]
        for area in sorted(stop.areas.values(), key=sortf):
            a_a = [[area.name, area.ifopt], []]
            for pos in sorted(area.positions.values(), key=sortf):
                a_p = [[pos.name, pos.ifopt, vocoords(pos.pos_x, pos.pos_y, stop.name+" "+pos.name, "20")], []]
                a_a[1].append(a_p)
            if not a_a[1]:
                a_a[1].append([["", "", ""], []])
            a_s[1].append(a_a)
        if not a_s[1]:
            a_s[1].append([["", ""], [[["", "", ""], []]]])
        a.append(a_s)
    return a


def tableatext(a, i, labels):
    text = ""
    for x, y in a:
        text += str(rowspan(y)) + " "
        text += "-"*i
        for ei, ex in enumerate(x):
            text += "\""+labels[i][ei]+"\": " + str(ex)
            if ei < len(x) - 1:
                text += " | "
            else:
                text += "\n"

        if y:
            text += tableatext(y, i+1, labels)
    return text


def tablerows(a, tfirstpre=""):
    text = ""
    for x in a:
        rs = rowspan(x[1])
        # ändern!
        if tfirstpre:
            prerowspan = (f" rowspan=\"{rs}\"" if rs > 1 else "")
            pre = ((tfirstpre + prerowspan + " | ") if tfirstpre or prerowspan else "")
            for i, y in enumerate(x[0]):
                text += "| " + (pre if not i else "") + str(y) + "\n"
        else:
            for y in x[0]:
                text += "| " + (f" rowspan=\"{rs}\" | " if rs > 1 else "") + str(y) + "\n"
        if x[1]:
            text += tablerows(x[1])
        else:
            text += "|-\n"
    return text


def wikitable(a, ttitle, tref, tcols,
              tfirstpre="",
              tclass="wikitable sortable mw-collapsible mw-collapsed",
              tstyle="width:100%; text-align:left; font-size:90%;",
              theadclass="hintergrundfarbe6"):
    wikitext = "{| class=\"" + tclass + "\" style=\"" + tstyle + "\"\n|-\n"
    wikitext += "|+ " + ttitle + tref + "\n|- class=\"" + theadclass + "\"\n"
    for colname, colsort in tcols:
        wikitext += "! "
        if colsort:
            if colsort == "unsortable":
                wikitext += "class=\"unsortable\" | "
            else:
                wikitext += "data-sort-type=\"" + colsort + "\" | "
        wikitext += colname + "\n"
    wikitext += "\n|-\n"
    wikitext += tablerows(a, tfirstpre)
    wikitext += "\n|}\n"
    return wikitext


if __name__ == "__main__":
    versionid = 11
    placelist = ["Hagen ", "HA-", "Hagen, "]
    lineids = []
    onlyew = False
    # printallcoursestops = False
    printstops = True
    outfilename = "./csv/wiki.txt"

    with open("./dino/set_version.din", 'r') as verfile:
        set_version = pandas.read_csv(verfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'VERSION_TEXT':str,'TIMETABLE_PERIOD':str,'TT_PERIOD_NAME':str,'PERIOD_DATE_FROM':str,'PERIOD_DATE_TO':str,'NET_ID':str,'PERIOD_PRIORITY':int}, index_col=0)
    version = Version(set_version.loc[versionid])

    with open("./dino/rec_trip.din", 'r') as tripfile:
        rec_trip = pandas.read_csv(tripfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'DEPARTURE_TIME':int,'DEP_STOP_NR':int,'ARR_STOP_NR':int,'DAY_ATTRIBUTE_NR':int,'RESTRICTION':str,'NOTICE':str,'NOTICE_2':str,'NOTICE_3':str,'NOTICE_4':str,'NOTICE_5':str,'TIMING_GROUP_NR':int})
    with open("./dino/service_restriction.din", 'r') as restrictionfile:
        service_restriction = pandas.read_csv(restrictionfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'RESTRICTION':str,'RESTRICT_TEXT1':str,'RESTRICT_TEXT2':str,'RESTRICT_TEXT3':str,'RESTRICT_TEXT4':str,'RESTRICT_TEXT5':str,'RESTRICTION_DAYS':str})
    with open("./dino/rec_stop.din", 'r') as stopfile:
        rec_stop = pandas.read_csv(stopfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'STOP_TYPE_NR':int,'STOP_NAME':str,'STOP_SHORTNAME':str,'STOP_POS_X':str,'STOP_POS_Y':str,'PLACE':str,'OCC':int,'IFOPT':str}, index_col=1)
    with open("./dino/rec_stop_area.din", 'r') as areafile:
        rec_stop_area = pandas.read_csv(areafile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'STOP_AREA_NR':int,'STOP_AREA_NAME':str,'IFOPT':str})
    with open("./dino/lid_course.din", 'r') as coursefile:
        lid_course = pandas.read_csv(coursefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_CONSEC_NR':int,'STOPPING_POINT_NR':int,'LENGTH':int})
    with open("./dino/lid_travel_time_type.din", 'r') as timefile:
        lid_travel_time_type = pandas.read_csv(timefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_CONSEC_NR':int,'TIMING_GROUP_NR':int})
    with open("./dino/rec_stopping_points.din", 'r') as platfile:
        rec_stopping_points = pandas.read_csv(platfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'STOP_NR':int,'STOP_AREA_NR':int,'STOPPING_POINT_NR':int,'STOPPING_POINT_SHORTNAME':str,'STOPPING_POINT_POS_X':str,'STOPPING_POINT_POS_Y':str,'IFOPT':str})
    with open("./dino/rec_lin_ber.din", 'r') as linefile:
        rec_lin_ber = pandas.read_csv(linefile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'LINE_NR':int,'STR_LINE_VAR':int,'LINE_DIR_NR':int,'LINE_NAME':str}, index_col=3)

    stops = readallstops(version, rec_stop, rec_stop_area, rec_stopping_points)
    allrestrictions = readrestrictions(service_restriction, version)

    if not lineids:
        for index, row in rec_lin_ber.query("VERSION == @version.id").iterrows():
            lineid = index
            linename = row["LINE_NAME"].strip()
            if (not onlyew or (onlyew and linename.startswith("E"))) and lineid not in lineids:
                lineids.append(lineid)

    # a = [[["'''514'''"], [[["'''Bathey'''&nbsp;\u2192 '''Hauptbahnhof'''", 27, "10,5 km"], [[["31 min"], [[["Samstag"], [[["Sa", "19:32-20:52"], []]]], [["so. u. fe."], [[["Di, So", "07:58-alle 60 min-18:58"], []]]], [["F\u00e4hrt nicht am 10.04.2018"], [[["Mo, Di, Mi, Do, Fr", "19:52-20:52"], []]]]]], [["34 min"], [[["Samstag"], [[["Sa", "05:33-alle 30 min-17:33-18:33"], []]]], [["F\u00e4hrt nicht am 10.04.2018"], [[["Mo, Di, Mi, Do, Fr", "04:33-05:33-alle 30 min-19:03"], []]]]]]]], [["'''Kabel'''&nbsp;\u2192 '''Hauptbahnhof'''", 19, "7,1 km"], [[["23 min"], [[["nur an verkaufsoffenen Sonntagen in Hagen"], [[["So", "13:19-alle 60 min-17:19"], []]]]]]]], [["'''Hauptbahnhof'''&nbsp;\u2192 '''Kabel'''", 20, "7,2 km"], [[["27 min"], [[["nur an verkaufsoffenen Sonntagen in Hagen"], [[["So", "13:44-alle 60 min-17:44"], []]]], [["F\u00e4hrt nicht am 10.04.2018"], [[["Mo, Di, Mi, Do, Fr", "18:46-alle 60 min-20:46"], []]]]]]]], [["'''Hauptbahnhof'''&nbsp;\u2192 '''Bathey'''", 25, "9,9 km"], [[["33 min"], [[["Samstag"], [[["Sa", "05:16-alle 30 min-18:16-alle 60 min-20:16"], []]]], [["so. u. fe."], [[["Di, So", "07:14-alle 60 min-18:14"], []]]], [["F\u00e4hrt nicht am 10.04.2018"], [[["Mo, Di, Mi, Do, Fr", "04:31-05:16-alle 30 min-07:16-07:49-08:16-alle 30 min-13:16-13:49-14:16-alle 30 min-18:16-alle 60 min-20:16"], []]]]]]]]]], [["'''522'''"], [[["'''Stadtmitte/Volme Galerie'''&nbsp;\u2192 '''Berchum Schule'''", 19, "7,6 km"], [[["24 min"], [[["Samstag"], [[["Sa", "05:35-alle 60 min-17:35"], []]]], [["F\u00e4hrt nicht am 10.04.2018"], [[["Mo, Di, Mi, Do, Fr", "04:35-alle 60 min-18:35"], []]]]]], [["21 min"], [[["Samstag"], [[["Sa", "18:35-alle 60 min-20:35"], []]]], [["so. u. fe."], [[["Di, So", "08:13-alle 60 min-18:13"], []]]], [["F\u00e4hrt nicht am 10.04.2018"], [[["Mo, Di, Mi, Do, Fr", "19:35-20:35"], []]]]]]]], [["'''Berchum Schule'''&nbsp;\u2192 '''Stadtmitte/Volme Galerie'''", 20, "8,4 km"], [[["26 min"], [[["Samstag"], [[["Sa", "04:59-alle 60 min-17:59"], []]]], [["F\u00e4hrt nicht am 10.04.2018"], [[["Mo, Di, Mi, Do, Fr", "04:59-alle 60 min-18:59"], []]]]]], [["23 min"], [[["Samstag"], [[["Sa", "18:59-alle 60 min-20:59"], []]]], [["F\u00e4hrt nicht am 10.04.2018"], [[["Mo, Di, Mi, Do, Fr", "19:56"], []]]]]]]], [["'''Berchum Schule'''&nbsp;\u2192 '''Stadtmitte/Volme Galerie'''", 20, "8,3 km"], [[["23 min"], [[["so. u. fe."], [[["Di, So", "08:46-alle 60 min-18:46"], []]]], [["F\u00e4hrt nicht am 10.04.2018"], [[["Mo, Di, Mi, Do, Fr", "20:56"], []]]]]]]]]], [["'''544'''"], [[["'''Hauptbahnhof'''&nbsp;\u2192 '''DO Spielbank Hohensyburg'''", 9, "10,3 km"], [[["26 min"], [[["Samstag"], [[["Sa", "16:08-17:08"], []]]], [["F\u00e4hrt nicht am 10.04.2018"], [[["Mo, Di, Mi, Do, Fr", "16:08-alle 60 min-19:08"], []]]]]], [["23 min"], [[["Samstag"], [[["Sa", "18:08-19:08-20:05-alle 60 min-22:05"], []]]], [["so. u. fe."], [[["Di, So", "11:05-alle 60 min-21:05"], []]]], [["F\u00e4hrt nicht am 10.04.2018"], [[["Mo, Di, Mi, Do, Fr", "20:05-alle 60 min-22:05"], []]]]]]]], [["'''DO Spielbank Hohensyburg'''&nbsp;\u2192 '''Hauptbahnhof'''", 9, "10,4 km"], [[["24 min"], [[["Samstag"], [[["Sa", "16:43-17:43"], []]]], [["F\u00e4hrt nicht am 10.04.2018"], [[["Mo, Di, Mi, Do, Fr", "16:43-alle 60 min-18:43"], []]]]]], [["21 min"], [[["Samstag"], [[["Sa", "18:42-alle 60 min-22:42"], []]]], [["so. u. fe."], [[["Di, So", "11:32-alle 60 min-21:32"], []]]], [["F\u00e4hrt nicht am 10.04.2018"], [[["Mo, Di, Mi, Do, Fr", "19:42-alle 60 min-22:42"], []]]]]]]]]], [["'''E104'''"], [[["'''Stadtmitte/Volme Galerie'''&nbsp;\u2192 '''Kabel'''", 18, "6,8 km"], [[["24 min"], [[["Nur an Schultagen. Nicht 12.+13.02., 11.05. und 01.06.2018."], [[["Mo, Di, Mi, Do, Fr", "13:20"], []]]]]]]]]], [["'''NE1'''"], [[["'''Stadtmitte/Volme Galerie'''&nbsp;\u2192 '''Bathey'''", 25, "9 km"], [[["27 min"], [[["Samstag"], [[["Sa", "21:32-alle 60 min-25:32"], []]]], [["so. u. fe."], [[["Di, So", "19:32-alle 60 min-23:32"], []]]], [["an Vorfeiertagen und in N\u00e4chten auf Samstag, Sonn- und Feiertag."], [[["Di, So", "24:32-25:32"], []], [["Mo, Mi, Do, Fr", "24:32-25:32"], []]]], [["Mo-Fr ohne Feiertage"], [[["Mo, Di, Mi, Do, Fr", "21:32-alle 60 min-23:32"], []]]]]]]], [["'''Bathey'''&nbsp;\u2192 '''Stadtmitte/Volme Galerie'''", 22, "8,4 km"], [[["27 min"], [[["Samstag"], [[["Sa", "22:00-alle 60 min-26:00"], []]]], [["so. u. fe."], [[["Di, So", "20:00-alle 60 min-24:00"], []]]], [["an Vorfeiertagen und in N\u00e4chten auf Samstag, Sonn- und Feiertag."], [[["Di, So", "25:00-26:00"], []], [["Mo, Mi, Do, Fr", "25:00-26:00"], []]]], [["Mo-Fr ohne Feiertage"], [[["Mo, Di, Mi, Do, Fr", "22:00-alle 60 min-24:00"], []]]]]]]]]]]
    a = fahrplanarray(lineids, placelist)
    # print(dumps(a), end="\n\n")
    # print(tableatext(a, 0, (("Linie"), ("Linienverlauf", "Haltestellen", "Strecke"), ("Fahrtzeit"), ("Einschränkung"), ("Wochentage", "Abfahrtszeiten"))), end="\n\n")

    tref = f"<ref name=\"VRR\">Basierend auf Fahrplandaten vom [[Verkehrsverbund Rhein-Ruhr]] ([https://www.openvrr.de/ OpenVRR]), {version.netid} {version.periodname} ({{{{FormatDate|{version.validfromstr}|M}}}}–{{{{FormatDate|{version.validtostr}|M}}}})</ref>"
    # name, sort type/unsortable
    linientcols = (("Linie", "text"),
                   ("Linienverlauf", "text"),
                   ("Haltestellen", "number"),
                   ("Strecke", "number"),
                   ("Fahrzeit", "number"),
                   ("Einschränkung", "text"),
                   ("Wochentage", "text"),
                   ("Abfahrtszeiten", "number"),
                   )
    linienfirstpre = "align=\"center\" style=\"background-color:#B404AE; color:white;\""

    wikitext = "Diese Seite wurde komplett aus DINO-Fahrplandaten vom [[Verkehrsverbund Rhein-Ruhr|VRR]] generiert<ref>https://github.com/d3d9/dino/blob/master/dino-wikitable.py</ref> und ist sehr experimentell. Dargestellt sind Fahrplaninformationen der [[Hagener Straßenbahn AG]].\n\n"
    if printstops:
        wikitext += "{{All Coordinates|pos=inline|section=Haltestellenliste}}\n\n"
    wikitext += "== Busverkehr ==\n=== Liniennetz ===\n==== " + ("Einsatzwagen" if onlyew else "Alles") + " ====\n"
    wikitext += wikitable(a, "Linien", tref, linientcols, linienfirstpre)
    wikitext += "\n==== Anmerkungen zu den Linien ====\n<references group=\"AnmL\"/>\n\n"

    if printstops:
        stopa = stoparray(stops)
        # print(tableatext(stopa, 0, (("Haltestelle", "IFOPT","Koordinaten", "Waben", "Kürzel"), ("Bereich", "IFOPT"), ("Steig", "IFOPT", "Koordinaten"))), end="\n\n")
        stoptcols = (("Haltestelle", "text"),
                     ("IFOPT", "text"),
                     ("Koordinaten", "unsortable"),
                     ("Waben", "number"),
                     ("Kürzel", "text"),
                     ("Bereich", "text"),
                     ("IFOPT", "text"),
                     ("Steig", "number"),
                     ("IFOPT", "text"),
                     ("Koordinaten", "unsortable"),
                     )

        wikitext += "== Haltestellen ==\n=== Haltestellenliste ===\n"
        wikitext += wikitable(stopa, "Haltestellen", "<ref name=\"VRR\" />", stoptcols)
        wikitext += "\n==== Anmerkungen zu den Haltestellen ====\n<references group=\"AnmH\"/>\n\n"

    wikitext += "== Einzelnachweise ==\n<references />\n"

    # print(wikitext, end="\n\n")
    with open(outfilename, 'w', encoding='utf-8') as f:
        f.write(wikitext)
        print(f"File {outfilename} written")
