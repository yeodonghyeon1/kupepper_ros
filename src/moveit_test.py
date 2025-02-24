#!/usr/bin/python

import sys
import math
import rospy
import moveit_commander

from geometry_msgs.msg import Pose
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive

from tf.transformations import quaternion_from_euler

FRAME_ID = 'base_link'
(X, Y, Z, W) = (0, 1, 2, 3)
OPEN = 0.9
CLOSE = 0.15
OBJECT_POSITIONS = {'target_1': [0.05, 0.35, 0.3]}
PICK_ORIENTATION_EULER = [-math.pi / 2, 0, 0]
PLACE_ORIENTATION_EULER = [-math.pi / 2, 0, -math.pi / 2]
SCENE = moveit_commander.PlanningSceneInterface()


def create_collision_object(id, dimensions, pose):
    object = CollisionObject()
    object.id = id
    object.header.frame_id = FRAME_ID

    solid = SolidPrimitive()
    solid.type = solid.BOX
    solid.dimensions = dimensions
    object.primitives = [solid]

    object_pose = Pose()
    object_pose.position.x = pose[X]
    object_pose.position.y = pose[Y]
    object_pose.position.z = pose[Z]

    object.primitive_poses = [object_pose]
    object.operation = object.ADD
    return object


def add_collision_objects():
    # floor_limit = create_collision_object(id='floor_limit',
    #                                       dimensions=[10, 10, 0.2],
    #                                       pose=[0, 0, -0.8])
    # table_1 = create_collision_object(id='table_1',
    #                                   dimensions=[0.3, 0.6, 0.2],
    #                                   pose=[0.45, 0.3, -0.3])
    # table_2 = create_collision_object(id='table_2',
    #                                   dimensions=[0.3, 0.3, 0.2],
    #                                   pose=[0.15, 0.45, -0.3])
    target_1 = create_collision_object(id='target_1',
                                       dimensions=[0.2, 0.2, 0.2],
                                       pose=[0.3, 0, -0.1])

    # SCENE.add_object(floor_limit)
    # SCENE.add_object(table_1)
    # SCENE.add_object(table_2)
    SCENE.add_object(target_1)


def reach_named_position(arm, target):
    arm.set_named_target(target)
    return arm.execute(arm.plan(), wait=True)


def reach_pose(arm, pose, tolerance=0.001):
    arm.set_pose_target(pose)
    arm.set_goal_position_tolerance(tolerance)
    return arm.go(wait=True)


def open_gripper(gripper):
    return gripper.move(gripper.max_bound() * OPEN, True)


def close_gripper(gripper):
    gripper.move(gripper.max_bound() * CLOSE, True)


def pick_object(name, arm, left_hand, right_hand, gripper, gripper2):
    pose = Pose()
    pose.position.x = OBJECT_POSITIONS[name][X]
    pose.position.y = OBJECT_POSITIONS[name][Y] - 0.1
    pose.position.z = OBJECT_POSITIONS[name][Z]
    orientation = quaternion_from_euler(*PICK_ORIENTATION_EULER)
    pose.orientation.x = orientation[X]
    pose.orientation.y = orientation[Y]
    pose.orientation.z = orientation[Z]
    pose.orientation.w = orientation[W]
    reach_pose(left_hand, pose)
    reach_pose(right_hand, pose)

    open_gripper(gripper=gripper)
    open_gripper(gripper=gripper2)
    pose.position.y += 0.1
    reach_pose(left_hand, pose)
    reach_pose(right_hand, pose)
    close_gripper(gripper=gripper)
    arm.attach_object(name)


def place_object(name, arm, left_hand, right_hand, gripper, gripper2):
    pose = Pose()
    pose.position.x = OBJECT_POSITIONS[name][Y]
    pose.position.y = OBJECT_POSITIONS[name][X]
    pose.position.z = OBJECT_POSITIONS[name][Z]
    orientation = quaternion_from_euler(*PLACE_ORIENTATION_EULER)
    pose.orientation.x = orientation[X]
    pose.orientation.y = orientation[Y]
    pose.orientation.z = orientation[Z]
    pose.orientation.w = orientation[W]

    reach_pose(left_hand, pose)
    reach_pose(right_hand, pose)

    open_gripper(gripper=gripper)
    open_gripper(gripper=gripper2)

    reach_pose(left_hand, pose)
    reach_pose(right_hand, pose)

    arm.detach_object(name)


def main():
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('pick_place')
    rospy.sleep(2)

    arm = moveit_commander.MoveGroupCommander('both_arms',
                                              ns=rospy.get_namespace())
    left_hand = moveit_commander.MoveGroupCommander('right_arm',
                                            ns=rospy.get_namespace())
    right_hand = moveit_commander.MoveGroupCommander('left_arm',
                                            ns=rospy.get_namespace())
    robot = moveit_commander.RobotCommander('robot_description')
    print(robot.get_joint_names('both_arms'))
    gripper = robot.get_joint('RWristYaw')
    gripper2 = robot.get_joint('LWristYaw')


    arm.set_num_planning_attempts(45)
    # left_hand.set_num_planning_attempts(45)
    # right_hand.set_num_planning_attempts(45)

    add_collision_objects()
    pick_object(name='target_1', arm=arm, left_hand=left_hand, right_hand=right_hand, gripper=gripper,gripper2=gripper2)
    place_object(name='target_1', arm=arm, left_hand=left_hand, right_hand=right_hand, gripper=gripper, gripper2=gripper2)
    
    try:
        reach_named_position(arm=arm, target='home')
    except:
        print("error")

if __name__ == '__main__':
    main()