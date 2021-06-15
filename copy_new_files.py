import json
import os, shutil

with open("Biobank_Bounding_Boxes.json","r") as f:
    bBDict = json.load(f)

currentFiles = os.listdir("./Data")
keys = [ x for x in bBDict.keys() if x not in currentFiles]

dataDirec = "D:/UKB_Liver/20204_2_0/"

for k in keys:
    if "Lungs" in bBDict[k].keys():
        if "Heart" in bBDict[k].keys():
            for i in range(1,7):
                try:
                    srcStr = os.path.join(dataDirec,"{}{}".format(i,k))
                    dstStr = os.path.join("./Data/","{}{}".format(i,k))
                    print(srcStr,dstStr)
                    shutil.copytree(srcStr,dstStr)
                except:
                    pass