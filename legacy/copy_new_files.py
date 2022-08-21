import json
import os, shutil

with open("Biobank_Bounding_Boxes.json","r") as f:
    bBDict = json.load(f)

currentFiles = os.listdir("./Data")
keys = [ x for x in bBDict.keys() if x not in currentFiles]

dataDirec = "D:/UKB_Liver/20204_2_0/"

cnt = 0
for k in keys:
    if "Liver" not in bBDict[k].keys():
        cnt += 1
        for i in range(1,7):
            try:
                srcStr = os.path.join(dataDirec,"{}{}".format(i,k))
                dstStr = os.path.join("./Data/","{}{}".format(i,k))
                shutil.copytree(srcStr,dstStr)
            except:
                pass

print(cnt)

newFolders = [os.path.join("./Data/",x) for x in os.listdir("./Data")]

for fol in newFolders:
    if len(os.listdir(fol)) != 24:
        shutil.rmtree(fol)
        cnt -= 1

print(cnt)