#!/usr/bin/env python
# coding=utf-8
import os, shutil
import codegen_generator_helper
import codegen_generator_autorun

assetName_rec = None # new feature for new dynamic blockly editor 

# global variable
compare_condition = None
indent_counter = 0
else_repeat = 0

#--------------------------------------------
# Class to hold infos that should get created
#--------------------------------------------
# Author: SRFG, Mathias Schmoigl-Tonis
# Author: Gowtham Sridhar 
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
		global assetName_rec

		if os.path.exists(os.path.dirname(filename)):
			shutil.rmtree(os.path.dirname(filename)) # recursive remove of dir and all files

		for blocks in self.listBlocks:
			# assetName = blocks[0].assetName.lower() # in case of ROS always use lower names (ROS package compatibility)
			for i in blocks:
				if i.assetName.lower() == "panda" or i.assetName.lower() == "chasi" or i.assetName.lower() == "qbo":
					assetName_rec = i.assetName.lower()
			assetName = assetName_rec
			self.dump_asset(filename + assetName + "_action_client.py", assetName, blocks)
			autoRunner = codegen_generator_autorun.AutoRunGeneratorClass()
			autoRunner.createWindowsAutoRunFile(filename + assetName + "_autorun_windows.bat", assetName + "_action_client.py")
			autoRunner.createUbuntuAutoRunFile(filename + assetName + "_autorun_ubuntu.desktop", assetName + "_action_client.py", assetName)

	#--------------------------------------------
	# dump all blocks of one asset to file
	#--------------------------------------------
	def dump_asset(self, filename, assetName, blocks):
		global indent_counter, else_repeat,compare_condition
		
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
		self.c.write('rospy.init_node(\''+ assetName + self.clientString +'\') # Initializes a rospy node so that the SimpleActionClient can publish and subscribe over ROS\n\n')
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


		for count,block in enumerate(blocks):	
			print("testing", count, block.blockName,block.blockSlotValue,block.blockSlotName)
			split_string = None
			for i in  block.blockName:
				try:
					to_split = i
					split_list = i.split('_-_')
					if len(split_list) == 1:
						pass
					else:
						split_string = split_list
				except:
					pass


			if "STATEMENT_ENDTAG" in block.blockName or block.blockName[0]=="STATEMENT_ENDTAG": ## bug detected trying to fix
				for i in range(block.blockName.count("STATEMENT_ENDTAG")):
					if indent_counter >= 1:
						self.c.dedent()
						indent_counter -= 1
					
					elif indent_counter == 0:
						indent_counter = 0

					else:
						indent_counter = -1


			if "logic_operation" not in block.blockName:
				if "logic_compare" in block.blockName: 
					self.compare_var(block,False)

			if "logic_operation" in block.blockName:
				if "logic_compare" in block.blockName:
					self.compare_var(block,True)

			if "logic_boolean" in block.blockName:
				if "TRUE" in block.blockSlotValue:
					compare_condition = "True"
				if "FALSE" in block.blockSlotValue:
					compare_condition = "False"

			

			if "controls_if" in block.blockName:
				else_repeat = 0
				self.if_control(compare_condition)

			if "ELSE" in block.blockName:
				if else_repeat == 1:
					self.c.dedent()
					indent_counter -= 1
				self.else_control()
				else_repeat = 1
			
			if "controls_repeat_ext" in block.blockName:
				self.for_loop(block.blockSlotValue)

			if "controls_whileUntil" in block.blockName:
				self.while_loop(compare_condition,block)

			if "ELSE_IF" in block.blockName:
				else_repeat = 0
				self.else_if(compare_condition)
			

			if "indent" in block.blockName:
				self.c.indent()
				indent_counter += 1

			try:
				if split_string[0] == "MoveToLocation":
					self.move_to_location(block,split_string)
				if split_string[0] == "SetData" and "variables_set" not in block.blockName:
					self.set_data(block.blockSlotValue,split_string)
				if split_string[0] == "GrabObject":
					self.grab_object(block.blockSlotValue,split_string)
				if split_string[0] == "PutObject":
					self.put_object(block.blockSlotValue,split_string)
				if split_string[0] == "WaitForExternalEvent":
					self.wait_for_event(block.blockSlotValue,split_string)
				if split_string[0] == "GraphicalUserInteraction":
					self.graphical_interface(block.blockSlotValue,split_string)
				if split_string[0] == "VoiceOutput":
					self.voice_out(block.blockSlotValue,split_string)
			except:
				pass
			

			if "SendMessage" in block.blockName:
				self.send_message(block.blockSlotValue,"SendMessage")

			if "OnMessageReceive" in block.blockName:
				self.receive_message(block.blockSlotValue,"OnMessageReceive")


			if "variables_set" in block.blockName:   
				try:
					if split_string[0] == "GetData" or split_string[0] == "WaitForUserInput":
						self.variable_set(block.blockSlotValue,"variables_set",split_string,block.blockSlotName)

				except:
					self.variable_set(block.blockSlotValue,"variables_set","None",None)


			split_string = None

		
		# function: main close
		for i in range(indent_counter+1):
			self.c.dedent()

		indent_counter = 0
		self.c.write('except rospy.ROSInterruptException:\n')
		self.c.indent()
		self.c.write('print(\"program interrupted before completion\")\n')
		self.c.dedent()	
		
		# write to filestream		
		os.makedirs(os.path.dirname(filename), exist_ok=True) # Note: only works in Python 3.6(!)
		f = open(os.open(filename, os.O_CREAT | os.O_WRONLY, 0o777),'w')
		f.write(self.c.end())
		# self.c.testing()
		f.close()


	def variable_set(self,blockSlotValue, skillName,store_bool,blockSlotName): 
		self.c.write('# request '+ skillName +'\n')
		if "STATEMENT_ENDTAG" in blockSlotValue:
			blockSlotValue.remove("STATEMENT_ENDTAG")

		if len(blockSlotValue) <= 2 and store_bool[0] not in ["GetData","WaitForUserInput"]:
			try:
				print(int(blockSlotValue[0]))
				var_pointer = blockSlotValue[1]
				value = blockSlotValue[0]
			except:
				try:
					var_pointer = blockSlotValue[0]
					value = blockSlotValue[1]
				except:
					raise ValueError("Error: Variable requires value or string shouldn't be empty")
			
			self.c.write(str(var_pointer)+' = '+str(value)+'\n')

		elif store_bool[0] == "GetData":
			assetName = assetName_rec
			skillName = store_bool[0]
			slotValue = blockSlotValue[1]
			self.c.write('print (\'----------------------------------\')\n')
			self.c.write('print (\'INVOKING RXT_SKILL: '+ skillName +'\')\n')
			self.c.write('result = send_ROSActionRequest_WithGoal(\''+ skillName +'\', rxt_skills_' + assetName + '.msg.'+ skillName +'Action, rxt_skills_' + assetName + '.msg.'+ skillName +'Goal('+'inputData' +'=b\''+ slotValue +'\'))\n')
			self.c.write('if result:\n')
			self.c.indent()
			self.c.write('print(\"Result was: \", \'\'.join([str(n) for n in result.data.decode("utf-8")]))\n')
			self.c.write(blockSlotValue[0]+' = str(result.data)'+'\n')
			self.c.dedent()
			self.c.write('print (\'----------------------------------\')\n\n')

		elif store_bool[0] == "WaitForUserInput":
			assetName = assetName_rec
			skillName = store_bool[0]
			slotValue = blockSlotValue[1]
			self.c.write('print (\'----------------------------------\')\n')
			self.c.write('print (\'INVOKING RXT_SKILL: '+ skillName +'\')\n')
			self.c.write('result = send_ROSActionRequest_WithGoal(\''+ skillName +'\', rxt_skills_' + assetName + '.msg.'+ skillName +'Action, rxt_skills_' + assetName + '.msg.'+ skillName +'Goal('+'inputContent' +'=b\''+ slotValue +'\'))\n')
			self.c.write('if result:\n')
			self.c.indent()
			self.c.write('print(\"Result was: \", \'\'.join([str(n) for n in result.returnMessage.decode("utf-8")]))\n')
			self.c.write(blockSlotValue[0]+' = str(result.returnMessage)'+'\n')
			self.c.dedent()
			self.c.write('print (\'----------------------------------\')\n\n')
						


		else:
			if "ADD" in blockSlotValue:
				blockSlotValue.remove("ADD")
				arith_op = " + "

			if "MINUS" in blockSlotValue:
				blockSlotValue.remove("MINUS")
				arith_op = " - "
			
			if "MULTIPLY" in blockSlotValue:
				blockSlotValue.remove("MULTIPLY")
				arith_op = " * "

			if "DIVIDE" in blockSlotValue:
				blockSlotValue.remove("DIVIDE")
				arith_op = " / "

			if "POWER" in blockSlotValue:
				blockSlotValue.remove("POWER")
				arith_op = " ** "
			
			self.c.write(blockSlotValue[0]+' = '+blockSlotValue[1]+arith_op+blockSlotValue[2])
		


	def move_to_location(self,block,split_string):
		skillName = split_string[0]
		assetName = assetName_rec
		for i in block.blockSlotValue:
			if i != "STATEMENT_ENDTAG":
				slotValue = i
				slotName = 'location'

		self.c.write('# request '+ skillName +'\n')
		self.c.write('print (\'----------------------------------\')\n')
		self.c.write('print (\'INVOKING RXT_SKILL: '+ skillName +'\')\n')	
		self.c.write('result = send_ROSActionRequest_WithGoal(\''+ skillName +'\', rxt_skills_' + assetName + '.msg.'+ skillName +'Action, rxt_skills_' + assetName + '.msg.'+ skillName +'Goal('+ slotName +'=b\''+ slotValue +'\'))\n')
		self.c.write('if result:\n')
		returnName = 'isOK'
		self.c.indent()
		self.c.write('print(\"Result was: \" + str(result.'+returnName+'))\n')
		self.c.dedent()	
		self.c.write('print (\'----------------------------------\')\n\n')



	def compare_var(self,block,logic_oper):
		global compare_condition
		
		if logic_oper == False:
			possible_compare = ["EQ","NEQ","LT","LTE","GT","GTE","WHILE","UNTIL"]
			var_to_compare = None
			for i in block.blockSlotValue:
				if i == "EQ":
					compare = ' == '
				elif i == "NEQ":
					compare = ' != '
				elif i == "LT":
					compare = ' < '
				elif i == "LTE":
					compare = ' <= '
				elif i == "GT":
					compare = ' > '
				elif i == "GTE":
					compare = ' >= '
				else:
						pass

				if i != "STATEMENT_ENDTAG":
					if i not in possible_compare:
						if var_to_compare == None:
							var_to_compare = i
						else:
							val_to_compare =i

			compare_condition = var_to_compare+compare+val_to_compare

		else:
			possible_compare = ["EQ","NEQ","LT","LTE","GT","GTE","WHILE","UNTIL","AND","OR","STATEMENT_ENDTAG"]
			comparison_symb = []
			logic_operation = []

			for i in block.blockSlotValue:
				if i == "EQ":
					comparison_symb.append(' == ')
				elif i == "NEQ":
					comparison_symb.append(' != ')
				elif i == "LT":
					comparison_symb.append(' < ')
				elif i == "LTE":
					comparison_symb.append(' <= ')
				elif i == "GT":
					comparison_symb.append(' > ')
				elif i == "GTE":
					comparison_symb.append(' >= ')
				elif i == "AND":
					logic_operation.append(' and ')
				elif i == "OR":
					logic_operation.append(' or ')
				else:
					pass

			remaining_var = [x for x in block.blockSlotValue if x not in possible_compare]
			compare_condition = remaining_var[0] + comparison_symb[0]+remaining_var[1]+logic_operation[0]+remaining_var[2]+comparison_symb[1]+remaining_var[3]




	def if_control(self,condition):
		self.c.write('# request if condition \n')
		self.c.write('if '+ condition +' :\n')

	def else_control(self):
		self.c.write('# request else condition \n')
		self.c.write('else:\n')


	def for_loop(self,times):
		self.c.write('# request for loop \n')
		if "STATEMENT_ENDTAG" not in times:
			repeat_for = times[0]
		else:
			times.remove("STATEMENT_ENDTAG")
			repeat_for = times[0] 
		
		self.c.write('for i in range('+repeat_for+'):\n')

	def while_loop(self,condition,block):
		temp_value = block.blockSlotValue
		if "WHILE" in temp_value:
			self.c.write('# request for loop \n')
			self.c.write('while '+condition+':\n')
		elif "UNTIL" in temp_value:
			self.c.write('# request for loop \n')
			self.c.write('while not '+condition+':\n')


	def else_if(self,condition):
		self.c.write('# request for else if \n')
		self.c.write('elif '+condition+':\n')


	def set_data(self,blockValue,split_data):
		# Note if set data is empty the value error is raised in xml reader file checkout there
		assetName = assetName_rec
		skillName = split_data[0]
		if "STATEMENT_ENDTAG" in blockValue:
			blockValue.remove("STATEMENT_ENDTAG")
		
		slotValue = blockValue[0]
		
		self.c.write('print (\'----------------------------------\')\n')
		self.c.write('print (\'INVOKING RXT_SKILL: '+ skillName +'\')\n')
		self.c.write('result = send_ROSActionRequest_WithGoal(\''+ skillName +'\', rxt_skills_' + assetName + '.msg.'+ skillName +'Action, rxt_skills_' + assetName + '.msg.'+ skillName +'Goal('+'outputData' +'=b\''+ slotValue +'\'))\n')
		self.c.write('if result:\n')
		returnName = 'isOK'
		self.c.indent()
		self.c.write('print(\"Result was: \" + str(result.'+returnName+'))\n')
		self.c.dedent()	
		self.c.write('print (\'----------------------------------\')\n\n')

	def voice_out(self,blockValue,split_data):
		assetName = assetName_rec
		skillName = split_data[0]
		if "STATEMENT_ENDTAG" in blockValue:
			blockValue.remove("STATEMENT_ENDTAG")
		slotValue = blockValue[0]
		
		self.c.write('print (\'----------------------------------\')\n')
		self.c.write('print (\'INVOKING RXT_SKILL: '+ skillName +'\')\n')
		self.c.write('result = send_ROSActionRequest_WithGoal(\''+ skillName +'\', rxt_skills_' + assetName + '.msg.'+ skillName +'Action, rxt_skills_' + assetName + '.msg.'+ skillName +'Goal('+'outputMessage' +'=b\''+ slotValue +'\'))\n')
		self.c.write('if result:\n')
		returnName = 'isOK'
		self.c.indent()
		self.c.write('print(\"Result was: \" + str(result.'+returnName+'))\n')
		self.c.dedent()	
		self.c.write('print (\'----------------------------------\')\n\n')


	def grab_object(self,blockValue,split_data):
		assetName = assetName_rec
		skillName = split_data[0]
		if "STATEMENT_ENDTAG" in blockValue:
			blockValue.remove("STATEMENT_ENDTAG")
		slotValue = blockValue[0]
		self.c.write('print (\'----------------------------------\')\n')
		self.c.write('print (\'INVOKING RXT_SKILL: '+ skillName +'\')\n')
		self.c.write('result = send_ROSActionRequest_WithGoal(\''+ skillName +'\', rxt_skills_' + assetName + '.msg.'+ skillName +'Action, rxt_skills_' + assetName + '.msg.'+ skillName +'Goal('+'objectPosition' +'=b\''+ slotValue +'\'))\n')
		self.c.write('if result:\n')
		returnName = 'isOK'
		self.c.indent()
		self.c.write('print(\"Result was: \" + str(result.'+returnName+'))\n')
		self.c.dedent()	
		self.c.write('print (\'----------------------------------\')\n\n')


	def put_object(self,blockValue,split_data):
		assetName = assetName_rec
		skillName = split_data[0]
		if "STATEMENT_ENDTAG" in blockValue:
			blockValue.remove("STATEMENT_ENDTAG")
		slotValue = blockValue[0]
		self.c.write('print (\'----------------------------------\')\n')
		self.c.write('print (\'INVOKING RXT_SKILL: '+ skillName +'\')\n')
		self.c.write('result = send_ROSActionRequest_WithGoal(\''+ skillName +'\', rxt_skills_' + assetName + '.msg.'+ skillName +'Action, rxt_skills_' + assetName + '.msg.'+ skillName +'Goal('+'position' +'=b\''+ slotValue +'\'))\n')
		self.c.write('if result:\n')
		returnName = 'isOK'
		self.c.indent()
		self.c.write('print(\"Result was: \" + str(result.'+returnName+'))\n')
		self.c.dedent()	
		self.c.write('print (\'----------------------------------\')\n\n')

	
	def wait_for_event(self,blockValue,split_data):
		assetName = assetName_rec
		skillName = split_data[0]
		if "STATEMENT_ENDTAG" in blockValue:
			blockValue.remove("STATEMENT_ENDTAG")
		slotValue = blockValue[0]
		self.c.write('print (\'----------------------------------\')\n')
		self.c.write('print (\'INVOKING RXT_SKILL: '+ skillName +'\')\n')
		self.c.write('result = send_ROSActionRequest_WithGoal(\''+ skillName +'\', rxt_skills_' + assetName + '.msg.'+ skillName +'Action, rxt_skills_' + assetName + '.msg.'+ skillName +'Goal('+'inputText' +'=b\''+ slotValue +'\'))\n')
		self.c.write('if result:\n')
		self.c.indent()
		self.c.write('print(\"Result was: \", \'\'.join([str(n) for n in result.returnMessage.decode("utf-8")]))\n')
		self.c.dedent()	
		self.c.write('print (\'----------------------------------\')\n\n')
		

	def graphical_interface(self,blockValue,split_data):
		assetName = assetName_rec
		skillName = split_data[0]
		if "STATEMENT_ENDTAG" in blockValue:
			blockValue.remove("STATEMENT_ENDTAG")
		slotValue = blockValue[0]
		self.c.write('print (\'----------------------------------\')\n')
		self.c.write('print (\'INVOKING RXT_SKILL: '+ skillName +'\')\n')
		self.c.write('result = send_ROSActionRequest_WithGoal(\''+ skillName +'\', rxt_skills_' + assetName + '.msg.'+ skillName +'Action, rxt_skills_' + assetName + '.msg.'+ skillName +'Goal('+'outputMessage' +'=b\''+ slotValue +'\'))\n')
		self.c.write('if result:\n')
		self.c.indent()
		self.c.write('print(\"Result was: \", \'\'.join([str(n) for n in result.returnMessage.decode("utf-8")]))\n')
		self.c.dedent()	
		self.c.write('print (\'----------------------------------\')\n\n')


	def send_message(self,blockValue,split_data):
		
		assetName = assetName_rec
		skillName = split_data
		if "STATEMENT_ENDTAG" in blockValue:
			blockValue.remove("STATEMENT_ENDTAG")
		try:
			slotValue = blockValue[1]
		except:
			raise ValueError("Error: SendMessage block need string")
		self.c.write('print (\'----------------------------------\')\n')
		self.c.write('print (\'INVOKING RXT_SKILL: '+ skillName +'\')\n')
		self.c.write('result = send_ROSActionRequest_WithGoal(\''+ skillName +'\', rxt_skills_' + assetName + '.msg.'+ skillName +'Action, rxt_skills_' + assetName + '.msg.'+ skillName +'Goal('+'messageContent' +'=b\''+ slotValue +'\'))\n')
		self.c.write('if result:\n')
		returnName = 'isOK'
		self.c.indent()
		self.c.write('print(\"Result was: \" + str(result.'+returnName+'))\n')
		self.c.dedent()	
		self.c.write('print (\'----------------------------------\')\n\n')


	def receive_message(self,blockValue,split_data):
		assetName = assetName_rec
		skillName = split_data
		if "STATEMENT_ENDTAG" in blockValue:
			blockValue.remove("STATEMENT_ENDTAG")
		slotValue = blockValue[1]
		self.c.write('print (\'----------------------------------\')\n')
		self.c.write('print (\'INVOKING RXT_SKILL: '+ skillName +'\')\n')
		self.c.write('result = send_ROSActionRequest_WithGoal(\''+ skillName +'\', rxt_skills_' + assetName + '.msg.'+ skillName +'Action, rxt_skills_' + assetName + '.msg.'+ skillName +'Goal('+'messageContent' +'=b\''+ slotValue +'\'))\n')
		self.c.write('if result:\n')
		returnName = 'isOK'
		self.c.indent()
		self.c.write('print(\"Result was: \" + str(result.'+returnName+'))\n')
		self.c.dedent()	
		self.c.write('print (\'----------------------------------\')\n\n')


