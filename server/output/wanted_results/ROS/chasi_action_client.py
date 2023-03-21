#! /usr/bin/env python

import rospy
import time

import actionlib # Brings in the SimpleActionClient
import rxt_skills_chasi.msg # Brings in the messages used by the chasi actions

#------------------------------------------------------------------------------------------------------------------------------------------------------------
# client request helper function
#------------------------------------------------------------------------------------------------------------------------------------------------------------
def send_ROSActionRequest_WithGoal(skillName, skillMsgType, skillGoal):

    rospy.init_node('chasi_client_py') # Initializes a rospy node so that the SimpleActionClient can publish and subscribe over ROS

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
        
        # request MoveToLocation
        print ('----------------------------------')
        print ('INVOKING RXT_SKILL: MoveToLocation')
        result = send_ROSActionRequest_WithGoal('MoveToLocation', rxt_skills_chasi.msg.MoveToLocationAction, rxt_skills_chasi.msg.MoveToLocationGoal(location=b'parkingslot'))
        if result:
            print("Result was: " + str(result.isOK))
        print ('----------------------------------')

        # request WaitForUserInput
        print ('----------------------------------')
        print ('INVOKING RXT_SKILL: WaitForUserInput')
        result = send_ROSActionRequest_WithGoal('WaitForUserInput', rxt_skills_chasi.msg.WaitForUserInputAction, rxt_skills_chasi.msg.WaitForUserInputGoal(inputContent=b'rviz'))
        if result:
            print("Result was:", ''.join([str(n) for n in result.returnMessage.decode("utf-8")]))
        print ('----------------------------------')
        
        # request WaitForExternalEvent
        print ('----------------------------------')
        print ('INVOKING RXT_SKILL: WaitForExternalEvent')
        result = send_ROSActionRequest_WithGoal('WaitForExternalEvent', rxt_skills_chasi.msg.WaitForExternalEventAction, rxt_skills_chasi.msg.WaitForExternalEventGoal(inputText=b'rviz'))
        if result:
            print("Result was: " + str(result.isOK))
        print ('----------------------------------')
        
        # request GraphicalUserInteraction
        print ('----------------------------------')
        print ('INVOKING RXT_SKILL: GraphicalUserInteraction')
        result = send_ROSActionRequest_WithGoal('GraphicalUserInteraction', rxt_skills_chasi.msg.GraphicalUserInteractionAction, rxt_skills_chasi.msg.GraphicalUserInteractionGoal(outputMessage=b'rviz'))
        if result:
            print("Result was: " + str(result.isOK))
        print ('----------------------------------')
        
        # request GetData
        print ('----------------------------------')
        print ('INVOKING RXT_SKILL: GetData')
        result = send_ROSActionRequest_WithGoal('GetData', rxt_skills_chasi.msg.GetDataAction, rxt_skills_chasi.msg.GetDataGoal(inputData=b'position'))
        if result:
            print("Result was:", ''.join([str(n) for n in result.data.decode("utf-8")]))
        print ('----------------------------------')
        
        # request SetData
        print ('----------------------------------')
        print ('INVOKING RXT_SKILL: SetData')
        result = send_ROSActionRequest_WithGoal('SetData', rxt_skills_chasi.msg.SetDataAction, rxt_skills_chasi.msg.SetDataGoal(outputData=b'position'))
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
