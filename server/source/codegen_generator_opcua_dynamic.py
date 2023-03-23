#!/usr/bin/env python
# coding=utf-8
import sys, string, os, shutil
import codegen_generator_helper

counter_control_rec = 0
counter_script_rec = 0

assetName_rec = None # new feature for new dynamic blockly editor 

# global variable
compare_condition = None
indent_counter = 0
else_repeat = 0
GetData_string = None

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
		self.messageContent = ""
	
	#--------------------------------------------
	# dump all blocks of all assets to files
	#--------------------------------------------
	def dump_all(self, filename):

		global counter_script_rec, counter_control_rec, assetName_rec, assetName
		nrOfControllersDetected = 0

		if os.path.exists(os.path.dirname(filename)):
			shutil.rmtree(os.path.dirname(filename)) # recursive remove of dir and all files

		# Important Note:
		# in OPCUA environment a "Controller" is needed to set starting point of application
		# this controller can be identified by having only one SendMessage-Command as a block
		# there should only be one "Controller" in a script to work in VM env
		
		for blocks in self.listBlocks:
			for i in blocks:
				if i.assetName == "UCI2aUr10":
					assetName_rec = i.assetName
					
				if i.assetName == "UCI2aMir":
					assetName_rec = i.assetName
			assetName = assetName_rec
			self.dump_asset(filename + "agent_rxta_" + assetName + ".py", assetName, blocks, "script")		
		# Important Note:
		# If we dont have excactly one controller for the moment we only print a warning
		# as there might be other ways to use OPCUA codegen in other local environments


	# +++++ Need to implement controller and receiver +++++ Gowtham

	#--------------------------------------------
	# dump all blocks of one asset to file
	#--------------------------------------------
	def dump_asset(self, filename, assetName, blocks,type_script):
		global indent_counter, else_repeat,compare_condition, GetData_string
	
		# imports and Co
		self.c = codegen_generator_helper.GeneratorHelper()
		self.c.begin(tab="    ")
		self.c.write('import asyncio\n')
		self.c.write('from logging import setLogRecordFactory\n')
		self.c.write('import robXTask.rxtx_helpers as rxtx_helpers\n\n')
		self.c.write('import rxta_' + assetName + ' as rxta_' + assetName + '\n\n')

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

			if "GetData" in split_list:
				self.getData(assetName,block)


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
				if "GetData" in split_list:
					self.while_getdata_loop(GetData_string,block)
				else:
					self.while_loop(compare_condition,block)

			if "ELSE_IF" in block.blockName:
				else_repeat = 0
				self.else_if(compare_condition)
			

			if "indent" in block.blockName:
				self.c.indent()
				indent_counter += 1

			if "variables_set" in block.blockName:
				if "GetData" in split_list:
					self.var_set(GetData_string,block)
					GetData_string = None
				else:
					self.var_set(None,block)



			if count == 0 and "OnMessageReceive" not in block.blockName:
				self.c.write('async def startRobXTask():\n')
				self.c.indent()
				indent_counter += 1

			if "OnMessageReceive" in block.blockName:
				if indent_counter > 0:
					for i in range(indent_counter):
						self.c.dedent()
						indent_counter -= 1
				self.message_listener(block)
				indent_counter += 2
			
			if "SendMessage" in block.blockName:
				self.write_sendmessage(block)

			try:
				if split_list[0] == "MoveToLocation":
					self.move_to_location(block,split_list[0],assetName)
				if split_list[0] == "GrabObject":
					self.grab_object(block,split_list[0],assetName)
				if split_list[0] == "PutObject":
					self.put_object(block,split_list[0],assetName)
				
			except:
				pass

			split_string = None


		#stop async
		self.c.write('await rxtx_helpers.stop()\n\n')

		
		for i in range(indent_counter):
			self.c.dedent()
		self.c.write('rxtx_helpers.startAsync()\n')

		indent_counter = 0

		# write to filestream
		os.makedirs(os.path.dirname(filename), exist_ok=True) # Note: only works in Python 3.6(!)
		f = open(filename,'w')
		f.write(self.c.end())
		f.close()



	def getData(self,assetName,block):
		global GetData_string
		if "STATEMENT_ENDTAG" in block.blockSlotValue:
			block.blockSlotValue.remove("STATEMENT_ENDTAG")

		GetData_string = "await rxta_"+assetName+".GetData("+block.blockSlotValue[1]+")"


	def var_set(self,to_store,block):
		if "STATEMENT_ENDTAG" in block.blockSlotValue:
			block.blockSlotValue.remove("STATEMENT_ENDTAG")
		
		if to_store != None:
			self.c.write(block.blockSlotValue[0]+' = '+to_store+'\n')

		elif to_store == None:
			self.c.write(block.blockSlotValue[0]+' = '+block.blockSlotValue[1]+'\n')



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

	def while_getdata_loop(self,Get_data,block):
		global GetData_string
		if "STATEMENT_ENDTAG" in block.blockSlotValue:
			block.blockSlotValue.remove("STATEMENT_ENDTAG")

		if "UNTIL" in block.blockSlotValue:
			block.blockSlotValue.remove("UNTIL")
			self.c.write('# request for loop \n')
			self.c.write('while (not ( '+Get_data+' == \''+block.blockSlotValue[1]+'\')):\n')

		
	def else_if(self,condition):
		self.c.write('# request for else if \n')
		self.c.write('elif '+condition+':\n')



	def write_sendmessage(self, block):

		temp_value = block.blockSlotValue

		if "MQTT" in temp_value:
			temp_value.remove("MQTT")

		if "STATEMENT_ENDTAG" in temp_value:
			temp_value.remove("STATEMENT_ENDTAG")

		slotValue = temp_value[0]
		
		self.c.write('# ----------------------------------\n')
		self.c.write('# Trying to send message \n')
		self.c.write('# ----------------------------------\n')
		self.c.write('await rxtx_helpers.sendMessage("' + slotValue + '", "' + self.messageContent + '")\n')



	def move_to_location(self, block,skillName, assetName):

		if "STATEMENT_ENDTAG" in block.blockSlotValue:
			block.blockSlotValue.remove("STATEMENT_ENDTAG")

		slotValue = block.blockSlotValue[0]

		self.c.write('# ----------------------------------\n')
		self.c.write('# Trying to invoke skill: ' + skillName + '\n')
		self.c.write('# ----------------------------------\n')
		self.c.write('await rxtx_helpers.logSkillCall("' + skillName + '","'+slotValue+'")\n')


		# TODO: temporary solution because only GrabObject skill on OPCUA currently needs both parameter slots
		# should be changed once we know how real GrabObject skill on OPCUAwill be implemented
		
		self.c.write('await rxta_' + assetName + '.' + skillName + '("' + slotValue + '")\n')
		

		# generate skill return handling (if needed)
	
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


	
	def grab_object(self, block,skillName, assetName):

		if "STATEMENT_ENDTAG" in block.blockSlotValue:
			block.blockSlotValue.remove("STATEMENT_ENDTAG")

		slotValue1 = block.blockSlotValue[0]
		slotValue2 = block.blockSlotValue[1]

		self.c.write('# ----------------------------------\n')
		self.c.write('# Trying to invoke skill: ' + skillName + '\n')
		self.c.write('# ----------------------------------\n')
		self.c.write('await rxtx_helpers.logSkillCall("' + skillName + '","'+slotValue1+'","'+slotValue2+'")\n')


		# TODO: temporary solution because only GrabObject skill on OPCUA currently needs both parameter slots
		# should be changed once we know how real GrabObject skill on OPCUAwill be implemented
		
		self.c.write('await rxta_' + assetName + '.' + skillName + '("' + slotValue1 + '","' + slotValue2+ '")\n')
		

		# generate skill return handling (if needed)
	
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



	def put_object(self, block,skillName, assetName):

		if "STATEMENT_ENDTAG" in block.blockSlotValue:
			block.blockSlotValue.remove("STATEMENT_ENDTAG")

		slotValue1 = block.blockSlotValue[0]

		self.c.write('# ----------------------------------\n')
		self.c.write('# Trying to invoke skill: ' + skillName + '\n')
		self.c.write('# ----------------------------------\n')
		self.c.write('await rxtx_helpers.logSkillCall("' + skillName + '","'+slotValue1+'")\n')


		# TODO: temporary solution because only GrabObject skill on OPCUA currently needs both parameter slots
		# should be changed once we know how real GrabObject skill on OPCUAwill be implemented
		
		self.c.write('await rxta_' + assetName + '.' + skillName + '("' + slotValue1 +'")\n')
		

		# generate skill return handling (if needed)
	
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



	def message_listener(self,block):
		if "STATEMENT_ENDTAG" in block.blockSlotValue:
			block.blockSlotValue.remove("STATEMENT_ENDTAG")

		if "MQTT" in block.blockSlotValue:
			block.blockSlotValue.remove("MQTT")

		message_name = block.blockSlotValue[0]

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
