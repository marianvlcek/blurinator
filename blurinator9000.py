# -*- coding: utf-8 -*-
"""
Copyright 2021 Marián Vlček

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import sys
from tkinter import Tk, Label, Button, Scale, Frame, filedialog, HORIZONTAL
from PIL import Image
from PIL import ImageTk
import cv2
import numpy as np

# define global variables
size = 24
GtGfraction = 4.0
strobe = 1.0
strobeNbr = 1
overdrive = 0.0
imageOrig = None
imageBlurred = None

def redraw_image():
	global size, GtGfraction, strobe, strobeNbr, imageBlurred, imageOrig
	
	if imageOrig is not None:
		# construct kernels
		kernelGtG = np.zeros((1, 3*size))
		for i in range(3*size):
		    if i < size:
		        kernelGtG[0, i] = 1 - np.exp(-(i+1)*GtGfraction/size) + overdrive*(np.exp(-(i+1)*GtGfraction/size) - np.exp(-(i+1)*2.0*GtGfraction/size))
		    else:
		        kernelGtG[0, i] = (1 - np.exp(-size*GtGfraction/size) + overdrive*(np.exp(-size*GtGfraction/size) - np.exp(-size*2.0*GtGfraction/size)))*(np.exp(-(i-size+1)*GtGfraction/size) - overdrive*(np.exp(-(i-size+1)*GtGfraction/size) - np.exp(-(i-size+1)*2.0*GtGfraction/size)))
		kernelGtG = kernelGtG / np.sum(kernelGtG)
		
		
		kernelStrobe = np.zeros((1, 3*size))
		for i in range(3*size):
		    if i % max(size // strobeNbr, 1) + 1 < max(size // strobeNbr, 1)*(1-strobe):
		        kernelStrobe[0, i] = 0
		    else:
		        kernelStrobe[0, i] = 1
		kernelStrobe = kernelStrobe / np.sum(kernelStrobe)
		
		kernelFinal = kernelGtG*kernelStrobe
		kernelFinal = kernelFinal / np.sum(kernelFinal)
		
		# blur image
		imageBlurred = np.power(imageOrig*1.0/255.0, 2.2)
		imageBlurred = cv2.filter2D(imageBlurred, -1, kernelFinal)
		imageBlurred = np.clip(imageBlurred, 0.0, 1.0)
		imageBlurred = 255*np.power(imageBlurred, 1.0/2.2)

		# convert images
		image = cv2.cvtColor(imageOrig, cv2.COLOR_BGR2RGB)
		blurred = cv2.cvtColor(imageBlurred.astype("uint8"), cv2.COLOR_BGR2RGB)
		
		image = Image.fromarray(image)
		blurred = Image.fromarray(blurred)
		
		image = ImageTk.PhotoImage(image)
		blurred = ImageTk.PhotoImage(blurred)
	        
		# update the pannels
		panelA.configure(image=image)
		panelB.configure(image=blurred)
		panelA.image = image
		panelB.image = blurred
	else:
		panelA.configure(image='')
		panelB.configure(image='')
		panelA.image = None
		panelB.image = None
		panelA.configure(text="No Image Loaded")
		panelB.configure(text="No Image Loaded")

def select_image():
	global imageOrig
	path = filedialog.askopenfilename()    
	if len(path) > 0:
		imageOrig = cv2.imread(path)
		redraw_image()
		
def save_image():
	global imageBlurred
	path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=(("JPG file", "*.jpg"),("PNG file", "*.png"),("All Files", "*.*")))
	if len(path) > 0:
		cv2.imwrite(path, imageBlurred)
		
def set_blur(v):
	global size
	size = int(v)
	redraw_image()
	
def set_GtG(v):
	global GtGfraction
	if float(v) >= 5.0:
		GtGfraction = 1000;
	else:
		GtGfraction = 2*np.exp(0.5*(float(v)-1))
	redraw_image()

def set_strobe(v):
	global strobe
	strobe = float(v)/100
	redraw_image()
	
def set_strobeNumber(v):
	global strobeNbr
	strobeNbr = int(2**int(v))
	redraw_image()
	
def set_overdrive(v):
	global overdrive
	overdrive = float(v)
	redraw_image()
	
def resource_path(relative_path):
	try:
		# PyInstaller stores temp path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		# use local path while running like a script
		base_path = os.path.abspath(".")
	return os.path.join(base_path, relative_path)

root = Tk()
root.title("Blurinator 9000")
root.minsize(480,480)



# lot of stuff below to create GUI layout
mainFrame = Frame(root)
imageFrame = Frame(mainFrame)
toolFrame = Frame(mainFrame)

panelA = Label(imageFrame, text = "Left")
panelA.pack(side="left", padx=10, pady=10)
panelB = Label(imageFrame, text = "Right")
panelB.pack(side="right", padx=10, pady=10)

s1Frame = Frame(toolFrame)
s1LeftLabel = Label(s1Frame, text = "1", anchor = "se", width = 7)
s1 = Scale(s1Frame, label='Movement Speed [pixels/frame]', from_=1, to=32, length=200, orient=HORIZONTAL, showvalue=1, resolution=1, command=set_blur)
s1.set(size)
s1RightLabel = Label(s1Frame, text = "32", anchor = "sw", width = 8)
s1LeftLabel.pack(side="left", fill="both")
s1.pack(side="left")
s1RightLabel.pack(side="left", fill="both")
s1Frame.pack(side="top", pady=10)

s2Frame = Frame(toolFrame)
s2LeftLabel = Label(s2Frame, text = "Slow", anchor = "se", width = 7)
s2 = Scale(s2Frame, label='GtG Speed', from_=1, to=5, length=200, orient=HORIZONTAL, showvalue=1, resolution=0.01, command=set_GtG)
s2.set(2.386294361119891);
s2RightLabel = Label(s2Frame, text = "Fast", anchor = "sw", width = 8)
s2LeftLabel.pack(side="left", fill="both")
s2.pack(side="left")
s2RightLabel.pack(side="left", fill="both")
s2Frame.pack(side="top", pady=10)

s5Frame = Frame(toolFrame)
s5LeftLabel = Label(s5Frame, text = "None", anchor = "se", width = 7)
s5 = Scale(s5Frame, label='Overdrive', from_=0, to=3, orient=HORIZONTAL, length=200, showvalue=1, resolution=0.01, command=set_overdrive)
s5.set(overdrive)
s5RightLabel = Label(s5Frame, text = "Extreme", anchor = "sw", width = 8)
s5LeftLabel.pack(side="left", fill="both")
s5.pack(side="left")
s5RightLabel.pack(side="left", fill="both")
s5Frame.pack(side="top", pady=10)

s3Frame = Frame(toolFrame)
s3LeftLabel = Label(s3Frame, text = "1", anchor = "se", width = 7)
s3 = Scale(s3Frame, label='Strobe Length [%]', from_=1, to=100, orient=HORIZONTAL, length=200, showvalue=1, resolution=1, command=set_strobe)
s3.set(100*strobe)
s3RightLabel = Label(s3Frame, text = "100", anchor = "sw", width = 8)
s3LeftLabel.pack(side="left", fill="both")
s3.pack(side="left")
s3RightLabel.pack(side="left", fill="both")
s3Frame.pack(side="top", pady=10)

s4Frame = Frame(toolFrame)
s4LeftLabel = Label(s4Frame, text = "Single", anchor = "se", width = 7)
s4 = Scale(s4Frame, label='Strobes per Frame', from_=0, to=5, orient=HORIZONTAL, length=200, showvalue=1, resolution=1, command=set_strobeNumber)
s4.set(0)
s4RightLabel = Label(s4Frame, text = "Many", anchor = "sw", width = 8)
s4LeftLabel.pack(side="left", fill="both")
s4.pack(side="left")
s4RightLabel.pack(side="left", fill="both")
s4Frame.pack(side="top", pady=10)

btnFrame = Frame(toolFrame)
btn1 = Button(btnFrame, text="Load Image", width = 15, command=select_image)
btn1.pack(side="left", padx="10", pady="10")
btn2 = Button(btnFrame, text="Save Image", width = 15, command=save_image)
btn2.pack(side="right", padx="10", pady="10")
btnFrame.pack(side="bottom")

imageFrame.pack(side="left", fill="both", expand="yes")
toolFrame.pack(side="right", fill="both", expand="yes")

mainFrame.pack(side="top", fill="both", expand="yes")

copyLabel = Label(root, text = "   Copyright © 2021 Marián Vlček", anchor = "w")
copyLabel.pack(side="bottom", fill="both")
# end of GUI layout

# load default image
imageOrig = cv2.imread(resource_path("blurinator_default_image.png"))
redraw_image()

# start the GUI
root.mainloop()