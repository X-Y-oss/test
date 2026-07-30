import numpy as np
import open3d as o3d
from scipy.spatial.transform import Rotation as R

import copy
from placeability_scoring.mapping.mapping_Marques.reconstruction import Reconstruction

from itertools import combinations

def quat_xyzw_to_matrix(qx, qy, qz, qw):
    q = np.array([qx, qy, qz, qw], dtype=np.float64)
    q = q / np.linalg.norm(q)
    x, y, z, w = q
    # Rotation matrix from unit quaternion
    R = np.array([
        [1-2*(y*y+z*z),   2*(x*y - z*w),   2*(x*z + y*w)],
        [  2*(x*y + z*w), 1-2*(x*x+z*z),   2*(y*z - x*w)],
        [  2*(x*z - y*w),   2*(y*z + x*w), 1-2*(x*x+y*y)]
    ], dtype=np.float64)
    T = np.eye(4, dtype=np.float64)
    T[:3, :3] = R
    return T

def make_T(tx, ty, tz, qx, qy, qz, qw):
    T = quat_xyzw_to_matrix(qx,qy,qz,qw)
    T[:3, 3] = [tx, ty, tz]
    return T

def quat_to_euler(qx, qy, qz, qw, degrees=False):
    """Convert quaternion (x,y,z,w) → Euler angles (roll,pitch,yaw)."""
    r = R.from_quat([qx, qy, qz, qw])
    return r.as_euler("xyz", degrees=degrees)  # returns (roll, pitch, yaw)

def euler_to_quat(roll, pitch, yaw, degrees=False):
    """Convert Euler angles (roll,pitch,yaw) → quaternion (x,y,z,w)."""
    r = R.from_euler("xyz", [roll, pitch, yaw], degrees=degrees)
    return r.as_quat()  # returns (x,y,z,w)

def pose6d_to_matrix(pose6d):
    """Convert [x,y,z,roll,pitch,yaw] to a 4x4 transform matrix."""
    x, y, z, roll, pitch, yaw = pose6d
    T = np.eye(4)
    T[:3, :3] = R.from_euler("xyz", [roll, pitch, yaw]).as_matrix()
    T[:3, 3] = [x, y, z]
    return T

def viridis_like(values):
    """Tiny scalar→color map (0..1) → RGB, numpy-only."""
    v = np.clip(values, 0.0, 1.0)
    # simple 5-point gradient (black→blue→green→yellow→white)
    stops = np.array([
        [0.0, 0.0, 0.0],
        [0.2, 0.1, 0.6],
        [0.1, 0.7, 0.2],
        [0.9, 0.9, 0.2],
        [0.9, 0.9, 0.9]
    ])
    idx = (v * (len(stops) - 1)).astype(int)
    idx2 = np.clip(idx + 1, 0, len(stops) - 1)
    t = (v * (len(stops) - 1)) - idx
    return (1 - t)[:, None] * stops[idx] + t[:, None] * stops[idx2]


def random_rotation_matrix():
    # Uniform SO(3) using unit quaternions
    u1, u2, u3 = np.random.rand(), np.random.rand(), np.random.rand()
    q = np.array([
        np.sqrt(1-u1) * np.sin(2*np.pi*u2),
        np.sqrt(1-u1) * np.cos(2*np.pi*u2),
        np.sqrt(u1)   * np.sin(2*np.pi*u3),
        np.sqrt(u1)   * np.cos(2*np.pi*u3)
    ])  # (x, y, z, w)
    x, y, z, w = q
    R = np.array([
        [1-2*(y*y+z*z),   2*(x*y - z*w),   2*(x*z + y*w)],
        [  2*(x*y + z*w), 1-2*(x*x+z*z),   2*(y*z - x*w)],
        [  2*(x*z - y*w),   2*(y*z + x*w), 1-2*(x*x+y*y)]
    ])
    return R

def rotate_pointcloud_random(pcd: o3d.geometry.PointCloud) -> o3d.geometry.PointCloud:
    pcd_r = copy.deepcopy(pcd)
    R = random_rotation_matrix()
    # rotate about origin; translate to origin first if you want rotation about centroid
    pcd_r.rotate(R, center=(0, 0, 0))
    return pcd_r



def obb_and_axis_align(pcd: o3d.geometry.PointCloud):
    """
    Returns:
      obb: OrientedBoundingBox (Open3D)
      aligned_pcd: point cloud transformed into OBB coordinates (axis-aligned)
      T_world_to_obb: 4x4 transform mapping world -> OBB frame
      T_obb_to_world: 4x4 transform mapping OBB -> world frame
    """
    #obb = o3d.geometry.OrientedBoundingBox()
    #obb = obb.create_from_points_minimal(pcd.points)
    # 1) Oriented bounding box of the (possibly rotated/filtered) cloud
    obb = pcd.get_minimal_oriented_bounding_box()  # PCA-based OBB
    R_obb = obb.R        # columns are the OBB axes in world coords
    c_obb = obb.center   # OBB center in world coords

    # 2) Build transforms
    T_obb_to_world = np.eye(4)
    T_obb_to_world[:3, :3] = R_obb
    T_obb_to_world[:3, 3]  = c_obb

    T_world_to_obb = np.eye(4)
    T_world_to_obb[:3, :3] = R_obb.T
    T_world_to_obb[:3, 3]  = -R_obb.T @ c_obb

    # 3) Transform points into OBB frame (becomes axis-aligned there)
    aligned_pcd = copy.deepcopy(pcd)
    aligned_pcd.translate(-c_obb)       # subtract center
    aligned_pcd.rotate(R_obb.T, center=(0, 0, 0))  # rotate into OBB axes

    return obb, aligned_pcd, T_world_to_obb, T_obb_to_world

def obb_and_axis_align_z_up(pcd: o3d.geometry.PointCloud):
    obb = pcd.get_minimal_oriented_bounding_box()
    R_obb = obb.R.copy()
    c_obb = obb.center

    z_world = np.array([0, 0, 1])
    dot_products = np.abs(R_obb.T @ z_world)
    z_index = np.argmax(dot_products)
    if z_index != 2:
        R_obb[:, [2, z_index]] = R_obb[:, [z_index, 2]]
    if np.dot(R_obb[:, 2], z_world) < 0:
        R_obb[:, 2] *= -1
        R_obb[:, 0] *= -1
    # Keep a proper right-handed frame after column swaps/sign fixes.
    if np.linalg.det(R_obb) < 0:
        R_obb[:, 1] *= -1

    T_obb_to_world = np.eye(4)
    T_obb_to_world[:3, :3] = R_obb
    T_obb_to_world[:3, 3] = c_obb

    T_world_to_obb = np.eye(4)
    T_world_to_obb[:3, :3] = R_obb.T
    T_world_to_obb[:3, 3] = -R_obb.T @ c_obb

    aligned_pcd = copy.deepcopy(pcd)
    aligned_pcd.translate(-c_obb)
    aligned_pcd.rotate(R_obb.T, center=(0, 0, 0))
    return obb, aligned_pcd, T_world_to_obb, T_obb_to_world


def visualize_survival(original_pcd, survived_mask):
    # Copy to avoid mutating
    vis_pcd = copy.deepcopy(original_pcd)

    # Default red (did NOT survive)
    colors = np.tile(np.array([[1.0, 0.0, 0.0]]), (len(vis_pcd.points), 1))

    # Overwrite survivors as blue
    colors[survived_mask] = np.array([0.0, 0.0, 1.0])

    vis_pcd.colors = o3d.utility.Vector3dVector(colors)

    return vis_pcd

class Offline_GraspingAreaReconstruction():
    def __init__(self, 
                 save_dir = "/home/ws/src/placeability_scoring/placeability_scoring/test_data/", 
                 extrinsics_save_dir = "/home/ws/src/placeability_scoring/placeability_scoring/camera_extrinsics/", 
                 viewpoints=[0,1,2],
                 use_static=True):
        # reconstruction parameters
        voxel_size = 0.0025
        res = 8
        depth_scale = 1000.0
        depth_max = 1.0
        weight_threshold = 0.1
        block_count = 100000
        
        self.use_static = use_static
        
        self.T_wrist_cam = np.load(f"{extrinsics_save_dir}T_wrist_cam.npy")
        self.T_static_cam = np.load(f"{extrinsics_save_dir}T_static_cam.npy")

        self.reconstruction = Reconstruction(
            depth_scale = depth_scale,
            depth_max=depth_max,
            res = res,
            voxel_size = voxel_size,
            device = o3d.core.Device('CPU:0'), #CPU:0
            miu = 0.001, # Laplace smoothing factor
            integrate_color=True,
            weight_threshold=weight_threshold,
            block_count=block_count
        )
        self.viewpoints = viewpoints
        self.save_dir = save_dir

    def reconstruct(self):
        for d_idx in self.viewpoints: 
            depth_path = f"{self.save_dir}depth_wrist_{d_idx}.npy"
            rgb_path= f"{self.save_dir}rgb_wrist_{d_idx}.npy"
            intr_path = f"{self.save_dir}intrinsics_wrist_{d_idx}.npy"
            pose_path = f"{self.save_dir}pose_wrist_{d_idx}.npy"
            depth_image_raw = np.load(depth_path)
            rgb_img = np.load(rgb_path)
            intrinsics = np.load(intr_path)
            wrist_cam_pose = np.load(pose_path)
            cam_pose = wrist_cam_pose @ self.T_wrist_cam
        
            self.reconstruction.update_vbg(depth=depth_image_raw, intrinsic=intrinsics, pose=cam_pose, color=rgb_img)
    
            # mesh, _ = self.reconstruction.extract_triangle_mesh()
            # pointcloud, _ = self.reconstruction.extract_point_cloud()
            # world_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.2)
            # cam_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.15)
            # cam_frame.transform(cam_pose)
            # # Visualize everything together
            # o3d.visualization.draw_geometries([mesh, world_frame, cam_frame])

        if(self.use_static):
            depth_path = f"{self.save_dir}depth_static.npy"
            rgb_path= f"{self.save_dir}rgb_static.npy"
            intr_path = f"{self.save_dir}intrinsics_static.npy"
            pose_path = f"{self.save_dir}pose_static.npy"
            depth_image_raw = np.load(depth_path)
            rgb_img = np.load(rgb_path)
            intrinsics = np.load(intr_path)
            static_cam_pose = np.load(pose_path)
            cam_pose = static_cam_pose @ self.T_static_cam
            
        
            self.reconstruction.update_vbg(depth=depth_image_raw, intrinsic=intrinsics, pose=cam_pose, color=rgb_img)
        
    
        mesh, _ = self.reconstruction.extract_triangle_mesh()
        pointcloud, _, weights = self.reconstruction.extract_point_cloud(return_weight=True)
        
        x_min, x_max = -0.6, 0.6
        y_min, y_max =  0.3, 1.2
        z_min, z_max =  0.70, 1.0
        
        aabb = o3d.geometry.AxisAlignedBoundingBox(
            min_bound=(x_min, y_min, z_min),
            max_bound=(x_max, y_max, z_max)
        )
        mesh = mesh.crop(aabb)
        
        #o3d.visualization.draw_geometries([mesh])
                
        return pointcloud, mesh, weights

def filter_object(environment_pointcloud, weights=None, plotting=False, table_height=0.72, object_area=[-0.2,0.2,0.3,0.9], save_dir="", pc_name="", annotation=""):
    # 1) Crop with AABB to object area
    x_min, x_max = object_area[0], object_area[1]
    y_min, y_max =  object_area[2], object_area[3]
    z_min, z_max =  table_height, table_height + 0.4
    
    # 1) Crop with AABB for indices
    N0 = np.asarray(environment_pointcloud.points).shape[0]
    orig_idx = np.arange(N0, dtype=np.int64)
    
    aabb = o3d.geometry.AxisAlignedBoundingBox(
        min_bound=(x_min, y_min, z_min),
        max_bound=(x_max, y_max, z_max)
    )
    ind_crop = aabb.get_point_indices_within_bounding_box(environment_pointcloud.points)
    pointcloud = environment_pointcloud.select_by_index(ind_crop)
    orig_idx = orig_idx[ind_crop]
    
    if weights is not None:
        weights = weights[ind_crop]
    
    
    # outlier removal due to camera noise
    pointcloud, ind = pointcloud.remove_radius_outlier(nb_points=50, radius=0.01)
    if weights is not None: weights = weights[ind]
    #pointcloud = pointcloud.select_by_index(ind)
    orig_idx = orig_idx[ind]
    pointcloud, ind = pointcloud.remove_radius_outlier(nb_points=25, radius=0.01)
    if weights is not None: weights = weights[ind]

    #pointcloud = pointcloud.select_by_index(ind)
    orig_idx = orig_idx[ind]
    pointcloud, ind = pointcloud.remove_statistical_outlier(nb_neighbors=100, std_ratio=5.0)
    if weights is not None: weights = weights[ind]

    #pointcloud = pointcloud.select_by_index(ind)
    orig_idx = orig_idx[ind]
    
    
    #pc_init = copy.deepcopy(pointcloud)
    
    #o3d.visualization.draw_geometries([pointcloud])
    pointcloud, _, weights = ground_from_lowest_convex_hull_and_reconstruct(
        pointcloud, weights=weights, low_frac=0.01, grid_scale=1.0, shrink_hull=0.2, trim_outer=0.03,
        rebuild_mesh=False, mesh_method="poisson", poisson_depth=9
    )
    
    # curr_pc = copy.deepcopy(pointcloud)
    pointcloud, ind = mahalanobis_filter(pointcloud, keep_quantile=0.975)
    if weights is not None: weights = weights[ind]
    # vis_keep_drop(curr_pc, ind, "Mahalanobis (input cloud)")
    
    # curr_pc = copy.deepcopy(pointcloud)
    pointcloud, ind = pointcloud.remove_radius_outlier(nb_points=25, radius=0.01)
    if weights is not None: weights = weights[ind]
    # vis_keep_drop(curr_pc, ind, "Radius (input cloud)")


    

    # 1) compute OBB on the (randomly rotated) cloud
    obb, aligned_pcd, T_world_to_obb, T_obb_to_world = obb_and_axis_align_z_up(pointcloud)
    #obb, aligned_pcd, T_world_to_obb, T_obb_to_world = obb_and_axis_align(pointcloud)

    
    # 4) If you want to continue with your pipeline in aligned (axis-aligned) coords:
    object_points = np.asarray(aligned_pcd.points, dtype=np.float32)

    
    cp_mean = object_points.mean(axis=0)               # OBB coords
    z_min  = object_points[:, 2].min()                 # OBB z

    # shift we want to apply *in OBB frame* (put mean at origin and floor z at 0)
    t_align = np.array([-cp_mean[0], -cp_mean[1], -z_min], dtype=float)

    # 1) move the points (OBB frame)
    object_points = object_points + t_align            # center XY and lift z so min z = 0

    # 2) compose transforms safely
    T_center = np.eye(4)
    T_center[:3, 3] = t_align                          # OBB-frame translation

    # world -> final aligned
    T_world_to_obb = T_center @ T_world_to_obb

    # final aligned -> world  (inverse of above)
    # NOTE: multiply by R * (+cp_mean, +z_min) — not by raw values
    T_obb_to_world = T_obb_to_world @ np.linalg.inv(T_center)

    
    return object_points, weights, orig_idx, T_obb_to_world
    
def fill_holes_via_mesh(pcd: o3d.geometry.PointCloud,
                        method="poisson",
                        target_points=None):
    if target_points is None:
        target_points = len(pcd.points)

    # Normals are required for both Poisson and BPA
    pcd = pcd.voxel_down_sample(max(pcd.get_max_bound()-pcd.get_min_bound())/200.0)
    pcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.02, max_nn=30)
    )
    pcd.orient_normals_consistent_tangent_plane(50)

    if method == "poisson":
        mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            pcd, depth=9
        )
        densities = np.asarray(densities)
        # prune very low-density (spurious) parts
        verts_to_remove = densities < np.quantile(densities, 0.02)
        mesh.remove_vertices_by_mask(verts_to_remove)
    elif method == "bpa":
        # Choose radii ~ local spacing; tweak as needed
        radii = o3d.utility.DoubleVector([0.005, 0.01, 0.02])
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pcd, radii)
    else:
        raise ValueError("method must be 'poisson' or 'bpa'")

    mesh.remove_degenerate_triangles()
    mesh.remove_duplicated_triangles()
    mesh.remove_duplicated_vertices()
    mesh.remove_non_manifold_edges()

    # Sample points back from the mesh
    pcd_filled = mesh.sample_points_poisson_disk(target_points)
    return pcd_filled

# ---------- helpers ----------
def _ensure_pcd(x):
    if isinstance(x, o3d.geometry.PointCloud):
        return x
    x = np.asarray(x, dtype=np.float64)
    p = o3d.geometry.PointCloud()
    p.points = o3d.utility.Vector3dVector(x[:, :3])
    return p

def _estimate_spacing(pcd, k=8, sample=5000):
    pts = np.asarray(pcd.points)
    if pts.shape[0] < 2:
        return 0.01
    idx = np.random.choice(pts.shape[0], min(sample, pts.shape[0]), replace=False)
    tree = o3d.geometry.KDTreeFlann(pcd)
    dists = []
    for i in idx:
        _, _, d = tree.search_knn_vector_3d(pts[i], min(k+1, pts.shape[0]))
        if len(d) > 1:
            dists.append(np.mean(np.sqrt(np.array(d[1:]))))
    return float(np.median(dists)) if dists else 0.01

def _fit_plane(points3d):
    # LS plane via SVD
    P = np.asarray(points3d, dtype=np.float64)
    c = P.mean(axis=0)
    U, S, Vt = np.linalg.svd(P - c, full_matrices=False)
    n = Vt[-1]
    if n[2] < 0:  # make "up" roughly +z
        n = -n
    # orthonormal basis of the plane
    t1 = Vt[0]; t1 = t1 / np.linalg.norm(t1)
    t2 = np.cross(n, t1); t2 = t2 / np.linalg.norm(t2)
    return c, n / np.linalg.norm(n), t1, t2  # plane point, normal, basis

def _convex_hull_2d(pts2):  # Andrew's monotone chain
    pts = np.unique(np.asarray(pts2), axis=0)
    if len(pts) <= 2:
        return pts
    pts = pts[np.lexsort((pts[:,1], pts[:,0]))]
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(tuple(p))
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(tuple(p))
    hull = np.array(lower[:-1] + upper[:-1], dtype=np.float64)
    return hull

def _shrink_polygon_radial(poly_uv, frac=0.0):
    if frac <= 0:
        return poly_uv
    c = poly_uv.mean(axis=0)
    return c + (poly_uv - c) * (1.0 - frac)

def _points_in_polygon(points_uv, poly_uv):
    x = points_uv[:,0]; y = points_uv[:,1]
    x0 = poly_uv[:,0]; y0 = poly_uv[:,1]
    x1 = np.roll(x0, -1); y1 = np.roll(y0, -1)
    inside = np.zeros(points_uv.shape[0], dtype=bool)
    for i in range(len(poly_uv)):
        xi0, yi0, xi1, yi1 = x0[i], y0[i], x1[i], y1[i]
        cond = ((yi0 > y) != (yi1 > y))
        x_int = (xi1 - xi0) * (y - yi0) / (yi1 - yi0 + 1e-12) + xi0
        inside ^= cond & (x < x_int)
    return inside

def _trim_outer_percentile(points, pct=0.05, mode="xy"):
    pts = np.asarray(points)
    if mode == "xy":
        ctr = np.median(pts[:, :2], axis=0)
        d = np.linalg.norm(pts[:, :2] - ctr, axis=1)
    else:
        ctr = np.median(pts, axis=0)
        d = np.linalg.norm(pts - ctr, axis=1)
    thr = np.percentile(d, 100*(1.0-pct))
    keep = d <= thr
    return keep

# ---------- main op ----------
def ground_from_lowest_convex_hull_and_reconstruct(
    cloud,
    weights=None,
    low_frac=0.005,          # take the lowest 10% by z
    grid_scale=1.0,         # 1.0 ~ match native spacing; <1 denser, >1 sparser
    shrink_hull=0.0,        # 0..0.2 is typical to avoid overreach
    trim_outer=0.05,        # remove outermost 5% after merge
    rebuild_mesh=True,      # Poisson/BPA reconstruction
    mesh_method="poisson",  # "poisson" or "bpa"
    poisson_depth=9
):
    """
    Returns:
      pcd_out: Open3D point cloud (merged + trimmed)
      mesh:    Open3D TriangleMesh or None
      weights_out: numpy array of weights (if weights provided) or None
    """
    pcd = _ensure_pcd(cloud)
    pts = np.asarray(pcd.points)

    # 1) pick lowest points by global Z
    z_thr = np.percentile(pts[:,2], 100*low_frac)
    low_pts = pts[pts[:,2] <= z_thr]
    if low_pts.shape[0] < 3:  # fallback
        low_pts = pts[np.argsort(pts[:,2])[:max(10, len(pts)//50)]]

    # 2) fit a plane to the lowest set and get its basis
    p0, n, t1, t2 = _fit_plane(low_pts)

    # 3) project low points into the plane (u,v), build convex hull
    U = (low_pts - p0) @ t1
    V = (low_pts - p0) @ t2
    low_uv = np.c_[U, V]
    hull_uv = _convex_hull_2d(low_uv)
    hull_uv = _shrink_polygon_radial(hull_uv, frac=shrink_hull)

    # 4) sample a uniform grid inside the hull
    spacing = _estimate_spacing(pcd) * grid_scale
    spacing = max(spacing, 1e-4)
    umin, vmin = hull_uv.min(axis=0)
    umax, vmax = hull_uv.max(axis=0)
    nu = max(1, int(np.ceil((umax - umin)/spacing)))
    nv = max(1, int(np.ceil((vmax - vmin)/spacing)))
    uu = np.linspace(umin, umax, nu)
    vv = np.linspace(vmin, vmax, nv)
    Ugrid, Vgrid = np.meshgrid(uu, vv, indexing='xy')
    uv_grid = np.c_[Ugrid.ravel(), Vgrid.ravel()]
    inside = _points_in_polygon(uv_grid, hull_uv)
    uv_in = uv_grid[inside]

    # back to 3D on the plane
    ground_pts = p0 + uv_in[:,[0]] * t1 + uv_in[:,[1]] * t2

    # 5) merge with original & trim outer ring
    if pts.size:
        merged = np.vstack([pts, ground_pts])
        if weights is not None:
            # Synthesize weights for ground points
            # Use high confidence (e.g., 90th percentile of existing) since ground is inferred
            syn_weight_val = np.percentile(weights, 90) if len(weights) > 0 else 1.0
            syn_weights = np.full(ground_pts.shape[0], syn_weight_val)
            merged_weights = np.concatenate([weights, syn_weights])
        else:
            merged_weights = None
    else:
        merged = ground_pts
        merged_weights = np.ones(ground_pts.shape[0]) if weights is not None else None
        
    keep = _trim_outer_percentile(merged, pct=trim_outer, mode="xy")
    merged = merged[keep]
    if merged_weights is not None:
        merged_weights = merged_weights[keep]

    pcd_out = o3d.geometry.PointCloud()
    pcd_out.points = o3d.utility.Vector3dVector(merged)

    mesh = None
    if rebuild_mesh:
        # normals then reconstruct
        pcd_n = pcd_out.voxel_down_sample(spacing) if spacing > 0 else pcd_out
        pcd_n.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=spacing*3, max_nn=30)
        )
        pcd_n.orient_normals_consistent_tangent_plane(50)
        if mesh_method == "poisson":
            mesh, dens = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
                pcd_n, depth=poisson_depth
            )
            dens = np.asarray(dens)
            # prune ultra-sparse areas (adjust quantile as needed)
            mesh.remove_vertices_by_mask(dens < np.quantile(dens, 0.02))
        else:  # BPA
            # radius ~ 2–4× spacing
            r = spacing * 3.0
            mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
                pcd_n, o3d.utility.DoubleVector([r*0.5, r, r*2.0])
            )
        mesh.remove_degenerate_triangles()
        mesh.remove_duplicated_triangles()
        mesh.remove_duplicated_vertices()
        mesh.remove_non_manifold_edges()
        
    return pcd_out, mesh, merged_weights

# ---------- helpers ----------
def _is_pcd(x): return isinstance(x, o3d.geometry.PointCloud)

def _to_points(x):
    if _is_pcd(x): return np.asarray(x.points)
    x = np.asarray(x, dtype=np.float64)
    if x.ndim != 2 or x.shape[1] < 3: raise ValueError("Expect (N,3[+]) array")
    return x[:, :3].copy()

def _from_points_like(src, pts, keep_mask):
    """Return (same_type_as_src_filtered, keep_idx)"""
    keep_idx = np.nonzero(keep_mask)[0]
    if _is_pcd(src):
        out = o3d.geometry.PointCloud()
        out.points = o3d.utility.Vector3dVector(pts[keep_mask])
        # copy colors/normals if present
        if len(src.colors) == len(pts):
            out.colors = o3d.utility.Vector3dVector(np.asarray(src.colors)[keep_mask])
        if len(src.normals) == len(pts):
            out.normals = o3d.utility.Vector3dVector(np.asarray(src.normals)[keep_mask])
        return out, keep_idx
    else:
        arr = np.asarray(src)
        return arr[keep_mask], keep_idx

def estimate_spacing(x, k=6, sample=5000):
    """Median mean distance to k nearest neighbors."""
    if not _is_pcd(x):
        p = o3d.geometry.PointCloud()
        p.points = o3d.utility.Vector3dVector(_to_points(x))
    else:
        p = x
    pts = np.asarray(p.points)
    if len(pts) < 2: return 0.01
    idx = np.random.choice(len(pts), min(sample, len(pts)), replace=False)
    tree = o3d.geometry.KDTreeFlann(p)
    dists = []
    for i in idx:
        _, _, d2 = tree.search_knn_vector_3d(pts[i], min(k+1, len(pts)))
        if len(d2) > 1:
            dists.append(np.mean(np.sqrt(np.array(d2[1:]))))
    return float(np.median(dists)) if dists else 0.01

# ---------- 1) Outermost percentile trim ----------
def trim_outer_percentile(x, pct=0.05, mode="xy", center="median"):
    """
    Remove farthest pct by radial distance.
    mode: 'xy' (2D footprint) or 'xyz' (full 3D radius).
    center: 'median' or 'mean' or a 2/3-vector.
    """
    pts = _to_points(x)
    if mode == "xy":
        C = np.median(pts[:, :2], axis=0) if center=="median" else \
            (np.mean(pts[:, :2], axis=0) if center=="mean" else np.asarray(center)[:2])
        d = np.linalg.norm(pts[:, :2] - C, axis=1)
    else:
        C = np.median(pts, axis=0) if center=="median" else \
            (np.mean(pts, axis=0) if center=="mean" else np.asarray(center)[:3])
        d = np.linalg.norm(pts - C, axis=1)
    thr = np.percentile(d, 100*(1.0-pct))
    keep = d <= thr
    return _from_points_like(x, pts, keep)

# ---------- 2) Radius outlier (Open3D) ----------
def radius_outlier(x, radius=None, min_neighbors=16):
    """
    Keep points that have at least `min_neighbors` neighbors within `radius`.
    If radius is None, it uses 2.5 * estimated spacing.
    """
    pts = _to_points(x)
    p = o3d.geometry.PointCloud(); p.points = o3d.utility.Vector3dVector(pts)
    if radius is None:
        radius = 2.5 * estimate_spacing(p)
    p_clean, ind = p.remove_radius_outlier(nb_points=min_neighbors, radius=float(radius))
    keep = np.zeros(len(pts), dtype=bool); keep[np.array(ind, dtype=int)] = True
    return _from_points_like(x, pts, keep)

# ---------- 3) Statistical outlier (Open3D) ----------
def statistical_outlier(x, nb_neighbors=20, std_ratio=2.0):
    """
    Remove points with mean neighbor distance > mean + std_ratio * std.
    """
    pts = _to_points(x)
    p = o3d.geometry.PointCloud(); p.points = o3d.utility.Vector3dVector(pts)
    p_clean, ind = p.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
    keep = np.zeros(len(pts), dtype=bool); keep[np.array(ind, dtype=int)] = True
    return _from_points_like(x, pts, keep)

# ---------- 4) DBSCAN (density clustering) ----------
def dbscan_keep_core(x, eps=None, min_points=10, largest_cluster_only=True):
    """
    Label clusters by density; drop noise (label = -1).
    If largest_cluster_only=True, keep only the biggest cluster.
    """
    pts = _to_points(x)
    p = o3d.geometry.PointCloud(); p.points = o3d.utility.Vector3dVector(pts)
    if eps is None:
        eps = 2.0 * estimate_spacing(p)
    labels = np.array(p.cluster_dbscan(eps=float(eps), min_points=int(min_points), print_progress=False))
    if labels.size == 0:
        return _from_points_like(x, pts, np.ones(len(pts), dtype=bool))
    if largest_cluster_only:
        lab, counts = np.unique(labels[labels>=0], return_counts=True)
        keep_lab = lab[np.argmax(counts)] if lab.size else -1
        keep = labels == keep_lab
    else:
        keep = labels >= 0
    return _from_points_like(x, pts, keep)

# ---------- 5) Plane-residual filter (good for “ground” scenes) ----------
def plane_residual_filter(x, tol=None):
    """
    Fit best plane (SVD) and keep points within residual tol.
    If tol is None, set tol = 3 * estimated spacing.
    """
    pts = _to_points(x)
    C = pts.mean(axis=0)
    U, S, Vt = np.linalg.svd(pts - C, full_matrices=False)
    n = Vt[-1]      # plane normal
    resid = np.abs((pts - C) @ n)
    if tol is None:
        tol = 3.0 * estimate_spacing(pts)
    keep = resid <= float(tol)
    return _from_points_like(x, pts, keep)

# ---------- 6) Mahalanobis distance (global ellipsoidal outliers) ----------
def mahalanobis_filter(x, keep_quantile=0.95):
    """
    Keep the closest `keep_quantile` fraction by Mahalanobis distance in 3D.
    """
    pts = _to_points(x)
    mu = pts.mean(axis=0)
    X = pts - mu
    cov = np.cov(X.T)
    # regularize in case of rank issues
    cov += 1e-10 * np.eye(3)
    inv = np.linalg.inv(cov)
    d2 = np.einsum('ij,jk,ik->i', X, inv, X)  # quadratic form
    thr = np.quantile(d2, keep_quantile)
    keep = d2 <= thr
    return _from_points_like(x, pts, keep)

# ---------- Composable pipeline ----------
def clean_outliers(
    x,
    trim_pct=0.05,          # outermost 5% in XY
    use_statistical=True, nb_neighbors=20, std_ratio=2.0,
    use_radius=False, radius=None, min_neighbors=16,
    use_dbscan=False, eps=None, min_points=15, largest_cluster_only=True,
):
    y, _ = trim_outer_percentile(x, pct=trim_pct, mode="xy")
    if use_statistical:
        y, _ = statistical_outlier(y, nb_neighbors=nb_neighbors, std_ratio=std_ratio)
    if use_radius:
        y, _ = radius_outlier(y, radius=radius, min_neighbors=min_neighbors)
    if use_dbscan:
        y, _ = dbscan_keep_core(y, eps=eps, min_points=min_points, largest_cluster_only=largest_cluster_only)
    return y



def main(args=None):
    
    path="/home/ws/src/placeability_scoring/placeability_scoring/test_data/mustard_bottle/"
    pc_name= "mustard_bottle"
    viewpoints = [0, 1, 2, 3]

    for r in range(1, len(viewpoints)+1):
        for combo in combinations(viewpoints, r):
            annotation = "_viewpoints_" + "_".join(map(str, combo))
            combo = list(combo)
            pointcloud, mesh = Offline_GraspingAreaReconstruction(save_dir=path, viewpoints=combo)
            pcdnp, _, _, _, T_obb_to_world = filter_object(environment_pointcloud=pointcloud, plotting=False, save_dir=path, pc_name=pc_name, annotation=annotation)
            #pcd = o3d.geometry.PointCloud()
            #world = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1, origin=[0, 0, 0])
            #pcd.points = o3d.utility.Vector3dVector(pcdnp)
            #o3d.visualization.draw_geometries([pcd, world])
    
    exit()
    
    
    pcd.transform(T_obb_to_world)
    
    pcd2, mesh = ground_from_lowest_convex_hull_and_reconstruct(
        pcd, low_frac=0.01, grid_scale=1.0, shrink_hull=0.01, trim_outer=0.05,
        rebuild_mesh=False, mesh_method="poisson", poisson_depth=9
    )
    o3d.visualization.draw_geometries([pcd2])
    alla, _ = mahalanobis_filter(pcd2, keep_quantile=0.95)
    print("mahalanobis_filter")
    o3d.visualization.draw_geometries([alla])
    
    
    
    #alla = fill_holes_via_mesh(alla, method="poisson")
    alla = fill_holes_via_mesh(alla, method="bpa")
    alla = fill_holes_via_mesh(alla, method="bpa")
    alla = fill_holes_via_mesh(alla, method="bpa")
    print("bpa-3x")
    o3d.visualization.draw_geometries([alla])
    
    # alla = fill_holes_via_mesh(alla, method="bpa")
    # alla = fill_holes_via_mesh(alla, method="bpa")
    # o3d.visualization.draw_geometries([alla])
    
    
    # alla = fill_holes_via_mesh(alla, method="bpa")
    # alla = fill_holes_via_mesh(alla, method="bpa")
    # o3d.visualization.draw_geometries([alla])
    
    x = np.array(alla.points)
    np.save("dumm.npy", x)
    
    


if __name__ == '__main__':
    main()
