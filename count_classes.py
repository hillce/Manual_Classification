import csv
import os
import re

with open("data.csv","r") as f:
    csvObj = csv.reader(f)
    coords = [line[1:] for line in csvObj]


overList = []
for li in coords:
    classes = [x for x in li if not x.isdigit()]
    overList.extend(classes)

for cl in set(overList):
    print(cl,overList.count(cl))

print(set(overList))

