import numpy as np
import torch, pickle

from reachability_maps.configuration_dict import params, robot_params, map_params

from scipy.spatial.transform import Rotation as R


class Reachability_Validation():
    def __init__(self, path_reachability_map="", debug=False, debug_samples=3):
        if(path_reachability_map == ""): print("Please provide a reachability map path")

        self.debug = bool(debug)
        self.debug_samples = int(debug_samples)
        self.dtype = "float32"
        with open(path_reachability_map,'rb') as f:
            reach_map = pickle.load(f)
            self._dprint("length reachability map:  ",len(reach_map))
            self._dprint(map_params["num_voxels"])
            assert len(reach_map) == map_params["num_voxels"], "Reachability map has different amount of voxels than configuration dict"
            self.reach_map = np.array(reach_map, dtype=self.dtype)

        # reachability params
        angular_res = params["angular_res"]
        r_lim, p_lim, yaw_lim = params["r_lim"], params["p_lim"], params["yaw_lim"]
        cartesian_res = params["cartesian_res"]
        x_lim, y_lim, z_lim = params["x_lim"], params["y_lim"], params["z_lim"]
        x_ind_offset, y_ind_offset, z_ind_offset = map_params["x_ind_offset"], map_params["y_ind_offset"], map_params["z_ind_offset"]
        roll_ind_offset, pitch_ind_offset, yaw_ind_offset = map_params["roll_ind_offset"], map_params["pitch_ind_offset"], map_params["yaw_ind_offset"]
        self.lower_lim = np.array([x_lim[0], y_lim[0], z_lim[0], r_lim[0], p_lim[0], yaw_lim[0]], dtype=self.dtype)
        self.resolution = np.array([cartesian_res]*3 + [angular_res]*3, dtype=self.dtype)
        self.bin_counts = np.array(
            [
                robot_params["x_bins"],
                robot_params["y_bins"],
                robot_params["z_bins"],
                robot_params["roll_bins"],
                robot_params["pitch_bins"],
                robot_params["yaw_bins"],
            ],
            dtype=int,
        )
        self.upper_lim = self.lower_lim + self.resolution * (self.bin_counts - 1)
        self.axis_names = ("x", "y", "z", "roll", "pitch", "yaw")
        self._dprint("Resolution reachability map: ",self.resolution)
        self._dprint("[reach-init] lower_lim:", self.lower_lim)
        self._dprint("[reach-init] upper_lim:", self.upper_lim)
        self.offsets = np.array([x_ind_offset, y_ind_offset, z_ind_offset, roll_ind_offset, pitch_ind_offset, yaw_ind_offset], dtype=int)
        self._dprint("[reach-init] offsets:", self.offsets)

    def _dprint(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def calculate_reachability(self, points):
        """
        for now assuming pose is 0x0 and points are in world coordinates
        params:
            points nx6d numpy array
        return:
            scores nx2d numpy array
        """
        points = np.asarray(points, dtype=self.dtype)
        if points.ndim != 2 or points.shape[1] != 6:
            raise ValueError(f"Expected points shape (N,6), got {points.shape}")

        self._dprint("[reach] input shape:", points.shape)
        self._dprint("[reach] xyz min/max:", points[:, :3].min(axis=0), points[:, :3].max(axis=0))
        self._dprint("[reach] rpy min/max:", points[:, 3:].min(axis=0), points[:, 3:].max(axis=0))
        if np.nanmax(np.abs(points[:, 3:])) > (2.0 * np.pi + 1e-3):
            self._dprint("[reach][warn] RPY values look like degrees while map limits are in radians.")

        points_shifted = points - self.lower_lim
        points_indexed_raw = np.floor(points_shifted / self.resolution)
        points_indexed = points_indexed_raw.copy()
        
        if self.debug:
            max_index_per_axis = self.bin_counts - 1
            oob_low = points_indexed_raw < 0
            oob_high = points_indexed_raw > max_index_per_axis
            oob_any = oob_low | oob_high

            if np.any(oob_any):
                self._dprint("[Warning] Some poses were outside grid limits and clipped.")
                self._dprint(
                    f"[reach] clipped rows pre-clip: {int(np.count_nonzero(np.any(oob_any, axis=1)))}/{points.shape[0]}"
                )
                for ax_i, ax_name in enumerate(self.axis_names):
                    low_count = int(np.count_nonzero(oob_low[:, ax_i]))
                    high_count = int(np.count_nonzero(oob_high[:, ax_i]))
                    if low_count == 0 and high_count == 0:
                        continue
                    self._dprint(
                        f"[reach][clip] {ax_name}: low={low_count}, high={high_count}, "
                        f"idx_range=[{float(np.min(points_indexed_raw[:, ax_i])):.2f}, {float(np.max(points_indexed_raw[:, ax_i])):.2f}], "
                        f"value_range=[{float(np.min(points[:, ax_i])):.4f}, {float(np.max(points[:, ax_i])):.4f}], "
                        f"allowed=[{float(self.lower_lim[ax_i]):.4f}, {float(self.upper_lim[ax_i]):.4f}]"
                    )
                bad_rows = np.where(np.any(oob_any, axis=1))[0]
                n_show_bad = min(self.debug_samples, bad_rows.shape[0])
                if n_show_bad > 0:
                    self._dprint("[reach][clip] sample offending rows [xyzrpy] and raw_idx")
                    for ridx in bad_rows[:n_show_bad]:
                        self._dprint(
                            f"  row={int(ridx)}",
                            points[ridx],
                            "raw_idx=",
                            points_indexed_raw[ridx],
                        )

        
        points_indexed[:, 0] = np.clip(points_indexed[:, 0], 0, robot_params["x_bins"] - 1)
        points_indexed[:, 1] = np.clip(points_indexed[:, 1], 0, robot_params["y_bins"] - 1)
        points_indexed[:, 2] = np.clip(points_indexed[:, 2], 0, robot_params["z_bins"] - 1)
        points_indexed[:, 3] = np.clip(points_indexed[:, 3], 0, robot_params["roll_bins"] - 1)
        points_indexed[:, 4] = np.clip(points_indexed[:, 4], 0, robot_params["pitch_bins"] - 1)
        points_indexed[:, 5] = np.clip(points_indexed[:, 5], 0, robot_params["yaw_bins"] - 1)

        if self.debug:
            clipped_rows = np.any(points_indexed_raw != points_indexed, axis=1)
            if np.any(clipped_rows):
                self._dprint(
                    f"[reach] clipped rows: {int(np.count_nonzero(clipped_rows))}/{points.shape[0]}"
                )

        indices_6d = points_indexed[:,5]*self.offsets[5] + points_indexed[:,4]*self.offsets[4] + points_indexed[:,3]*self.offsets[3] + \
                        points_indexed[:,2]*self.offsets[2] + points_indexed[:,1]*self.offsets[1] + points_indexed[:,0]*self.offsets[0]
                        
        scores = self.reach_map[indices_6d.astype(np.int64)]

        if self.debug:
            self._dprint(
                "[reach] score stats (col1 min/max/mean):",
                float(np.min(scores[:, 1])),
                float(np.max(scores[:, 1])),
                float(np.mean(scores[:, 1])),
            )
            self._dprint(
                f"[reach] reachable (score>1e-5): {int(np.count_nonzero(scores[:, 1] > 1e-5))}/{scores.shape[0]}"
            )
            n_show = min(self.debug_samples, points.shape[0])
            if n_show > 0:
                self._dprint("[reach] sample rows [xyzrpy] -> idx -> score1")
                for i in range(n_show):
                    self._dprint(
                        points[i],
                        "->",
                        int(indices_6d[i]),
                        "->",
                        float(scores[i, 1]),
                    )

        return scores
    

if __name__ == "__main__":
    reacher = Reachability_Validation(path_reachability_map=f"/home/ws/src/maps/reach_map_gripper_virtual_link_0.1_2025-06-21-19-05-44.pkl")
    points = np.array( [[-8.65410015e-01 , 4.34263189e-01 ,-2.11957235e-02 ,-1.41652312e+02,
                            6.07967888e+01 , 5.09375331e+01],
                            [-9.65350105e-01 , 5.34323063e-01 ,-2.11957235e-02, -1.41652312e+02,
                            6.07967888e+01 , 5.09375331e+01]])
    
    xy = reacher.calculate_reachability(points=points)
    
    mask = np.nonzero(reacher.reach_map)
    print(reacher.reach_map[mask].shape)
    print(reacher.reach_map.shape)
    
