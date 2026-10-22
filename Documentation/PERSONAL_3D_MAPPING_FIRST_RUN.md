# First protected 3D mapping run

This procedure follows confirmation that AMCL is installed and that the old `test.db` contains no map. It creates a separate RTAB-Map database under the user's `fahad` folder without editing the WHEELTEC workspace.

The supplied personal launch still starts the physical base controller because wheel/IMU odometry is needed while mapping. Starting it should not command movement by itself, but it makes the robot capable of responding to `/cmd_vel`. Establish the robot's normal physical stop method and use a clear supervised area before starting it.

## 1. Place the launch file

The user has created the personal folder. Ensure these subfolders exist:

```bash
mkdir -p ~/fahad/launch ~/fahad/maps ~/fahad/reports
```

Copy `Tools/fahad_3d_mapping.launch` from this project into:

```text
/home/wheeltec/fahad/launch/fahad_3d_mapping.launch
```

Confirm both paths:

```bash
ls -l ~/fahad/launch/fahad_3d_mapping.launch
ls -ld ~/fahad/maps
```

The XML file is data for `roslaunch`; it does not need executable permission or `catkin_make`.

## 2. Stop duplicate sensor launches

Close the terminals that separately launched the camera or LiDAR using Ctrl+C. Close one of the two reported RViz instances. Verify that the old sensor nodes are gone before the combined launch:

```bash
rosnode list
```

Do not kill arbitrary ROS processes if their purpose is unknown. The combined launch starts its own LiDAR, camera and base nodes; duplicate drivers can compete for the same USB device.

## 3. Start the mapping stack without driving

Keep the robot stationary and run:

```bash
source ~/wheeltec_robot/devel/setup.bash
roslaunch /home/wheeltec/fahad/launch/fahad_3d_mapping.launch
```

The default database is:

```text
/home/wheeltec/fahad/maps/lab_room.db
```

This custom launch does not pass `--delete_db_on_start`. If that database already exists, RTAB-Map may load and extend it. To start a different experiment, use a different name:

```bash
roslaunch /home/wheeltec/fahad/launch/fahad_3d_mapping.launch database_path:=/home/wheeltec/fahad/maps/lab_room_trial2.db
```

Do not use a path containing the old `~/.ros/test.db`.

## 4. Stationary verification

In a second sourced terminal:

```bash
rosnode list | grep -E 'rtabmap|slam_gmapping|camera|lsn10|base|ekf'
rostopic hz /odom
rostopic hz /scan
rostopic hz /camera/depth/image
rostopic echo -n 1 /rtabmap/grid_map/info
```

Run each `hz` command separately for about 15 seconds and stop it with Ctrl+C. Capture the launch errors and these results. `/odom`, `/scan`, camera depth and an RTAB-Map node must exist before driving. A map can remain small while the robot is stationary; that is expected.

Open RViz separately:

```bash
rviz
```

Use Fixed Frame `map` and add:

- Map `/rtabmap/grid_map`;
- LaserScan `/scan`;
- TF and RobotModel;
- Image `/camera/rgb/image_raw`;
- PointCloud2 `/camera/depth_registered/points` if it is live.

Do not use Publish Point or 2D Nav Goal during mapping. Neither is needed for manual mapping.

## 5. Manual motion for mapping

Only after the stationary checks and physical stop procedure are satisfactory, open a third sourced terminal:

```bash
roslaunch wheeltec_robot_rc keyboard_teleop.launch
```

This terminal must retain keyboard focus. The copied controller starts at 0.2 m/s linear speed and 0.5 rad/s turn command. Press `x` repeatedly to reduce linear speed before the first movement. The terminal prints the current value.

Useful keys for this Ackermann robot:

```text
i       forward
u / o   forward left / forward right
,       reverse
m / .   reverse arcs
space   immediate commanded stop
k       immediate commanded stop
x       reduce linear speed by 10%
c       reduce angular command by 10%
Ctrl+C  exit teleoperation after stopping
```

Do not select OmniMode (`b`). The car cannot rotate in place; make slow, wide arcs. Keep a hand ready on the established physical stop. Do not rely only on the terminal.

Drive through overlapping views rather than quickly covering maximum distance. Revisit the starting area to help loop closure. Keep the manually adjustable camera at one marked angle. Avoid abrupt turns and long views of blank walls; visual texture, corners and stable furniture help RGB-D registration. The Astra S depth range is approximately 0.4-2 m, while LiDAR supplies the occupancy grid in this configuration.

## 6. Stop and preserve the map

1. Press space or `k` in the teleop terminal.
2. Press Ctrl+C in the teleop terminal.
3. Keep the robot stationary for several seconds.
4. Press Ctrl+C once in the mapping launch terminal and allow nodes to close cleanly.
5. Check the database:

   ```bash
   ls -lh ~/fahad/maps/lab_room.db
   sha256sum ~/fahad/maps/lab_room.db
   ```

Copy the resulting database and terminal report to the project. A larger file is expected after real observations, but size alone does not prove map quality. Read-only inspection can count stored nodes and confirm saved map/cloud data before preparing navigation against this database.

## 7. What this launch preserves and changes

- It leaves the original WHEELTEC source and old `~/.ros/test.db` untouched.
- It follows the vendor 3D-mapping architecture: GMapping/base/LiDAR, Astra and RTAB-Map.
- It writes a new RTAB-Map database in `~/fahad/maps`.
- It starts hardware communication and can accept motion commands.
- It keeps the vendor choice `Grid/FromDepth=false`; the occupancy grid is created from LiDAR while RGB-D observations support the RTAB-Map database/3D view.

After a useful map is verified, prepare a matching personal navigation launch that reads the new database in localization mode and does not modify it.
