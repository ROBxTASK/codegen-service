#!/usr/bin/env python

#--------------------------------------------
# Class to create python code
#--------------------------------------------
# Author: SRFG, Mathias Schmoigl-Tonis
# Project: ROBxTASK
# Date: Q1-Q2 2022
#--------------------------------------------
class GeneratorHelper:

	def begin(self, tab="\t"):
		self.code = []
		self.tab = tab
		self.level = 0

	def end(self):
		return "".join(self.code)

	def write(self, string):
		self.code.append(self.tab * self.level + string)

	def indent(self):
		self.level = self.level + 1

	def dedent(self):
		#if self.level == 0:
		#    raise SyntaxError, "internal error in code generator"
		self.level = self.level - 1


#--------------------------------------------
# helper class needed to statically hold 
# goal position offsets (different for every skill)
#--------------------------------------------
# Author: SRFG, Mathias Schmoigl-Tonis
# Project: ROBxTASK
# Date: Q1-Q2 2022
#--------------------------------------------
class GoalPositionHelper:

	#--------------------------------------------
	# CTOR: init class with variable members
	#--------------------------------------------
	def __init__(self):

		self.goalPositions = 	{	'SendMessage': (0,1), 					# goal position (slotName, slotValue) for Skill SendMessage
									'OnMessageReceive': (0,1), 				# goal position (slotName, slotValue) for Skill OnMessageReceive
									'MoveToPosition': (0,0),				# goal position (slotName, slotValue) for Skill MoveToPosition
									'MoveToLocation': (0,0),				# goal position (slotName, slotValue) for Skill MoveToLocation
									'DeliverObject': (1,1),					# goal position (slotName, slotValue) for Skill DeliverObject
									'FetchObject': (1,1),					# goal position (slotName, slotValue) for Skill FetchObject
									'MeasureHydration': (1,1),				# goal position (slotName, slotValue) for Skill MeasureHydration
									'DetectObject': (0,0),					# goal position (slotName, slotValue) for Skill DetectObject
									'GrabObject': (1,1),					# goal position (slotName, slotValue) for Skill GrabObject
									'PutObject': (0,0),						# goal position (slotName, slotValue) for Skill PutObject
									'TeachingWorkspacePosition': (1,1),		# goal position (slotName, slotValue) for Skill TeachingWorkspacePosition
									'TeachingObjectRecognition': (1,1),		# goal position (slotName, slotValue) for Skill TeachingObjectRecognition
									'Loop': (-1,-1), 						# not needed for ROS generator implementation atm
									'Selection': (-1,-1), 					# not needed for ROS generator implementation atm
									'WaitForCondition': (1,1),				# goal position (slotName, slotValue) for Skill WaitForCondition
									'GetData': (1,1),						# goal position (slotName, slotValue) for Skill GetData
									'SetData': (1,1),						# goal position (slotName, slotValue) for Skill SetData
									'WaitForExternalEvent': (1,1),			# goal position (slotName, slotValue) for Skill WaitForExternalEvent
									'WaitForUserInput': (0,1),				# goal position (slotName, slotValue) for Skill WaitForUserInput
									'VoiceOutput': (0,0),					# goal position (slotName, slotValue) for Skill VoiceOutput
									'GraphicalUserInteraction': (1,1)		# goal position (slotName, slotValue) for Skill GraphicalUserInteraction
								}

	#--------------------------------------------
	# getGoalPositionForSkill
	# will return the position for every skill
	# where the real main goal parameter is
	#--------------------------------------------
	def getGoalPositionForSkill(self, skillName):

		return self.goalPositions[skillName]
