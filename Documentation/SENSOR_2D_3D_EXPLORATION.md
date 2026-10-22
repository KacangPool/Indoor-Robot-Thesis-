# Camera and LiDAR: understanding and testing 2D/3D output

Evidence reviewed: 2026-09-16. This guide uses the copied robot source, the uploaded terminal report, and manufacturer documentation. Run commands on the robot's existing ROS installation. Store reports and RViz configurations under the separate `~/fahad` folder.

## 1. Conclusions and remaining uncertainty

- Camera: the live driver identified **Orbbec ASTRA S**, serial `17121811539`. This is an original Astra-series **structured-light RGB-D camera**. It has a colour camera and an infrared depth system; describing the entire device as an ordinary monocular camera would omit its depth capability. It is not a conventional left/right stereo camera. Do not confuse it with the separately named Astra Stereo S U3, Astra Embedded S, Astra+, or Astra 2.
- LiDAR: the copied wrapper selects `ls_N10`; the copied driver publishes one planar `sensor_msgs/LaserScan`. This supports the configured 2D-scanner identification. The physical model still needs a readable label and the live driver output. A `/scan` topic alone cannot establish hardware identity because other systems can also generate a planar scan.
- A fixed horizontal 2D scanner measures a slice of a room. Software settings cannot add the missing vertical measurements.
- A 2D scanner can be part of a 3D scanning apparatus if its plane is deliberately swept through measured poses and the scans are transformed into one coordinate system. That requires additional mechanics/pose measurement/calibration and reconstruction software. Driving at the same height on a level floor mainly extends horizontal coverage.
- The Astra depth cloud is the immediate available route to viewing actual local 3D surfaces. A full room model requires combining overlapping views using tracked camera poses; an RViz display by itself does not perform this reconstruction.

## 2. Camera specification and measurement boundaries

| Item | What is known |
|---|---|
| Method | Infrared structured light: a projected pattern and its observed displacement provide depth by triangulation. |
| RGB output on this robot | CameraInfo reports 640 x 480; measured RGB rate approximately 29.60 FPS. |
| Depth specification | Manufacturer lists up to 640 x 480 at 30 FPS; robot depth performance still needs measurement. |
| Astra S depth range | Manufacturer specifies 0.4-2 m. RGB visibility/ML detection range is a separate measurement. |
| Depth field of view | Current original-series page lists 58.4 degrees horizontal, 45.5 degrees vertical. |
| RGB field of view | Same page lists 63.1 degrees horizontal, 49.4 degrees vertical for the non-Pro-Plus version. |
| Claimed precision | Manufacturer quotes +/-3 mm at 1 m. This is not a guarantee for every material, pixel or robot test. |
| Infrared wavelength | 850 nm; this is not a thermal camera. |
| Connection | USB 2.0 power/data. |
| IMU | Original-series specification lists none. |
| Environment | Indoor; current page lists 10-40 C. |

Source: [Orbbec original Astra Series](https://www.orbbec.com/products/structured-light-camera/astra-series/). These are model/family specifications, not new measured robot results. Older Astra documentation may quote different fields of view; use verified per-stream calibration and measured image boundaries for thesis geometry. Do not substitute successor-model specifications.

The user's RGB calibration is `fx=582.795354`, `fy=584.395006`, `cx=321.415982`, `cy=245.98941`, with `plumb_bob` distortion. Nonzero calibration values do not independently prove that the calibration is accurate.

The camera can supply colour pictures, an IR image, a depth image, depth aligned to colour, and derived 3D point clouds. Stream concurrency depends on the device/driver; the copied driver has an RGB-versus-IR preference, so do not assume RGB and IR can always run together.

Structured light depends on a visible IR pattern: strong ambient infrared, occlusion between emitter and receiver, and unsuitable surfaces can cause holes or incorrect depth. Test glass, mirrors, shiny surfaces and dark materials separately. Low visible light does not necessarily prevent active depth, but it can seriously degrade RGB recognition. See [Orbbec's explanation of structured light](https://www.orbbec.com/blog/structured-light-vs-itof-depth-cameras/).

One depth frame samples visible surfaces only; it does not reveal the back of objects, objects behind furniture, or the entire room. Registered depth aligns depth pixels with RGB geometry; it does not itself establish temporal synchronization or camera-to-LiDAR calibration.

## 3. First LiDAR experiment: prove the scan geometry

If the LiDAR is already publishing, do not start a duplicate driver. Otherwise, terminal 1:

```bash
source ~/wheeltec_robot/devel/setup.bash
roslaunch turn_on_wheeltec_robot wheeltec_lidar.launch
```

Terminal 2:

```bash
source ~/wheeltec_robot/devel/setup.bash
rostopic info /scan
rostopic type /scan
rostopic echo -n 1 /scan/header
rostopic echo -n 1 /scan
rostopic hz /scan
```

Stop the rate check after about 15 seconds with Ctrl+C. The complete scan message contains angles in radians, distances in metres and possibly return intensities. It contains no independent elevation angle per beam. `inf` is not a surface infinitely far away; it represents an invalid/missing/filtered return in this driver.

Run `rviz` in another terminal and configure:

1. Fixed Frame: the `frame_id` printed above, expected `laser`.
2. Add `LaserScan`, topic `/scan`.
3. Style: `Points` or `Flat Squares`; try point size 0.02-0.05 m if using a metre-sized style.
4. Views: `TopDownOrtho` for the horizontal outline, then `Orbit` to inspect the same points from the side.
5. Decay Time: compare 0 with about 1 second while the robot remains still. A longer decay retains history; it can leave trails when objects move.
6. If an intensity colour option exists and intensity data are populated, compare it with a single colour. Intensity indicates returned signal strength, not photographic colour or object identity.

Observe a wall, a corner, a tall cardboard box and chair legs. A wall should give a row, a corner two joined rows, and the box a nearer outline. The side view should show the samples lying in one plane. Merely rotating the RViz view does not collect new data.

At the reported approximately 14-16 cm scan height, the sensor intersects low furniture parts and legs. It can miss a tabletop or obstacle entirely above the scan plane.

Save the RViz setup using File > Save Config As inside `~/fahad`. These display experiments do not require editing vendor launch files.

## 4. What LiDAR settings actually exist in the copied driver

Capture the active parameters:

```bash
rosnode list
rosparam get /lsn10
```

Use the actual publisher node from `rostopic info /scan` if it differs.

| Setting | Actual meaning in the copied source |
|---|---|
| `scan_topic`, `frame_id` | Output name and coordinate-frame label. Renaming a frame does not geometrically transform data. |
| `serial_port`, `versions` | Device connection and protocol/baud selection; not a 2D/3D or resolution switch. |
| `min_range`, `max_range` | Copied into scan metadata; their values are not measured physical range capability. Wrapper sets 0 and 100 m. |
| `truncated_mode`, `disable_min`, `disable_max` | Enable and define masked angular sectors. Masking removes returns. |
| `angle_disable_min`, `angle_disable_max` | Additional angular exclusion handling in the source. |

The inspected implementation also discards low nonzero intensities at or below 5. This is hard-coded behaviour, not a surveyed live sensor threshold.

Parameters are read during driver initialization. A later `rosparam set` is not evidence that an already-running driver applied the change. Start by capturing the baseline and testing display settings. If a justified filtering experiment is needed, use a separate launch under `~/fahad`, change one value, restart that sensor driver, and compare recordings. No vertical-channel or 3D-mode setting was found.

Converting LaserScan to PointCloud2 only expresses the same measurements as coordinates. Points can still all lie in a plane. The PointCloud2 name does not establish volumetric coverage. See the ROS definitions of [LaserScan](https://raw.githubusercontent.com/ros/common_msgs/noetic-devel/sensor_msgs/msg/LaserScan.msg) and [PointCloud2](https://raw.githubusercontent.com/ros/common_msgs/noetic-devel/sensor_msgs/msg/PointCloud2.msg).

## 5. Camera experiment: view actual depth and 3D surfaces

Start the camera if it is not already running:

```bash
source ~/wheeltec_robot/devel/setup.bash
roslaunch turn_on_wheeltec_robot wheeltec_camera.launch
```

In another sourced terminal:

```bash
rostopic list | grep -E '^/camera/.*(image_raw|points|camera_info)$'
rostopic type /camera/depth_registered/points
rostopic echo -n 1 /camera/depth_registered/points/header
rostopic hz /camera/depth_registered/image_raw
```

Stop the rate command with Ctrl+C. Substitute actual topic names if these do not exist. Some processing is activated only when a viewer subscribes.

In RViz:

1. Fixed Frame: the cloud header's exact frame, expected `camera_rgb_optical_frame`.
2. Add `Image`: `/camera/rgb/image_raw`.
3. Add `PointCloud2`: `/camera/depth_registered/points`.
4. Choose `RGB8` if the cloud contains colour, otherwise `AxisColor`; keep Decay Time at 0 initially.
5. Use `Orbit` and view a matte box or chair from the side in the display. Place it approximately 0.5-1.5 m in front of the physical camera.

The points should occupy different heights and distances and show the visible shape of the object. Gaps and missing rear surfaces are expected. The camera/LiDAR may both run, but overlaying them accurately requires a valid calibrated transform; separate sensor-frame views are sufficient for this first comparison.

For a depth image, run `rqt_image_view` and select `/camera/depth/image_raw` or the available registered-depth topic. Displayed grey/colour values visualize depth, not the object's real colour.

Run the existing diagnostic script from `~/fahad/tools` for numeric frame rates, image encoding and depth validity. Its whole-image median is not the distance to a chosen target; a target-specific region and tape measure are needed for distance-accuracy testing.

## 6. Explore camera settings after saving the baseline

```bash
rosrun rqt_reconfigure rqt_reconfigure
```

Select the camera node if present. The copied `Astra.cfg` exposes auto-exposure, white balance, colour/depth/IR modes, depth registration, colour/depth synchronization, frame skipping and calibration/time offsets. A GUI edit can apply immediately. Photograph current values, change one setting, compare the same scene and restore the baseline.

Begin with auto-exposure/white-balance comparisons. The mode menu is shared across multiple cameras and explicitly has a source-code TODO about unsupported modes. Seeing a resolution or FPS in the menu does not mean this Astra S can supply it. Do not change depth scale/offset or timestamp offsets to improve the appearance; these alter measurement interpretation and require calibration evidence.

## 7. From live 3D view to a room model

Astra point clouds can be combined using RGB-D mapping software when overlapping views and reliable camera poses are available. The copied `3d_mapping.launch` includes 2D mapping, the camera and RTAB-Map. Thus a vendor-labelled 3D mapping feature does not imply a 3D LiDAR: the camera supplies depth surfaces and the LiDAR can assist planar localization. That launch also includes the base/mapping stack and is a separate experiment from sensor viewing.

Manually changing camera tilt invalidates any fixed camera-to-base transform unless its measured orientation is updated. Arbitrarily tilting the LiDAR and accumulating points with an unchanged transform does not produce a geometrically valid room map.

For the next lab session, capture the LiDAR label, `/scan` publisher/type/message/rate, a top and side RViz screenshot, the camera topic list, cloud header, and numeric depth diagnostics. Then measure a matte target at 0.5, 1, 1.5 and 2 m. Save results with the session date in `~/fahad/reports`. These measurements establish the usable sensing limits before changing mapping or detector scope.
