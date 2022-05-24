#!/usr/bin/env python
# coding=utf-8
import os, shutil
import codegen_generator_helper
import codegen_generator_autorun

#--------------------------------------------
# Class to hold infos that should get created
#--------------------------------------------
# Author: SRFG, Mathias Schmoigl-Tonis
# Project: ROBxTASK
# Date: Q1-Q2 2022
#--------------------------------------------
class ROSGeneratorClass():

	#--------------------------------------------
	# CTOR: init class with variable members
	#--------------------------------------------
	def __init__(self, clientString, listBlocks):
		self.clientString = clientString
		self.listBlocks = listBlocks

	#--------------------------------------------
	# dump all blocks of all assets to files
	#--------------------------------------------
	def dump_all(self, filename):

		if os.path.exists(os.path.dirname(filename)):
			shutil.rmtree(os.path.dirname(filename)) # recursive remove of dir and all files

		for blocks in self.listBlocks:
			assetName = blocks[0].assetName.lower() # in case of ROS always use lower names (ROS package compatibility)
			self.dump_asset(filename + assetName + "_action_client.py", assetName, blocks)

			autoRunner = codegen_generator_autorun.AutoRunGeneratorClass()
			autoRunner.createWindowsAutoRunFile(filename + assetName + "_autorun_windows.bat", assetName + "_action_client.py")
			autoRunner.createUbuntuAutoRunFile(filename + assetName + "_autorun_ubuntu.desktop", assetName + "_action_client.py", assetName)

	#--------------------------------------------
	# dump all blocks of one asset to file
	#--------------------------------------------
	def dump_asset(self, filename, assetName, blocks):
		
		# imports and Co
		self.c = codegen_generator_helper.GeneratorHelper()
		self.c.begin(tab="    ")
		self.c.write('#! /usr/bin/env python\n\n')
		self.c.write('import rospy\n')
		self.c.write('import time\n\n')
		self.c.write('import actionlib # Brings in the SimpleActionClient\n')
		self.c.write('import rxt_skills_'+ assetName +'.msg # Brings in the messages used by the '+ assetName +' actions\n\n')	
		
		# function: send_ROSActionRequest_WithGoal
		self.c.write('#--------------------------------------------------------------------------------------\n')
		self.c.write('# client request helper function\n')
		self.c.write('#--------------------------------------------------------------------------------------\n')
		self.c.write('def send_ROSActionRequest_WithGoal(skillName, skillMsgType, skillGoal):\n\n')
		self.c.indent()
		self.c.write('rospy.init_node('+ self.clientString +') # Initializes a rospy node so that the SimpleActionClient can publish and subscribe over ROS\n\n')
		self.c.write('client = actionlib.SimpleActionClient(skillName, skillMsgType) # Creates SimpleActionClient with skillMsgType action type\n')
		self.c.write('client.wait_for_server() # Waits until the action server has started up and started listening for goals\n')
		self.c.write('client.send_goal(skillGoal) # Sends the goal to the action server\n')
		self.c.write('client.wait_for_result() # Waits for the server to finish performing the action\n\n')
		self.c.write('return client.get_result() # Prints out the result (WaitForUserInputResult) of executing the action\n\n')
		self.c.dedent()	
		
		# function: main open
		self.c.write('#--------------------------------------------------------------------------------------\n')
		self.c.write('# main function\n')
		self.c.write('#--------------------------------------------------------------------------------------\n')
		self.c.write('if __name__ == \'__main__\':\n')
		self.c.indent()
		self.c.write('try:\n')
		
		# create all blocks read from XML
		self.c.indent()
		for block in blocks:			
			if block.blockName[0] == 'STATEMENT_ENDTAG': # end of control statement
				self.c.dedent()	
			elif block.blockName[0] == 'Loop': # begin of control statement (Loop)
				self.write_loopblock(block)
				self.c.indent()
			elif block.blockName[0] == 'Selection': # begin of control statement (Selection)
				self.write_selectionblock(block)
				self.c.indent()
			else:
				self.write_requestblock(block)
		self.c.dedent()			
		
		# function: main close
		self.c.write('except rospy.ROSInterruptException:\n')
		self.c.indent()
		self.c.write('print(\"program interrupted before completion\")\n')
		self.c.dedent()	
		
		# write to filestream		
		os.makedirs(os.path.dirname(filename), exist_ok=True) # Note: only works in Python 3.6(!)
		f = open(filename,'w')
		f.write(self.c.end())
		f.close()

	#--------------------------------------------
	# write a simple request block to file
	#--------------------------------------------
	def write_requestblock(self, block):
		
		assetName = block.assetName.lower() # use lower string to allow capital letter user input on 'setAsset'
		skillName = block.blockName[0]

		(slotNamePos, slotValuePos) = codegen_generator_helper.GoalPositionHelper().getGoalPositionForSkill(skillName)
		slotName = block.blockSlotName[slotNamePos]
		slotValue = block.blockSlotValue[slotValuePos]
		
		self.c.write('# request '+ skillName +'\n')
		self.c.write('print (\'----------------------------------\')\n')
		self.c.write('print (\'INVOKING RXT_SKILL: '+ skillName +'\')\n')	
		self.c.write('result = send_ROSActionRequest_WithGoal(\''+ skillName +'\', rxt_skills_' + assetName + '.msg.'+ skillName +'Action, rxt_skills_' + assetName + '.msg.'+ skillName +'Goal('+ slotName +'=b\''+ slotValue +'\'))\n')
		self.c.write('if result:\n')
		self.c.indent()
		self.c.write('print(\"Result was: \" + str(result.isOK))\n')
		self.c.dedent()	
		self.c.write('print (\'----------------------------------\')\n\n')

	#--------------------------------------------
	# write a simple loop block to file
	#--------------------------------------------
	def write_loopblock(self, block):

		slotValue = block.blockSlotValue[0]
		[loopVar, loopMax] = slotValue.split('=') # assume syntax always is 'X=Number'

		self.c.write('print (\'----------------------------------\')\n')
		self.c.write('print (\'Generated Loop\')\n')
		self.c.write('print (\'----------------------------------\')\n')
		self.c.write('for ' + loopVar + ' in range(' + loopMax + '):\n\n')

	#--------------------------------------------
	# write a simple selection block to file
	#--------------------------------------------
	def write_selectionblock(self, block):
		
		slotValue = block.blockSlotValue[0]
		
		self.c.write('print (\'----------------------------------\')\n')
		self.c.write('print (\'Generated Selection\')\n')
		self.c.write('print (\'----------------------------------\')\n')
		self.c.write('if ' + slotValue + ':\n\n')