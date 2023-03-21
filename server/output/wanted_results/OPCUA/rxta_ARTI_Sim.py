import asyncio
import robXTask.rxtx_xrob_opcua as rxtx_xrob_opcua;
from opcua import ua
from enum import Enum
from functools import wraps

CONST_XROB_OPCUAIP = "opc.tcp://localhost:4840"

class enVariables(dict, Enum):
    MoveToLocationARTI_State = {"id": "ns=1;s=MoveToLocationARTI:State", "varianttype" : ua.VariantType.Int32 },
    fromSimulationARTI_AGVPositionTheta = {"id": "ns=1;s=fromSimulationARTI:AGVPositionTheta", "varianttype" : ua.VariantType.Double },
    fromSimulationARTI_AGVPositionX = {"id": "ns=1;s=fromSimulationARTI:AGVPositionX", "varianttype" : ua.VariantType.Double },
    fromSimulationARTI_AGVPositionY = {"id": "ns=1;s=fromSimulationARTI:AGVPositionY", "varianttype" : ua.VariantType.Double },
    fromSimulationARTI_BatteryState = {"id": "ns=1;s=fromSimulationARTI:BatteryState", "varianttype" : ua.VariantType.Double },
    fromSimulationARTI_ErrorMessage = {"id": "ns=1;s=fromSimulationARTI:ErrorMessage", "varianttype" : ua.VariantType.String },
    fromSimulationARTI_HasErrorOccurred = {"id": "ns=1;s=fromSimulationARTI:HasErrorOccurred", "varianttype" : ua.VariantType.Boolean },
    fromSimulationARTI_HasTargetGoalReached = {"id": "ns=1;s=fromSimulationARTI:HasTargetGoalReached", "varianttype" : ua.VariantType.Boolean },
    fromSimulationARTI_LastReachedGoalName = {"id": "ns=1;s=fromSimulationARTI:LastReachedGoalName", "varianttype" : ua.VariantType.String },
    toSimulationARTI_GetBatteryState = {"id": "ns=1;s=toSimulationARTI:GetBatteryState", "varianttype" : ua.VariantType.Boolean },
    toSimulationARTI_MoveToTargetGoal = {"id": "ns=1;s=toSimulationARTI:MoveToTargetGoal", "varianttype" : ua.VariantType.Boolean },
    toSimulationARTI_TargetGoalName = {"id": "ns=1;s=toSimulationARTI:TargetGoalName", "varianttype" : ua.VariantType.String },

EVENT_HANDLERS_SUPPORTED = {
    "varchange": enVariables
}

# decorator that doesn't change the decorated method in any way but tell us that we shall export this function for Blockly
# Our Generator tool later searches for '__IsBlockly__' attribute on the function to find out what functions shall be exported
# see: 'The best explanation of Python decorators' -> https://gist.github.com/Zearin/2f40b7b9cfc51132851a
def blockly(func):
    func.__IsBlockly__ = True
    return func

# this is a blockly skill - decorate this when implementing a robotic skill
def blocklySkill(func):
    func.__IsBlockly__ = True
    func.__IsBlocklySkill__ = True
    return func

# decorator to specify that this is a blockly EventHandler, also holds the arguments to be expected by the EventHandler by the Python function e.g. 'sName: str, oData : str'
# this information can be used to implement a concrete eventhandler. 
# usually you should use an enum as first part ot the function you tag HERE to support good eventhandlers. and the second argument should be the concrete mainfunction to call using 'sEventArgs'
# in blockly then these argments will be given as blockly-variables to the event-function
# see: https://towardsdatascience.com/tearing-the-mask-off-python-decorators-c964344853c3
def blocklyEventHandler(sEventArgs):
    def decorator(func):
        func.__IsBlockly__ = True
        func.__IsBlocklyEventHandler__ = True
        func.__BlocklyEventArgs__ = sEventArgs        
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

# mode init code - not to export on blockly
async def initModule(*args, **kwargs):
    print("rxta_ARTI_Panda_Sim.initModule()")


# mode exit code - not to export on blockly
async def exitModule():
    print("rxta_ARTI_Panda_Sim.exitModule()")

# we remind the last result of a skill call
GLOBAL_LastSkillCallResult = False


@blockly
async def getResultBool() -> bool:
    """Returns the last Result of a skill-call as a bool"""
    return (str(GLOBAL_LastSkillCallResult) == "True")


@blockly
async def getResult():
    """Returns the last Result of a skill-call"""
    return GLOBAL_LastSkillCallResult


@blocklySkill
async def MoveToLocationARTI(sLocation: str):
    """Calls the PlugBot OPCUA Skill 'MoveToLocationARTI' from PROFACTOR'"""
    sFuncName:str = "rxta_ARTI_Panda_Sim.MoveToLocationARTI(" + str(sLocation) + ")"
    global GLOBAL_LastSkillCallResult
    print(sFuncName + "-BEGIN")
    await asyncio.sleep(2) #zh. we just sleep for 2 seconds
    GLOBAL_LastSkillCallResult = True
    print(sFuncName + "-END-" + str(GLOBAL_LastSkillCallResult))


@blockly
async def getData(enVarName : enVariables) -> str:
    """Returns the value for the given PlugBot OPCUA variable"""
    return "Simulation"


@blockly
async def setData(enVarName : enVariables, anyValue):
    """This method could set the value of the given PlugBot OPCUA variable (but setting variables is mostly not supported by access-restrictions)"""
    pass

@blocklyEventHandler(sEventArgs="sNewValue")
def addVariableChangeHandler(enVarName : enVariables, oFuncForVarChange):
    pass




