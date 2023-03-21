import asyncio
from logging import setLogRecordFactory
import robXTask.rxtx_helpers as rxtx_helpers

import rxta_ARTI_Sim as rxta_ARTI_Sim

async def startRobXTask():
  print("*** startRobXTask")
  # This is the main-code - place any startup things here as needed...

# sample messagehandler for message-type 'SampleMessageType' - you get a 'paho-mqtt-message' (also holds the 'robxtask'-specific topic...)
async def on_rxte__message__FetchDrink__rxtx_helpers(messages):
    async for message in messages:
        await rxtx_helpers.logMessageReceived(message)
        print("*** on_rxte__message__FetchWater__rxtx_helpers()")
        sDrink = str(message.payload.decode("utf-8")).strip()
        print("got Message: " + sDrink)
        await rxtx_helpers.log(rxtx_helpers.enLogType.BLOCKLY,"rxta_ARTI_Sim.MoveToLocationARTI(Goal_Roboter)")
        await rxta_ARTI_Sim.MoveToLocationARTI("Goal_Roboter")
        await rxtx_helpers.sendMessage("GrabDrink", sDrink)


async def on_rxte__message__DrinkGrabbed__rxtx_helpers(messages):
    async for message in messages:
        await rxtx_helpers.logMessageReceived(message)
        print("*** on_rxte__message__DrinkGrabbed__rxtx_helpers()")
        sDrink = str(message.payload.decode("utf-8")).strip()
        print("got Message: " + sDrink)
        await rxtx_helpers.log(rxtx_helpers.enLogType.BLOCKLY,"rxta_ARTI_Sim.MoveToLocationARTI(Goal_Couch)")
        await rxta_ARTI_Sim.MoveToLocationARTI("Goal_Couch")
        await rxtx_helpers.sendMessage("DrinkFetched", sDrink)


rxtx_helpers.startAsync()
