# Manual_Classification

Manual Classification for Bounding Boxes

This code allows the user to bounding box and segment regions of interest in the image, and additionally and class labels to it. Was used to generate ISMRM abstract and can be used again if more labelled data is needed.

## Cropping/Segmentation Shortcuts

The shortcuts for cropping can be found below. When the screen opens, then to submit the label, the user must press the space bar when complete. This will submit the labels to a csv file.

```python
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
```
