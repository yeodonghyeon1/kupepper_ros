#!/usr/bin/env python
# license removed for brevity

import rospy

# Brings in the SimpleActionClient
import actionlib
from geometry_msgs.msg import PoseStamped
# Brings in the .action file and messages used by the move base action

def movebase_move(x, y):

    pub_move = rospy.Publisher("/move_base_simple/goal", PoseStamped, queue_size=100)
    goal = PoseStamped()
    goal.header.frame_id = "map"
    goal.header.stamp = rospy.Time.now()
   # Move 0.5 meters forward along the x axis of the "map" coordinate frame 
    goal.pose.position.x = x
   # No rotation of the mobile base frame w.r.t. map frame
    goal.pose.position.y = y

    pub_move.publish(goal)
    print("start~~")    


# If the python node is executed as main process (sourced directly)
if __name__ == '__main__':
    rospy.init_node('movebase_client_py')
    pass

    # try:
    #    # Initializes a rospy node to let the SimpleActionClient publish and subscribe
    #     result = movebase_client()
    #     if result:
    #         rospy.loginfo("Goal execution done!")
    # except rospy.ROSInterruptException:
    #     rospy.loginfo("Navigation test finished.")