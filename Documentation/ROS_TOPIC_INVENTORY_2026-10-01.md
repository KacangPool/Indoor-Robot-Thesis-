# Complete ROS topic inventory — 2026-10-01 core report

Source: `reports/Ros topic report 22 topics.txt`, generated 2026-10-01 13:09:20 +02:00, reviewed 2026-10-02. This index transcribes the uploaded inventory; it does not query the robot.

188 unique topic names, 39 message types. 176 topics have registered publishers; 12 are subscriber-only. 74 are dynamic-reconfigure settings channels (37 descriptions, 37 updates). The core sampler attempted 22 topics: 15 received, 7 silent during their individual ten-second windows. The other 166 were not sampled.

Publisher/subscriber counts are the inventory snapshot, not guaranteed current counts or proof of actual message delivery. A reader can trigger lazy processing; `0` subscribers before sampling does not mean a topic is unusable. The report's temporary reader may register after connection information was collected. Message types alone do not establish hardware availability: e.g. GPS and AprilTag inputs have no publishers here.

See `ROS_CORE_REPORT_ANALYSIS_2026-10-01.md` for interpretation, units, measured values, limitations and follow-up priorities.

## Message-type counts

| Message type | Topic count |
|---|---:|
| `apriltag_ros/AprilTagDetectionArray` | 1 |
| `bond/Status` | 1 |
| `dynamic_reconfigure/Config` | 37 |
| `dynamic_reconfigure/ConfigDescription` | 37 |
| `geometry_msgs/PointStamped` | 1 |
| `geometry_msgs/PoseArray` | 1 |
| `geometry_msgs/PoseStamped` | 3 |
| `geometry_msgs/PoseWithCovarianceStamped` | 5 |
| `geometry_msgs/Twist` | 1 |
| `map_msgs/OccupancyGridUpdate` | 1 |
| `nav_msgs/MapMetaData` | 1 |
| `nav_msgs/OccupancyGrid` | 5 |
| `nav_msgs/Odometry` | 1 |
| `nav_msgs/Path` | 3 |
| `octomap_msgs/Octomap` | 2 |
| `rosgraph_msgs/Log` | 2 |
| `rtabmap_ros/Goal` | 1 |
| `rtabmap_ros/Info` | 1 |
| `rtabmap_ros/MapData` | 1 |
| `rtabmap_ros/MapGraph` | 2 |
| `rtabmap_ros/Path` | 2 |
| `rtabmap_ros/RGBDImage` | 2 |
| `rtabmap_ros/UserData` | 1 |
| `sensor_msgs/CameraInfo` | 5 |
| `sensor_msgs/CompressedImage` | 22 |
| `sensor_msgs/Image` | 11 |
| `sensor_msgs/Imu` | 2 |
| `sensor_msgs/JointState` | 1 |
| `sensor_msgs/LaserScan` | 1 |
| `sensor_msgs/NavSatFix` | 1 |
| `sensor_msgs/PointCloud2` | 14 |
| `std_msgs/Bool` | 1 |
| `std_msgs/Float32` | 1 |
| `std_msgs/Float64` | 1 |
| `std_msgs/Int32MultiArray` | 1 |
| `std_msgs/Int8` | 1 |
| `tf2_msgs/TFMessage` | 2 |
| `theora_image_transport/Packet` | 11 |
| `visualization_msgs/MarkerArray` | 1 |

## Every topic

Status `Received` means one sample arrived, not that all fields were valid. `No sample` means no message arrived during that topic's ten-second subscription window; it is not a diagnosis. `Not sampled` means inventory evidence only. Source line points to the detailed section in the uploaded text report.

| Topic | Message type | Publishers | Subscribers | Sample status | Source line |
|---|---|---:|---:|---|---:|
| `/camera/camera_nodelet_manager/bond` | `bond/Status` | 2 | 2 | Not sampled | — |
| `/camera/depth_rectify_depth/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth_rectify_depth/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered_rectify_depth/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered_rectify_depth/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/camera_info` | `sensor_msgs/CameraInfo` | 1 | 0 | Received | 726 |
| `/camera/depth_registered/hw_registered/image_rect` | `sensor_msgs/Image` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect_raw` | `sensor_msgs/Image` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect_raw/compressed` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect_raw/compressed/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect_raw/compressed/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect_raw/compressedDepth` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect_raw/compressedDepth/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect_raw/compressedDepth/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect_raw/theora` | `theora_image_transport/Packet` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect_raw/theora/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect_raw/theora/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect/compressed` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect/compressed/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect/compressed/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect/compressedDepth` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect/compressedDepth/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect/compressedDepth/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect/theora` | `theora_image_transport/Packet` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect/theora/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/hw_registered/image_rect/theora/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image` | `sensor_msgs/Image` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image_raw` | `sensor_msgs/Image` | 1 | 0 | Received | 672 |
| `/camera/depth_registered/image_raw/compressed` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image_raw/compressed/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image_raw/compressed/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image_raw/compressedDepth` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image_raw/compressedDepth/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image_raw/compressedDepth/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image_raw/theora` | `theora_image_transport/Packet` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image_raw/theora/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image_raw/theora/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image/compressed` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image/compressed/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image/compressed/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image/compressedDepth` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image/compressedDepth/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image/compressedDepth/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image/theora` | `theora_image_transport/Packet` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image/theora/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/image/theora/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth_registered/points` | `sensor_msgs/PointCloud2` | 1 | 0 | Received | 894 |
| `/camera/depth/camera_info` | `sensor_msgs/CameraInfo` | 1 | 0 | Not sampled | — |
| `/camera/depth/image` | `sensor_msgs/Image` | 1 | 1 | Received | 562 |
| `/camera/depth/image_raw` | `sensor_msgs/Image` | 1 | 1 | Received | 617 |
| `/camera/depth/image_raw/compressed` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_raw/compressed/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_raw/compressed/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_raw/compressedDepth` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_raw/compressedDepth/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_raw/compressedDepth/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_raw/theora` | `theora_image_transport/Packet` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_raw/theora/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_raw/theora/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect` | `sensor_msgs/Image` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect_raw` | `sensor_msgs/Image` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect_raw/compressed` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect_raw/compressed/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect_raw/compressed/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect_raw/compressedDepth` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect_raw/compressedDepth/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect_raw/compressedDepth/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect_raw/theora` | `theora_image_transport/Packet` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect_raw/theora/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect_raw/theora/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect/compressed` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect/compressed/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect/compressed/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect/compressedDepth` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect/compressedDepth/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect/compressedDepth/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect/theora` | `theora_image_transport/Packet` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect/theora/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth/image_rect/theora/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth/image/compressed` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/depth/image/compressed/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth/image/compressed/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth/image/compressedDepth` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/depth/image/compressedDepth/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth/image/compressedDepth/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth/image/theora` | `theora_image_transport/Packet` | 1 | 0 | Not sampled | — |
| `/camera/depth/image/theora/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/depth/image/theora/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/depth/points` | `sensor_msgs/PointCloud2` | 1 | 0 | Received | 821 |
| `/camera/driver/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/driver/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/ir/camera_info` | `sensor_msgs/CameraInfo` | 1 | 0 | Not sampled | — |
| `/camera/ir/image` | `sensor_msgs/Image` | 1 | 0 | Not sampled | — |
| `/camera/ir/image/compressed` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/ir/image/compressed/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/ir/image/compressed/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/ir/image/compressedDepth` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/ir/image/compressedDepth/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/ir/image/compressedDepth/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/ir/image/theora` | `theora_image_transport/Packet` | 1 | 0 | Not sampled | — |
| `/camera/ir/image/theora/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/ir/image/theora/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/projector/camera_info` | `sensor_msgs/CameraInfo` | 1 | 0 | Not sampled | — |
| `/camera/rgb_rectify_color/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/rgb_rectify_color/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/rgb/camera_info` | `sensor_msgs/CameraInfo` | 1 | 1 | Received | 466 |
| `/camera/rgb/image_raw` | `sensor_msgs/Image` | 1 | 2 | Received | 410 |
| `/camera/rgb/image_raw/compressed` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/rgb/image_raw/compressed/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/rgb/image_raw/compressed/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/rgb/image_raw/compressedDepth` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/rgb/image_raw/compressedDepth/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/rgb/image_raw/compressedDepth/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/rgb/image_raw/theora` | `theora_image_transport/Packet` | 1 | 0 | Not sampled | — |
| `/camera/rgb/image_raw/theora/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/rgb/image_raw/theora/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/rgb/image_rect_color` | `sensor_msgs/Image` | 1 | 0 | Not sampled | — |
| `/camera/rgb/image_rect_color/compressed` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/rgb/image_rect_color/compressed/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/rgb/image_rect_color/compressed/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/rgb/image_rect_color/compressedDepth` | `sensor_msgs/CompressedImage` | 1 | 0 | Not sampled | — |
| `/camera/rgb/image_rect_color/compressedDepth/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/rgb/image_rect_color/compressedDepth/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/camera/rgb/image_rect_color/theora` | `theora_image_transport/Packet` | 1 | 0 | Not sampled | — |
| `/camera/rgb/image_rect_color/theora/parameter_descriptions` | `dynamic_reconfigure/ConfigDescription` | 1 | 0 | Not sampled | — |
| `/camera/rgb/image_rect_color/theora/parameter_updates` | `dynamic_reconfigure/Config` | 1 | 0 | Not sampled | — |
| `/clicked_point` | `geometry_msgs/PointStamped` | 1 | 0 | Not sampled | — |
| `/cmd_vel` | `geometry_msgs/Twist` | 0 | 1 | No sample | 1708 |
| `/imu` | `sensor_msgs/Imu` | 1 | 1 | No sample | 1117 |
| `/initialpose` | `geometry_msgs/PoseWithCovarianceStamped` | 1 | 0 | Not sampled | — |
| `/joint_states` | `sensor_msgs/JointState` | 1 | 1 | Received | 1187 |
| `/map` | `nav_msgs/OccupancyGrid` | 1 | 0 | Received | 1358 |
| `/map_metadata` | `nav_msgs/MapMetaData` | 1 | 0 | Received | 1435 |
| `/move_base_simple/goal` | `geometry_msgs/PoseStamped` | 1 | 0 | No sample | 1740 |
| `/odom` | `nav_msgs/Odometry` | 1 | 2 | No sample | 1063 |
| `/PowerVoltage` | `std_msgs/Float32` | 1 | 0 | No sample | 1162 |
| `/rev_order` | `std_msgs/Int8` | 0 | 1 | Not sampled | — |
| `/robot_pose_ekf/odom_combined` | `geometry_msgs/PoseWithCovarianceStamped` | 1 | 0 | Not sampled | — |
| `/rosout` | `rosgraph_msgs/Log` | 30 | 1 | Not sampled | — |
| `/rosout_agg` | `rosgraph_msgs/Log` | 1 | 0 | Not sampled | — |
| `/rtabmap/cloud_ground` | `sensor_msgs/PointCloud2` | 1 | 0 | Not sampled | — |
| `/rtabmap/cloud_map` | `sensor_msgs/PointCloud2` | 1 | 0 | No sample | 1660 |
| `/rtabmap/cloud_obstacles` | `sensor_msgs/PointCloud2` | 1 | 0 | Not sampled | — |
| `/rtabmap/global_path` | `nav_msgs/Path` | 1 | 0 | Not sampled | — |
| `/rtabmap/global_path_nodes` | `rtabmap_ros/Path` | 1 | 0 | Not sampled | — |
| `/rtabmap/global_pose` | `geometry_msgs/PoseWithCovarianceStamped` | 0 | 1 | Not sampled | — |
| `/rtabmap/goal` | `geometry_msgs/PoseStamped` | 0 | 1 | Not sampled | — |
| `/rtabmap/goal_node` | `rtabmap_ros/Goal` | 0 | 1 | Not sampled | — |
| `/rtabmap/goal_out` | `geometry_msgs/PoseStamped` | 1 | 0 | Not sampled | — |
| `/rtabmap/goal_reached` | `std_msgs/Bool` | 1 | 0 | Not sampled | — |
| `/rtabmap/gps/fix` | `sensor_msgs/NavSatFix` | 0 | 1 | Not sampled | — |
| `/rtabmap/grid_map` | `nav_msgs/OccupancyGrid` | 1 | 1 | Received | 1484 |
| `/rtabmap/grid_map_updates` | `map_msgs/OccupancyGridUpdate` | 0 | 1 | Not sampled | — |
| `/rtabmap/grid_prob_map` | `nav_msgs/OccupancyGrid` | 1 | 0 | Not sampled | — |
| `/rtabmap/imu` | `sensor_msgs/Imu` | 0 | 1 | Not sampled | — |
| `/rtabmap/info` | `rtabmap_ros/Info` | 1 | 0 | No sample | 1562 |
| `/rtabmap/initialpose` | `geometry_msgs/PoseWithCovarianceStamped` | 0 | 1 | Not sampled | — |
| `/rtabmap/labels` | `visualization_msgs/MarkerArray` | 1 | 0 | Not sampled | — |
| `/rtabmap/landmarks` | `geometry_msgs/PoseArray` | 1 | 0 | Not sampled | — |
| `/rtabmap/local_grid_empty` | `sensor_msgs/PointCloud2` | 1 | 0 | Not sampled | — |
| `/rtabmap/local_grid_ground` | `sensor_msgs/PointCloud2` | 1 | 0 | Not sampled | — |
| `/rtabmap/local_grid_obstacle` | `sensor_msgs/PointCloud2` | 1 | 0 | Not sampled | — |
| `/rtabmap/local_path` | `nav_msgs/Path` | 1 | 0 | Not sampled | — |
| `/rtabmap/local_path_nodes` | `rtabmap_ros/Path` | 1 | 0 | Not sampled | — |
| `/rtabmap/localization_pose` | `geometry_msgs/PoseWithCovarianceStamped` | 1 | 0 | Not sampled | — |
| `/rtabmap/mapData` | `rtabmap_ros/MapData` | 1 | 0 | Not sampled | — |
| `/rtabmap/mapGraph` | `rtabmap_ros/MapGraph` | 1 | 0 | Not sampled | — |
| `/rtabmap/mapOdomCache` | `rtabmap_ros/MapGraph` | 1 | 0 | Not sampled | — |
| `/rtabmap/mapPath` | `nav_msgs/Path` | 1 | 0 | Not sampled | — |
| `/rtabmap/octomap_binary` | `octomap_msgs/Octomap` | 1 | 0 | Not sampled | — |
| `/rtabmap/octomap_empty_space` | `sensor_msgs/PointCloud2` | 1 | 0 | Not sampled | — |
| `/rtabmap/octomap_full` | `octomap_msgs/Octomap` | 1 | 0 | Not sampled | — |
| `/rtabmap/octomap_global_frontier_space` | `sensor_msgs/PointCloud2` | 1 | 0 | Not sampled | — |
| `/rtabmap/octomap_grid` | `nav_msgs/OccupancyGrid` | 1 | 0 | Not sampled | — |
| `/rtabmap/octomap_ground` | `sensor_msgs/PointCloud2` | 1 | 0 | Not sampled | — |
| `/rtabmap/octomap_obstacles` | `sensor_msgs/PointCloud2` | 1 | 0 | Not sampled | — |
| `/rtabmap/octomap_occupied_space` | `sensor_msgs/PointCloud2` | 1 | 0 | Not sampled | — |
| `/rtabmap/proj_map` | `nav_msgs/OccupancyGrid` | 1 | 0 | Not sampled | — |
| `/rtabmap/republish_node_data` | `std_msgs/Int32MultiArray` | 0 | 1 | Not sampled | — |
| `/rtabmap/rgbd_image` | `rtabmap_ros/RGBDImage` | 1 | 1 | Not sampled | — |
| `/rtabmap/rgbd_image/compressed` | `rtabmap_ros/RGBDImage` | 1 | 0 | Not sampled | — |
| `/rtabmap/scan_map` | `sensor_msgs/PointCloud2` | 1 | 0 | Not sampled | — |
| `/rtabmap/tag_detections` | `apriltag_ros/AprilTagDetectionArray` | 0 | 1 | Not sampled | — |
| `/rtabmap/user_data_async` | `rtabmap_ros/UserData` | 0 | 1 | Not sampled | — |
| `/scan` | `sensor_msgs/LaserScan` | 1 | 3 | Received | 971 |
| `/slam_gmapping/entropy` | `std_msgs/Float64` | 1 | 0 | Not sampled | — |
| `/tf` | `tf2_msgs/TFMessage` | 8 | 4 | Received | 1235 |
| `/tf_static` | `tf2_msgs/TFMessage` | 5 | 4 | Received | 1298 |

