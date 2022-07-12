#!/usr/bin/env python
# coding=utf-8
import sys, string, os, shutil
import codegen_generator_helper
		
#--------------------------------------------
# Class to hold infos that should get created
#--------------------------------------------
# Author: SRFG, Mathias Schmoigl-Tonis
# Project: ROBxTASK
# Date: Q1-Q2 2022
#--------------------------------------------
class OPCUAGeneratorClass():

	#--------------------------------------------
	# CTOR: init class with variable members
	#--------------------------------------------
	def __init__(self, clientString, listBlocks):
		self.clientString = clientString
		self.listBlocks = listBlocks
		self.messageContent = "[Empty Message Content]"
	
	#--------------------------------------------
	# dump all blocks of all assets to files
	#--------------------------------------------
	def dump_all(self, filename):

		if os.path.exists(os.path.dirname(filename)):
			shutil.rmtree(os.path.dirname(filename)) # recursive remove of dir and all files

		# Important Note:
		# in OPCUA environment a "Controller" is needed to set starting point of application
		# this controller can be identified by having only one SendMessage-Command as a block
		# there should only be one "Controller" in a script to work in VM env
		nrOfControllersDetected = 0
		for blocks in self.listBlocks:
			assetName = blocks[0].assetName
		
			if len(blocks) == 1 and blocks[0].blockName[0] == "SendMessage": # check if it has only one SendMessage-Block
				self.dump_controller(filename + "agent_01_" + assetName + ".py", assetName, blocks)
				nrOfControllersDetected+=1
			else:
				self.dump_asset(filename + "agent_rxta_" + assetName + "_01.py", assetName, blocks)
		
		# Important Note:
		# If we dont have excactly one controller for the moment we only print a warning
		# as there might be other ways to use OPCUA codegen in other local environments
		if(nrOfControllersDetected != 1):
			print('WARNING: Found ' + nrOfControllersDetected + ' Controllers instead of one! Your execution might not work as expected')

	#--------------------------------------------
	# dump all blocks of one asset to file
	#--------------------------------------------
	def dump_asset(self, filename, assetName, blocks):
	
		# imports and Co
		self.c = codegen_generator_helper.GeneratorHelper()
		self.c.begin(tab="    ")
		self.c.write('import asyncio\n')
		self.c.write('from logging import setLogRecordFactory\n')
		self.c.write('import robXTask.rxtx_helpers as rxtx_helpers\n\n')
		self.c.write('import rxta_' + assetName + ' as rxta_' + assetName + '\n\n')

		# create all blocks read from XML
		for block in blocks:
			if block.blockName[0] == 'STATEMENT_ENDTAG': # end of control statement
				self.c.dedent()	
			elif block.blockName[0] == 'Loop': # begin of control statement (Loop)
				self.write_loopblock(block)
				self.c.indent()
			elif block.blockName[0] == 'Selection': # begin of control statement (Selection)
				self.write_selectionblock(block)
				self.c.indent()
			elif block.blockName[0] == 'OnMessageReceive':
				self.write_messagelistener(block.blockSlotValue[1], block)
			elif block.blockName[0] == 'SendMessage':
				self.write_sendmessage(block, assetName)
			else:
				self.write_skillblock(block, assetName, True)	
		
		# start async
		self.c.dedent()
		self.c.dedent()
		self.c.write('rxtx_helpers.startAsync()\n')

		# write to filestream
		os.makedirs(os.path.dirname(filename), exist_ok=True) # Note: only works in Python 3.6(!)
		f = open(filename,'w')
		f.write(self.c.end())
		f.close()

	#--------------------------------------------
	# dump main controller file
	#--------------------------------------------
	def dump_controller(self, filename, assetName, blocks):

		startMessage = blocks[0].blockSlotValue[1] # assumes Controller only uses send first message block!

		# imports and Co
		self.c = codegen_generator_helper.GeneratorHelper()
		self.c.begin(tab="    ")
		self.c.write('import asyncio\n')
		self.c.write('from logging import setLogRecordFactory\n')
		self.c.write('import robXTask.rxtx_helpers as rxtx_helpers\n\n')

		# create main routine
		self.c.write('async def startRobXTask():\n')
		self.c.indent()
		self.c.write('# This is the automatically generated main-code with the start message to begin workflow\n')
		self.c.write('print("*** startRobXTask")\n')	
		self.c.write('await rxtx_helpers.sleep(5)\n')
		self.c.write('await rxtx_helpers.log(rxtx_helpers.enLogType.INFO,"agent_01_Controller - First Log")\n')
		self.c.write('await rxtx_helpers.sendMessage("' + startMessage + '", "' + self.messageContent + '")\n\n')
		self.c.dedent()	

		# message handler for workflow end
		self.c.write('async def on_rxte__message__WorkflowEnded__rxtx_helpers(messages):\n')
		self.c.indent()
		self.c.write('async for message in messages:\n')
		self.c.indent()
		self.c.write('await rxtx_helpers.logMessageReceived(message)\n')
		self.c.write('print("*** on_rxte__message__Ur10Tested__rxtx_helpers()")\n')
		self.c.write('sMsg = str(message.payload.decode("utf-8")).strip()\n')
		self.c.write('print("Total Workflow was Tested: " + sMsg)\n')
		self.c.write('await rxtx_helpers.stop()\n\n')
			
		# start async
		self.c.dedent()	
		self.c.dedent()
		self.c.write('rxtx_helpers.startAsync()\n')

		# write to filestream
		os.makedirs(os.path.dirname(filename), exist_ok=True) # Note: only works in Python 3.6(!)
		f = open(filename,'w')
		f.write(self.c.end())
		f.close()
	
	#--------------------------------------------
	# write message listener to file
	#--------------------------------------------
	def write_messagelistener(self, message_name, block):

		self.c.write('async def on_rxte__message__'+ message_name +'__rxtx_helpers(messages):\n')
		self.c.indent()
		self.c.write('async for message in messages:\n\n')
		self.c.indent()
		self.c.write('# ----------------------------------\n')
		self.c.write('# This is the automatically generated message execution code\n')
		self.c.write('# ----------------------------------\n')
		self.c.write('await rxtx_helpers.logMessageReceived(message)\n')
		self.c.write('print("*** on_rxte__message__' + message_name + '__rxtx_helpers()")\n')
		self.c.write('sMessage = str(message.payload.decode("utf-8")).strip()\n')
		self.c.write('print("got Message: " + sMessage)\n\n')

	#--------------------------------------------
	# write single skill block to file
	#--------------------------------------------
	def write_skillblock(self, block, assetName, skill_hasreturn):

		skillName = block.blockName[0]

		(slotNamePos, slotValuePos) = codegen_generator_helper.GoalPositionHelper().getGoalPositionForSkill(skillName)
		slotName = block.blockSlotName[slotNamePos]
		slotValue = block.blockSlotValue[slotValuePos]

		self.c.write('# ----------------------------------\n')
		self.c.write('# Trying to invoke skill: ' + skillName + '\n')
		self.c.write('# ----------------------------------\n')
		self.c.write('await rxtx_helpers.logSkillCall("' + skillName + '","' + slotValue + '")\n')


		# TODO: temporary solution because only GrabObject skill on OPCUA currently needs both parameter slots
		# should be changed once we know how real GrabObject skill on OPCUAwill be implemented
		if skillName == 'GrabObject':
			self.c.write('await rxta_' + assetName + '.' + skillName + '("' + block.blockSlotValue[0] + '", ' + block.blockSlotValue[1] + ')\n')
		else:
			self.c.write('await rxta_' + assetName + '.' + skillName + '("' + slotValue + '")\n')
		

		# generate skill return handling (if needed)
		if(skill_hasreturn):

			self.c.write('bResOk = await rxta_' + assetName + '.getResultBool()\n')
			self.c.write('if (bResOk):\n')
			self.c.indent()
			self.c.write('await rxtx_helpers.log(rxtx_helpers.enLogType.INFO,"' + skillName + ' - OK :-)")\n')
			self.c.dedent()	
			self.c.write('else:\n')
			self.c.indent()
			self.c.write('await rxtx_helpers.log(rxtx_helpers.enLogType.INFO,"' + skillName + ' - NOK :-)")\n')
			self.c.write('sErrCode = await rxta_' + assetName + '.GetData(rxta_' + assetName + '.enVariables.Status' + skillName + '_ErrorCode)\n')
			self.c.write('sErrMsg = await rxta_' + assetName + '.GetData(rxta_' + assetName + '.enVariables.Status' + skillName + '_StatusMessage)\n')
			self.c.write('await rxtx_helpers.log(rxtx_helpers.enLogType.ERROR,"' + skillName + ' - ERROR (" + sErrCode + ") - " + sErrMsg)\n')
			self.c.dedent()	

		self.c.write('\n')

	#--------------------------------------------
	# write send message
	#--------------------------------------------
	def write_sendmessage(self, block, assetName):
		
		slotValue = block.blockSlotValue[1]

		self.c.write('# ----------------------------------\n')
		self.c.write('# Trying to send message \n')
		self.c.write('# ----------------------------------\n')
		self.c.write('await rxtx_helpers.sendMessage("' + slotValue + '", "' + self.messageContent + '")\n')
		self.c.write('await rxtx_helpers.stop()\n\n')

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