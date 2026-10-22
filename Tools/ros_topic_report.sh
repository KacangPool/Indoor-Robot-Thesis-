#!/usr/bin/env bash

# Read-only ROS 1 inventory, definitions and bounded actual-value samples.

set -u
set -o pipefail

TASK_REPORT_DIR="${1:-${HOME}/fahad/reports}"
TASK_SAMPLE_TIMEOUT="${ROS_TOPIC_SAMPLE_TIMEOUT:-25s}"
TASK_QUERY_TIMEOUT="${ROS_TOPIC_QUERY_TIMEOUT:-15s}"
TASK_MODE="${ROS_TOPIC_REPORT_MODE:-core}"
TASK_PYTHON="${ROS_REPORT_PYTHON:-python}"
TASK_SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v rostopic >/dev/null 2>&1; then
  echo "rostopic was not found. Source the robot workspace first."
  exit 1
fi

if ! command -v timeout >/dev/null 2>&1; then
  echo "The GNU timeout command is required but was not found."
  exit 1
fi

for TASK_TOOL in rosmsg "${TASK_PYTHON}"; do
  if ! command -v "${TASK_TOOL}" >/dev/null 2>&1; then
    echo "Missing command: ${TASK_TOOL}. Source the robot workspace first."
    exit 1
  fi
done
if [ ! -f "${TASK_SCRIPT_DIR}/ros_message_sample.py" ]; then
  echo "Copy ros_message_sample.py beside this script before running it."
  exit 1
fi
case "${TASK_MODE}" in core|all) ;; *) echo "ROS_TOPIC_REPORT_MODE must be core or all"; exit 1 ;; esac

task_bounded() {
  timeout --signal=TERM --kill-after=2s "${TASK_QUERY_TIMEOUT}" "$@"
}
task_status() {
  case "$1" in
    0) ;;
    124|137) echo "[Command deadline reached; partial output may exist. Not proof of no data.]" ;;
    *) echo "[Command failed with status $1; see output above.]" ;;
  esac
}

if ! TASK_TOPICS="$(task_bounded rostopic list 2>&1)"; then
  echo "Could not read the ROS topic list:"
  echo "${TASK_TOPICS}"
  exit 1
fi

mkdir -p -- "${TASK_REPORT_DIR}" || exit 1
TASK_STAMP="$(date +%Y%m%d_%H%M%S)"
TASK_REPORT_FILE="$(mktemp "${TASK_REPORT_DIR}/ros_topic_report_${TASK_STAMP}_XXXXXX.txt")" || exit 1
TASK_TOPIC_COUNT="$(printf '%s\n' "${TASK_TOPICS}" | sed '/^[[:space:]]*$/d' | wc -l)"

# Prioritize useful interfaces over alphabetically earlier transport settings.
TASK_CORE=(/camera/rgb/image_raw /camera/rgb/camera_info
  /camera/depth/image /camera/depth/image_raw
  /camera/depth_registered/image_raw /camera/depth_registered/camera_info
  /camera/depth/points /camera/depth_registered/points /scan
  /odom /imu /PowerVoltage /joint_states /tf /tf_static
  /map /map_metadata /rtabmap/grid_map /rtabmap/info
  /rtabmap/cloud_map /cmd_vel /move_base_simple/goal)
TASK_SELECTED=()
declare -A TASK_SEEN=()
for TASK_TOPIC in "${TASK_CORE[@]}"; do
  if grep -Fxq -- "${TASK_TOPIC}" <<< "${TASK_TOPICS}"; then
    TASK_SELECTED+=("${TASK_TOPIC}")
    TASK_SEEN["${TASK_TOPIC}"]=1
  fi
done
if [ "${TASK_MODE}" = all ]; then
  while IFS= read -r TASK_TOPIC; do
    if [ -n "${TASK_TOPIC}" ] && [ -z "${TASK_SEEN[${TASK_TOPIC}]:-}" ]; then
      TASK_SELECTED+=("${TASK_TOPIC}")
    fi
  done <<< "${TASK_TOPICS}"
fi

{
  echo "ROS programming reference report v2"
  echo "Generated: $(date --iso-8601=seconds)"
  echo "Host: $(hostname)"
  echo "ROS distribution: ${ROS_DISTRO:-unknown}"
  echo "ROS master: ${ROS_MASTER_URI:-unknown}"
  echo "Topic count: ${TASK_TOPIC_COUNT}"
  echo "Mode: ${TASK_MODE}; selected topics: ${#TASK_SELECTED[@]}"
  echo "Query deadline: ${TASK_QUERY_TIMEOUT}; sample deadline: ${TASK_SAMPLE_TIMEOUT}; kill grace: 2s"
  echo "Samples are sequential, truncated, NOT synchronized recordings or rate measurements."
  echo "ALL TOPIC NAMES (including those not sampled in core mode)"
  printf '%s\n' "${TASK_TOPICS}"
  echo
  echo "Complete topic inventory"
  task_bounded rostopic list -v 2>&1
  task_status "$?"

  TASK_INDEX=0
  for TASK_TOPIC in "${TASK_SELECTED[@]}"; do
    TASK_INDEX=$((TASK_INDEX + 1))
    echo
    echo "================================================================"
    echo "TOPIC ${TASK_INDEX}/${#TASK_SELECTED[@]}: ${TASK_TOPIC}"
    echo "STEP: resolve message type"
    TASK_TYPE="$(task_bounded rostopic type "${TASK_TOPIC}" 2>&1)"
    TASK_TYPE_STATUS=$?
    echo "TYPE: ${TASK_TYPE}"
    if [ "${TASK_TYPE_STATUS}" -ne 0 ]; then
      task_status "${TASK_TYPE_STATUS}"
      continue
    fi
    echo
    echo "STEP: connections"
    task_bounded rostopic info "${TASK_TOPIC}" 2>&1
    task_status "$?"
    echo "STEP: message definition (structure, NOT measured values)"
    task_bounded rosmsg show "${TASK_TYPE}" 2>&1
    task_status "$?"
    echo
    echo "STEP: one received message (actual values; arrays previewed)"

    timeout --signal=TERM --kill-after=2s "${TASK_SAMPLE_TIMEOUT}" \
      "${TASK_PYTHON}" -u "${TASK_SCRIPT_DIR}/ros_message_sample.py" "${TASK_TOPIC}" "${TASK_TYPE}" 2>&1
    task_status "$?"
  done
  echo "REPORT COMPLETE: ${TASK_REPORT_FILE}"
} | tee "${TASK_REPORT_FILE}"
