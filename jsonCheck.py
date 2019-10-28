import json
import time

def jsonCheck(tagOI):
    with open("UK_Biobank_large_test_n19695.json",'r') as f:
        datastore = json.load(f)

    lines = []
    with open("bFile_shMOLLI.txt",'r',newline="\n") as f:
        for line in f:
            lines.append(line)

    outTag = []
    for i in range(len(datastore)):
        for line in lines:
            if str(datastore[i]["id"]) in line:
                if tagOI in str(datastore[i]["Tags"]):
                    outTag.append(line)

    with open(tagOI+'.txt','w') as f:
        f.writelines(outTag)

def tagTypes():
    with open("UK_Biobank_large_test_n19695.json",'r') as f:
        datastore = json.load(f)

    total_tags = []
    for i in range(len(datastore)):
        tempTags = datastore[i]["Tags"]
        try:
            if tempTags not in total_tags:
                total_tags.append(tempTags)
        except:
            pass

    print(total_tags)

def duplicateCheck():
    cysts = []
    with open("Cysts.txt",'r',newline="\n") as f:
        for line in f:
            cysts.append(line)

    wrongslice = []
    with open("wrongslice.txt",'r',newline="\n") as f:
        for line in f:
            wrongslice.append(line)

    print(len(cysts))
    print(len(wrongslice))

    notDupl = []
    Dupl = []
    for item in wrongslice:
        isDupl = False
        for line in cysts:
            if line == item:
                Dupl.append(item)
                isDupl = True
        if isDupl == False:
            notDupl.append(item)

    print(len(Dupl))
    print(len(notDupl))

    with open('Duplwrongslice.txt','w') as f:
        f.writelines(Dupl)

def csvSort():
    t0 = time.time()
    fileName = "C:/Users/shug4421/UKB_Liver/shMOLLI_10765/ukb24794.csv"
    targetF = "C:/Users/shug4421/UKB_Liver/shMOLLI_10765/bFile_DIXON.txt"
    with open(targetF,'w') as targF:
        with open(fileName,'r') as f:
            csvFile = csv.DictReader(f)
            i = 1
            for line in csvFile:
                if line['20201-2.0'] == '20201_2_0':
                    targF.write(line['eid']+" "+line['20201-2.0']+"\n")
                    if i % 1000 == 0:
                        print("Line "+str(i)+" Elapsed Time: "+str(time.time()-t0),end='\r', flush=True)
                    i += 1        

def json2List():
    with open("TagLists/UK_Biobank_large_test_n19695.json",'r') as f:
        datastore = json.load(f)

    idTags = []
    for i in range(len(datastore)):
        idTags.append([datastore[i]['id'],datastore[i]['Tags']])

    with open("TagLists/TagList.txt",'w') as f:
        for iD in idTags:
            f.write(str(iD[0])+' '+str(iD[1])+'\n')
    print(idTags)


json2List()