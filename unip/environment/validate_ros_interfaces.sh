#!/usr/bin/env bash
set -Eeuo pipefail

# -----------------------------------------------------------------------------
# UniP ROS / Isaac interface validator
#
# Purpose:
#   Validate the runtime ROS interface contract after Isaac Sim is running.
#
# Checks
# ------
# R1  ROS graph visibility
# R2  Camera topics / types
# R3  TF availability
# R4  Joint-state availability
# R5  Latest Nils UR5e command interface:
#       /joint_command
#       sensor_msgs/msg/JointState
#
# This script is read-only by default. It does NOT move the robot.
#
# Optional:
#   --command-probe
#       Publish a single known-safe joint command to /joint_command.
#       Use only when the latest Nils UR5e Isaac scene is running and the user
#       explicitly wants to test actuation.
#
# Environment overrides:
#   COLOR_TOPIC
#   DEPTH_TOPIC
#   COLOR_INFO_TOPIC
#   DEPTH_INFO_TOPIC
#   JOINT_STATE_TOPIC
#   JOINT_COMMAND_TOPIC
#   BASE_FRAME
#   CAMERA_FRAME
# -----------------------------------------------------------------------------

SCRIPT_NAME="$(basename "$0")"

COLOR_TOPIC="${COLOR_TOPIC:-/camera/color/image_raw}"
DEPTH_TOPIC="${DEPTH_TOPIC:-/camera/depth/image_raw}"
COLOR_INFO_TOPIC="${COLOR_INFO_TOPIC:-/camera/color/camera_info}"
DEPTH_INFO_TOPIC="${DEPTH_INFO_TOPIC:-/camera/depth/camera_info}"

JOINT_STATE_TOPIC="${JOINT_STATE_TOPIC:-/joint_states}"
JOINT_COMMAND_TOPIC="${JOINT_COMMAND_TOPIC:-/joint_command}"

BASE_FRAME="${BASE_FRAME:-ur5e_base_link}"
CAMERA_FRAME="${CAMERA_FRAME:-camera_link}"

RUN_COMMAND_PROBE=0
FAIL_COUNT=0
WARN_COUNT=0

pass() {
    printf '  [PASS] %s\n' "$*"
}

warn() {
    WARN_COUNT=$((WARN_COUNT + 1))
    printf '  [WARN] %s\n' "$*" >&2
}

fail() {
    FAIL_COUNT=$((FAIL_COUNT + 1))
    printf '  [FAIL] %s\n' "$*" >&2
}

section() {
    printf '\n============================================================\n'
    printf '%s\n' "$1"
    printf '============================================================\n'
}

usage() {
    cat <<EOF
Usage:
  $SCRIPT_NAME [--command-probe]

Options:
  --command-probe   Publish one known UR5e JointState command to /joint_command.
                    This can move the simulated robot.
  -h, --help        Show this help.
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --command-probe)
                RUN_COMMAND_PROBE=1
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                printf '[%s] ERROR: unknown argument: %s\n' "$SCRIPT_NAME" "$1" >&2
                usage >&2
                exit 2
                ;;
        esac
        shift
    done
}

require_ros2() {
    section "R1 — ROS Graph"

    if ! command -v ros2 >/dev/null 2>&1; then
        fail "ros2 CLI is not available."
        return 1
    fi

    pass "ros2 CLI is available."

    local topics nodes
    topics="$(ros2 topic list 2>/dev/null || true)"
    nodes="$(ros2 node list 2>/dev/null || true)"

    if [[ -n "$topics" ]]; then
        pass "ROS topics are visible."
        printf '%s\n' "$topics" | sed 's/^/         /'
    else
        fail "No ROS topics are visible."
    fi

    if [[ -n "$nodes" ]]; then
        pass "ROS nodes are visible."
        printf '%s\n' "$nodes" | sed 's/^/         /'
    else
        warn "No ROS nodes are visible."
    fi
}

topic_exists() {
    local topic="$1"
    ros2 topic list 2>/dev/null | grep -Fxq "$topic"
}

topic_type() {
    local topic="$1"
    ros2 topic type "$topic" 2>/dev/null || true
}

check_topic() {
    local topic="$1"
    local expected_type="$2"
    local label="$3"
    local required="$4"

    if ! topic_exists "$topic"; then
        if [[ "$required" == "required" ]]; then
            fail "$label topic missing: $topic"
        else
            warn "$label topic missing: $topic"
        fi
        return
    fi

    pass "$label topic exists: $topic"

    local actual_type
    actual_type="$(topic_type "$topic")"

    if [[ -z "$actual_type" ]]; then
        warn "Could not determine type for $topic"
        return
    fi

    printf '         type: %s\n' "$actual_type"

    if [[ -n "$expected_type" && "$actual_type" != "$expected_type" ]]; then
        warn "$label type differs from expected '$expected_type'."
    else
        pass "$label message type is compatible."
    fi
}

check_camera_topics() {
    section "R2 — Camera Interfaces"

    printf '  Color topic      : %s\n' "$COLOR_TOPIC"
    printf '  Depth topic      : %s\n' "$DEPTH_TOPIC"
    printf '  Color info       : %s\n' "$COLOR_INFO_TOPIC"
    printf '  Depth info       : %s\n' "$DEPTH_INFO_TOPIC"

    # Current exact topic names are integration contracts and may differ between
    # Isaac scenes. Missing defaults are warnings rather than architecture fails.
    check_topic "$COLOR_TOPIC" "sensor_msgs/msg/Image" "Color image" "optional"
    check_topic "$DEPTH_TOPIC" "sensor_msgs/msg/Image" "Depth image" "optional"
    check_topic "$COLOR_INFO_TOPIC" "sensor_msgs/msg/CameraInfo" "Color CameraInfo" "optional"
    check_topic "$DEPTH_INFO_TOPIC" "sensor_msgs/msg/CameraInfo" "Depth CameraInfo" "optional"
}

check_tf() {
    section "R3 — TF"

    local tf_exists=0

    if topic_exists "/tf"; then
        pass "/tf topic exists."
        tf_exists=1
    else
        warn "/tf topic is missing."
    fi

    if topic_exists "/tf_static"; then
        pass "/tf_static topic exists."
        tf_exists=1
    else
        warn "/tf_static topic is missing."
    fi

    printf '  Requested transform : %s -> %s\n' "$BASE_FRAME" "$CAMERA_FRAME"

    if ! command -v timeout >/dev/null 2>&1; then
        warn "timeout command unavailable; transform lookup skipped."
        return
    fi

    if ! ros2 run tf2_ros tf2_echo --help >/dev/null 2>&1; then
        warn "tf2_echo executable unavailable; transform lookup skipped."
        return
    fi

    if [[ "$tf_exists" -eq 0 ]]; then
        warn "TF topics unavailable; transform lookup skipped."
        return
    fi

    local tmp
    tmp="$(mktemp -t unip_tf_probe.XXXXXX.log)"

    set +e
    timeout 4s ros2 run tf2_ros tf2_echo "$BASE_FRAME" "$CAMERA_FRAME" \
        >"$tmp" 2>&1
    local rc=$?
    set -e

    if grep -Eq 'Translation:|At time' "$tmp"; then
        pass "Transform is available: $BASE_FRAME -> $CAMERA_FRAME"
    else
        warn "Requested transform was not observed."
        tail -n 10 "$tmp" | sed 's/^/         /'
    fi

    rm -f "$tmp"
}

check_robot_state() {
    section "R4 — Robot State"

    check_topic "$JOINT_STATE_TOPIC" "sensor_msgs/msg/JointState" "Joint state" "optional"

    if topic_exists "$JOINT_STATE_TOPIC"; then
        if command -v timeout >/dev/null 2>&1; then
            local tmp
            tmp="$(mktemp -t unip_joint_state.XXXXXX.log)"

            set +e
            timeout 4s ros2 topic echo --once "$JOINT_STATE_TOPIC" \
                >"$tmp" 2>&1
            local rc=$?
            set -e

            if [[ "$rc" -eq 0 && -s "$tmp" ]]; then
                pass "Received one JointState message."
                head -n 20 "$tmp" | sed 's/^/         /'
            else
                warn "Joint-state topic exists but no message was received in the probe window."
            fi

            rm -f "$tmp"
        fi
    fi
}

check_joint_command_contract() {
    section "R5 — Latest Nils UR5e Joint Command Contract"

    printf '  Expected topic : %s\n' "$JOINT_COMMAND_TOPIC"
    printf '  Expected type  : sensor_msgs/msg/JointState\n'

    if ! topic_exists "$JOINT_COMMAND_TOPIC"; then
        warn "Latest UR5e command topic is not visible: $JOINT_COMMAND_TOPIC"
        return
    fi

    pass "Joint command topic exists."

    local actual_type
    actual_type="$(topic_type "$JOINT_COMMAND_TOPIC")"
    printf '  Actual type    : %s\n' "${actual_type:-<unknown>}"

    if [[ "$actual_type" == "sensor_msgs/msg/JointState" ]]; then
        pass "Joint command topic matches Nils' latest interface contract."
    else
        fail "Joint command topic type does not match sensor_msgs/msg/JointState."
    fi
}

run_command_probe() {
    section "R6 — Optional Actuation Probe"

    if [[ "$RUN_COMMAND_PROBE" -ne 1 ]]; then
        printf '  [SKIP] Actuation probe not requested.\n'
        printf '         Use --command-probe only with the latest UR5e Isaac scene.\n'
        return
    fi

    if ! topic_exists "$JOINT_COMMAND_TOPIC"; then
        fail "Cannot run command probe because $JOINT_COMMAND_TOPIC is missing."
        return
    fi

    local actual_type
    actual_type="$(topic_type "$JOINT_COMMAND_TOPIC")"

    if [[ "$actual_type" != "sensor_msgs/msg/JointState" ]]; then
        fail "Cannot run command probe: unexpected topic type '$actual_type'."
        return
    fi

    warn "Publishing one JointState command. The simulated robot may move."

    set +e
    ros2 topic pub --once "$JOINT_COMMAND_TOPIC" sensor_msgs/msg/JointState \
        "{name: ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint', 'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint'], position: [0.0, -1.57, 1.57, 0.0, 1.57, 0.0]}"
    local rc=$?
    set -e

    if [[ "$rc" -eq 0 ]]; then
        pass "Joint command message published successfully."
        warn "This only validates publication, not physical/simulated motion."
    else
        fail "Failed to publish joint command."
    fi
}

print_summary() {
    section "ROS / Isaac Interface Validation Summary"

    printf '  Failures : %s\n' "$FAIL_COUNT"
    printf '  Warnings : %s\n' "$WARN_COUNT"

    if [[ "$FAIL_COUNT" -gt 0 ]]; then
        printf '\nRESULT: FAIL [INTEGRATION]\n'
        return 1
    fi

    if [[ "$WARN_COUNT" -gt 0 ]]; then
        printf '\nRESULT: PASS WITH WARNINGS\n'
        return 0
    fi

    printf '\nRESULT: PASS\n'
    return 0
}

main() {
    parse_args "$@"

    printf '========================================================================\n'
    printf 'UniP ROS / Isaac Runtime Interface Validation\n'
    printf '========================================================================\n'

    require_ros2 || {
        print_summary
        return 1
    }

    check_camera_topics
    check_tf
    check_robot_state
    check_joint_command_contract
    run_command_probe
    print_summary
}

main "$@"
