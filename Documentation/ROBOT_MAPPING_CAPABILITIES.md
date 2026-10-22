# What the robot's mapping system does

Reviewed 2026-09-16 from the copied ROS 1 launch/configuration files. This explains the installed software architecture; individual outputs remain subject to live verification.

## Mapping is live computation plus storage

Mapping does not simply record raw sensor data. During a mapping run the software repeatedly:

1. receives LiDAR, colour, depth and robot-motion estimates;
2. estimates where each observation was taken;
3. aligns new geometry with previous geometry;
4. marks space as free, occupied or unknown;
5. builds a connected history of robot poses and sensor observations;
6. recognizes revisited areas where possible and optimizes accumulated pose error;
7. publishes maps and transforms for live visualization;
8. stores the RTAB-Map graph/sensor data so it can later be loaded for localization, viewing, export and navigation.

Saving is the persistence step. The map-building and pose-estimation work happens continuously while the program runs.

## What `3d_mapping.launch` actually starts

The vendor launch starts two related mapping paths:

```text
LiDAR + wheel/IMU odometry
        -> GMapping
        -> /map (2D occupancy map)

RGB + depth + camera calibration + LiDAR scan + odometry
        -> RGB-D synchronization and RTAB-Map
        -> pose graph + /rtabmap/grid_map + ~/.ros/test.db
```

It also starts the physical base, LiDAR driver and Astra camera.

### GMapping functions

- Constructs a top-down occupancy grid from `/scan` and odometry.
- Estimates the planar map-to-robot relationship while the robot moves.
- Represents free, occupied and unknown cells rather than object identities.
- Publishes the conventional `/map` output used by many ROS tools.

The copied configuration uses 5 cm cells and begins with an approximately 10 x 8 m configured map region that can be managed by the mapping algorithm. Its LiDAR-range parameters are configuration values and do not independently prove physical range.

### RTAB-Map functions in this launch

- Synchronizes RGB and depth observations.
- Subscribes to `/scan` and `/odom` as well as synchronized RGB-D data.
- Creates map nodes: sensor observations associated with estimated robot poses.
- Connects consecutive/revisited nodes into a pose graph.
- Uses proximity/neighbor refinement and ICP scan registration in this configuration.
- Constrains motion to x, y and heading through `Reg/Force3DoF=true`, matching a ground robot.
- Publishes `/rtabmap/grid_map` for later localization/navigation.
- Stores observations, calibration, poses, graph links, features and map products in `~/.ros/test.db` when mapping succeeds.
- Can be inspected later with RTAB-Map's database viewer and can support point-cloud/mesh export where the stored depth data are valid.

The name `Force3DoF` here means planar pose `(x, y, heading)`, not a three-dimensional LiDAR.

The copied launch explicitly sets `Grid/FromDepth=false`. Therefore its occupancy grid is made from LiDAR geometry rather than from the camera depth image. RGB-D observations can still be stored and used for the RTAB-Map database/3D visualization, but the current grid setting does not make camera depth a navigation obstacle source.

## What becomes possible after making a good map

### Localization

The robot can compare current scan/camera observations with the stored map to estimate its position. The copied `3d_navigation.launch` loads `~/.ros/test.db` in localization mode and uses AMCL with `/rtabmap/grid_map` and `/scan`.

### Route planning and goal navigation

`move_base` can plan a path through the 2D grid, while the TEB local planner generates a drivable Ackermann trajectory that respects the configured footprint and turning radius. RViz goals or the included waypoint helper can send destinations.

### Live obstacle response

The navigation costmap can add current obstacles and clear free space as new LiDAR readings arrive. In the current configuration, `observation_sources: scan`; it uses the physical 2D LiDAR for live obstacle marking. Camera-visible overhead objects are not automatically added.

### Multi-waypoint movement

The included `send_mark.py` can accept RViz points/goals and cycle through stored target points. This is a movement function, not part of passive map viewing.

### Map review and repeatable experiments

The saved database can preserve the sensor/pose graph for later inspection, localization and reconstruction. A `.pgm`/`.yaml` snapshot can preserve the 2D occupancy grid. ROS bags are still valuable because they preserve original topics for repeatable offline processing; the database is not a complete substitute for a deliberately recorded experimental bag.

### Adding detected rescue targets

A future detector can use registered camera depth to estimate a visible person's or animal's 3D position relative to the camera. With calibrated transforms and a localized robot pose, that point can be transformed into the map frame and displayed/logged as a possible target location. This function is not present automatically in the vendor mapping launch and would be thesis-specific implementation.

## What the mapping system does not automatically do

- It does not recognize a person, animal or living being.
- It does not name rooms, furniture or objects.
- It cannot recover surfaces never observed by the camera or LiDAR.
- It does not turn the planar LiDAR into a 3D sensor.
- It does not guarantee that an apparent map is geometrically accurate.
- It does not automatically use the camera cloud for obstacle avoidance in this configuration.
- It cannot keep a reliable static map if moving people dominate the observations.
- It cannot compensate for a manually changed camera tilt unless the camera-to-base transform is updated.

Map quality depends on odometry/TF accuracy, sensor calibration, slow motion, overlapping observations, useful scene geometry/visual texture, stable camera angle and successful revisiting/loop alignment.

## The separate `pure3d` variants

`pure3d_mapping.launch` maps using RGB-D and odometry without the physical LiDAR input. It is a camera-based alternative, not proof of 3D LiDAR capability.

`pure3d_navigation.launch` converts selected depth-image rows into artificial `/scan` and `/scan2` topics for 2D navigation. It contains static transforms at 0.5 m and 0.1 m plus a configured maximum of 4 m. These values do not match the user's measured camera height of approximately 0.12-0.13 m or the Astra S's published 0.4-2 m depth range. This mode must be recalibrated and tested before use; its hard-coded frame names/heights must not be treated as measurements of this robot.

## See the exact live functions during mapping

With `3d_mapping.launch` running, use a separate sourced terminal:

```bash
rosnode info /slam_gmapping
rosnode info /rtabmap/rtabmap
rostopic list | grep -E '^/rtabmap|^/map$|^/map_metadata$'
rosservice list | grep -E 'rtabmap|dynamic_map'
rosparam get /rtabmap/rtabmap
```

These commands reveal the actual publishers, subscribers, services and parameters in the installed version. Service names must be captured before assuming that pause, resume, map retrieval, database backup or mode-switch services are available.

In RViz, compare:

- `/map`: GMapping's 2D LiDAR occupancy map;
- `/rtabmap/grid_map`: RTAB-Map's grid used by the copied 3D navigation launch;
- `/scan`: the current LiDAR slice;
- `/camera/depth_registered/points`: the current camera 3D surface cloud;
- RobotModel/TF: sensor/robot poses;
- Path, if a trajectory topic is actually published.

The two occupancy maps may differ because they are produced by different mapping processes and parameter sets. A map display becoming visible is the beginning of validation, not the end: compare walls, corners, scale, loop closure and robot pose against the real room.
