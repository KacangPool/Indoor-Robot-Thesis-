# Agreed direction: pretrained detection plus camera-LiDAR labelling

User decision recorded 2026-10-14. This document supersedes alternative-model
comparison/fine-tuning as prerequisites for the current implementation. It does
not claim any new fusion code or hardware test has been completed.

## Selected implementation approach

Keep the existing working general YOLOv3-tiny detector and its pretrained weights.
Do not train from scratch or fine-tune a custom detector dataset in this phase.
Do not install an alternative just to complete a comparison. SSD, newer YOLO and
low-viewpoint research remain references, not required implementation branches.
Changing this direction later requires an explicit justified decision.

Terminology: the model's pretrained weights encode what it learned from training
data (the existing generic configuration uses COCO categories). The live robot
runs inference using those weights; it does not need the original training dataset
to detect objects. Continuing inference does not automatically train the model.

The implementation contribution is connecting detection, supported spatial
measurements and visual labels, then evaluating results and limitations. This is
not a claim of a new detector architecture or a lecturer-approved final thesis
scope; discuss the contribution/required evaluation with the lecturer.

## Intended staged outputs

1. **Camera detections:** use the working YOLO outputs with class, score, image
   rectangle and source-image header. Person is the initial integration target;
   pretrained furniture categories can support association tests. Existing human/
   animal objectives are not silently removed, but supported vocabulary does not
   guarantee reliable recognition of all those targets from this viewpoint.
2. **Camera-LiDAR association:** validate sensor geometry/TF and timing; associate
   only scan measurements defensibly belonging to the detected object. First
   display a labelled observation in a sensor/robot-relative frame while stationary.
   Camera RGB-D remains an available position source or comparison aid after its
   own alignment/accuracy checks; it is not a substitute for demonstrating the
   requested physical camera-LiDAR connection.
3. **Basic labelled map:** use an existing validated occupancy map and trustworthy
   robot pose/TF to place a separate object-label/marker layer. No new SLAM algorithm,
   3D LiDAR mode or autonomous driving is required. Preserve existing map databases.
4. **Evaluation:** record misses/false labels, depth/range validity, false associations,
   timing and label-position error against suitable references. Use existing pilot
   labels where relevant, plus bounded additional test observations. Small evaluation
   data are still needed; a large custom training dataset is not.

## Non-negotiable interpretation boundaries

- The camera supplies semantic labels. The physical planar LiDAR provides geometry;
  it does not independently learn person/chair labels through this connection.
- The approximately 14-16 cm scan plane may hit legs/supports but miss tabletop,
  seat, hand or other parts. A camera box containing projected wall returns does
  not prove those returns belong to the detected object. Unmatched camera detections
  remain visible with unknown/unassociated position rather than forced labels.
- A wrong camera classification can become a wrong spatial label. Filtering,
  synchronization and calibration do not correct the detector's learned mistakes.
- Frame/geometry agreement and user-confirmed clicks are not full calibration.
  Prior RGB/depth metadata discrepancies and measured range accuracy remain open;
  live LiDAR-camera TF and base pose/odometry must also be checked.
- Detection of a visible human/animal is not evidence of physiological life.
  Claims about smoke, fire, field rescue readiness or full-room 3D object shape
  require separate evidence and are not delivered by this plan.
- Current general weights do not add generic hand/box categories merely by editing
  labels. Such extra detection tasks are not implicitly promised under this scope.
- Moving people must not accumulate as permanent static-map obstacles/identities;
  display current/expiring observations separately and retain the measurement time.

## Boundaries and immediate next work

December 2026 remains the user's soft implementation target with four intended
hours/day; no formal completion date or automatic schedule introduced. No work on
the live robot is required while the user is away/exhausted. The next offline work
can specify the shared observation format and the sensor/time/coordinate checks.
The next lab work is bounded read-only validation of the live scan/camera frames,
TF, timing and available robot pose before implementation of valid association.
Existing person-only and manual depth helpers remain reusable diagnostics.

No software install, system upgrade, model/configuration change, training,
sensor launch, robot movement or new benchmark occurred in recording this decision.
