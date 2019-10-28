# Python Script - GUI for segmentation/mask/classification of artefacts
# Charles Hill
# 08/02/19

# Python Libraries
import sys, os

#Site-packages
from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
#User functions

#https://stackoverflow.com/questions/48046462/pyqt5-i-save-the-image-but-it-is-always-empty

class Tagged_Images():

	def __init__(self):
		super().__init__()
		self.imageData = []
		self.imageTags = []

	def appendTag(self,tags):
		self.imageTags.append(tags)

class Draw(QtWidgets.QWidget):
	def __init__(self,penColor = QtCore.Qt.red):
		super().__init__()
		self.setAttribute(QtCore.Qt.WA_StaticContents)
		self.myPenWidth = 3
		self.image = QtGui.QImage(np.random.choice([x for x in os.listdir() if '.jpeg' in x]))
		self.myPenColor = penColor
		self.update()
		self.path = QtGui.QPainterPath()

	def setPenColor(self, newColor):
		self.myPenColor = newColor
		self.update()

	def setPenWidth(self, newWidth):
		self.myPenWidth = newWidth

	def nextImage(self):
		self.path = QtGui.QPainterPath()
		self.image = QtGui.QImage(np.random.choice([x for x in os.listdir() if '.jpeg' in x]))  ## switch it to else
		self.update()

	def saveImage(self, fileName, fileFormat):
		self.image.save(fileName, fileFormat)

	def paintEvent(self, event):
		painter = QtGui.QPainter(self)
		painter.drawImage(event.rect(), self.image, self.rect())
		self.myPenColor = QtCore.Qt.red
		self.update()


	def mousePressEvent(self, event):
		self.path.moveTo(event.pos())

	def mouseMoveEvent(self, event):
		self.path.lineTo(event.pos())
		p = QtGui.QPainter(self.image)
		p.setPen(QtGui.QPen(self.myPenColor,
					  self.myPenWidth, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap,
					  QtCore.Qt.RoundJoin))
		p.drawPath(self.path)
		p.end()
		self.update()

	def sizeHint(self):
		return self.image.size()

class Main_Window(QtWidgets.QWidget):

	def __init__(self):
		super().__init__()
		self.main_w()
		self.currentTags = []

	def main_w(self):
		self.b_Save = QtWidgets.QPushButton("Save image")
		self.b_Next = QtWidgets.QPushButton("Next image")
		self.cb_artefact = QtWidgets.QComboBox()
		self.cb_artefact.addItems(['Accept','Borderline','Reject','Phase Encoding Artefact',
									'Evidence of Motion','Field Heterogeneity','Susceptibility Artefact',
									'Shim Box Error','Atypical RRs','Mistriggerring','low SNR','Over-Anonymised Data',
									'Evidence of Fat/Water swap','Protocol Incorrect','Protocol Modificiation',
									'Effect of high fat on T1','Series not available','Liver not in FOV',
									'Centre Frequency Variation','Contrast agent suspected/confirmed',
									'Data Acquired in suboptimal anatomical location','Unsupported Acquisition Parameters'])
		self.b_addTag = QtWidgets.QPushButton("Add Tag")
		self.b_remTag = QtWidgets.QPushButton("Remove Tag")
		self.draw = Draw()
		self.draw.update()

		self.gb_imageInfo = QtWidgets.QGroupBox("Image Metrics")
		self.tb_imageInfoTable = QtWidgets.QTableWidget()
		
		v_box_gb = QtWidgets.QVBoxLayout()
		v_box_gb.addWidget(self.tb_imageInfoTable)
		self.gb_imageInfo.setLayout(v_box_gb)

		self.gb_draw = QtWidgets.QGroupBox("Image")
		#self.gb_draw.setMinimumSize(600,600)
		v_box_gb_2 = QtWidgets.QVBoxLayout()
		v_box_gb_2.addStretch()
		h_box_gb_2 = QtWidgets.QHBoxLayout()
		h_box_gb_2.addStretch()
		h_box_gb_2.addWidget(self.draw)
		h_box_gb_2.addStretch()
		v_box_gb_2.addLayout(h_box_gb_2)
		self.gb_draw.setLayout(v_box_gb_2)

		h_box = QtWidgets.QHBoxLayout()
		h_box.addWidget(self.gb_draw)
		h_box.addWidget(self.gb_imageInfo)

		h_box_2 = QtWidgets.QHBoxLayout()
		h_box_2.addWidget(self.cb_artefact)
		h_box_2.addWidget(self.b_addTag)
		h_box_2.addWidget(self.b_remTag)

		v_box = QtWidgets.QVBoxLayout()
		v_box.addWidget(self.b_Save)
		v_box.addWidget(self.b_Next)
		v_box.addLayout(h_box_2)
		v_box.addLayout(h_box)

		self.b_Save.clicked.connect(lambda: self.draw.saveImage("image.png", "PNG"))
		self.b_Next.clicked.connect(self.draw.nextImage)
		self.b_addTag.clicked.connect(self.add_tag)
		self.b_remTag.clicked.connect(self.remove_tag)

		self.check = QtCore.QTimer()
		self.check.setInterval(1000)
		self.check.timeout.connect(self.update_table)
		self.check.start()

		self.setLayout(v_box)
		self.show()

	def add_tag(self):
		tag = self.cb_artefact.currentText()
		self.currentTags.append(tag)

	def update_table(self):
		if self.currentTags:
			if self.tb_imageInfoTable.rowCount() < 1:
				self.tb_imageInfoTable.setColumnCount(self.tb_imageInfoTable.columnCount()+1)
				self.tb_imageInfoTable.setRowCount(self.tb_imageInfoTable.rowCount()+1)
				self.tb_imageInfoTable.setVerticalHeaderItem(0,QtWidgets.QTableWidgetItem("Quality Tags"))
			self.tb_imageInfoTable.setCellWidget(0,0,QtWidgets.QLabel(', '.join(self.currentTags)))
			self.update()
		else:
			if self.tb_imageInfoTable.rowCount() >= 1:
				self.tb_imageInfoTable.setColumnCount(self.tb_imageInfoTable.columnCount()-1)
				self.tb_imageInfoTable.setRowCount(self.tb_imageInfoTable.rowCount()-1)				

	def remove_tag(self):
		tempList = self.tb_imageInfoTable.cellWidget(0,0).text().split(', ')
		self.currentTags.remove(self.tb_imageInfoTable.cellWidget(0,0).text())
		self.tb_imageInfoTable.setCellWidget(0,0,QtWidgets.QLabel(''))

	
if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	mainWin = Main_Window()
	mainWin.show()
	sys.exit(app.exec_())