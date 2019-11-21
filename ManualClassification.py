############# Programme for tagging of dicom images into Artefact Classes ##############
# 26/04/19
# Charles Hill

"""
Artefact List:

01 - Evidence of Motion
02 - Field Heterogeneity
03 - Susceptibility Artefact
04 - Shim Box Error
05 - Atypical RRs
06 - Mistriggering
07 - Low SNR
08 - Over-anonymised data
09 - Evidence of Fat/Water Swap
10 - Incorrect Protocol
11 - Protocol Modification
12 - Effect of high fat on T1
13 - Series not available
14 - Liver not in FOV
15 - Centre Frequency Variation
16 - Contrast agent suspected/confirmed
17 - Data acquired in subpotimal location
18 - Unsupported Acquisition Parameters

"""

# Python Standard Libraries
import os, time, sys, csv, copy, re

# Site packages
from PyQt5 import Qt, QtWidgets, QtCore, QtGui
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
import pydicom
from PIL import Image
import mahotas

# User Functions
from GUI_functions import general_layout

class UI_classification(QtWidgets.QMainWindow):
    """
    Things to Include:
        1) Image to analyse
        2) Drop down list of artefacts
        3) Current Tags
        4) confirmation buttons etc.
        5) Folder Selection (I/O)

        # Future
        - segmentation contouring
        - Linked Images
        - Multi User
    """
    def __init__(self,test=False,dm=True):
        super().__init__()
        self.dm = dm
        self.artefacts = {1:"Evidence of Motion",2:"Field Heterogeneity",3:"Susceptibility Artefact",4:"Shim Box Error",5:"Atypical RRs",6:"Mistriggering",7:"Low SNR",
                    8:"Over-anonymised data",9:"Evidence of Fat/Water Swap",10:"Incorrect Protocol",11:"Protocol Modification",12:"Effect of high fat on T1",13:"Series not available",
                    14:"Liver not in FOV",15:"Centre Frequency Variation",16:"Contrast agent suspected/confirmed",17:"Data acquired in suboptimal location",
                    18:"Unsupported Acquisition Parameters"}
        self.cropListOptions = ['Body','Heart','Cyst','Lung','Liver','Kidney','IVC','Aorta','Spleen']
        self.penColor = {'Liver':QtGui.QColor(255,0,0,255),'Body':QtGui.QColor(0,255,0,255),'Cyst':QtGui.QColor(0,0,255,255),'Lung':QtGui.QColor(255,0,255,255),
                        'Heart':QtGui.QColor(255,255,0,255),'Kidney':QtGui.QColor(255,0,0,255),'IVC':QtGui.QColor(0,255,0,255),'Aorta':QtGui.QColor(0,0,255,255),
                        'Spleen':QtGui.QColor(0,255,255,255)}
        self.brushColor = {'Liver':QtGui.QColor(255,0,0,255//10),'Body':QtGui.QColor(0,255,0,255//10),'Cyst':QtGui.QColor(0,0,255,255//10),'Lung':QtGui.QColor(255,0,255,255//10),
                        'Heart':QtGui.QColor(255,255,0,255//10),'Kidney':QtGui.QColor(255,0,0,255//10),'IVC':QtGui.QColor(0,255,0,255//10),'Aorta':QtGui.QColor(0,0,255,255//10),
                        'Spleen':QtGui.QColor(0,255,255,255//10)}
        self.curImg = 0
        self.curSub = 0
        self.imgDirec = "./Data/"
        self.PatientID = ''
        self.cropNum = 0
        self.test = test
        self.user = 'CH'
        self.boundingBoxCSV = 'Manual_Bounding_Boxes.csv'
        self.segmentationCSV = 'Segmentations.csv'
        self.cropList = []
        self.UI_setup()
        self.showFullScreen()
        #self.show()

    def UI_setup(self):
        general_layout(self,dark_mode=self.dm)
        self.l_img = QtWidgets.QLabel()
        self.t_hdrs = QtWidgets.QTableWidget()

        self.gb_artefacts = QtWidgets.QGroupBox("Object Classes")
        self.cb_artefacts = QtWidgets.QComboBox()
        self.t_artefacts = QtWidgets.QTableWidget()
        self.t_segmentations = QtWidgets.QTableWidget()
        self.b_delete_crop = QtWidgets.QPushButton("Delete Selected ROIs")
        self.b_redraw_crop = QtWidgets.QPushButton("Redraw Selected ROIs Only")
        self.cb_artefacts.addItems(self.artefacts.values())
        self.vBox_artefacts = QtWidgets.QVBoxLayout()
        self.vBox_artefacts.addWidget(self.t_artefacts)
        self.vBox_artefacts.addWidget(self.t_segmentations)
        self.vBox_artefacts.addWidget(self.cb_artefacts)
        self.vBox_artefacts.addWidget(self.b_delete_crop)
        self.vBox_artefacts.addWidget(self.b_redraw_crop)
        self.gb_artefacts.setLayout(self.vBox_artefacts)

        self.b_delete_crop.clicked.connect(self.delete_crops)
        self.b_redraw_crop.clicked.connect(self.redraw_crops)

        self.b_submit = QtWidgets.QPushButton("Submit Tags")
        self.b_clear = QtWidgets.QPushButton("Clear Tags")
        self.b_next_img = QtWidgets.QPushButton("Next Image")
        self.b_prev_img = QtWidgets.QPushButton("Previous Image")
        self.b_next_sub = QtWidgets.QPushButton("Next Subject")
        self.b_prev_sub = QtWidgets.QPushButton("Previous Subject")
        self.b_crop = QtWidgets.QPushButton("Crop Image")
        self.b_seg = QtWidgets.QPushButton("Segment Image")
        self.cb_classes = QtWidgets.QComboBox()
        self.cb_classes.addItems(self.cropListOptions)
        self.init_load_image()

        self.b_next_img.clicked.connect(lambda checked,button='next': self.change_img(button))
        self.b_prev_img.clicked.connect(lambda checked,button='prev': self.change_img(button))
        self.b_next_sub.clicked.connect(lambda checked,button='next': self.change_sub(button))
        self.b_prev_sub.clicked.connect(lambda checked,button='prev': self.change_sub(button))
        self.b_crop.clicked.connect(self.open_crop)
        self.b_seg.clicked.connect(self.open_seg)

        self.next_sub_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Right),self)
        self.next_sub_shortcut.activated.connect(lambda button='next': self.change_sub(button))
        self.prev_sub_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Left),self)
        self.prev_sub_shortcut.activated.connect(lambda button='prev': self.change_sub(button))
        self.next_img_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Up),self)
        self.next_img_shortcut.activated.connect(lambda button='next': self.change_img(button))
        self.prev_img_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Down),self)
        self.prev_img_shortcut.activated.connect(lambda button='prev': self.change_img(button))

        self.next_sub_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("D"),self)
        self.next_sub_shortcut.activated.connect(lambda button='next': self.change_sub(button))
        self.prev_sub_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("A"),self)
        self.prev_sub_shortcut.activated.connect(lambda button='prev': self.change_sub(button))
        self.next_img_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("W"),self)
        self.next_img_shortcut.activated.connect(lambda button='next': self.change_img(button))
        self.prev_img_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("S"),self)
        self.prev_img_shortcut.activated.connect(lambda button='prev': self.change_img(button))

        self.crop_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("1"),self)
        self.crop_shortcut.activated.connect(lambda cl='Liver' : self.open_crop(cl=cl))
        self.crop_shortcut_B = QtWidgets.QShortcut(QtGui.QKeySequence("2"),self)
        self.crop_shortcut_B.activated.connect(lambda cl='Body' : self.open_crop(cl=cl))
        self.crop_shortcut_C = QtWidgets.QShortcut(QtGui.QKeySequence("3"),self)
        self.crop_shortcut_C.activated.connect(lambda cl='Cyst' : self.open_crop(cl=cl))
        self.crop_shortcut_H = QtWidgets.QShortcut(QtGui.QKeySequence("4"),self)
        self.crop_shortcut_H.activated.connect(lambda cl='Heart' : self.open_crop(cl=cl))
        self.crop_shortcut_L = QtWidgets.QShortcut(QtGui.QKeySequence("5"),self)
        self.crop_shortcut_L.activated.connect(lambda cl='Lung' : self.open_crop(cl=cl))
        self.crop_shortcut_K = QtWidgets.QShortcut(QtGui.QKeySequence("6"),self)
        self.crop_shortcut_K.activated.connect(lambda cl='Kidney' : self.open_crop(cl=cl))
        self.crop_shortcut_IVC = QtWidgets.QShortcut(QtGui.QKeySequence("7"),self)
        self.crop_shortcut_IVC.activated.connect(lambda cl='IVC' : self.open_crop(cl=cl))
        self.crop_shortcut_A = QtWidgets.QShortcut(QtGui.QKeySequence("8"),self)
        self.crop_shortcut_A.activated.connect(lambda cl='Aorta' : self.open_crop(cl=cl))
        self.crop_shortcut_S = QtWidgets.QShortcut(QtGui.QKeySequence("9"),self)
        self.crop_shortcut_S.activated.connect(lambda cl='Spleen' : self.open_crop(cl=cl))

        self.seg_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+1"),self)
        self.seg_shortcut.activated.connect(lambda cl='Liver' : self.open_seg(cl=cl))
        self.seg_shortcut_B = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+2"),self)
        self.seg_shortcut_B.activated.connect(lambda cl='Body' : self.open_seg(cl=cl))
        self.seg_shortcut_C = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+3"),self)
        self.seg_shortcut_C.activated.connect(lambda cl='Cyst' : self.open_seg(cl=cl))
        self.seg_shortcut_H = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+4"),self)
        self.seg_shortcut_H.activated.connect(lambda cl='Heart' : self.open_seg(cl=cl))
        self.seg_shortcut_L = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+5"),self)
        self.seg_shortcut_L.activated.connect(lambda cl='Lung' : self.open_seg(cl=cl))
        self.seg_shortcut_K = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+6"),self)
        self.seg_shortcut_K.activated.connect(lambda cl='Kidney' : self.open_seg(cl=cl))
        self.seg_shortcut_IVC = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+7"),self)
        self.seg_shortcut_IVC.activated.connect(lambda cl='IVC' : self.open_seg(cl=cl))
        self.seg_shortcut_A = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+8"),self)
        self.seg_shortcut_A.activated.connect(lambda cl='Aorta' : self.open_seg(cl=cl))
        self.seg_shortcut_S = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+9"),self)
        self.seg_shortcut_S.activated.connect(lambda cl='Spleen' : self.open_seg(cl=cl))
        
        self.close_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("ESC"),self)
        self.close_shortcut.activated.connect(self.close)

        self.check = QtCore.QTimer()
        self.check.setInterval(1000)
        self.check.timeout.connect(self.check_for_crop)
        self.check.start()

        buttonBox = QtWidgets.QGridLayout()
        buttonBox.addWidget(self.b_submit,0,0,2,1)
        buttonBox.addWidget(self.b_clear,0,1,2,1)
        buttonBox.addWidget(self.b_next_img,0,2)
        buttonBox.addWidget(self.b_prev_img,0,3)
        buttonBox.addWidget(self.b_next_sub,1,2)
        buttonBox.addWidget(self.b_prev_sub,1,3)

        hBox = QtWidgets.QHBoxLayout()
        hBox.addWidget(self.t_hdrs)
        hBox.addWidget(self.l_img)
        hBox.addWidget(self.gb_artefacts)

        hBox2 = QtWidgets.QHBoxLayout()
        hBox2.addWidget(self.b_crop)
        hBox2.addWidget(self.b_seg)
        hBox2.addWidget(self.cb_classes)

        vBox = QtWidgets.QVBoxLayout()
        vBox.addLayout(hBox)
        vBox.addLayout(buttonBox)
        vBox.addLayout(hBox2)

        self.main_widget = QtWidgets.QWidget(self)
        self.main_widget.setLayout(vBox)
        self.setCentralWidget(self.main_widget)

    def init_load_image(self):
        self.numPatients = [os.path.join(self.imgDirec,x) for x in os.listdir(self.imgDirec) if x.endswith('0')]		
        self.imgsPatient = [x for x in os.listdir(self.numPatients[self.curSub]) if x.endswith('.dcm')]

        #self.numPatients = [os.path.join(self.imgDirec,x) for x in os.listdir(self.imgDirec) if x.endswith('3')]		
        #self.imgsPatient = [x for x in os.listdir(self.numPatients[self.curSub]) if x.endswith('.IMA')]

        self.curImg = int(np.random.choice(np.linspace(0,len(self.imgsPatient)-1,num=len(self.imgsPatient))))
        print("Number of Patients %i with %i images each" %(len(self.numPatients),len(self.imgsPatient)))

        dicom0 = pydicom.dcmread(os.path.join(self.numPatients[self.curSub],self.imgsPatient[self.curImg]),force=True)
        while 'P' in dicom0.ImageType:
            if self.curImg == len(self.imgsPatient)-1:
                self.curImg = 0
            else:
                self.curImg += 1
            dicom0 = pydicom.dcmread(os.path.join(self.numPatients[self.curSub],self.imgsPatient[self.curImg]),force=True)
        self.t_hdrs.setRowCount(len(dicom0))
        self.t_hdrs.setColumnCount(2)
        for line,i in zip(dicom0,range(len(dicom0))):
            tableItem = QtWidgets.QTableWidgetItem(str(line))
            self.t_hdrs.setItem(i,0,tableItem)
        self.t_hdrs.resizeColumnsToContents()
        self.pxArr = dicom0.pixel_array
        mpimg.imsave("Temp_Image.png",self.pxArr,cmap='gray')
        #ar32 = self.pxArr.astype(np.uint16)
        #tempImage = Image.fromarray(ar32)
        #tempImage.save("Temp_Image.png")
        img0Patient0 = QtGui.QPixmap("Temp_Image.png")
        self.l_img.setPixmap(img0Patient0.scaled(750, 1500, QtCore.Qt.KeepAspectRatio))
        self.PatientID = self.numPatients[self.curSub][7:]
        self.check_for_crop()

    def change_img(self,button):
        if button == "next":
            if self.curImg == len(self.imgsPatient)-1:
                self.curImg = 0
            else:
                self.curImg += 1
        elif button == "prev":
            if self.curImg == 0:
                self.curImg = len(self.imgsPatient)-1
            else:
                self.curImg -= 1

        dicom = pydicom.dcmread(os.path.join(self.numPatients[self.curSub],self.imgsPatient[self.curImg]),force=True)
        self.pxArr = dicom.pixel_array

        mpimg.imsave("Temp_Image.png",self.pxArr,cmap='gray')

        imgPatient = QtGui.QPixmap("Temp_Image.png")

        if self.boundingBoxCSV in os.listdir():
            painterImgPatient = QtGui.QPainter(imgPatient)
            with open(self.boundingBoxCSV,'r') as f:
                csvObj = csv.DictReader(f)
                for line in csvObj:
                    if self.PatientID in line['File']:
                        painterImgPatient.setPen(self.penColor[line['Object']])
                        painterImgPatient.drawRect(int(line['x0']),int(line['y0']),int(line['x1'])-int(line['x0']),int(line['y1'])-int(line['y0']))
            painterImgPatient.end()

        self.l_img.setPixmap(imgPatient.scaled(750, 1500, QtCore.Qt.KeepAspectRatio))
        self.l_img.update()
        self.update()

    def change_sub(self,button):
        self.cropNum = 0
        self.cropList = []
        currOrig = [os.path.join('./Data/',x[:-4]) for x in os.listdir('./Images/Original/')]
        #currTest = [os.path.join(self.imgDirec,x[:-4]) for x in os.listdir(self.imgDirec+'Original_Test/')]

        #currOrig = np.concatenate((currOrig,currTest))
        if button == "next":
            if self.curSub == len(self.numPatients)-1:
                self.curSub = 0
            else:
                self.curSub +=1
        elif button == "prev":
            if self.curSub == 0:
                self.curSub = len(self.numPatients)-1
            else:
                self.curSub -= 1

        while self.numPatients[self.curSub] in currOrig:
            if button == "next":
                if self.curSub == len(self.numPatients)-1:
                    self.curSub = 0
                else:
                    self.curSub +=1
            elif button == "prev":
                if self.curSub == 0:
                    self.curSub = len(self.numPatients)-1
                else:
                    self.curSub -= 1
        self.PatientID = self.numPatients[self.curSub][7:]

        self.imgsPatient = [x for x in os.listdir(self.numPatients[self.curSub]) if x.endswith('.dcm')]
        self.curImg = int(np.random.choice(np.linspace(0,len(self.imgsPatient)-1,num=len(self.imgsPatient))))

        dicom = pydicom.dcmread(os.path.join(self.numPatients[self.curSub],self.imgsPatient[self.curImg]),force=True)
        while 'P' in dicom.ImageType:
            if self.curImg == len(self.imgsPatient)-1:
                self.curImg = 0
            else:
                self.curImg += 1
            dicom = pydicom.dcmread(os.path.join(self.numPatients[self.curSub],self.imgsPatient[self.curImg]),force=True)
        self.pxArr = dicom.pixel_array
        mpimg.imsave("Temp_Image.png",self.pxArr,cmap='gray')
        imgPatient = QtGui.QPixmap("Temp_Image.png")

        if self.boundingBoxCSV in os.listdir():
            painterImgPatient = QtGui.QPainter(imgPatient)
            with open(self.boundingBoxCSV,'r') as f:
                csvObj = csv.DictReader(f)
                for line in csvObj:
                    if self.PatientID in line['File']:
                        painterImgPatient.setPen(self.penColor[line['Object']])
                        painterImgPatient.drawRect(int(line['x0']),int(line['y0']),int(line['x1'])-int(line['x0']),int(line['y1'])-int(line['y0']))
            painterImgPatient.end()

        self.l_img.setPixmap(imgPatient.scaled(750, 1500, QtCore.Qt.KeepAspectRatio))
        self.l_img.update()
        self.update_table()
        self.update()

    def open_crop(self,cl=False):
        if not cl:
            cl = self.cb_classes.currentText()
        self.crop = QCropLabel(image='Temp_Image.png',PatientID=self.PatientID,cl=cl,cropNum=self.cropNum,test=self.test,user=self.user)
        mpimg.imsave("./Images/Original/"+self.PatientID+".png",self.pxArr,cmap='gray')
        if cl in ['Lung','Cyst']:
            self.cropNum += 1
        self.crop.show()

    def open_seg(self,cl=False):
        if not cl:
            cl = self.cb_classes.currentText()
        self.crop = QCropLabel_Segmentation(image='Temp_Image.png',PatientID=self.PatientID,cl=cl,cropNum=self.cropNum,test=self.test,user=self.user)
        mpimg.imsave("./Images/Original/"+self.PatientID+".png",self.pxArr,cmap='gray')
        self.crop.show()

    def check_for_crop(self):
        update = False
        if self.boundingBoxCSV in os.listdir():
            imgPatient = QtGui.QPixmap("Temp_Image.png")
            painterImgPatient = QtGui.QPainter(imgPatient)         
            with open(self.boundingBoxCSV,'r') as f:
                csvObj = csv.DictReader(f)
                for line in csvObj:
                    if self.PatientID in line['File']:
                        painterImgPatient.setPen(self.penColor[line['Object']])
                        painterImgPatient.drawRect(int(line['x0']),int(line['y0']),int(line['x1'])-int(line['x0']),int(line['y1'])-int(line['y0']))
                        if line not in self.cropList:
                            update = True
                            self.cropList.append(line)

        if self.segmentationCSV in os.listdir():
            with open(self.segmentationCSV,'r') as f:
                csvObj = csv.DictReader(f)
                for line in csvObj:
                    if self.PatientID in line['File']:
                        painterImgPatient.setPen(self.penColor[line['Object']])
                        painterImgPatient.setBrush(self.brushColor[line['Object']])
                        polygon = QtGui.QPolygon()
                        points = self.format_points(line['Points'])
                        for pnts in points:
                            qP = QtCore.QPoint(pnts[0]*384//800,pnts[1]*288//600)
                            polygon.append(qP)

                        painterImgPatient.drawPolygon(polygon,fillRule=QtCore.Qt.OddEvenFill)
                        update = True
            
            painterImgPatient.end()

        if update:
            self.update_table()
            self.l_img.setPixmap(imgPatient.scaled(750, 1500, QtCore.Qt.KeepAspectRatio))
            self.l_img.update()
            self.update()

    def update_table(self):
        rowCnt = 0
        tempList = []
        with open(self.boundingBoxCSV,'r') as f:
            csvObj = csv.DictReader(f)
            for line in csvObj:
                if self.PatientID in line['File']:
                    tempList.append([line['Object'],line['x0'],line['y0'],line['x1'],line['y1']])
                    rowCnt += 1
        self.t_artefacts.setRowCount(rowCnt)
        self.t_artefacts.setColumnCount(5)

        for ii,li in enumerate(tempList):
            for jj,itm in enumerate(li):
                tableItem = QtWidgets.QTableWidgetItem(itm)
                self.t_artefacts.setItem(ii,jj,tableItem)

        self.t_artefacts.setHorizontalHeaderItem(0,QtWidgets.QTableWidgetItem('Object'))
        self.t_artefacts.setHorizontalHeaderItem(1,QtWidgets.QTableWidgetItem('x0'))
        self.t_artefacts.setHorizontalHeaderItem(2,QtWidgets.QTableWidgetItem('y0'))
        self.t_artefacts.setHorizontalHeaderItem(3,QtWidgets.QTableWidgetItem('x1'))
        self.t_artefacts.setHorizontalHeaderItem(4,QtWidgets.QTableWidgetItem('y1'))

        rowCnt = 0
        tempList = []
        with open(self.segmentationCSV,'r') as f:
            csvObj = csv.DictReader(f)
            for line in csvObj:
                if self.PatientID in line['File']:
                    tempList.append([line['Object'],line['Points']])
                    rowCnt += 1
        self.t_segmentations.setRowCount(rowCnt)
        self.t_segmentations.setColumnCount(2)

        for ii,li in enumerate(tempList):
            for jj,itm in enumerate(li):
                tableItem = QtWidgets.QTableWidgetItem(itm)
                self.t_segmentations.setItem(ii,jj,tableItem)

        self.t_segmentations.setHorizontalHeaderItem(0,QtWidgets.QTableWidgetItem('Object'))
        self.t_segmentations.setHorizontalHeaderItem(1,QtWidgets.QTableWidgetItem('Points'))

        self.update()

    def delete_crops(self):
        itemRemove = self.t_artefacts.currentItem()
        curRow = self.t_artefacts.currentRow()
        numCols = self.t_artefacts.columnCount()
        tempStr = self.PatientID
        for i in range(numCols):
            tempStr = ','.join((tempStr,self.t_artefacts.item(curRow,i).text()))
        with open(self.boundingBoxCSV,'r') as inp, open('temp.csv','w',newline='') as out:
            reader = csv.DictReader(inp)
            writer = csv.DictWriter(out,fieldnames=reader.fieldnames)
            writer.writeheader()
            for row in reader:
                tempStr2 = ','.join(row.values())
                if tempStr2 != tempStr:
                    writer.writerow(row)
        self.t_artefacts.removeRow(self.t_artefacts.currentRow())
        os.remove(self.boundingBoxCSV)
        os.rename('temp.csv',self.boundingBoxCSV)

        imgPatient = QtGui.QPixmap("Temp_Image.png")

        painterImgPatient = QtGui.QPainter(imgPatient)
        with open(self.boundingBoxCSV,'r') as f:
            csvObj = csv.DictReader(f)
            for line in csvObj:
                if self.PatientID in line['File']:
                    painterImgPatient.setPen(self.penColor[line['Object']])
                    painterImgPatient.drawRect(int(line['x0']),int(line['y0']),int(line['x1'])-int(line['x0']),int(line['y1'])-int(line['y0']))
        painterImgPatient.end()

        self.l_img.setPixmap(imgPatient.scaled(750, 1500, QtCore.Qt.KeepAspectRatio))
        self.l_img.update()
        self.update()

    def redraw_crops(self):
        itemDraw = self.t_artefacts.currentItem()
        curRow = self.t_artefacts.currentRow()
        numCols = self.t_artefacts.columnCount()
        tempList = []
        for i in range(numCols):
            tempList.append(self.t_artefacts.item(curRow,i).text())

        imgPatient = QtGui.QPixmap("Temp_Image.png")

        painterImgPatient = QtGui.QPainter(imgPatient)
        for itm in tempList:
            painterImgPatient.setPen(self.penColor[tempList[0]])
            painterImgPatient.drawRect(int(tempList[1]),int(tempList[2]),int(tempList[3])-int(tempList[1]),int(tempList[4])-int(tempList[2]))
        painterImgPatient.end()

        self.l_img.setPixmap(imgPatient.scaled(750, 1500, QtCore.Qt.KeepAspectRatio))
        self.l_img.update()
        self.update()

    def format_points(self,line):
        # str like "[(384, 326), (369, 340), (359, 355)]"
        m = re.findall(r'\d+',line)
        it = iter(m)
        retList = [(int(x),int(next(it))) for x in it]
        return retList

class QCropLabel (QtWidgets.QLabel):
    def __init__(self,image='Temp_Image.png',PatientID='',cl='Liver',cropNum=0,test=False,user='CH',parentQWidget = None):
        super(QCropLabel, self).__init__(parentQWidget)
        self.image = image
        self.PatientID = PatientID
        self.cl = cl
        self.cropNum = cropNum
        self.test = test
        self.imgDirec = "./Data/"
        self.user = user
        self.setWindowTitle('Select Crop Location')
        self.initUI()

    def initUI (self):
        self.setPixmap(QtGui.QPixmap(self.image))
        self.crop_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(" "),self)
        self.crop_shortcut.activated.connect(self.close_app)

    def mousePressEvent (self, eventQMouseEvent):
        self.originQPoint = eventQMouseEvent.pos()
        self.currentQRubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        self.currentQRubberBand.setGeometry(QtCore.QRect(self.originQPoint, QtCore.QSize()))
        self.currentQRubberBand.show()

    def mouseMoveEvent (self, eventQMouseEvent):
        self.currentQRubberBand.setGeometry(QtCore.QRect(self.originQPoint, eventQMouseEvent.pos()).normalized())

    def mouseReleaseEvent (self, eventQMouseEvent):
        self.currentQRubberBand.hide()

        currentQRect = self.currentQRubberBand.geometry()
        self.coord = currentQRect.getCoords()

        self.currentQRubberBand.deleteLater()
        cropQPixmap = self.pixmap().copy(currentQRect)

        if self.cl in ['Liver','Body','Heart']:
            cropQPixmap.save("./Images/"+self.cl+"/"+self.PatientID+'.png')
        if self.cl in ['Cyst','Lung']:
            currentCrops = os.listdir("./Images/"+self.cl+"/")
            cropNum = 0
            for crop in currentCrops:
                if self.PatientID in crop:
                    cropNum += 1
            cropQPixmap.save("./Images/"+self.cl+"/"+self.PatientID+'_'+str(cropNum)+'.png')

    def saveBoundingBox(self):
        """
        Writes a csvFile of the Patient Tag, Object cropped and the coordinates.
        
        Tags the work to a user as well for reproducibility study.
        
        Will need to write a function to unpack and format.

        NOTE: Can crop any object multiple times, could be used for reproducibility study, but will have to be aware.
        """
        csvfN = 'Manual_Bounding_Boxes.csv'
        fNames = ['File','Object','x0','y0','x1','y1']
        if csvfN not in os.listdir():
            with open(csvfN,'w',newline='') as f:
                csvObj = csv.DictWriter(f,fieldnames=fNames)
                csvObj.writeheader()
        saveDict = {'File':self.PatientID,'Object':self.cl,'x0':self.coord[0],'y0':self.coord[1],'x1':self.coord[2],'y1':self.coord[3]}
        with open(csvfN,'a',newline='') as f:
            csvObj = csv.DictWriter(f,fieldnames=fNames)
            csvObj.writerow(saveDict)

    def close_app(self):
        self.saveBoundingBox()
        self.close()

class QCropLabel_Segmentation (QtWidgets.QLabel):

    def __init__(self,image='Temp_Image.png',PatientID='',cl='Liver',cropNum=0,test=False,user='CH',parentQWidget = None):
        super(QCropLabel_Segmentation, self).__init__(parentQWidget)
        self.image = image
        self.segColor = {'Liver':1,'Body':2,'Cyst':3,'Lung':4,'Heart':5,'Kidney':6,'IVC':7,'Aorta':8,'Spleen':9}
        self.scaling = 800
        self.imgDims = (384,288)
        self.PatientID = PatientID
        self.cl = cl
        self.cropNum = cropNum
        self.test = test
        self.imgDirec = "./Data/"
        self.user = user
        self.setWindowTitle('Select Crop Location')

        self.myPenWidth = 5
        self.myPenColor = QtGui.QColor(255,0,255,255)
        self.myBrushColor = QtGui.QColor(255,0,255,255//10)
        self.myBrush = QtGui.QBrush(self.myBrushColor)

        self.points = []
        self.formatPoints = []
        self.firstPoint = True
        self.initUI()

    def initUI (self):
        self.setPixmap(QtGui.QPixmap(self.image).scaled(self.scaling,self.scaling,QtCore.Qt.KeepAspectRatio))
        self.closeShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("ESC"),self)
        self.closeShortcut.activated.connect(self.close_app)

        self.drawPolygon = QtWidgets.QShortcut(QtGui.QKeySequence("P"),self)
        self.drawPolygon.activated.connect(self.draw_function)

        self.deletePoints = QtWidgets.QShortcut(QtGui.QKeySequence("Del"),self)
        self.deletePoints.activated.connect(self.delete_points)

        self.savePoints = QtWidgets.QShortcut(QtGui.QKeySequence(" "),self)
        self.savePoints.activated.connect(self.save_points)

    def mousePressEvent (self, eventQMouseEvent):
        if eventQMouseEvent.button() == QtCore.Qt.LeftButton:
            if self.firstPoint:
                self.points.append(eventQMouseEvent.pos())
                self.firstPoint = False
            else:
                imgPaint = QtGui.QPixmap(self.image).scaled(self.scaling,self.scaling,QtCore.Qt.KeepAspectRatio)
                scaling = imgPaint.size().height()-self.height()
                painter = QtGui.QPainter(imgPaint)
                painter.setPen(self.myPenColor)
                self.points.append(eventQMouseEvent.pos())
                for ii,pnt in enumerate(self.points):
                    if ii != 0:
                        painter.drawLine(self.points[ii-1].x(),self.points[ii-1].y()+scaling//2,pnt.x(),pnt.y()+scaling//2)
                painter.end()
                self.setPixmap(imgPaint)
                self.update() 

    def draw_function(self):
        imgPaint = QtGui.QPixmap(self.image).scaled(self.scaling,self.scaling,QtCore.Qt.KeepAspectRatio)
        scaling = imgPaint.size().height()-self.height()
        painter = QtGui.QPainter(imgPaint)
        painter.setPen(self.myPenColor)
        painter.setBrush(self.myBrush)
        polygon = QtGui.QPolygon()
        for pnt in self.points:
            polygon.append(pnt)
        painter.drawPolygon(polygon,fillRule=QtCore.Qt.OddEvenFill)
        painter.end()
        self.setPixmap(imgPaint)
        self.update()

    def delete_points(self):
        self.points = []
        imgPaint = QtGui.QPixmap(self.image).scaled(self.scaling,self.scaling,QtCore.Qt.KeepAspectRatio)
        self.setPixmap(imgPaint)
        self.update()

    def save_points(self):
        """
        Writes a csvFile of the Patient Tag, Object cropped and the points.
        """
        self.format_points()
        csvfN = 'Segmentations.csv'
        fNames = ['File','Object','Points']
        if csvfN not in os.listdir():
            with open(csvfN,'w',newline='') as f:
                csvObj = csv.DictWriter(f,fieldnames=fNames)
                csvObj.writeheader()
        saveDict = {'File':self.PatientID,'Object':self.cl,'Points':self.formatPoints}
        with open(csvfN,'a',newline='') as f:
            csvObj = csv.DictWriter(f,fieldnames=fNames)
            csvObj.writerow(saveDict)

        self.close_app()

    def format_points(self):
        for qP in self.points:
            self.formatPoints.append((qP.x(),qP.y()))

    def save_mask(self):
        fName = self.PatientID+'_MASK.npy'
        
        if fName in os.listdir('./Masks/'):
            canvas = np.load('./Masks/'+fName)
        else:
            canvas = np.zeros((self.imgDims[1],self.imgDims[0]))

        tempPoints = []
        for pnt in self.formatPoints:
            tempPoints.append((pnt[1]*self.imgDims[1]//(self.scaling*self.imgDims[1]//self.imgDims[0]),pnt[0]*self.imgDims[0]//self.scaling))

        mahotas.polygon.fill_polygon(tempPoints,canvas,color=self.segColor[self.cl])

        np.save('./Masks/'+self.PatientID+'_MASK',canvas)

    def close_app(self):
        self.save_mask()
        self.close()   

def main():
    myQApplication = QtWidgets.QApplication(sys.argv)
    myQExampleLabel = QCropLabel_Segmentation()
    myQExampleLabel.show()
    sys.exit(myQApplication.exec_())
    return 0    

if __name__ == "__main__":
    main()