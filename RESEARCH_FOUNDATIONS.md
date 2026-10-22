# Robot, manuals, datasets, and thesis direction

Date: 2026-08-17

## Executive conclusion

The photographed platform is a **WHEELTEC high-configuration Ackermann robot**, with the chassis/software variant `senior_akm`. The platform marking printed on the internal label is **WHEELTEC R PLUS**. It is not the current R550. Cross-checking the photographs against JKK Research Center's robot and the 2023 English Roboworks manual indicates that **Roboworks Rosbot Mini Ackermann** is the closest documented export/rebrand of this WHEELTEC chassis generation.

The platform is suitable for a laboratory bachelor-thesis prototype that detects and localizes **visible rescue targets** (initially people, cats, and dogs) using RGB plus depth. It is not capable of proving that a detected person or animal is alive from a single RGB image. It is also not a fire-rated robot and should not be presented as ready for deployment in heat, flames, water, or dense smoke.

The recommended thesis task is **real-time object detection**, not whole-image classification. A detector can draw a bounding box around each target, assign a class and confidence, and combine the camera's depth value to estimate distance.

## Identification from the photographs

| Item | Finding | Confidence | Basis |
|---|---|---:|---|
| Manufacturer | WHEELTEC | Confirmed | Chassis labels and logo |
| Platform marking | WHEELTEC R PLUS | Confirmed | Internal label in `photo_2026-08-17_10-03-33.jpg`; this is not proof that the robot is an R550 |
| Product description | High-configuration Ackermann robot car, standard version | Confirmed | Direct translation of `高配版阿克曼小车 / 常规型版本` on the label |
| Motion model | Ackermann steering | Confirmed | Chinese label and visible front steering linkage |
| ROS configuration name | `senior_akm` | Confirmed | Printed chassis label |
| Computer | NVIDIA Jetson Nano, probably 4 GB | High | Board layout/heatsink matches; matching WHEELTEC configuration listings use Jetson Nano |
| Camera | Orbbec Astra-series RGB-D camera, probably Astra Pro | High | Housing and sensor arrangement match; matching configuration lists Astra Pro RGB-D |
| Lidar | LSLiDAR N10/N10P-class single-line 2D lidar | Medium-high | Physical form and matching configuration listing; exact suffix is not readable |
| Chassis tier | Mid-size/advanced Ackermann with about 125 mm wheels and pendulum suspension | High | Wheel size, front axle mechanism, and matching WHEELTEC configuration |
| Export/rebrand identity | Roboworks Rosbot Mini Ackermann | High-confidence equivalent, not shipment-confirmed | JKK's robot photograph closely matches the chassis/wheels and their hardware/software description matches the visible Jetson Nano, Orbbec camera, N10 lidar, network defaults, and WHEELTEC ROS stack |
| Motors/steering candidate | 2 x MD36N 35 W motors and HWZ020 20 kg digital servo | Medium-high | 2023 Rosbot Mini manual and matching chassis diagram; verify component labels before final citation |
| Battery product-spec candidate | 22.4 V 6000 mAh, 7S LiFePO4; 25.55 V full charge; 3 A charge; DC 4.0 x 1.7 mm charge socket; XT60U-F discharge | Medium-high | User-supplied WHEELTEC product graphic `robotspecs15.avif` and matching WHEELTEC R5-series product documentation; the installed battery label and charging-port polarity remain unreadable/unverified |

The label's QR instructions indicate that the exact manufacturer's product-material package can be requested from WHEELTEC's official WeChat account using retrieval code `G4bBr330`. This is the strongest route to the exact original manual, ROS image, source packages, and wiring information for this particular shipment.

## Likely chassis specifications (must be verified on the physical robot)

The closest documented older-generation configuration is the 2023 Roboworks Rosbot Mini:

- 445 x 358 x 125 mm chassis dimensions (sensor/computer installation adds height);
- 125 mm wheels and coaxial pendulum suspension;
- 0.320 m wheelbase, consistent with the `senior_akm` ROS parameter;
- approximately 0.77 m minimum turning radius;
- maximum speed around 1.3 m/s;
- stated load capacity 10 kg;
- 2 x MD36N 35 W motors, 500-line encoders, and HWZ020 20 kg steering servo;
- N10/M10-family lidar and Orbbec Astra RGB-D camera;
- 22.4 V, 6000 mAh, 7S LiFePO4 battery is now the stronger product-spec candidate. Its documented charging requirement is a 25.55 V, maximum 3 A LiFePO4 CC/CV charger with a DC 4.0 x 1.7 mm plug and verified polarity.

The chassis, motor, steering, and geometry values above come from the visually matching Rosbot Mini manual and related ROS references, not a serial-number-specific WHEELTEC document. The newer user-supplied battery product graphic provides stronger battery evidence than the older manual's 22.2 V/5000 mAh listing, but physical measurement, the installed battery label, and verified charging-port polarity must still take priority.

## What the platform can do

### Mobility and low-level feedback

- Drive forward/backward and steer like a car.
- Publish wheel odometry and IMU data through its WHEELTEC ROS base controller.
- Accept motion commands through ROS, with the common WHEELTEC stack publishing/subscribing through `/cmd_vel` and base-controller nodes.
- Report battery voltage and support controller/serial diagnostics in the WHEELTEC stack.
- Important limitation: Ackermann steering cannot turn on the spot. Navigation planners and recovery behaviours must respect its turning radius and wheelbase.

### Lidar navigation

- Produce a 360-degree horizontal laser scan for obstacle detection and 2D mapping.
- Run 2D SLAM and map-based navigation through the WHEELTEC ROS packages.
- The generic WHEELTEC guide documents lidar following, Gmapping/Hector/Karto/Cartographer mapping, map saving, and ROS navigation.
- A 2D lidar sees a single horizontal slice. It can miss low or high obstacles and does not classify a return as a person or animal.

### RGB-D vision

- Produce RGB images, depth maps, and point clouds through the Astra/OpenNI stack.
- Use depth to estimate the distance from the camera to a detected person or animal.
- Support OpenCV/ROS image processing, visual tracking, line following, AR-tag recognition, and depth-based behaviours in the supplied WHEELTEC software family.
- Structured-light depth is intended for indoor use. Smoke, sunlight, reflective surfaces, and sensor occlusion can reduce or invalidate depth readings.

### Machine-learning deployment

- The probable Jetson Nano has a 128-core Maxwell GPU, quad-core ARM Cortex-A57 CPU, and 4 GB LPDDR4 memory.
- It can run a lightweight object detector locally, especially after ONNX/TensorRT conversion and FP16 optimization.
- It is too constrained for large modern models at high resolution while simultaneously running heavy SLAM. The thesis should measure detector latency, frame rate, memory usage, and the effect of concurrent robot workloads.
- NVIDIA lists JetPack 4 as end-of-life. This matters because the original Jetson Nano software stack is old and current Python/PyTorch packages may not install directly. First inspect the installed JetPack, Ubuntu, CUDA, TensorRT, ROS, and Python versions before selecting the final training/deployment framework.

## What can be manipulated for the thesis

1. **Camera stream:** image size, frame rate, RGB/depth registration, camera calibration, exposure, and the region sampled for depth.
2. **Detector:** class set, input resolution, confidence threshold, non-maximum suppression, augmentations, model size, and TensorRT precision.
3. **Target output:** bounding boxes, class, confidence, estimated distance, track ID, timestamp, and robot/map position.
4. **Tracking:** temporal confirmation can suppress one-frame false alarms and provide motion evidence, but motion alone is not proof of life.
5. **Navigation integration:** slow/stop the robot near a candidate, place a marker in the map, save an image, and notify an operator.
6. **Safety policy:** default to high recall, keep a human operator in the loop, and never allow a detector result to be treated as a medical determination.

## Manuals and technical sources

### Files saved in this workspace

- `Documentation/WHEELTEC_Roboworks_Rosbot_Mini_Manual_EN_2023.pdf` - 11-page English Rosbot manual for the closest documented WHEELTEC/Roboworks chassis generation. It contains the matching Ackermann chassis diagram, 0.320 m wheelbase, 125 mm wheels, Jetson Nano option, N10 lidar, Orbbec Astra camera, STM32 board, motors, servo, battery, and control interfaces.
- `Documentation/WHEELTEC_R550_Product_Manual_CN.pdf` - official WHEELTEC R550 family product manual. It is a related modern ecosystem reference only; the photographed label does not say R550, so this file is not the robot's exact product manual.
- `Documentation/WHEELTEC_ROS_LiDAR_Vision_Guide_RU.pdf` - detailed WHEELTEC ROS guide covering lidar following, mapping, 2D navigation, colour following, line following, KCF tracking, and AR tags. The guide is in Russian and is generic across WHEELTEC ROS robots.
- `Documentation/LSLiDAR_N10_Datasheet_EN.pdf` - official English N10 lidar datasheet. The photographed unit may be the N10P variant, so verify the label before citing exact range/accuracy values.
- `Reference Library/WHEELTEC ACKERMAN ROS Small Robot Car Manual .pdf` - 51-page image compilation of the AliExpress listing. It is a capability/curriculum catalogue, not a conventional operating manual.
- `Reference Library/robot user manual.pdf` - 16-page 2024 Roboworks Rosbot family manual with ROS2 quick start, control methods and a list of pre-installed packages. It covers newer/larger Rosbot variants and is not proof of the exact R PLUS shipment.
- `Reference Library/WHEELTEC_CAPABILITY_DOCUMENTATION_MAP.md` - access map for the advertised public manuals, videos, source repositories, Baidu images and seller-only course bundle.

### Online references

- [JKK Research Center WHEELTEC/Roboworks ROS 1 workshop](https://jkk-research.github.io/workshops/wheeltec_real_a/) - documents a visually matching Rosbot Mini Ackermann with Jetson Nano, Orbbec depth camera, LSN10 lidar, WHEELTEC network defaults, and ROS 1 launch commands.
- [JKK Research Center WHEELTEC 101](https://jkk-research.github.io/workshops/wheeltec_real_b/) - current ROS 2 operational notes.
- [JKK/Robotverseny ROS 2 driver repository](https://github.com/robotverseny/drivers) - community-maintained ROS 2 drivers for the WHEELTEC/Roboworks platform.
- [2023 Roboworks Rosbot Mini manual (direct PDF)](https://static1.squarespace.com/static/5e76e0c52a318c0c1a850442/t/63f4408fe7287f4a231273ad/1676951781181/Rosbot%2BUser%2BManual.pdf)
- [Roboworks apps and developer resources](https://www.roboworks.net/apps) - ROS resources, disk-image links, URDF/STP files, mobile controller apps, and STM32 source/schematic downloads.
- [Roboworks Wheelbots ROS 2 repository](https://github.com/Roboworks-Global/wheelbots) - current open-source packages; use cautiously because the current repository targets newer product revisions.
- [Older WHEELTEC STM32 mobile-chassis development manual mirror](https://www.scribd.com/document/873153288/2-STM32%E8%BF%90%E5%8A%A8%E5%BA%95%E7%9B%98%E5%BC%80%E5%8F%91%E6%89%8B%E5%86%8C-ROS%E6%9C%BA%E5%99%A8%E4%BA%BA-2023-10-19) - contains the exact category `高配版阿克曼小车(常规型)` and Ackermann control details; third-party Scribd mirror, not an official download host.
- [Older WHEELTEC ROS functions and analysis manual mirror](https://www.scribd.com/document/873153290/1-WHEELTEC-ROS%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%8A%9F%E8%83%BD%E4%BD%BF%E7%94%A8%E4%B8%8E%E8%A7%A3%E6%9E%90) - explicitly contains the `senior_akm` software profile; third-party Scribd mirror.
- [Official WHEELTEC R550 product manual](https://www.wheeltec.net/R550.pdf)
- [Official WHEELTEC ROS product/function documentation](https://lubancat.wheeltec.net/zh-cn/main/)
- [Downloadable PDF of the official WHEELTEC online manual](https://lubancat.wheeltec.net/_/downloads/zh_CN/main/pdf/)
- [Official GitHub source for the WHEELTEC online manual](https://github.com/wheeltec/docs)
- [Official WHEELTEC ROS introductory video series](https://www.bilibili.com/video/BV1h84y1F7DD/)
- [Official WHEELTEC ROS2 function video series](https://www.bilibili.com/video/BV1gs421G7Jp/)
- [Official WHEELTEC ROS2 introductory video series](https://www.bilibili.com/video/BV1wS411P7Hy/)
- [Detailed WHEELTEC ROS lidar and vision guide](https://supereyes.ru/img/instructions/wheeltec_mecanum_wheel_manual_rus.pdf)
- [Closest matching WHEELTEC Ackermann configuration and specifications](https://supereyes.ru/catalog/roboty_nvidia_jetson_nano/robot_avtomobil_wheeltec_ackerman_ros/)
- [Official NVIDIA Jetson Nano specifications](https://developer.nvidia.com/embedded/jetson-nano)
- [Official NVIDIA Jetson Nano developer-kit guide](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit)
- [NVIDIA JetPack archive](https://developer.nvidia.com/embedded/jetpack-archive)
- [Official Orbbec Astra-series specifications](https://www.orbbec.com/products/structured-light-camera/astra-series/)
- [Official LSLiDAR N10 datasheet](https://www.lslidar.com/wp-content/uploads/2024/09/N10.pdf)

### Chinese/Baidu search conclusion

- Searches for the exact Chinese chassis description together with `senior_akm` did not surface an indexed WHEELTEC product manual.
- Searching the unique retrieval key `G4bBr330` returned no relevant robot documentation.
- This does not prove that documentation never existed. It supports the conclusion that the original package was distributed through WHEELTEC's WeChat retrieval system, private download links, seller archives, or the pre-installed robot filesystem rather than a stable public product page.
- The pre-installed Jetson storage may be the best surviving copy of the exact source tree and configuration. Back it up before upgrades or reinstallation.
- The AliExpress curriculum images specifically advertise more than 130 video sections and a Baidu Netdisk archive larger than 30 GB. No share URL or extraction code for that complete archive appears in the saved listing pages. This is therefore a seller/manufacturer fulfilment item, distinct from the smaller set of public WHEELTEC manuals and playlists.
- The official WHEELTEC manual does publish R550 ROS1/ROS2 and PC virtual-machine Baidu links, but these are family references rather than confirmed `senior_akm` images. They must not be flashed onto the robot without a complete backup and compatibility check.

## Recommended thesis scope

### Current-stage boundary

The thesis currently focuses on the perception tool, not autonomous robotics. The robot may remain stationary or be driven manually with a controller while the detector processes its camera stream. Mapping, path planning, autonomous navigation, and automatic approach to a target are possible later extensions and are not required for the first implementation or evaluation.

### Suggested research question

> How accurately and efficiently can a lightweight camera-based object detector identify visible humans, cats, and dogs from a stationary or manually controlled indoor robot under normal, low-light, occluded, and unusual-pose conditions?

This scope is measurable and matches the available hardware. Use wording such as **rescue-target detection** or **human/animal presence detection**, not **living-being verification**, unless an additional life-sign sensor and an appropriate temporal validation method are introduced.

### Suggested system output

For every detection, publish/store:

- class: `person`, `cat`, `dog` (optionally `other_animal` only if sufficient data exists);
- confidence score;
- RGB bounding box;
- median valid depth inside a safe central part of the box, if depth is used;
- track ID and persistence duration, if tracking is added;
- alert image and timestamp.

Class, confidence, and bounding boxes are the essential initial outputs. Depth, tracking, and map coordinates are enhancements; map coordinates are not required at the current stage.

## Dataset sources

### Recommended core datasets

| Dataset | Best use here | Important details and license notes |
|---|---|---|
| [COCO](https://cocodataset.org/) | Starting weights and baseline for person/cat/dog/bird and common objects | Mature detection benchmark with 80 classes. Image licenses originate from Flickr and vary; read COCO's terms before redistributing images. A pretrained detector avoids downloading the full set for the first prototype. |
| [Open Images V7](https://storage.googleapis.com/openimages/web/index.html) and [downloads](https://storage.googleapis.com/openimages/web/download_v7.html) | Main source for filtered person and animal bounding boxes | About 9M images overall and 16M boxes over 600 classes. Google licenses annotations under CC BY 4.0 and lists images as CC BY 2.0, while warning users to verify individual image licensing. Subsets can be downloaded by class. |
| [CrowdHuman](https://www.crowdhuman.org/) | Occluded and partially visible people | 15,000 training and 4,370 validation images, with about 470k human instances and visible/full/head boxes. Terms limit use to non-commercial research/education and prohibit redistributing the images. |
| [Oxford-IIIT Pet](https://www.robots.ox.ac.uk/~vgg/data/pets/) | Cat/dog appearance, segmentation, and species experiments | 7,349 images across 37 breeds, with species/breed labels, head ROI, and foreground masks. CC BY-SA 4.0; it is not a ready-made full-body object-detection set. |
| [LLVIP](https://github.com/bupt-ai-cz/LLVIP) | Low-light person detection research | 15,488 aligned visible/infrared pairs with pedestrian boxes. Most data are outdoor night scenes and the robot currently has no thermal camera. Confirm terms before use because a clear dataset license is not displayed on the project page. |
| [C2A disaster human dataset](https://www.kaggle.com/datasets/rgbnihal/c2a-dataset/versions/2) | Auxiliary study of lying, sitting, bent, and kneeling people in disaster backgrounds | 10,215 largely synthetic UAV-view images and over 360k instances. The viewpoint/domain differs substantially from an indoor ground robot; do not use it as the only validation set, and verify its current license/data-card terms. |
| [Post-Disaster survivor dataset](https://github.com/HaoqianSong/Post-Disaster-Dataset) | Small auxiliary post-disaster test/fine-tuning source | Includes 879 real survivor images with YOLO labels, mainly UAV views. License/provenance limitations require review before incorporation. |

### Dataset discovery sites

- [Roboflow Universe](https://universe.roboflow.com/) - large hub of annotated computer-vision datasets and pretrained models. Quality, class definitions, provenance, and licenses vary per project.
- [Kaggle Datasets](https://www.kaggle.com/datasets) - broad community dataset catalogue. Check the license and source chain on every dataset page.
- [Hugging Face Datasets](https://huggingface.co/datasets?task_categories=computer-vision) - searchable image datasets and programmatic loading. Check each dataset card and license.
- [FiftyOne Dataset Zoo](https://docs.voxel51.com/user_guide/dataset_zoo/index.html) - convenient programmatic access to established datasets, including class-filtered subsets where supported.

Do not merge community datasets merely because they are downloadable. Check duplicate images, incorrect labels, class definitions, source provenance, privacy, redistribution rights, and train/test leakage first.

## Recommended data strategy

1. Start with a compact detector pretrained on COCO and verify person/cat/dog inference on ordinary images.
2. Build a filtered Open Images subset for the selected classes instead of downloading every image.
3. Add CrowdHuman examples for occlusion and unusual partial visibility.
4. Collect a robot-specific dataset because public images do not reproduce this camera height, lens, depth sensor, indoor clutter, low light, or robot motion blur.
5. Begin with roughly 1,000-3,000 carefully labelled robot frames across at least 20 distinct scenes/conditions; increase based on error analysis rather than a fixed target alone.
6. Split by room, recording session, and subject/animal - not by adjacent video frames - to prevent leakage.
7. Keep a separate final test set containing lying/crouching people, partial occlusion, dark clothing, blankets, clutter, backlighting, low light, blur, and negative scenes with no rescue target.
8. Use only safe, approved laboratory conditions. Do not create real fire or hazardous smoke for data collection.

## Evaluation plan

- Detection accuracy: precision, recall, F1, AP50, and mAP50-95 per class.
- Safety emphasis: false negatives and recall for the `person` class, including condition-specific recall.
- Localization: bounding-box quality and RGB-D distance error against measured ground truth.
- Runtime: end-to-end latency, frames per second, GPU/CPU memory, and dropped frames on the Jetson Nano.
- Robustness: normal light, low light, occlusion, unusual pose, motion blur, and concurrent SLAM.
- Generalization: test on rooms, people/animals, and recording sessions excluded from training.
- Comparison: at least one lightweight baseline and one alternative model/configuration, using the same split and metrics.

## Hardware verification checklist before implementation

1. Photograph all labels on the Jetson, lidar, camera, battery, charger, motor controller, motors, and steering servo.
2. Back up the Jetson's storage before changing the operating system or ROS packages.
3. Record Ubuntu, JetPack/L4T, CUDA, cuDNN, TensorRT, Python, OpenCV, ROS distribution, and free storage.
4. Record ROS topics, nodes, transforms, camera calibration, and parameter files; confirm `car_mode`/variant equals `senior_akm`.
5. Verify the RGB, depth, lidar, IMU, odometry, battery, and motor-command streams individually with the wheels safely lifted.
6. Measure the actual wheelbase, track width, wheel diameter, turning radius, camera height/tilt, and lidar height.
7. Change default wireless credentials after the original software has been backed up.
8. Keep the first experiments teleoperated and use an emergency-stop procedure.

## Safety and thesis wording

The official Astra-series operating range is 10-40 degrees C and the official N10 lidar range is -10-40 degrees C. Neither source establishes that this robot is heat-resistant, waterproof, smoke-certified, intrinsically safe, or suitable for an active fire scene. The thesis should explicitly call it a **laboratory search-and-rescue perception prototype** and state that operational deployment would require a certified rugged platform, thermal/other sensing, redundant safety controls, and validation with first responders.
