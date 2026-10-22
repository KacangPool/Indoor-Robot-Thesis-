# Direct WHEELTEC 3D mapping command sequence

Decision recorded 2026-09-16: use the installed vendor `3d_mapping.launch` for the first mapping trial. The previous `~/.ros/test.db` was inspected and found empty, and a copy is preserved in the project. The vendor mapping include passes `--delete_db_on_start`, so every new start recreates `~/.ros/test.db`.

This launch starts the physical base controller as well as LiDAR, camera, GMapping and RTAB-Map. It does not normally command motion on its own, but the robot becomes able to respond to `/cmd_vel`. Use a clear supervised area and the established physical stop method.

## Before starting

Stop separately launched camera, LiDAR, navigation, follower or teleoperation terminals with Ctrl+C. Do not run `3d_navigation.launch` at the same time.

Check for unexpected movement publishers:

```bash
source ~/wheeltec_robot/devel/setup.bash
rostopic info /cmd_vel
```

Before the base is started, it is acceptable for the topic not to exist. If an unexpected Publisher is listed, identify and stop that node before mapping.

## Terminal 1: start mapping

```bash
source ~/wheeltec_robot/devel/setup.bash
roslaunch turn_on_wheeltec_robot 3d_mapping.launch
```

Leave this terminal open. This recreates `/home/wheeltec/.ros/test.db` and begins storing mapping observations.

## Terminal 2: verify the stack while stationary

```bash
source ~/wheeltec_robot/devel/setup.bash
rosnode list | grep -E 'rtabmap|slam_gmapping|camera|lsn10|base|ekf'
rostopic list | grep -E '(^/odom$|^/scan$|grid_map|rgbd)'
rostopic info /cmd_vel
```

Measure these one at a time for about 15 seconds, stopping each with Ctrl+C:

```bash
rostopic hz /odom
rostopic hz /scan
rostopic hz /camera/depth/image
```

Then inspect map metadata:

```bash
rostopic echo -n 1 /rtabmap/grid_map/info
```

Do not drive if `/odom`, `/scan`, camera depth or the RTAB-Map node is absent, if the launch prints repeated red errors, or if an unknown `/cmd_vel` publisher exists.

## Terminal 3: RViz

```bash
source ~/wheeltec_robot/devel/setup.bash
rviz
```

Set Fixed Frame to `map`, then add:

- Map `/rtabmap/grid_map`;
- LaserScan `/scan`;
- TF;
- RobotModel;
- Image `/camera/rgb/image_raw`;
- PointCloud2 `/camera/depth_registered/points`, if published.

Use Orbit/pan/zoom only. Publish Point and 2D Nav Goal are not required for manual mapping.

The `/rtabmap/grid_map` display is a top-down occupancy grid. The PointCloud2 display is the camera's current visible 3D surface. A live cloud is not automatically a finished accumulated room model.

## Terminal 4: manual keyboard driving

Start this only after the stationary checks and physical stop procedure are satisfactory:

```bash
source ~/wheeltec_robot/devel/setup.bash
roslaunch wheeltec_robot_rc keyboard_teleop.launch
```

The terminal must retain keyboard focus. The copied program begins at 0.2 m/s. Press `x` several times before the first motion to reduce linear speed; it prints the resulting speed.

```text
i       forward
u / o   forward left / forward right
,       reverse
m / .   reverse arcs
space   commanded stop
k       commanded stop
x       reduce linear speed by 10 percent
c       reduce turn command by 10 percent
Ctrl+C  exit after stopping
```

Do not press `b`, which selects an omni-wheel mode unsuitable for this Ackermann car. The car cannot rotate in place. Drive slow wide arcs, keep the camera at a fixed marked tilt, collect overlapping views, and revisit the starting area. Avoid rapid motion and people walking closely around the robot during the baseline map.

## Useful observation commands during the run

```bash
rostopic echo -n 1 /odom
rostopic echo -n 1 /scan/header
rostopic echo -n 1 /camera/depth/image/header
rostopic hz /rtabmap/grid_map
ls -lh ~/.ros/test.db
```

The database growing in size indicates data are being stored; it does not by itself prove geometric map quality.

## Save a conventional 2D map snapshot

Near the end of the mapping run, while `/rtabmap/grid_map` is being published:

```bash
mkdir -p ~/fahad/maps
rosrun map_server map_saver -f ~/fahad/maps/lab_room_2d map:=/rtabmap/grid_map
```

Expected output files are `lab_room_2d.pgm` and `lab_room_2d.yaml`. These are useful for viewing and backup, but the later vendor 3D navigation launch uses the RTAB-Map database.

## Stop and preserve the database

1. In the teleop terminal, press space or `k`, then Ctrl+C.
2. Leave the robot still for several seconds.
3. In the mapping terminal, press Ctrl+C once and allow all nodes to close.
4. Only after shutdown, preserve the new database:

   ```bash
   mkdir -p ~/fahad/maps
   cp -p ~/.ros/test.db ~/fahad/maps/lab_room.db
   ls -lh ~/.ros/test.db ~/fahad/maps/lab_room.db
   sha256sum ~/.ros/test.db ~/fahad/maps/lab_room.db
   ```

The hashes should match immediately after copying. Keep `~/.ros/test.db` in place because the original `3d_navigation.launch` expects that path. Copy `~/fahad/maps/lab_room.db`, the 2D map files, terminal output and RViz screenshots to the project for inspection.

Starting `3d_mapping.launch` again will delete and recreate `~/.ros/test.db`. The personal copy remains safe unless deliberately overwritten.

## After mapping

With mapping stopped, the database can be viewed if the installed utility is available:

```bash
rtabmap-databaseViewer ~/.ros/test.db
```

The next decision is based on map evidence: stored-node count, database integrity, occupancy-grid shape, loop alignment and whether the LiDAR scan agrees with walls. Only then proceed to a stationary startup of `3d_navigation.launch`.
