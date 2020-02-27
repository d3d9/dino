import pandas
from DINO import nullorstrip

def tworowbox(length, row1, row2, row3="", row4=""):
    double = bool((row3 or row4) and not ((row1 == row3) and (row2 == row4)))
    print((" "+"-"*length+" ")*(1+double))
    print("|"+("{:^"+str(length)+"}").format(row1), end="|")
    print(("|"+("{:^"+str(length)+"}").format(row3)+"|") if double else "")
    print("|"+("{:^"+str(length)+"}").format(row2), end="|")
    print(("|"+("{:^"+str(length)+"}").format(row4)+"|") if double else "")
    print((" "+"-"*length+" ")*(1+double))

with open("./dino2.1/vehicle_destination_text.din", 'r') as vdtfile:
    vdt = pandas.read_csv(vdtfile, skipinitialspace=True, sep=';', dtype={'VERSION':int,'BRANCH_NR':str,'VDT_NR':int,
                                                                          'VDT_TEXT_DRIVER1':str, 'VDT_TEXT_DRIVER2':str,
                                                                          'VDT_TEXT_FRONT1':str, 'VDT_TEXT_FRONT2':str,
                                                                          'VDT_TEXT_FRONT3':str, 'VDT_TEXT_FRONT4':str,
                                                                          'VDT_TEXT_SIDE1':str, 'VDT_TEXT_SIDE2':str,
                                                                          'VDT_TEXT_SIDE3':str, 'VDT_TEXT_SIDE4':str,
                                                                          'VDT_LONG_NAME':str, 'VDT_SHORT_NAME':str}, index_col=2)

versionid = 11

maxfront = max(max([(len(nullorstrip(row['VDT_TEXT_FRONT1'])), nullorstrip(row['VDT_TEXT_FRONT1'])) for index, row in vdt.query("VERSION == @versionid").iterrows()]),
               max([(len(nullorstrip(row['VDT_TEXT_FRONT2'])), nullorstrip(row['VDT_TEXT_FRONT2'])) for index, row in vdt.query("VERSION == @versionid").iterrows()]),
               max([(len(nullorstrip(row['VDT_TEXT_FRONT3'])), nullorstrip(row['VDT_TEXT_FRONT3'])) for index, row in vdt.query("VERSION == @versionid").iterrows()]),
               max([(len(nullorstrip(row['VDT_TEXT_FRONT4'])), nullorstrip(row['VDT_TEXT_FRONT4'])) for index, row in vdt.query("VERSION == @versionid").iterrows()]))[0]

maxside = max(max([(len(nullorstrip(row['VDT_TEXT_SIDE1'])), nullorstrip(row['VDT_TEXT_SIDE1'])) for index, row in vdt.query("VERSION == @versionid").iterrows()]),
              max([(len(nullorstrip(row['VDT_TEXT_SIDE2'])), nullorstrip(row['VDT_TEXT_SIDE2'])) for index, row in vdt.query("VERSION == @versionid").iterrows()]),
              max([(len(nullorstrip(row['VDT_TEXT_SIDE3'])), nullorstrip(row['VDT_TEXT_SIDE3'])) for index, row in vdt.query("VERSION == @versionid").iterrows()]),
              max([(len(nullorstrip(row['VDT_TEXT_SIDE4'])), nullorstrip(row['VDT_TEXT_SIDE4'])) for index, row in vdt.query("VERSION == @versionid").iterrows()]))[0]

for index, row in vdt.query("VERSION == @versionid").iterrows():
    frow1 = nullorstrip(row['VDT_TEXT_FRONT1'])
    frow2 = nullorstrip(row['VDT_TEXT_FRONT2'])
    frow3 = nullorstrip(row['VDT_TEXT_FRONT3'])
    frow4 = nullorstrip(row['VDT_TEXT_FRONT4'])
    srow1 = nullorstrip(row['VDT_TEXT_SIDE1'])
    srow2 = nullorstrip(row['VDT_TEXT_SIDE2'])
    srow3 = nullorstrip(row['VDT_TEXT_SIDE3'])
    srow4 = nullorstrip(row['VDT_TEXT_SIDE4'])
    print(index, "front")
    tworowbox(maxfront, frow1, frow2, frow3, frow4)
    print(index, "side")
    tworowbox(maxside, srow1, srow2, srow3, srow4)
    print()
