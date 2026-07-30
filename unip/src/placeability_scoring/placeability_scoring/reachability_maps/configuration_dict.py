import numpy as np
import torch
import math


import numpy as np
import torch
import math

params = {
    "device": "cpu", #if torch.cuda.is_available() else "cpu",
    "dtype": torch.float32,
    "robot_urdf_name": "steve_static.urdf", #"steve.urdf",
    "name_base_link": "ur5e_base_link",
    "name_end_effector": "gripper_virtual_link", #"hand_base",
    "n_dof": 6, # Implied from the URDF and chosen links
    "N_fk": 25600000000, #1280000000, #320000000 # 25600000000 # Number of Forward Kinematic solutions to sample, Sampling 20^8 joint configurations. NOTE: Tweak this paramter based on GPU Memory available
    # Rotation
    "angular_res": np.pi/8, # or 22.5 degrees per bin)
    "r_lim": [-np.pi, np.pi], # NOTE: Using 'intrinsic' euler rotations in XYZ
    "p_lim": [-np.pi/2, np.pi/2], # Gimbal lock?
    "yaw_lim": [-np.pi, np.pi],
    # Voxels
    "cartesian_res": 0.025, # maybe 0.025 metres
    "x_lim": [-1.15, 1.15], # min,max in metres (Set these as per your robot links)
    "y_lim": [-1.15, 1.15],
    "z_lim": [-1.0, 1.30],
    # IK 
    "success_mask_type": "abs" # "squared_error"
}

robot_params = {
    "joint_pos_min": torch.full((params["n_dof"],), -math.pi, dtype=params["dtype"], device=params["device"]),
    "joint_pos_max": torch.full((params["n_dof"],), math.pi, dtype=params["dtype"], device=params["device"]),
    # Rotation
    "roll_bins": math.ceil((2*np.pi)/params["angular_res"]), # 16
    "pitch_bins": math.ceil((np.pi)/params["angular_res"]),  # 8. Only half the bins needed (half elevation and full azimuth sufficient to cover sphere)
    "yaw_bins": math.ceil((2*np.pi)/params["angular_res"]),  # 16
    # Voxels
    "x_bins": math.ceil((params["x_lim"][1] - params["x_lim"][0])/params["cartesian_res"]),
    "y_bins": math.ceil((params["y_lim"][1] - params["y_lim"][0])/params["cartesian_res"]),
    "z_bins": math.ceil((params["z_lim"][1] - params["z_lim"][0])/params["cartesian_res"]),
}

map_params = {
    "num_voxels": robot_params["x_bins"]*robot_params["y_bins"]*robot_params["z_bins"]*robot_params["roll_bins"]*robot_params["pitch_bins"]*robot_params["yaw_bins"],
    "num_values": 2, # 'Visitation Frequency' and 'Manipulability' - could cut first technically
    "x_ind_offset": robot_params["y_bins"]*robot_params["z_bins"]*robot_params["roll_bins"]*robot_params["pitch_bins"]*robot_params["yaw_bins"],
    "y_ind_offset": robot_params["z_bins"]*robot_params["roll_bins"]*robot_params["pitch_bins"]*robot_params["yaw_bins"],
    "z_ind_offset": robot_params["roll_bins"]*robot_params["pitch_bins"]*robot_params["yaw_bins"],
    "roll_ind_offset": robot_params["pitch_bins"]*robot_params["yaw_bins"],
    "pitch_ind_offset": robot_params["yaw_bins"],
    "yaw_ind_offset": 1,
}