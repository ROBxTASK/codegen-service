#! /usr/bin/env python

import rospy
import time

import actionlib # Brings in the SimpleActionClient
import rxt_skills_panda.msg # Brings in the messages used by the panda actions

#------------------------------------------------------------------------------------------------------------------------------------------------------------
# client request helper function
#------------------------------------------------------------------------------------------------------------------------------------------------------------
def send_ROSActionRequest_WithGoal(skillName, skillMsgType, skillGoal):

    rospy.init_node('panda_client_py') # Initializes a rospy node so that the SimpleActionClient can publish and subscribe over ROS

    client = actionlib.SimpleActionClient(skillName, skillMsgType) # Creates SimpleActionClient with skillMsgType action type
    client.wait_for_server() # Waits until the action server has started up and started listening for goals
    client.send_goal(skillGoal) # Sends the goal to the action server
    client.wait_for_result() # Waits for the server to finish performing the action
    
    return client.get_result() # Prints out the result (WaitForUserInputResult) of executing the action
	
#------------------------------------------------------------------------------------------------------------------------------------------------------------
# main function
#------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    try:

        # request GrabObject
        print ('----------------------------------')
        print ('INVOKING RXT_SKILL: GrabObject')
        result = send_ROSActionRequest_WithGoal('GrabObject', rxt_skills_panda.msg.GrabObjectAction, rxt_skills_panda.msg.GrabObjectGoal(objectPosition=b'3'))
        if result:
            print("Result was: " + str(result.isOK))
        print ('----------------------------------')

        # request PutObject
        print ('----------------------------------')
        print ('INVOKING RXT_SKILL: PutObject')
        result = send_ROSActionRequest_WithGoal('PutObject', rxt_skills_panda.msg.PutObjectAction, rxt_skills_panda.msg.PutObjectGoal(position=b'3'))
        if result:
            print("Result was: " + str(result.isOK))
        print ('----------------------------------')

        # request MoveToLocation
        print ('----------------------------------')
        print ('INVOKING RXT_SKILL: MoveToLocation')
        result = send_ROSActionRequest_WithGoal('MoveToLocation', rxt_skills_panda.msg.MoveToLocationAction, rxt_skills_panda.msg.MoveToLocationGoal(location=b'pack pose'))
        if result:
            print("Result was: " + str(result.isOK))
        print ('----------------------------------')
        
        # request MoveToLocation
        print ('----------------------------------')
        print ('INVOKING RXT_SKILL: MoveToLocation')
        result = send_ROSActionRequest_WithGoal('MoveToLocation', rxt_skills_panda.msg.MoveToLocationAction, rxt_skills_panda.msg.MoveToLocationGoal(location=b'cups init'))
        if result:
            print("Result was: " + str(result.isOK))
        print ('----------------------------------')
        
        # request MoveToLocation
        print ('----------------------------------')
        print ('INVOKING RXT_SKILL: MoveToLocation')
        result = send_ROSActionRequest_WithGoal('MoveToLocation', rxt_skills_panda.msg.MoveToLocationAction, rxt_skills_panda.msg.MoveToLocationGoal(location=b'cart init'))
        if result:
            print("Result was: " + str(result.isOK))
        print ('----------------------------------')

        # request MoveToLocation
        print ('----------------------------------')
        print ('INVOKING RXT_SKILL: MoveToLocation')
        result = send_ROSActionRequest_WithGoal('MoveToLocation', rxt_skills_panda.msg.MoveToLocationAction, rxt_skills_panda.msg.MoveToLocationGoal(location=b'final cart position 2'))
        if result:
            print("Result was: " + str(result.isOK))
        print ('----------------------------------')
        
        # request GetData
        print ('----------------------------------')
        print ('INVOKING RXT_SKILL: GetData')
        result = send_ROSActionRequest_WithGoal('GetData', rxt_skills_panda.msg.GetDataAction, rxt_skills_panda.msg.GetDataGoal(inputData=b'void'))
        if result:
            print("Result was:", ''.join([str(n) for n in result.data.decode("utf-8")]))
        print ('----------------------------------')
        
        # request SetData
        print ('----------------------------------')
        print ('INVOKING RXT_SKILL: SetData')
        result = send_ROSActionRequest_WithGoal('SetData', rxt_skills_panda.msg.SetDataAction, rxt_skills_panda.msg.SetDataGoal(outputData=b'data: \'SC 1\''))
        if result:
            print("Result was: " + str(result.isOK))
        print ('----------------------------------')

        # request WaitForUserInput
        print ('----------------------------------')
        print ('INVOKING RXT_SKILL: WaitForUserInput')
        result = send_ROSActionRequest_WithGoal('WaitForUserInput', rxt_skills_panda.msg.WaitForUserInputAction, rxt_skills_panda.msg.WaitForUserInputGoal(inputContent=b'void'))
        if result:
            print("Result was:", ''.join([str(n) for n in result.returnMessage.decode("utf-8")]))
        print ('----------------------------------')
                
        # request WaitForExternalEvent
        print ('----------------------------------')
        print ('INVOKING RXT_SKILL: WaitForExternalEvent')
        result = send_ROSActionRequest_WithGoal('WaitForExternalEvent', rxt_skills_panda.msg.WaitForExternalEventAction, rxt_skills_panda.msg.WaitForExternalEventGoal(inputText=b'void'))
        if result:
            print("Result was: " + str(result.isOK))
        print ('----------------------------------')

        # shutdown node
        #print ('----------------------------------')
        #print ('All requests done: Now trying to shutdown everything...')
        #print ('----------------------------------')
        #rospy.signal_shutdown("Finished with success!")
        #rospy.spin()
             
    except rospy.ROSInterruptException:
        print("program interrupted before completion")
