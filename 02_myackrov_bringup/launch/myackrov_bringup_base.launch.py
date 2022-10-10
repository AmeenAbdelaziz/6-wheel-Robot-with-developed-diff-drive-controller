# created by MecRoKa GBi 07.4.2022
# if there ist no joystick, the following comand can be used to publish a velocity command (depending on loaded controller):
# $ ros2 topic pub /my_diffdrive_controller/cmd_vel_unstamped geometry_msgs/msg/Twist "{linear: {x: 0.2}, angular: {z: 0.2}}"
# $ ros2 topic pub /my_ackrov_controller/cmd_vel_unstamped    geometry_msgs/msg/Twist "{linear: {x: 0.2}, angular: {z: 0.2}}"
#
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import ExecuteProcess, IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition, LaunchConfigurationEquals
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution, PythonExpression

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

import os 
import xacro
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    # robot description file to be loaded - can be set via launch file parameters too!
    my_robot_description_file = os.path.join(
        get_package_share_directory("myackrov_bringup"),
        "urdf",
        "create_myackrov_base.urdf.xacro",
    )   
    
    my_rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("myackrov_bringup"), "config", "myackrov.rviz"]
    )
    
    declared_arguments = []
       
    declared_arguments.append(
        DeclareLaunchArgument(
            "model",
            default_value=my_robot_description_file, 
            description="robot urdf file",       
        
        )
    )
    
    declared_arguments.append(
        DeclareLaunchArgument(
            "gazebo_world_file",
            default_value='worlds/empty.world',
            description="Gazebo world file",
        )
    )   
    
    declared_arguments.append(
        DeclareLaunchArgument(
            "rviz_config_file",
            default_value=my_rviz_config_file,
            description="Rviz configuration file",
        )
    )           
                
    robot_description  = {'robot_description': 
        Command(['xacro',' ', LaunchConfiguration('model'), 
                 ])}
            
    node_robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description],
    )

    myackrov_controllers = PathJoinSubstitution(
        [
            FindPackageShare("myackrov_bringup"),
            "config",
            "myackrov_base.yaml",
        ]
    )
       
    node_robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description],
    )

    controller_manager_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description, 
                    myackrov_controllers,
                   ], 
    )

    spawn_my_jsb_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["my_joint_state_broadcaster"],
        output="screen",
    )

    spawn_my_rover_controller = Node(
        package="controller_manager",
        executable="spawner",
#        arguments=["my_diffdrive_controller"],                                     # CHANGE here you controller (diff or ackerman) !!!!!!!!!!!!!!!!!
        arguments=["my_ackrov_controller"],
        output="screen",
    )    
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [PathJoinSubstitution([FindPackageShare("gazebo_ros"), "launch", "gazebo.launch.py"])]
        ),
        launch_arguments={'world': LaunchConfiguration('gazebo_world_file'), "verbose": "true"}.items(),
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", LaunchConfiguration('rviz_config_file')],
    )

    key_teleop_node = Node(
        package="teleop_twist_keyboard",
        executable="teleop_twist_keyboard",
        output='screen',
        prefix = 'xterm -e',
        name="teleop_twist_keyboard",
        remappings=[("/cmd_vel","/my_ackrov_controller/cmd_vel_unstamped")]
    )
 
    spawn_entity_gazebo = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=["-topic", "/robot_description", "-entity", "my_rover"],
        output="screen",       
    )
       
    nodes = [
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn_entity_gazebo,
                on_exit=[spawn_my_jsb_controller],
            )
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn_my_jsb_controller,
                on_exit=[spawn_my_rover_controller],                       
            )
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn_my_rover_controller,                   
                on_exit=[rviz_node,],
            )
        ),
        gazebo,                              
        node_robot_state_publisher,  
        spawn_entity_gazebo,
        key_teleop_node,
        #controller_manager_node,                 # in case of simulation automatically loaded by ros2_gazebo_plugin
     ]        
        
            
    return LaunchDescription(declared_arguments + nodes)
