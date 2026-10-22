# YOLO basics and model direction

Discussion recorded: 2026-10-09. No detector, training, robot settings or annotation labels changed. Final model selection remains open.

## What YOLO is

YOLO (You Only Look Once) is a family of deep-learning object detectors. Deep learning is a form of machine learning. A neural network processes an image and predicts object categories, bounding rectangles and scores. Detection means locating objects as well as classifying them. A score is a model output, not a validated probability that a prediction is correct. A person prediction does not establish whether someone is alive, injured or conscious.

During **training**, annotated example images are used to adjust the network's learned numerical parameters, called weights. During **inference**, a trained model applies those weights to new images. Our current live camera demonstration is inference: watching more camera frames or saving recordings does not automatically teach it anything.

The original [YOLO paper, CVPR 2016](https://arxiv.org/abs/1506.02640) explains the single-network detection approach. Think of its stages as image preparation, learned feature extraction, candidate boxes/classes, and output processing; exact details differ by version.

## What is currently on this robot

The selected baseline configuration is generic YOLOv3-tiny through `darknet_ros`, with 80 categories and a configured score cutoff of 0.3. Uploaded reports confirm the selected YAML and working detections; this discussion does not newly verify the binary's internal model identity or GPU execution.

There are four separate things:

- Architecture: the network design, such as YOLOv3-tiny.
- Weights: what a particular trained network has learned.
- Class vocabulary and dataset: which categories the training examples identify.
- ROS integration: camera subscription and publishing detections for other programs.

The copied YAML selects `yolov3-tiny.cfg` and `yolov3-tiny.weights`. The copied CFG has two detection heads with `classes=80`, and their preceding convolutions have `filters=255`. The wrapper derives its class count and names from the YAML. These must agree. Do not delete or reorder names in the existing YAML while continuing to use the same 80-class configuration and weights.

Source paths: `From Robotics Lab/wheeltec_dev/wheeltec_robot_src/darknet_ros/darknet_ros/config/yolov3-tiny.yaml`, `yolo_network_config/cfg/yolov3-tiny.cfg`, and `src/YoloObjectDetector.cpp` under the same package.

## Unwanted categories and possible modifications

Outdoor categories mainly reflect the broad pretrained dataset. They do not force the application to use those categories. An application can retain only selected results, initially person and chair for the evaluation pilot. Cat/dog and other thesis categories remain separate requirements; hand is not in the current generic class list.

Filtering means preserving the original detector and label map, then ignoring unwanted outputs downstream. It does not retrain the network or substantially remove its main computation. A chair predicted as traffic light would disappear after filtering, not become a correct chair detection. A chair predicted as person would remain a false person.

Three different changes are possible:

| Change | What changes | Requires training? |
| --- | --- | --- |
| Output processing | Class filtering, score cutoff, temporal stability, duplicate handling | No |
| Fine-tuning/custom training | Learned weights adapted to robot scenes and/or chosen categories | Yes |
| Architecture research | Network structure or a new detection method | Usually yes, plus more implementation and evaluation |

The copied detector already calls non-maximum suppression, a standard duplicate-removal step. Observed duplicates do not prove this step is absent. Additional suppression must be evaluated because it can also remove adjacent real objects. Tracking/persistence can reduce flicker, but can keep a wrong label stable too.

## Adding a category such as hand

1. Define the required categories and annotation rules: for example what counts as a visible hand and how partial occlusion is marked.
2. Collect representative labelled examples, including robot-height views, clutter and scenes without the target. Include all categories that the custom model should retain.
3. Separate training, validation and final test data by capture session, and preferably room/person where feasible. Do not spread adjacent near-identical frames across splits.
4. Configure an appropriate detector output for the chosen class set and initialize training from compatible pretrained features/weights. Fine-tune rather than assume training from scratch is necessary.
5. Train on suitable off-robot hardware, validate, export for a supported robot runtime, and test accuracy, memory and latency on the actual platform.

Adding a word to a label file does not teach the model that category. Changing the category count changes the network output requirements and requires compatible trained weights. [Darknet's custom-object training guide](https://github.com/AlexeyAB/darknet#how-to-train-to-detect-your-custom-objects) documents the corresponding labels/configuration workflow. It is a reference for that implementation, not a verified installation recipe for this old robot or an instruction to run training now.

## Improving performance for this thesis

The most relevant examples are people seen from approximately 12-13 cm camera height, including seated, lying and partly hidden people; different subjects and clothing; backlighting and dim scenes; and negative scenes containing chairs or other misleading shapes. Household-animal examples are needed if that remains in the final target scope. Ordinary object detection alone cannot validate rescue performance in smoke or darkness; these require defined conditions and separate evidence.

Useful options are domain-specific fine-tuning, a different compact detector, camera mounting/lighting improvements, and measured output-processing adjustments. Larger models or image inputs may improve detail but cost time and memory; improvements are not guaranteed. Raising the cutoff can reduce false alarms while increasing missed people, as the pilot already suggests.

The 31-image reviewer is a small development reference, not enough to claim final performance or guarantee sufficient training diversity. Its labels can compare detectors as well as YOLO: human reference boxes are independent of which detector makes predictions. A final untouched test set should be collected separately, not repeatedly used to select settings.

## Proposed sequence, not a finalized model commitment

1. Understand detection, training/inference, boxes, scores, precision (how many predictions are correct) and recall (how many actual targets are found).
2. Review the small pilot and measure the unchanged baseline, including false people and occlusion misses.
3. Compare one practical alternative on the same images. SSD-MobileNet-v2 via jetson-inference is a compatibility-oriented candidate; a compact newer YOLO may also be considered after runtime checks. No alternative is installed or selected by this discussion.
4. Choose using target recall, false alarms, timing, memory and integration effort, then fine-tune if the data and measured failures justify it.
5. Integrate detection with validated RGB/depth association and robot pose before attaching semantic labels to the LiDAR/map. Recognition alone does not provide trustworthy map coordinates.

[jetson-inference](https://github.com/dusty-nv/jetson-inference) documents SSD-MobileNet models and original Jetson Nano/JetPack 4 support. This makes it worth investigating, not proof of compatibility with the installed libraries. The robot report confirms L4T R32.5.2 and Python 2.7/3.6; exact CUDA/TensorRT versions still need checking. Modern Windows Python/PyTorch instructions must not be applied blindly to this robot.

## Beginner reading order and version differences

1. [You Only Look Once: Unified, Real-Time Object Detection — CVPR 2016](https://arxiv.org/abs/1506.02640): start with the abstract, pipeline figure and introduction. Ask what the input/output is, what training teaches, and where the authors report failures.
2. [YOLOv3: An Incremental Improvement — 2018 technical report](https://arxiv.org/abs/1804.02767): closest family to the current baseline. Full YOLOv3 improves feature extraction and predicts at multiple scales. The tiny variant is a separate compact configuration, not the full network described in every paper detail.
3. Optional history: [YOLO9000: Better, Faster, Stronger — CVPR 2017, preprint 2016](https://arxiv.org/abs/1612.08242): explains the YOLOv2/YOLO9000 developments. YOLO9000's large-vocabulary joint-training result is not evidence that the current 80-class model recognizes those categories.
4. Then return to `Reference Library/LITERATURE_READING_LIST.md` for robotics/search-and-rescue and low-viewpoint work. Compare conditions and hardware, not only headline accuracy.

The author's [YOLO implementation page](https://pjreddie.com/darknet/yolo/) describes tiny as a compact model for constrained environments. Later numbered YOLO releases involve different designs and software ecosystems; a larger number is not a guarantee of the best deployable result on an old Jetson. Replacing a Darknet weights file with an unrelated modern model file is not a general upgrade method.

For each paper, record task/classes, dataset and viewpoint, model size, input resolution, accuracy metric, timing hardware, failure cases, and relevance to this robot. Published desktop-GPU FPS is not the robot's FPS. It is reasonable to read for concepts first and revisit equations after understanding the pipeline.

## Verification and remaining questions

Documentation-only discussion. Primary papers/implementation documentation checked on 2026-10-09; copied YAML/CFG/wrapper checked for class-count coupling and existing NMS. No training, new benchmark, robot connection, model selection or annotation confirmation occurred. Remaining decisions: final categories, available training hardware, independently labelled evaluation data, compatible alternative runtime, and RGB/depth registration.
