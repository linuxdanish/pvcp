#! /usr/bin/python

import Tkinter
import tkFileDialog
from multiprocessing import Process
import subprocess
import hashlib
import os
import time

class App:
	# Constructor that creates the UI for program
	def __init__(self, master):
		self.master = master

		# Tkinter Frames
		self.container = Tkinter.Frame(master)
		self.logArea = Tkinter.Frame(master, width=100, height=50)

		# Tkinter textvariables
		self.sourceValue = Tkinter.StringVar()
		self.destValue = Tkinter.StringVar()
		self.rollLabelVal = Tkinter.StringVar()
		self.isIngest = Tkinter.IntVar()

		# Key Buttons
		master.title("Verified Copy GUI")
		self.sourceBtn = Tkinter.Button(self.container, text = "Source Directory", command = self.getSourceDir).grid(row=0,column=0,sticky='w')
		self.sourceLoc = Tkinter.Message(self.container, textvariable = self.sourceValue).grid(row=0,column=1,sticky="w")
		self.destBtn = Tkinter.Button(self.container, text = "Destination Directory", command = self.getDestDir).grid(row=1,column=0,sticky='w')
		self.destLoc = Tkinter.Message(self.container, textvariable = self.destValue).grid(row=1,column=1, sticky="w")
		self.rollLabel = Tkinter.Label(self.container, text="Roll Name:").grid(row=2, column=0,sticky='w')
		self.rollNum = Tkinter.Entry(self.container, textvariable = self.rollLabelVal).grid(row=2,column=1,sticky='w')
		self.doItBtn = Tkinter.Button(self.container, text = "Start transfer", command = self.transferFiles).grid(row=3,column=0,sticky='w')
		self.printValBtn = Tkinter.Button(self.container, text = "Print Values", command = self.printValues).grid(row=4,column=0,sticky='w')
		self.verifyOnly = Tkinter.Button(self.container, text = "Verify Only", command = self.verify_checksums).grid(row=3,column=1,sticky='w')

		# Check box for firstime ingest
		self.ingest = Tkinter.Checkbutton(self.container, text="Ingest", variable=self.isIngest).grid(row=3,column=2)

		# Pack the frames
		self.container.pack(fill=None)
		self.logArea.pack(fill=None)

		# Scrollable text output for program progress
		self.textArea = Tkinter.Text(self.logArea, width=100, height=50)
		self.textArea.grid(row=0, column=0)
		self.scrollbar = Tkinter.Scrollbar(self.logArea, command=self.textArea.yview)
		self.scrollbar.grid(row=0, column=1, sticky='nsew')
		self.textArea['yscrollcommand'] = self.scrollbar.set



	source = ""
	dest = ""
	files = []
	extProcesses = []

	# Opens file dialog box to get the source path
	def getSourceDir(self): 
		self.source = tkFileDialog.askdirectory(initialdir = "/Volumes",title = "Select a source to copy")
		self.sourceValue.set(self.source)

	# Opens file dialog box to get the destination path
	def getDestDir(self):
		self.dest = tkFileDialog.askdirectory(initialdir = "~/APCH_Footage_Drop",title = "Select a destination")
		self.destValue.set(self.dest)

	# Debug like function to print important variables to the process
	def printValues(self):
		print(self.source)
		print(self.dest)
		print(self.isIngest)
		self.textArea.insert(Tkinter.END, "Source path: " + self.source + "\n")
		self.textArea.insert(Tkinter.END, "Destination path: " + self.dest + "\n")
		self.textArea.insert(Tkinter.END, "Rollname: " + self.rollLabelVal.get() + "\n")
		self.textArea.insert(Tkinter.END, "isIngest: " + str(self.isIngest.get()) + "\n")

	# Main process that actually transfers the file
	def transferFiles(self):
		# Is this the first time a transfer has taken place?
		if self.isIngest.get() == 1:
			self.ingest_files()
		else:
			self.copy_files()


	def stillRunning(self):
		# Check to see if MD5 processes are still running. Wait till they complete.
		print("In still running")
		stillRunning = True
		while stillRunning:
			stillRunning = False
			for proc in self.extProcesses:
				poll = proc.poll()
				if poll == None:
					stillRunning = True
	
	def write_checksum_file(self):
		# When the sub processes are done, work through them retrieving the checksum and writing it to the checksum file.
		checksumFile = open(self.dest + "/" + self.rollLabelVal.get() + "_checksum.txt", "a+")
		for proc in self.extProcesses:
			output, err = proc.communicate()
			sumVal, fileVal = output.split()
			# Remove the source directory to give a relative path to what you wanted to copy
			fileVal = fileVal[(len(self.sourceValue.get())+1):]
			checksumFile.write("%s %s\n" % (sumVal,fileVal))
		checksumFile.close()

	def checksum_file(self, file):
		if file != "":
			command = "/sbin/md5 -r " + file 
			proc = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
			return proc

	def checksum_files(self):
		self.extProcesses = []
		startTS = time.time()
		self.textArea.insert(Tkinter.END, "Creating initial checksums and checksum file...\n")
		for r, d, f in os.walk(self.sourceValue.get()):
			for file in f:
				if file != ".DS_Store":
					self.files.append(os.path.join(r, file))
		for file in self.files:
			proc = self.checksum_file(file)
			self.extProcesses.append(proc)
		
		self.stillRunning()
		print("done running")
		if self.isIngest.get() == 1:
			print("writing checksum files")
			self.write_checksum_file()	
		runTime = time.time() - startTS
		self.textArea.insert(Tkinter.END, "Checksummed files in:" + str(runTime) + "\n")
	# END checksum_files

	# Check if the transferred files match the original checksums
	def verify_checksums(self):
		startTS = time.time()
		self.textArea.insert(Tkinter.END, "Verifying Checksums...\n")
		sourceSums = {}
		destSums = {}
		self.extProcesses = []
		print("Beginning of processes: " + str(len(self.extProcesses)))
		files = []
		for r, d, f in os.walk(self.destValue.get() + "/" + self.rollLabelVal.get()):
			for file in f:
				if file != ".DS_Store" and file != ".chksm" and file != self.rollLabelVal.get() + "_checksum.txt":
					print(os.path.join(r,file))
					files.append(os.path.join(r,file))

			print("Files Length: " + str(len(files) ))
		for file in files:
			proc = self.checksum_file(file)
			self.extProcesses.append(proc)

		checksumFile = open(self.dest + "/" + self.rollLabelVal.get() + "_checksum.txt", "r")
		for line in checksumFile:
			sumVal, fileVal = line.split()
			if self.sourceValue.get() != "":
				outputBase = os.path.basename(self.sourceValue.get())
			else:
				outputBase = self.rollLabelVal.get()
			fileVal = self.destValue.get() + "/" + outputBase + "/" + fileVal
			sourceSums[fileVal] = sumVal
		
		checksumFile.close()
		
		self.stillRunning()
		print(sourceSums)
		print("Number of processes running: " + str(len(self.extProcesses)))
		for proc in self.extProcesses:
			output, err = proc.communicate()
			sumVal, fileVal = output.split()
			if fileVal in sourceSums:
				if sumVal == sourceSums[fileVal]:
					self.textArea.insert(Tkinter.END, sumVal + " " + fileVal + " OK" + "\n")
					success = True
				else:
					self.textArea.insert(Tkinter.END,  sumVal + " " + fileVal + " FAILED" + "\n")
					success = False
		
		if 'success' in locals():
			if success == True:
				self.textArea.insert(Tkinter.END, "##### SUCCESS #####\n" + "All Files transferred successfully\n")
			else:
				self.textArea.insert(Tkinter.END, "##### FAILED #####\nSomething went wrong. Please check logs\n")
		else:
			self.textArea.insert(Tkinter.END, "No SUCCESS ##### FAILED #####\nSomething went wrong. Please check logs\n")
		runTime = time.time() - startTS
		self.textArea.insert(Tkinter.END, "Finished verifying in:" + str(runTime) + "\n")


		

	def ingest_files(self):
		startTS = time.time()
		# Check if required data is filled in, otherwise warn
		if self.source !="" and self.dest != "" and self.rollLabelVal.get() != "":
			self.textArea.insert(Tkinter.END, "Ingesting files...\n")
			# Create initial checksum values
			self.checksum_files()
			
			#Copy files
			command = "/bin/cp -RP " + self.source + " " + self.dest + " && /bin/chmod -R 755 " + self.dest
			proc = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
			while True:
				line = proc.stdout.readline()
				if not line:
					break
				self.textArea.insert(Tkinter.END, line)
			
			# Wait for copy operation to finish before beginning to verify checksums. 
			stillRunning = True
			while stillRunning:
				stillRunning = False
				poll = proc.poll()
				if poll == None:
					stillRunning = True

			self.verify_checksums()
		else:
			self.textArea.insert(Tkinter.END, "Missing a parameter. Please select a source, destination, and enter a roll name")
		runTime = time.time() - startTS
		self.textArea.insert(Tkinter.END, "Total run time in seconds:" + str(runTime) + "\n")
	
	def copy_files(self):
		startTS = time.time()

		if self.source !="" and self.dest != "" and self.rollLabelVal.get() != "":
			self.textArea.insert(Tkinter.END, "Copying files...\n")
			command = "/bin/cp -RP " + self.source + " " + self.dest + " && /bin/chmod -R 755 " + self.dest
			proc = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
			while True:
				line = proc.stdout.readline()
				if not line:
					break
				self.textArea.insert(Tkinter.END, line)
			# Wait for copy operation to finish before beginning to verify checksums. 
			stillRunning = True
			while stillRunning:
				stillRunning = False
				poll = proc.poll()
				if poll == None:
					stillRunning = True

			if os.path.isfile(self.sourceValue.get() + "/../" + self.rollLabelVal.get() + "_checksum.txt"):
				command = "/bin/cp -RP " + self.sourceValue.get() + "/../" + self.rollLabelVal.get() + "_checksum.txt " + self.dest + " && /bin/chmod -R 755 " + self.dest
				proc = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
				while True:
					line = proc.stdout.readline()
					if not line:
						break
					self.textArea.insert(Tkinter.END, line)
				# Wait for copy operation to finish before beginning to verify checksums. 
				stillRunning = True
				while stillRunning:
					stillRunning = False
					poll = proc.poll()
					if poll == None:
						stillRunning = True
			

			self.verify_checksums()
		else:
			self.textArea.insert(Tkinter.END, "Missing one or more parameters. Please select a source, destination, and enter a roll name")
		runTime = time.time() - startTS
		self.textArea.insert(Tkinter.END, "Total run time in seconds:" + str(runTime) + "\n")
			








window = Tkinter.Tk()
# Create app
gui = App(window)
# Start Tkinter loop for displaying the gui
window.mainloop()