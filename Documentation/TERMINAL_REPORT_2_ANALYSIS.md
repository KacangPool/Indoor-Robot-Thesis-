# Terminal report 2: navigation prerequisites

Reviewed 2026-09-16. Evidence: `Terminal Reports/Terminal Report 2 _ 16 9 2026 _ 1255 _ Terminal results.txt`. The user explicitly has not started 3D navigation. The raw report has been preserved unchanged.

Follow-up user result: `rospack find amcl` resolves to `/home/wheeltec/wheeltec_robot/src/navigation-melodic/amcl`; AMCL is therefore discoverable. This result was reported after the attached terminal file and does not alter the preserved report.

## Findings

| Check | Evidence | Interpretation |
|---|---|---|
| RTAB-Map | `rospack find rtabmap_ros` resolves under `/opt/ros/melodic/share` | ROS Melodic RTAB-Map package is discoverable; successful runtime execution is not yet tested. |
| move_base | Package resolves in `navigation-melodic/move_base` | Navigation package is discoverable. |
| TEB | Package resolves in `teb_local_planner-melodic-devel` | Local-planner package is discoverable. |
| AMCL | Report used `amc1`; follow-up `rospack find amcl` resolved to `/home/wheeltec/wheeltec_robot/src/navigation-melodic/amcl` | Package is discoverable; runtime localization is not yet tested. |
| Saved database | `/home/wheeltec/.ros/test.db`, displayed size 104K, modification date March 2, 2023 | File exists; contents, map coverage, integrity and compatibility with the current room are unknown. Size/date do not prove it is empty or useful. |
| Active sensor nodes | `/camera/driver`, camera-processing nodes and `/lsn10` | Camera processing and the expected LiDAR driver are active. A node name does not independently identify physical hardware or validate scan quality. |
| Required depth topic | `/camera/depth/image`, `sensor_msgs/Image`, publisher `/camera/camera_nodelet_manager` | Exact topic expected by the copied navigation synchronizer exists. |
| Depth message rate | Final average 29.694 Hz; displayed window 822; min/max intervals 0.022/0.049 s; interval standard deviation 0.00307 s | Depth image messages are arriving at roughly 30 FPS. Pixel validity, distance accuracy, resolution/encoding, RGB alignment and synchronization remain unverified. |
| Depth subscribers | None before the rate test | Not an error. The rate command subsequently subscribes and receives messages. |
| Registered cloud and depth | `/camera/depth_registered/points`, `/camera/depth_registered/image_raw`, other derived topics listed | Interfaces are advertised; this alone does not prove valid cloud/depth payloads or their frame rates. |
| Navigation state | No move_base, AMCL or RTAB-Map processing node in the list; no `/odom` or `/rtabmap/grid_map` topic | Consistent with camera/LiDAR viewing only. Missing base odometry/map is expected at this stage, not proof of failure. |
| Goal-like topics | `/move_base_simple/goal`, `/initialpose`, `/clicked_point`, `/rtabmap/republish_node_data` listed | Topic existence does not prove navigation is running; RViz tools/displays may advertise or subscribe to these names. |
| RViz | Two RViz processes listed | Both can be viewers; keeping one open can reduce unnecessary Jetson load. |

## Readiness conclusion

Follow-up: the user subsequently uploaded `test.db`. Read-only inspection found zero Node/Data/Link rows and NULL saved grid/cloud fields, with SQLite integrity `ok`. This uploaded database contains no room map. See `RTABMAP_DATABASE_INSPECTION_2026-09-16.md`; the earlier unknown-content status below is now resolved for this snapshot.

Software discovery and depth delivery checks have progressed. A usable map and a verified complete navigation chain are still missing evidence. Do not yet treat this as clearance for an autonomous goal. No new mapping run is required merely to inspect the old database.

## Next actions

1. Correct the package check:

   ```bash
   rospack find amcl
   ```

   The last character is a lowercase letter L.

2. With mapping/navigation still stopped, copy `/home/wheeltec/.ros/test.db` to the USB drive, then into this project's `Terminal Reports` folder. In Ubuntu Files, Ctrl+L allows entering `/home/wheeltec/.ros` directly; Ctrl+H also reveals hidden folders. Copy rather than move the original. If files called `test.db-wal` or `test.db-shm` are present, preserve those alongside the database and report their presence. Inspect the copied database locally before any map-resetting launch.

3. Capture depth metadata without dumping the image pixels:

   ```bash
   rostopic echo -n 1 /camera/depth/image/encoding
   rostopic echo -n 1 /camera/depth/image/width
   rostopic echo -n 1 /camera/depth/image/height
   rostopic echo -n 1 /camera/depth/image/header
   ```

   These checks still do not measure distance accuracy. The existing diagnostic monitor can report valid-depth fraction; a measured target distance is needed to assess correctness.

Optional local database inspection on the robot, if `sqlite3` is already installed:

```bash
sqlite3 -readonly ~/.ros/test.db "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
```

This lists table names only. Inspect the returned schema before choosing map-node queries; table existence does not establish a usable map. SQLite's `-readonly` option prohibits database writes: [official command-line documentation](https://sqlite.org/cli.html).

## Preserved caveats

The copied mapping launch deletes `~/.ros/test.db` at startup. The full navigation launch starts physical drive control, and its waypoint helper can treat RViz Publish Point as a driving goal. The next step is database and depth-content inspection, followed by a reviewed stationary navigation startup if the prerequisites are met.
