# -- created by MecRoKa GBi 15.7.2021-->
# -- simple script for reading the urdf and showing it in with rviz
# -- urdf can be checked to be correct via command line using: 'check_urdf <(xacro model.urdf.xacro)' too

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

import xacro

def generate_launch_description():


    #Set filename for xacro file with robot description
    robot_description_file = os.path.join(
        get_package_share_directory('myackrov_description'),
        'urdf',
        'create_myackrov_base.urdf.xacro')
        
    # Convert xacro robot description file to urdf   
    robot_description_config = xacro.process_file(robot_description_file)
    #Convert urdf robot description to xml
    robot_description = {'robot_description': robot_description_config.toxml()}
    
    #Set filename for rviz configuration
    rviz_config_file = os.path.join(
        get_package_share_directory('myackrov_description'),
        'config',
        'myackrov.rviz'
        )

    #Define joint_state_publisher for rviz to publish joint states
    # run with gui to set joint states easily
    joint_state_publisher_node = Node(
      package='joint_state_publisher_gui',
      executable='joint_state_publisher_gui',
    )
 
    #Define robot state publisher to make robot tf's avaliable for rviz visualisation
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='both',
        parameters=[robot_description]
    )
    
    #Define rviz node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='log',
        arguments=['-d', rviz_config_file],
    )
    
    # return what shoud be launched
    return LaunchDescription([
        joint_state_publisher_node,
        robot_state_publisher_node,
        rviz_node,
    ])
