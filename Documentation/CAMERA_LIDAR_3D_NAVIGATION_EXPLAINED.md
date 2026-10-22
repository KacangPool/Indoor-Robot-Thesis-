# Camera, LiDAR and the WHEELTEC 3D navigation demonstration

Reviewed 2026-09-16 against the copied ROS 1 source. This is an explanation and staged test procedure; no robot launch, motion, database change or navigation configuration change has been performed.

Update from terminal report 2: the expected depth topic delivers messages at 29.694 Hz; RTAB-Map, move_base and TEB resolve; the AMCL check needs the corrected spelling `amcl`. The uploaded database (104K, modified March 2, 2023) has now been inspected read-only: it is valid SQLite but has no saved observations, grid or cloud. It cannot serve as the navigation map. Navigation has not been started. See `TERMINAL_REPORT_2_ANALYSIS.md` and `RTABMAP_DATABASE_INSPECTION_2026-09-16.md` for evidence.

## What combining sensors can mean

| Use | Camera contribution | LiDAR contribution | Additional work |
|---|---|---|---|
| Shared RViz view | Colour and local depth surfaces | Horizontal obstacle outline | Correct sensor-to-base TF transforms |
| Mapping and navigation | Recorded RGB-D views and 3D surfaces | Planar map geometry and localization | Odometry, synchronization, mapping database and working navigation stack |
| Target marked on a map | Detect person/animal; registered depth locates visible surface | Helps determine robot pose on the map | Detector, target association and camera-to-map transform |
| Live obstacle coverage | Depth can observe obstacles above/below LiDAR plane | Surrounding low-plane measurements | Explicit depth obstacle source, filtering, calibration and evaluation |
| Detector/range comparison | RGB detection and short-range camera depth | Independent geometric returns | Time alignment and association; a return need not belong to the detected target |

The last three are possible developments, not capabilities proven by the current demo. A box around a person in an RGB image does not automatically identify which LiDAR return belongs to that person, particularly with this low scan plane and foreground furniture.

## Actual copied 3D navigation launch

`turn_on_wheeltec_robot/launch/3d_navigation.launch` includes:

1. `turn_on_wheeltec_robot.launch` with `navigation=true`, starting base communication, robot transforms, odometry/IMU filtering and `move_base` with the TEB local planner for `senior_akm`.
2. The physical LiDAR wrapper.
3. AMCL, configured to use `/rtabmap/grid_map` and scan data for planar localization.
4. The Astra camera wrapper.
5. `include/rtabmap_nav.launch`, consuming RGB-D, `/scan` and `/odom`, with saved database `~/.ros/test.db` and localization mode enabled.
6. `send_mark.py`, a waypoint helper capable of sending goals to the planner.

RTAB-Map synchronizes/stores sensor views, aligns measurements and supports mapping/localization. See the [official RTAB-Map project](https://introlab.github.io/rtabmap/). In this particular configuration, `Reg/Strategy=1` selects ICP registration and `Reg/Force3DoF=true` constrains registration to planar motion (x, y and heading). "3DoF" here does not mean three spatial dimensions of driving.

The navigation map is a top-down occupancy grid: cells describe occupied/free/unknown space. `move_base` plans travel on the floor and TEB handles the local driving trajectory. A reconstructed room can be displayed in 3D while the robot's path planning remains planar.

The copied mapping configuration explicitly sets `Grid/FromDepth=false`, generating the occupancy grid from LiDAR. The common navigation obstacle layer sets `observation_sources: scan`; its local obstacle input is LaserScan, not the camera cloud. Thus an overhead obstacle visible in the 3D cloud is not automatically a live obstacle for the planner. The presence of a voxel layer in the global costmap does not create additional camera observations.

## Three concrete issues to check before trying it

### Saved map and destructive mapping default

The navigation include defaults to `localization=true` and `~/.ros/test.db`. It expects a usable existing map of the environment. File existence alone does not prove a compatible or current map.

The companion `include/rtabmap_mapping.launch` uses the **same database path** and passes `--delete_db_on_start`. Starting the supplied `3d_mapping.launch` can delete the existing RTAB-Map database. Before any new mapping session, close the mapping/navigation processes and preserve the existing database. Create a separate reviewed launch with a new database path under `~/fahad` for experiments. The top-level vendor launches do not expose `database_path` as a top-level argument, so simply appending `database_path:=...` is not a verified override.

### Motion and RViz clicks

The navigation command enables the physical base and planner. The copied Ackermann planner permits forward and reverse speeds up to 0.5 m/s; these are configured limits, not a measured hardware maximum or an appropriate first-test recommendation.

The waypoint helper subscribes to `/clicked_point` and `/send_mark_goal`, publishes `/move_base_simple/goal`, and can cycle through waypoints. **RViz Publish Point can therefore start navigation**, as can 2D Nav Goal. Neither should be used during a stationary display inspection. Mouse Orbit/pan/zoom is different and does not submit a goal.

A first navigation test needs a known physical stop method and an open, supervised area. A motor inhibit must preserve the sensors/control-computer power if used for stationary inspection. Do not rely on Ctrl+C as the emergency-stop mechanism.

### Live compatibility, sensor alignment and TF

The navigation RGB-D synchronizer expects `/camera/depth/image`, not necessarily the `/camera/depth_registered/image_raw` topic used in earlier viewing examples. Verify the live topic, encoding, alignment with RGB and frame rate. A similarly named topic is not sufficient proof of registration.

The copied files combine AMCL, RTAB-Map and `odom`/`odom_combined` frames. Check the live TF tree and map-to-robot alignment before motion; do not assume all installed defaults match the copied files or that multiple localization nodes publish compatible transforms. Manual camera tilt changes require an updated camera-to-base transform.

## Immediate read-only check on the robot

These commands inspect the existing installation; they do not start the navigation stack:

```bash
source ~/wheeltec_robot/devel/setup.bash
rospack find turn_on_wheeltec_robot
rospack find rtabmap_ros
rospack find move_base
rospack find amcl
rospack find teb_local_planner
ls -lh ~/.ros/test.db
rosnode list
rostopic list
```

With the camera already running, inspect the topic expected by navigation:

```bash
rostopic info /camera/depth/image
rostopic hz /camera/depth/image
```

Stop `hz` with Ctrl+C after about 15 seconds. Missing `/odom` or base TF is expected if only sensor drivers are running; it means full navigation prerequisites are not yet active.

Capture the live launch files, which may differ from the transferred copy:

```bash
roscd turn_on_wheeltec_robot
sed -n '1,160p' launch/3d_navigation.launch
sed -n '1,180p' launch/include/rtabmap_nav.launch
```

Save the terminal results under `~/fahad/reports` and transfer them into the project's Terminal Reports folder.

## Conditional navigation trial

After verifying a suitable saved database, live RGB-D/scan/odometry, transforms and the physical stop procedure:

1. Stop manually started duplicate sensor/base/navigation launches cleanly; the full launch starts its own drivers. Do not run the mapping and navigation launches together.
2. Start the vendor command on the robot:

   ```bash
   source ~/wheeltec_robot/devel/setup.bash
   roslaunch turn_on_wheeltec_robot 3d_navigation.launch
   ```

3. Initially inspect it with motion inhibited and without submitting goals. If map/database/sensor/TF errors occur, stop the trial and preserve the output.
4. Open RViz separately: the copied RTAB-Map include does not automatically open it. Use Fixed Frame `map`, add Map `/rtabmap/grid_map`, LaserScan `/scan`, RobotModel/TF, and camera Image. Add a PointCloud2 only after selecting an actual published cloud topic. A live camera cloud is distinct from an accumulated map cloud.
5. Confirm that the laser scan matches walls in the map and that the robot pose/orientation is plausible. If needed and supported by the installed AMCL setup, 2D Pose Estimate initializes localization; it is distinct from 2D Nav Goal. It does not itself validate localization accuracy.
6. Review actual footprint, turning radius, speed limits and obstacle coverage before enabling a supervised short driving test. The first driving test is a separate step after stationary checks; the current user reports have not yet established these prerequisites.

If `test.db` is missing or describes another room, navigation is not ready. Plan a protected mapping session with a new database path, rather than casually starting the vendor mapping launch.

## Recommended project progression

First demonstrate that both sensors agree spatially in a common robot frame. Then evaluate RGB-D target detection and locating those detections relative to the robot. A later mapped experiment can attach target positions to the room map using LiDAR-supported robot localization. Direct camera/LiDAR range fusion and camera-enhanced obstacle avoidance should each have a separate measured benefit before becoming thesis requirements.

## Local source evidence

- `turn_on_wheeltec_robot/launch/3d_navigation.launch`
- `turn_on_wheeltec_robot/launch/include/rtabmap_nav.launch`
- `turn_on_wheeltec_robot/launch/include/rtabmap_mapping.launch`
- `turn_on_wheeltec_robot/launch/turn_on_wheeltec_robot.launch`
- `turn_on_wheeltec_robot/launch/include/teb_local_planner.launch`
- `turn_on_wheeltec_robot/launch/include/amcl.launch`
- `turn_on_wheeltec_robot/params_costmap_common/costmap_common_params.yaml`
- `turn_on_wheeltec_robot/params_costmap_common/global_costmap_params.yaml`
- `turn_on_wheeltec_robot/params_costmap_common/local_costmap_params.yaml`
- `turn_on_wheeltec_robot/params_costmap_car/param_senior_akm/teb_local_planner_params.yaml`
- `turn_on_wheeltec_robot/scripts/send_mark.py`

These paths are relative to the copied `From Robotics Lab/wheeltec_dev/wheeltec_robot_src/` tree. No edits were made to those vendor sources.
