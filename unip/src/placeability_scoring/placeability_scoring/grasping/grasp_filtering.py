import numpy as np
import open3d as o3d
import copy


def filter_grasps_by_obb_alignment(grasp_transforms, T_obb_to_world, should_plot=False, obb_proxy=None, obj_points_pcd_world=None):
    """
    Filter grasps based on alignment with the object's Oriented Bounding Box (OBB).
    
    Args:
        grasp_transforms (np.ndarray): Grasp transforms of shape (N, 4, 4)
        T_obb_to_world (np.ndarray): Transform from OBB to world frame (4, 4)
        should_plot (bool, optional): Whether to visualize the OBB alignment filter. Default: False
        obb_proxy (object, optional): OBB proxy object for visualization
        obj_points_pcd_world (o3d.PointCloud, optional): Object point cloud for visualization
        
    Returns:
        tuple: (keep_mask, drop_mask) where:
            - keep_mask: Boolean mask of kept grasps (True = passes alignment)
            - drop_mask: Boolean mask of dropped grasps (True = fails alignment)
    """
    # OBB alignment calculation
    R_obb = np.asarray(T_obb_to_world[:3, :3], dtype=float)
    c_obb = np.asarray(T_obb_to_world[:3, 3], dtype=float)
    U, _, Vt = np.linalg.svd(R_obb)
    R_obb = U @ Vt  # optional cleanup

    # Grasp rotations in world frame: (N,3,3)
    R_grasps = np.asarray(grasp_transforms[:, :3, :3], dtype=float)

    # C[n, i, j] = | dot(obb_axis_i, grasp_axis_j) |
    # For one grasp this is: C = |R_obb^T @ R_grasp|, shape (3,3)
    C = np.abs(np.einsum("ij,njk->nik", R_obb.T, R_grasps))  # (N,3,3)

    cos15 = float(np.cos(np.deg2rad(25.0)))

    # "Each axis, not combined":
    # for each grasp axis j, at least one OBB axis i must pass threshold
    keep = (C.max(axis=1) >= cos15).all(axis=1)  # (N,)
    drop = ~keep

    # Optional debug angles (deg): worst per-grasp axis mismatch
    best_per_grasp_axis = C.max(axis=1)  # (N,3)
    axis_angles_deg = np.rad2deg(np.arccos(np.clip(best_per_grasp_axis, -1.0, 1.0)))
    worst_angle_deg = axis_angles_deg.max(axis=1)

    print(f"OBB alignment: kept {keep.sum()}/{len(keep)}, dropped {drop.sum()}")
    if drop.any():
        print(f"Dropped grasps worst-angle deg min/mean/max: "
              f"{worst_angle_deg[drop].min():.2f} / {worst_angle_deg[drop].mean():.2f} / {worst_angle_deg[drop].max():.2f}")

    # Visualization
    if should_plot:
        _visualize_obb_alignment(grasp_transforms, keep, drop, R_obb, c_obb, 
                               obb_proxy, obj_points_pcd_world)

    return keep, drop


def _visualize_obb_alignment(grasp_transforms, keep_mask, drop_mask, R_obb, c_obb, 
                            obb_proxy=None, obj_points_pcd_world=None):
    """Helper function for OBB alignment visualization"""
    def _grasp_axes_lines(Ts, color=(0.1, 0.8, 0.1), axis_len=0.04, max_show=300):
        if Ts.shape[0] == 0:
            return None
        if Ts.shape[0] > max_show:
            idx = np.linspace(0, Ts.shape[0] - 1, max_show, dtype=int)
            Ts = Ts[idx]

        pts, lines, cols = [], [], []
        for T in Ts:
            o = T[:3, 3]
            Rg = T[:3, :3]
            base = len(pts)
            pts.extend([o, o + axis_len * Rg[:, 0], o + axis_len * Rg[:, 1], o + axis_len * Rg[:, 2]])
            lines.extend([[base, base + 1], [base, base + 2], [base, base + 3]])
            cols.extend([color, color, color])

        ls = o3d.geometry.LineSet()
        ls.points = o3d.utility.Vector3dVector(np.asarray(pts, dtype=float))
        ls.lines = o3d.utility.Vector2iVector(np.asarray(lines, dtype=np.int32))
        ls.colors = o3d.utility.Vector3dVector(np.asarray(cols, dtype=float))
        return ls

    # OBB frame axis
    if obb_proxy is not None:
        ext = np.asarray(obb_proxy.get_oriented_bounding_box().extent, dtype=float)
        obb_ref = o3d.geometry.OrientedBoundingBox(c_obb, R_obb, ext)
        T_obb_vis = np.eye(4, dtype=float)
        T_obb_vis[:3, :3] = R_obb
        T_obb_vis[:3, 3] = np.asarray(obb_ref.center, dtype=float)
        obb_axes = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.08)
        obb_axes.transform(T_obb_vis)
    else:
        obb_axes = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.08, origin=c_obb)
        obb_axes.rotate(R_obb)
    
    pcd_world = copy.deepcopy(obj_points_pcd_world) if obj_points_pcd_world else None
    if pcd_world:
        pcd_world.paint_uniform_color([0.2, 0.6, 1.0])  # blue points

    keep_ls = _grasp_axes_lines(grasp_transforms[keep_mask], color=(0.1, 0.8, 0.1))
    drop_ls = _grasp_axes_lines(grasp_transforms[drop_mask], color=(0.9, 0.2, 0.2))
    world_axes = o3d.geometry.TriangleMesh.create_coordinate_frame(
        size=0.12, origin=[0.0, 0.0, 0.0]
    )

    vis = [obb_axes, world_axes]
    if pcd_world:
        vis.append(pcd_world)
    if keep_ls is not None:
        vis.append(keep_ls)
    if drop_ls is not None:
        vis.append(drop_ls)

    o3d.visualization.draw_geometries(
        vis,
        window_name="OBB alignment filter (green=keep, red=drop)"
    )
