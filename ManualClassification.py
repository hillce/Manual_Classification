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
import os, time, sys, csv

# Site packages
from PyQt5 import Qt, QtWidgets, QtCore, QtGui
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import nibabel
import pydicom
import qimage2ndarray as q2nd
import scipy.misc

# User Functions

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
	def __init__(self,test=False):
		super().__init__()
		self.artefacts = {1:"Evidence of Motion",2:"Field Heterogeneity",3:"Susceptibility Artefact",4:"Shim Box Error",5:"Atypical RRs",6:"Mistriggering",7:"Low SNR",
					8:"Over-anonymised data",9:"Evidence of Fat/Water Swap",10:"Incorrect Protocol",11:"Protocol Modification",12:"Effect of high fat on T1",13:"Series not available",
					14:"Liver not in FOV",15:"Centre Frequency Variation",16:"Contrast agent suspected/confirmed",17:"Data acquired in suboptimal location",
					18:"Unsupported Acquisition Parameters"}
		self.curImg = 0
		self.curSub = 0
		self.imgDirec = "C:/Users/shug4421/UKB_Liver/shMOLLI/Data/"
		self.PatientID = ''
		self.cropNum = 0
		self.test = test
		self.UI_setup()
		self.showFullScreen()

	def UI_setup(self):
		self.l_img = QtWidgets.QLabel()
		self.t_hdrs = QtWidgets.QTableWidget()
		self.init_load_image()

		self.gb_artefacts = QtWidgets.QGroupBox("Artefact Classes")
		self.cb_artefacts = QtWidgets.QComboBox()
		self.t_artefacts = QtWidgets.QTableWidget()
		self.load_classification()
		self.cb_artefacts.addItems(self.artefacts.values())
		self.vBox_artefacts = QtWidgets.QVBoxLayout()
		self.vBox_artefacts.addWidget(self.t_artefacts)
		self.vBox_artefacts.addWidget(self.cb_artefacts)
		self.gb_artefacts.setLayout(self.vBox_artefacts)

		self.b_submit = QtWidgets.QPushButton("Submit Tags")
		self.b_clear = QtWidgets.QPushButton("Clear Tags")
		self.b_next_img = QtWidgets.QPushButton("Next Image")
		self.b_prev_img = QtWidgets.QPushButton("Previous Image")
		self.b_next_sub = QtWidgets.QPushButton("Next Subject")
		self.b_prev_sub = QtWidgets.QPushButton("Previous Subject")
		self.b_crop = QtWidgets.QPushButton("Crop Image")

		self.b_next_img.clicked.connect(lambda checked,button='next': self.change_img(button))
		self.b_prev_img.clicked.connect(lambda checked,button='prev': self.change_img(button))
		self.b_next_sub.clicked.connect(lambda checked,button='next': self.change_sub(button))
		self.b_prev_sub.clicked.connect(lambda checked,button='prev': self.change_sub(button))
		self.b_crop.clicked.connect(self.open_crop)

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
		self.crop_shortcut.activated.connect(self.open_crop)
		self.crop_shortcut_C = QtWidgets.QShortcut(QtGui.QKeySequence("3"),self)
		self.crop_shortcut_C.activated.connect(lambda cl='Cyst' : self.open_crop(cl=cl))
		self.crop_shortcut_H = QtWidgets.QShortcut(QtGui.QKeySequence("4"),self)
		self.crop_shortcut_H.activated.connect(lambda cl='Heart' : self.open_crop(cl=cl))
		self.crop_shortcut_L = QtWidgets.QShortcut(QtGui.QKeySequence("5"),self)
		self.crop_shortcut_L.activated.connect(lambda cl='Lung' : self.open_crop(cl=cl))
		self.crop_shortcut_B = QtWidgets.QShortcut(QtGui.QKeySequence("2"),self)
		self.crop_shortcut_B.activated.connect(lambda cl='Body' : self.open_crop(cl=cl))

		self.close_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("ESC"),self)
		self.close_shortcut.activated.connect(self.close)

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

		vBox = QtWidgets.QVBoxLayout()
		vBox.addLayout(hBox)
		vBox.addLayout(buttonBox)
		vBox.addWidget(self.b_crop)

		self.main_widget = QtWidgets.QWidget(self)
		self.main_widget.setLayout(vBox)
		self.setCentralWidget(self.main_widget)


	def init_load_image(self):
		self.numPatients = [os.path.join(self.imgDirec,x) for x in os.listdir(self.imgDirec) if x.endswith('0')]
		self.imgsPatient = [x for x in os.listdir(self.numPatients[self.curSub]) if x.endswith('.dcm')]
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
		scipy.misc.imsave("Temp_Image.png",self.pxArr)
		img0Patient0 = QtGui.QPixmap("Temp_Image.png")
		self.l_img.setPixmap(img0Patient0.scaled(1000, 2000, QtCore.Qt.KeepAspectRatio))
		self.PatientID = self.numPatients[self.curSub][41:]

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
		scipy.misc.imsave("Temp_Image.png",self.pxArr)
		imgPatient = QtGui.QPixmap("Temp_Image.png")
		self.l_img.setPixmap(imgPatient.scaled(1000, 2000, QtCore.Qt.KeepAspectRatio))
		self.l_img.update()
		self.update()

	def change_sub(self,button):
		self.cropNum = 0
		currOrig = [os.path.join(self.imgDirec,x[:-4]) for x in os.listdir(self.imgDirec+'Original/')]
		currTest = [os.path.join(self.imgDirec,x[:-4]) for x in os.listdir(self.imgDirec+'Original_Test/')]

		currOrig = np.concatenate((currOrig,currTest))
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
		self.PatientID = self.numPatients[self.curSub][41:]

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
		scipy.misc.imsave("Temp_Image.png",self.pxArr)
		imgPatient = QtGui.QPixmap("Temp_Image.png")
		self.l_img.setPixmap(imgPatient.scaled(1000, 2000, QtCore.Qt.KeepAspectRatio))
		self.l_img.update()
		self.update()

	def save_classification(self):
		return 0

	def load_classification(self):
		return 0

	def open_crop(self,cl='Liver'):
		self.crop = QCropLabel(image='Temp_Image.png',PatientID=self.PatientID,cl=cl,cropNum=self.cropNum,test=self.test)
		if self.test:
			scipy.misc.imsave(self.imgDirec+"Original_Test/"+self.PatientID+".png",self.pxArr)
		if cl in ['Lung','Cyst']:
			self.cropNum += 1
		self.crop.show()

class QCropLabel (QtWidgets.QLabel):
	def __init__(self,image='Temp_Image.png',PatientID='',cl='Liver',cropNum=0,test=False,parentQWidget = None):
		super(QCropLabel, self).__init__(parentQWidget)
		self.image = image
		self.PatientID = PatientID
		self.cl = cl
		self.cropNum = cropNum
		self.test = test
		self.imgDirec = "C:/Users/shug4421/UKB_Liver/shMOLLI/Data/"
		self.setWindowTitle('Select Crop Location')
		self.initUI()

	def initUI (self):
		self.setPixmap(QtGui.QPixmap(self.image))
		self.crop_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(" "),self)
		self.crop_shortcut.activated.connect(self.close)

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
		self.currentQRubberBand.deleteLater()
		cropQPixmap = self.pixmap().copy(currentQRect)
		if self.test:
			if self.cl in ['Liver','Body','Heart']:
				cropQPixmap.save(self.imgDirec+self.cl+"_Test_Cropped/"+self.PatientID+'_crop.png')
			if self.cl in ['Cyst','Lung']:
				cropQPixmap.save(self.imgDirec+self.cl+"_Test_Cropped/"+self.PatientID+'_crop_'+str(self.cropNum)+'.png')
		else:
			if self.cl in ['Liver','Body','Heart']:
				cropQPixmap.save(self.imgDirec+self.cl+"_Cropped/"+self.PatientID+'_crop.png')
			if self.cl in ['Cyst','Lung']:
				cropQPixmap.save(self.imgDirec+self.cl+"_Cropped/"+self.PatientID+'_crop_'+str(self.cropNum)+'.png')



class Classification_CSV():
	def __init__(self,fileName):
		super().__init__()
		self.fileName = fileName
		self.headers = ['Patient ID','Image ID','Artefacts']
		self.artefacts = {1:"Evidence of Motion",2:"Field Heterogeneity",3:"Susceptibility Artefact",4:"Shim Box Error",5:"Atypical RRs",6:"Mistriggering",7:"Low SNR",
					8:"Over-anonymised data",9:"Evidence of Fat/Water Swap",10:"Incorrect Protocol",11:"Protocol Modification",12:"Effect of high fat on T1",13:"Series not available",
					14:"Liver not in FOV",15:"Centre Frequency Variation",16:"Contrast agent suspected/confirmed",17:"Data acquired in suboptimal location",
					18:"Unsupported Acquisition Parameters"}

	def create_csv(self):
		with open(fileName,'w',newline=' ') as f:
			csvFile = csv.DictWriter(f,fields=self.headers)
			csvFile.writeheader()
			
	def load_classes(self,curSub,curImg):
		with open(fileName,'r',newline=' ') as f:
			csvFile = csv.DictReader(f,fields=self.headers)
			for row in csvFile:
				if row['Patient ID'] == curSub:
					if row['curImg'] == curImg:
						curArt = row['Artefacts']
		return curArt

	def save_classes(self,curSub,curImg,passArte):
		with open(fileName,'a',newline=' ') as f:
			csvFile = csv.DictWriter(f,fields=self.headers)
			for arte in passArte:
				csvFile.writerow({'Patient ID':curSub,'Image ID':curImg,'Artefacts':arte})

	def clean_csv():
		with open(fileName,'r') as f, tempF:
			pass

def main():
	myQApplication = QtWidgets.QApplication(sys.argv)
	myQExampleLabel = QCropLabel()
	myQExampleLabel.show()
	sys.exit(myQApplication.exec_())
	return 0    

if __name__ == "__main__":
	main()