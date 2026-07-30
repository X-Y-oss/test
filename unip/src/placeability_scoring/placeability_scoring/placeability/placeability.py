import numpy as np
import matplotlib.pyplot as plt
import open3d as o3d

from placeability_scoring.placeability.graspability import compute_graspability
from placeability_scoring.placeability.stability import compute_stability, plot_stability
from placeability_scoring.placeability.probabilistic_stability import compute_stability_probabilistic, plot_probabilistic_stability


def compute_altitude_based_clearance(pointcloud_z, clearance=0.03):
    return (pointcloud_z >= clearance).astype(np.float32)


def sort_grasps_by_score(grasps):
    # Sort rows by column 13 (score) in descending order
    sorted_indices = np.argsort(grasps[:, 13])[::-1]
    sorted_grasps = grasps[sorted_indices]
    return sorted_grasps

def sort_arrays_by_score(grasps, array_list):
    """Sort grasps and array list based on grasp scores (column 13).
       Only keeps grasps with positive scores.

    Args:
        grasps (Nx17 np.array): grasps from GPD
        array_list (list of arrays, each shape N x o): Arrays aligned with grasps

    Returns:
        sorted_grasps
        sorted_array_list
    """
    # Mask for positive scores
    positive_mask = grasps[:, 13] > 0
    #print(np.sum(positive_mask))
    grasps = grasps[positive_mask]

    # Apply same mask to all arrays in array_list
    filtered_array_list = [arr[positive_mask] for arr in array_list]

    # Sort remaining grasps by score
    sorted_indices = np.argsort(grasps[:, 13])[::-1]
    sorted_grasps = grasps[sorted_indices]
    sorted_array_list = [arr[sorted_indices] for arr in filtered_array_list]

    return sorted_grasps, sorted_array_list

def get_stability(pointcloud, weights=None, plotting=False, config=None, use_completion_uncertainty=False, orientation_flag=""): # Updated signature
    if config is None:
        config = {}
    config = dict(config)

    n_rotations = max(1, int(config.get("rotation_averaging_n", 5)))
    max_tilt_deg = float(config.get("rotation_perturbation_deg", 5.0))
    rotation_rng = np.random.default_rng(config.get("rotation_sampling_seed", None))

    def _to_numpy_points(pc):
        if isinstance(pc, o3d.geometry.PointCloud):
            return np.asarray(pc.points)
        return np.asarray(pc)

    def _rotate_numpy_points(points_np, angle_x_deg, angle_y_deg):
        if points_np.shape[0] == 0:
            return points_np.copy()

        center = np.mean(points_np, axis=0, keepdims=True)
        ax = np.deg2rad(angle_x_deg)
        ay = np.deg2rad(angle_y_deg)

        rot_x = np.array([
            [1.0, 0.0, 0.0],
            [0.0, np.cos(ax), -np.sin(ax)],
            [0.0, np.sin(ax), np.cos(ax)],
        ])
        rot_y = np.array([
            [np.cos(ay), 0.0, np.sin(ay)],
            [0.0, 1.0, 0.0],
            [-np.sin(ay), 0.0, np.cos(ay)],
        ])
        rotation = rot_y @ rot_x
        return (points_np - center) @ rotation.T + center

    def _rotate_input(sample_input, angle_x_deg, angle_y_deg):
        if use_completion_uncertainty and isinstance(sample_input, (list, tuple)):
            rotated_collection = []
            for pcd in sample_input:
                pcd_np = _to_numpy_points(pcd)
                rotated_np = _rotate_numpy_points(pcd_np, angle_x_deg, angle_y_deg)
                if isinstance(pcd, o3d.geometry.PointCloud):
                    pcd_rot = o3d.geometry.PointCloud()
                    pcd_rot.points = o3d.utility.Vector3dVector(rotated_np)
                    rotated_collection.append(pcd_rot)
                else:
                    rotated_collection.append(rotated_np)
            return rotated_collection

        return _rotate_numpy_points(_to_numpy_points(sample_input), angle_x_deg, angle_y_deg)

    def _compute_single(sample_input, do_plot=False):
        if config.get('mode') == 'probabilistic_mc':
            single_config = dict(config)
            single_config['return_viz_data'] = bool(do_plot)
            result = compute_stability_probabilistic(sample_input, weights, single_config, use_completion_uncertainty)

            if isinstance(result, tuple):
                score = float(result[0])
                hull = result[1] if len(result) > 1 else None
                viz_data = result[2] if len(result) > 2 else None
            else:
                score = float(result)
                hull = None
                viz_data = None

            if do_plot and viz_data is not None:
                plot_pointcloud = sample_input[0] if use_completion_uncertainty and isinstance(sample_input, (list, tuple)) else sample_input
                if isinstance(plot_pointcloud, o3d.geometry.PointCloud):
                    plot_pointcloud = np.asarray(plot_pointcloud.points)

                fig = plt.figure(figsize=(16, 10))
                ax = fig.add_subplot(111, projection='3d')
                plot_probabilistic_stability(ax, plot_pointcloud, viz_data, orientation_flag)
                plt.show()

            return score, hull
        else:
            n_samples = int(config.get("n_mc_samples", 1000))
            ground_threshold = float(config.get("ground_threshold", 0.02))
            result = compute_stability(sample_input.copy(), n_samples, ground_threshold, compute_edge_evaluation=True)

            if isinstance(result, tuple):
                score = float(result[0])
                viz_data = result[1] if len(result) > 1 else None
            else:
                score = float(result)
                viz_data = None

            if do_plot and viz_data is not None:
                plot_pointcloud = sample_input
                if isinstance(plot_pointcloud, o3d.geometry.PointCloud):
                    plot_pointcloud = np.asarray(plot_pointcloud.points)

                fig = plt.figure(figsize=(16, 10))
                ax = fig.add_subplot(111, projection='3d')
                plot_stability(ax=ax,pointcloud=plot_pointcloud,
                            middle_point=viz_data[0],
                            projected_middle_point=viz_data[1],
                            radius=viz_data[2],
                            support_polygons=viz_data[3],
                            sampled_com=viz_data[4],
                            stability_score=score,
                            orientation_flag=orientation_flag)
                plt.show()

            hull = None
            if isinstance(viz_data, (list, tuple)) and len(viz_data) > 3:
                hull = viz_data[3]
            return score, hull

    angle_pairs = list(zip(
        rotation_rng.uniform(-max_tilt_deg, max_tilt_deg, size=n_rotations),
        rotation_rng.uniform(-max_tilt_deg, max_tilt_deg, size=n_rotations),
    ))

    scores = []
    return_hull = None
    for idx, (angle_x, angle_y) in enumerate(angle_pairs):
        rotated_input = _rotate_input(pointcloud, angle_x, angle_y)
        score, hull = _compute_single(rotated_input, do_plot=(plotting and idx == 0))
        print(
            f"[get_stability] sample {idx + 1}/{len(angle_pairs)} "
            f"(tilt_x={angle_x:.2f} deg, tilt_y={angle_y:.2f} deg): stability={score:.4f}"
        )
        scores.append(score)
        if return_hull is None:
            return_hull = hull

    mean_score = float(np.mean(scores))
    print(f"[get_stability] mean stability over {len(angle_pairs)} samples: {mean_score:.6f}")
    return mean_score, return_hull
    

def compute_placeability(grasps_array, pointcloud, weights=None,
                         orientations=None,
                         plotting=False, clearance=0.03, calculate_stability=True,
                         path="/home/ws",
                         stability_config=None):

    grasp_pointcloud = compute_graspability(grasps=grasps_array, pointcloud=pointcloud) # N_grasp x 17
    # Create a boolean mask where column 13 (score) is NOT zero
    mask_grasp = grasp_pointcloud[:, 13] > 0
    filtered_grasps = grasp_pointcloud[mask_grasp]
    
    # flip pcl here and compute and append I guess?
    convex_hulls = []
    placeability_maps_rotated = []
    center_alignments = []
    
    st_list = []
    for rot in orientations:
        pcd_rot = pointcloud.copy() # overwrite
        pcd_rot = pcd_rot @ rot.as_matrix().T # Flip to wanted orientation
        center = [np.mean(pcd_rot[:,0]), np.mean(pcd_rot[:,1]), np.min(pcd_rot[:,2])]
        center_alignments.append(center)
        pcd_rot[:,:3] -= center # make z positive
        stability, convex_hull = get_stability(pcd_rot, weights=weights, config=stability_config, plotting=plotting)

        st_list.append(stability)
        if(convex_hull == None): continue
        
        convex_hulls.append(convex_hull)
    
        altitude_pointcloud = compute_altitude_based_clearance(pointcloud_z=pcd_rot[:,2], clearance=clearance)
        
        # grasps: Nx17, score is at 13
        place_pointcloud = filtered_grasps.copy()
        place_pointcloud[:, 13] = 1
        
        if(calculate_stability):
            place_pointcloud[:, 13] *= stability

        place_pointcloud[:, 13] *= altitude_pointcloud[mask_grasp]
        
        print("GRASP POINTCLOUD SHAPE: ", filtered_grasps.shape)
        print("PLACE POINTCLOUD SHAPE: ", filtered_grasps.shape)
        placeability_maps_rotated.append(place_pointcloud)
    
    np.save(f"{path}stability_scores", np.array(st_list))

    filtered_grasps_sorted, filtered_place_grasps_sorted_list = sort_arrays_by_score(
        grasps=filtered_grasps,
        array_list=placeability_maps_rotated,
    )
    return filtered_grasps_sorted, np.array(filtered_place_grasps_sorted_list), convex_hulls, center_alignments

   
