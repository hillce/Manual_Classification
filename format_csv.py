import csv

csvDict = {}
with open("Manual_Bounding_Boxes.csv","r") as f:
    csvObj = csv.DictReader(f)
    for line in csvObj:
        print(line)
        if line['File'] not in csvDict.keys():
            csvDict[line["File"]] = []
        csvDict[line["File"]].extend([line['Object'],line['x0'],line['y0'],line['x1'],line['y1']])


keys = csvDict.keys()


with open("data.csv","w",newline="") as f:
    csvObj = csv.writer(f)
    for k in keys:
        tempList = [k]
        tempList.extend(csvDict[k])
        csvObj.writerow(tempList)



