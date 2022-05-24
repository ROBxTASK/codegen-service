import sys, string, os
import codegen_generator_helper

#--------------------------------------------
# Class to generate AutoRun files
#--------------------------------------------
# Author: SRFG, Mathias Schmoigl-Tonis
# Project: ROBxTASK
# Date: Q1-Q2 2022
#--------------------------------------------
class AutoRunGeneratorClass():

    #--------------------------------------------
	# will create an autorun batch file for windows
	#--------------------------------------------
	def createWindowsAutoRunFile(self, filename, scriptname):

		self.c = codegen_generator_helper.GeneratorHelper()
		self.c.begin(tab="    ")
		self.c.write('ECHO ON\n')
		self.c.write('REM A batch script to execute a Python script\n')
		self.c.write('SET PATH=%PATH%;C:\Python27\n')
		self.c.write("python " + scriptname + '\n')
		self.c.write('PAUSE')

		# write to filestream		
		os.makedirs(os.path.dirname(filename), exist_ok=True) # Note: only works in Python 3.6(!)
		f = open(filename,'w')
		f.write(self.c.end())
		f.close()
	
	#--------------------------------------------
	# will create an autorun batch file for Ubuntu
	#--------------------------------------------
	def createUbuntuAutoRunFile(self, filename, scriptname, assetname):

		self.c = codegen_generator_helper.GeneratorHelper()
		self.c.begin(tab="    ")
		self.c.write('#!/usr/bin/env xdg-open\n')
		self.c.write('[Desktop Entry]\n')
		self.c.write('Version=v0.8.5\n')
		self.c.write('Name='+ assetname +'_autorun_ubuntu\n')
		self.c.write('Exec=python /home/panda/ros_workspace/src/rxt_codegen/output/generated_results/' + scriptname + '\n')
		self.c.write('Terminal=true\n')
		self.c.write('Type=Application\n')

		# write to filestream		
		os.makedirs(os.path.dirname(filename), exist_ok=True) # Note: only works in Python 3.6(!)
		f = open(filename,'w')
		f.write(self.c.end())
		f.close()