#--------------------------------------------------------------------------------|
# Name:        Image Crop Tool GUI					         |
# Purpose:     Crop images for Object detection & Computer Vision		 |
# Author:      Youssef Lazreg							 |
# Email:       Youssef.lazreg30@gmail.com					 |
# Created:     01/05/2017							 |
#--------------------------------------------------------------------------------|
from __future__ import division
from Tkinter import *
import tkMessageBox
from PIL import Image, ImageTk
import os
import glob
import random
import cv2
import numpy as np
# colors for the bboxes
COLORS = ['red', 'blue', 'yellow', 'pink', 'cyan', 'green', 'black']
SIZE=1054,682
datatype = ".jpg"
class LabelTool():
	def __init__(self, master):
		# set up the main frame
		self.parent = master
		self.parent.title("CropTool")
		self.frame = Frame(self.parent)
		self.frame.pack(fill=BOTH, expand=1)
		self.parent.resizable(width = FALSE, height = FALSE)

		# initialize global state
		self.imageDir = ''
		self.imageList= []
		self.outDir = ''
		self.cur = 0
		self.total = 0
		self.category = 0
		self.imagename = ''
		self.tkimg = None

        # initialize mouse state
		self.STATE = {}
		self.STATE['click'] = 0
		self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
		self.bboxIdList = []
		self.bboxId = None
		self.bboxList = []
		self.hl = None
		self.vl = None

        # ----------------- GUI stuff ---------------------
        # dir entry & load
		self.label = Label(self.frame, text = "Image Dir:")
		self.label.grid(row = 0, column = 0, sticky = E)
		self.entry = Entry(self.frame)
		self.entry.grid(row = 0, column = 1, sticky = W+E)
		self.ldBtn = Button(self.frame, text = "Load", command = self.loadDir)
		self.ldBtn.grid(row = 0, column = 2, sticky = W+E)

        # main panel for Selecting
		self.mainPanel = Canvas(self.frame, cursor='tcross')
		self.mainPanel.bind("<Button-1>", self.mouseClick)
		self.mainPanel.bind("<Motion>", self.mouseMove)
		self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
		self.parent.bind("s", self.cancelBBox)
		self.parent.bind("a", self.prevImage) # press 'a' to go backforward
		self.parent.bind("d", self.nextImage) # press 'd' to go forward
		self.mainPanel.grid(row = 1, column = 1, rowspan = 4, sticky = W+N)

		# showing boxes info & delete boxes
		self.lb1 = Label(self.frame, text = 'Cropping boxes:')
		self.lb1.grid(row = 1, column = 2,  sticky = W+N)
		self.listbox = Listbox(self.frame, width = 22, height = 12)
		self.listbox.grid(row = 2, column = 2, sticky = N)
		self.btnDel = Button(self.frame, text = 'Delete', command = self.delBBox)
		self.btnDel.grid(row = 3, column = 2, sticky = W+E+N)
		self.btnClear = Button(self.frame, text = 'ClearAll', command = self.clearBBox)
		self.btnClear.grid(row = 4, column = 2, sticky = W+E+N)

        # control panel for image navigation
		self.ctrPanel = Frame(self.frame)
		self.ctrPanel.grid(row = 5, column = 1, columnspan = 2, sticky = W+E)
		self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 10, command = self.prevImage)
		self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
		self.nextBtn = Button(self.ctrPanel, text='Next >>', width = 10, command = self.nextImage)
		self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
		self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
		self.progLabel.pack(side = LEFT, padx = 5)
		self.tmpLabel = Label(self.ctrPanel, text = "Go to Image No.")
		self.tmpLabel.pack(side = LEFT, padx = 5)
		self.idxEntry = Entry(self.ctrPanel, width = 5)
		self.idxEntry.pack(side = LEFT)
		self.goBtn = Button(self.ctrPanel, text = 'Go', command = self.gotoImage)
		self.goBtn.pack(side = LEFT)


        # display mouse position
		self.disp = Label(self.ctrPanel, text='')
		self.disp.pack(side = RIGHT)

		self.frame.columnconfigure(1, weight = 1)
		self.frame.rowconfigure(4, weight = 1)

        # for debugging
##        self.setImage()
##        self.loadDir()

	def loadDir(self, dbg = False):
		if not dbg:
			s = self.entry.get()
			self.parent.focus()
			self.category = s
		if self.category =="" : self.category = "tof"
		print s
		if not os.path.isdir(r'./Images/%s' %s):
			tkMessageBox.showerror("Error!", message = "The specified dir doesn't exist!")
			return
        # get image list
		self.imageDir = os.path.join(r'./Images', '%s' %(self.category))
		print "-" + str(self.imageDir)
		self.imageList = glob.glob(os.path.join(self.imageDir, "*"+datatype))
		#print "+" + str(len(self.imageList))
		if len(self.imageList) == 0:
			print 'No ' + datatype+' images found in the specified dir!'
			return

        # default to the 1st image in the collection
		self.cur = 1
		self.total = len(self.imageList)

		 # set up output dir
		self.outDir = os.path.join(r'./Crops', '%s' %(self.category))
		if not os.path.exists(self.outDir):
			os.mkdir(self.outDir)
		self.loadImage()
		print '%d images loaded from %s' %(self.total, s)

	"""# load example bboxes
        self.egDir = os.path.join(r'./Examples', '%03d' %(self.category))
        if not os.path.exists(self.egDir):
            return
        filelist = glob.glob(os.path.join(self.egDir, '*.JPEG'))
        self.tmp = []
        self.egList = []
        random.shuffle(filelist)
        for (i, f) in enumerate(filelist):
            if i == 3:
                break
            im = Image.open(f)
            r = min(SIZE[0] / im.size[0], SIZE[1] / im.size[1])
            new_size = int(r * im.size[0]), int(r * im.size[1])
            self.tmp.append(im.resize(new_size, Image.ANTIALIAS))
            self.egList.append(ImageTk.PhotoImage(self.tmp[-1]))
            self.egLabels[i].config(image = self.egList[-1], width = SIZE[0], height = SIZE[1])

        self.loadImage()
        print '%d images loaded from %s' %(self.total, s)"""

	def loadImage(self):
		# load image
		imagepath = self.imageList[self.cur - 1]
		#print imagepath
		self.img = Image.open(imagepath)
		new_size = self.img.size
		self.r = 1
		if new_size[0] > SIZE[0] | new_size[1] > SIZE[1] :
			self.r = min(SIZE[0] / self.img.size[0],SIZE[1] / self.img.size[1])
			print self.r
			new_size = int(self.r * self.img.size[0]), int(self.r * self.img.size[1])
		self.tkimg = ImageTk.PhotoImage(self.img.resize(new_size, Image.ANTIALIAS))
		self.mainPanel.config(width = min(self.tkimg.width(), SIZE[0]), height = min(self.tkimg.height(), SIZE[1]))
		self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
		self.progLabel.config(text = "%04d/%04d" %(self.cur, self.total))


	def saveImage(self):
		image_path = self.imageList[self.cur - 1]
		imagename = str(os.path.split(image_path)[-1].split('.')[0])
		img= cv2.imread(image_path)
		num = len(self.bboxList) 
		for bbox in self.bboxList :
			[x1, y1, x2, y2]= np.asarray(bbox) * 1/float(self.r)
			coord = np.asarray([min(x1,x2),min(y1,y2), abs(x1-x2), abs(y1-y2)])
			[x, y, w, h] = coord.astype(int)
			crop = img[y:y+h, x:x+w]
			save = str(self.outDir)+"/"+ imagename +"_"+ str(num) + datatype
			cv2.imwrite(save, crop)
			print "Image \" "  + imagename +"_"+ str(num) + " \"  saved."
			num-=1


	def mouseClick(self, event):
		if self.STATE['click'] == 0:
			self.STATE['x'], self.STATE['y'] = event.x, event.y
		else:
			x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
			y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
			self.bboxList.append((x1, y1, x2, y2))
			self.bboxIdList.append(self.bboxId)
			self.bboxId = None
			self.listbox.insert(END, '(%d, %d) - (%d, %d)' %(x1, y1, x2, y2))
			self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
		self.STATE['click'] = 1 - self.STATE['click']

	def mouseMove(self, event):
		self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
		if self.tkimg:
			if self.hl:
				self.mainPanel.delete(self.hl)
			self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width = 2)
			if self.vl:
				self.mainPanel.delete(self.vl)
			self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width = 2)
		if 1 == self.STATE['click']:
			if self.bboxId:
				self.mainPanel.delete(self.bboxId)
			self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
															event.x, event.y, \
															width = 2, \
															outline = COLORS[len(self.bboxList) % len(COLORS)])

	def cancelBBox(self, event):
		if 1 == self.STATE['click']:
			if self.bboxId:
				self.mainPanel.delete(self.bboxId)
				self.bboxId = None
				self.STATE['click'] = 0

	def delBBox(self):
		sel = self.listbox.curselection()
		if len(sel) != 1 :
			return
		idx = int(sel[0])
		self.mainPanel.delete(self.bboxIdList[idx])
		self.bboxIdList.pop(idx)
		self.bboxList.pop(idx)
		self.listbox.delete(idx)

	def clearBBox(self):
		for idx in range(len(self.bboxIdList)):
			self.mainPanel.delete(self.bboxIdList[idx])
		self.listbox.delete(0, len(self.bboxList))
		self.bboxIdList = []
		self.bboxList = []

	def prevImage(self, event = None):
		self.saveImage()
		if self.cur > 1:
			self.cur -= 1
			self.loadImage()

	def nextImage(self, event = None):
		self.saveImage()
		self.clearBBox()
		if self.cur < self.total:
			self.cur += 1
			self.loadImage()

	def gotoImage(self):
		idx = int(self.idxEntry.get())
		if 1 <= idx and idx <= self.total:
			self.saveImage()
			self.cur = idx
			self.loadImage()

##    def setImage(self, imagepath = r'test2.png'):
##        self.img = Image.open(imagepath)
##        self.tkimg = ImageTk.PhotoImage(self.img)
##        self.mainPanel.config(width = self.tkimg.width())
##        self.mainPanel.config(height = self.tkimg.height())
##        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)

if __name__ == '__main__':
	root = Tk()
	tool = LabelTool(root)
	root.resizable(width =  True, height = True)
	root.mainloop()
