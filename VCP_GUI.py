#! /usr/bin/python

import Tkinter
import tkFileDialog
import subprocess


class App:
	def __init__(self, master):
		self.master = master
		self.container = Tkinter.Frame(master)
		self.logArea = Tkinter.Frame(master, width=100, height=50)
		self.messages = Tkinter.StringVar()
		self.sourceValue = Tkinter.StringVar()
		self.destValue = Tkinter.StringVar()
		self.rollLabelVal = Tkinter.StringVar()

		master.title("Verified Copy GUI")
		self.sourceBtn = Tkinter.Button(self.container, text = "Source Directory", command = self.getSourceDir).grid(row=0,column=0,sticky='w')
		self.sourceLoc = Tkinter.Message(self.container, textvariable = self.sourceValue).grid(row=0,column=1,sticky="w")
		self.destBtn = Tkinter.Button(self.container, text = "Destination Directory", command = self.getDestDir).grid(row=1,column=0,sticky='w')
		self.destLoc = Tkinter.Message(self.container, textvariable = self.destValue).grid(row=1,column=1, sticky="w")
		self.rollLabel = Tkinter.Label(self.container, text="Roll Name:").grid(row=2, column=0,sticky='w')
		self.rollNum = Tkinter.Entry(self.container, textvariable = self.rollLabelVal).grid(row=2,column=1,sticky='w')
		self.doItBtn = Tkinter.Button(self.container, text = "Start transfer", command = self.transferFiles).grid(row=3,column=0,sticky='w')
		self.printValBtn = Tkinter.Button(self.container, text = "Print Values", command = self.printValues).grid(row=4,column=0,sticky='w')
		self.output = Tkinter.Message(self.container, textvariable = self.messages ).grid(row=5)
		self.container.pack(fill=None)
		self.logArea.pack(fill=None)

		self.textArea = Tkinter.Text(self.logArea, width=100, height=50)
		self.textArea.grid(row=0, column=0)
		self.scrollbar = Tkinter.Scrollbar(self.logArea, command=self.textArea.yview)
		self.scrollbar.grid(row=0, column=1, sticky='nsew')
		self.textArea['yscrollcommand'] = self.scrollbar.set



	source = ""
	dest = ""

	def getSourceDir(self): 
		self.source = tkFileDialog.askdirectory(initialdir = "/Volumes",title = "Select a source to copy")
		self.sourceValue.set(self.source)

	def getDestDir(self):
		self.dest = tkFileDialog.askdirectory(initialdir = "~/APCH_Footage_Drop",title = "Select a destination")
		self.destValue.set(self.dest)

	def printValues(self):
		print(self.source)
		print(self.dest)
		self.textArea.insert(Tkinter.END, "Source path: " + self.source + "\n")
		self.textArea.insert(Tkinter.END, "Destination path: " + self.dest + "\n")
		self.textArea.insert(Tkinter.END, "Rollname: " + self.rollLabelVal.get() + "\n")


	def transferFiles(self):
		if self.source != "" and self.dest != "" and self.rollLabelVal.get() != "":
			self.command = "/usr/local/bin/vcp.sh " + self.source + " " + self.dest + " " + self.rollLabelVal.get()
			self.proc = subprocess.Popen(self.command,shell=True, stdout=subprocess.PIPE)
			while True:
				line = self.proc.stdout.readline()
				if not line:
					break
				self.textArea.insert(Tkinter.END, line )
				#self.messages.set(self.messages.get() + "\n" + line)

	def stillRunning(self):
		return proc.poll()



window = Tkinter.Tk()
#
gui = App(window)


#output.insert(END, "Hello world")
# if gui.stillRunning != None:
# 		s = gui.proc.readline()
# 		output.insert(END, s)

# window.source = tkFileDialog.askdirectory(initialdir = "/Volumes",title = "Select a source to copy")

window.mainloop()

