#!/usr/bin/env python
# coding=utf-8
import xml.etree.ElementTree as ET
import sys

indent = 0
counter_skip1 = 3
dedent_else_if_repeat = 0
#--------------------------------------------
# Helper class to hold infos of one block 616724 307572
#--------------------------------------------
class SimpleBlockEntry():	

	def __init__(self, assetName, blockName, blockSlotName, blockSlotValue,indent):
		self.assetName = assetName
		self.blockName = blockName
		self.blockSlotName = blockSlotName
		self.blockSlotValue = blockSlotValue
		self.indent = indent

#--------------------------------------------
# Class to parse XML File from Blockly
#--------------------------------------------
# Author: SRFG, Mathias Schmoigl-Tonis
# Project: ROBxTASK
# Date: Q1-Q2 2022
#--------------------------------------------
class XML_BlocklyProject_Parser():

	#--------------------------------------------
	# CTOR: init class with variable members
	#--------------------------------------------
	def __init__(self, xmlString):
		self.root = []
		#self.tree = ET.parse(fileName)

		#self.root = self.tree.getroot()
		read_xml = ET.fromstring(xmlString)

		for i in range(len(read_xml)):
			if read_xml[i].tag == "{https://developers.google.com/blockly/xml}block":
				self.root.append(read_xml[i])

		self.listBlocks = []

	#--------------------------------------------
	# read the assets involved in the script
	#--------------------------------------------
	def readAssets(self):

		print ("Searching for all involved assets...")
		# for asset in self.root:
		# 	print ("-----------------------------------------------------")
		# 	print ("Found involved Asset with following tag and attrib: ")		
		# 	print ("^^^^^^^^^^",asset.tag, asset.attrib)
		# 	print ("-----------------------------------------------------")

		for i in range(len(self.root)):
			blocks = self.readBlocks(self.root[i])
			self.listBlocks.append(blocks)

	#--------------------------------------------
	# read all blocks at once
	#--------------------------------------------
	def readBlocks(self, asset):
		global counter_skip1, dedent_else_if_repeat

		print ("Parsing XML Tree searching for blocks...")
		print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		
		#var for raising exceptions
 
		# variables needed for appending blocks to block list
		blockCounter = 0
		blocks = []
		blocks.append(SimpleBlockEntry("", [],[],[],None))

		# statementBlockCounters contains all statement counters, which are needed to 
		# count down the number of blocks within Statement (Loop or Selection)
		statementBlockCounters = [] 


	
		for entry in asset.iter():
				
			if(entry.tag=="{https://developers.google.com/blockly/xml}next"):
				print ("Found <next>-attribute")

				# Add a Stament End Tag, when any counter is zero again (reached end of a statement)
				
				for index in range(len(statementBlockCounters)):
				    
					if(statementBlockCounters[index] > 0):
						statementBlockCounters[index] -= 1
						if (statementBlockCounters[index] == 0):
							blockCounter += 1
							blocks.append(SimpleBlockEntry("", ["STATEMENT_ENDTAG"],["STATEMENT_ENDTAG"],["STATEMENT_ENDTAG"],"end"))
							dedent_else_if_repeat = 0
							
				
				# remove all zeros from array
				statementBlockCounters = [i for i in statementBlockCounters if i > 0]

				# normally start a new block
				blockCounter += 1

				blocks.append(SimpleBlockEntry("", [],[],[],None))
			
			elif(entry.tag=="{https://developers.google.com/blockly/xml}statement"):
				if entry.attrib.get('name') == "ELSE":
					blockCounter += 1
					blocks.append(SimpleBlockEntry("", ["STATEMENT_ENDTAG"],["STATEMENT_ENDTAG"],["STATEMENT_ENDTAG"],"end"))
					if dedent_else_if_repeat == 1:
						blocks[blockCounter].blockName.append("STATEMENT_ENDTAG")
					blocks[blockCounter].blockName.append("ELSE")
					blocks[blockCounter].blockName.append("indent")
					dedent_else_if_repeat = 0
				# hello = entry.findall("{https://developers.google.com/blockly/xml}statement")
				blockCounter += 1
				blocks.append(SimpleBlockEntry("", [],[],[],None))
				statementBlockCounters.append(len(list(entry.iter('{https://developers.google.com/blockly/xml}next'))) + 1)
				

					
			elif(entry.tag=="{https://developers.google.com/blockly/xml}value"): 
				if entry.attrib.get('name') != "IF1":
					print ("Found <value>-attribute with name = " + entry.attrib.get('name'),entry.text)
					blocks[blockCounter].blockSlotName.append(entry.attrib.get('name'))

				else:
					blocks.append(SimpleBlockEntry("", [],[],[],None))
					blockCounter += 1
					blocks[blockCounter].blockName.append("STATEMENT_ENDTAG")
					print ("Found <value>-attribute with name = " + entry.attrib.get('name'),entry.text)
					blocks[blockCounter].blockSlotName.append(entry.attrib.get('name'))
					blocks[blockCounter].blockName.append("ELSE_IF")
					blocks[blockCounter].blockName.append("indent")

					
				
			elif(entry.tag=="{https://developers.google.com/blockly/xml}field"):
				print ("Found <field>-attribute with name = " + entry.attrib.get('name'),entry.text)
				blocks[blockCounter].blockSlotValue.append(entry.text)
				if entry.text == "" or entry.text == None:
					raise ValueError("ERROR: A block with empty text was found in your design. Please first remove the empty text element and try again.")	


			elif(entry.tag=="{https://developers.google.com/blockly/xml}block"):
				print ("Found <block>-attribute with type = " + entry.attrib.get('type') + " and 'id = " + entry.attrib.get('id'),entry.text)
				blocks[blockCounter].blockName.append(entry.attrib.get('type'))
				if  entry.attrib.get('type') == "controls_whileUntil" or entry.attrib.get('type') =="controls_if" or entry.attrib.get('type') =="controls_repeat_ext":
					blocks[blockCounter].blockName.append("indent")
					if entry.attrib.get('type') =="controls_repeat_ext":
						dedent_else_if_repeat = 1




			
				
			else:
				print ("detent--------------",entry.tag)

		

		self.assignBlocksToAssets(blocks) # now put everything in order assigned to correct asset
		return blocks
			
	#--------------------------------------------
	# assign all blocks to an asset
	#--------------------------------------------
	def assignBlocksToAssets(self, blocks):
		
		# assign blocks
		assetName = ""
		prev_device = ""


		for entry in blocks:
			if entry.blockName != []:
				block_string = entry.blockName[0]
				split_block_string = block_string.split("_-_")
				
				
				if "30:9c:23:84:fe:51" in split_block_string:
					assetName = "panda"
					entry.assetName = assetName

				elif "00:e0:4c:68:02:30" in split_block_string:
					assetName = "chasi"
					entry.assetName = assetName

				
				elif "b8:27:eb:24:1f:b2" in split_block_string:
					assetName = "qbo"
					entry.assetName = assetName

				elif "rxta_UCI2aUr10" in split_block_string:
					assetName = "UCI2aUr10"
					entry.assetName = assetName

				elif "rxta_UCI2aMir" in split_block_string:
					assetName = "UCI2aMir"
					entry.assetName = assetName

				elif split_block_string == None:
					raise ValueError("Error: choose at least one block from the device to control")
				
				if assetName != "" and prev_device != "":
					try:
						if assetName != prev_device:
							raise ValueError("Error: Included blocks of two different devices in single block diagram. Arrange two different device blocks seperately")
						
					except Exception as e:
						print(e)
						print('a'/'b')
						
				prev_device = assetName

				print('\nFound entry - assetName:' + entry.assetName + '; name: ' + entry.blockName[0] + '; value:' + entry.blockSlotValue[0])
				last_name = entry.blockName[0]
		try:
			if last_name == "controls_if" or last_name == "controls_whileUntil" or last_name == "controls_repeat_ext":
				raise ValueError("Error: if condition or loop shouldn't be empty")
			if assetName == "":
				raise ValueError("Error: No block from the available device is included")
		except Exception as e:
			print(e)
			print('a'/'b')

		

	#--------------------------------------------
	# GETTER: return listBlock member variable
	#--------------------------------------------
	def getList(self):
		return self.listBlocks