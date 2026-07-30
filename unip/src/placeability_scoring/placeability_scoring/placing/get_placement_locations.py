import open3d as o3d
import numpy as np
import time
import argparse
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation as R
from shapely.geometry import Point, Polygon
import copy
import pyfqmr

from utils.o3d_klampt_conversions import klampt_geom_to_open3d, o3d_mesh_to_klampt_geom
from placeability_scoring.planning.environment import (
    make_shelf, make_bin
)

def keep_large_components(mesh: o3d.geometry.TriangleMesh,
                          min_triangles: int = 100) -> o3d.geometry.TriangleMesh:
    m = o3d.geometry.TriangleMesh(mesh)
    clusters, tri_counts, _ = m.cluster_connected_triangles()
    tri_counts = np.asarray(tri_counts)
    clusters = np.asarray(clusters)
    keep = tri_counts >= min_triangles
    tri_mask = ~keep[clusters]  # True => remove
    m.remove_triangles_by_mask(tri_mask)
    m.remove_unreferenced_vertices()
    m.remove_degenerate_triangles()
    m.compute_vertex_normals()
    return m

def simplify_with_pyfqmr(mesh: o3d.geometry.TriangleMesh,
                         target_face_count: int = None,
                         reduction: float = 1.0,
                         aggressiveness: int = 7,
                         preserve_border: bool = True,
                         verbose: bool = False) -> o3d.geometry.TriangleMesh:
    """
    Simplify an Open3D mesh using pyfqmr (Fast Quadric Mesh Reduction).
    - target_face_count: absolute target number of triangles. If None, uses `reduction`.
    - reduction: fraction of faces to remove (e.g. 0.9 => keep ~10%).
    """

    # --- extract numpy arrays ---
    V = np.asarray(mesh.vertices, dtype=np.float32)
    F = np.asarray(mesh.triangles, dtype=np.int32)

    if target_face_count is None:
        target_face_count = max(4, int((1.0 - reduction) * len(F)))

    # --- run pyfqmr ---
    simp = pyfqmr.Simplify()
    simp.setMesh(V, F)
    simp.simplify_mesh(target_count=int(target_face_count),
                       aggressiveness=aggressiveness,
                       preserve_border=preserve_border,
                       verbose=verbose)

    V2, F2, _ = simp.getMesh()

    # --- drop degenerate (duplicate-index) faces ---
    invalid = (F2[:,0] == F2[:,1]) | (F2[:,0] == F2[:,2]) | (F2[:,1] == F2[:,2])
    F2 = F2[~invalid]

    # --- rebuild Open3D mesh ---
    out = o3d.geometry.TriangleMesh(
        vertices=o3d.utility.Vector3dVector(V2.astype(np.float64)),
        triangles=o3d.utility.Vector3iVector(F2.astype(np.int32))
    )

    # optional cleanup (fix isolated verts, duplicates, norms)
    out.remove_unreferenced_vertices()
    out.remove_duplicated_vertices()
    out.remove_duplicated_triangles()
    out.remove_degenerate_triangles()
    out.compute_vertex_normals()
    return out

def get_points(mesh, number_of_poses=200):
    sampled_points = np.empty((0, 3))
    pcd_env = None


    while sampled_points.shape[0] < number_of_poses:
        pcd_env = mesh.sample_points_poisson_disk(
            number_of_points=number_of_poses, init_factor=1
        )
        pcd_env.estimate_normals()
        pcd_env.orient_normals_to_align_with_direction(np.array([0, 0, 1]))

        normals = np.asarray(pcd_env.normals)
        points = np.asarray(pcd_env.points)

        # normals within ~15° of +Z
        z_axis = np.array([0, 0, 1])
        mask = (normals @ z_axis) > 0.95

        new_points = points[mask]
        sampled_points = np.vstack([sampled_points, new_points])

        print(
            f"Got {len(new_points)} new horizontal candidates, "
            f"total={len(sampled_points)}"
        )

    # trim extra if we overshot
    if sampled_points.shape[0] > number_of_poses:
        sampled_points = sampled_points[:number_of_poses]

    return sampled_points, pcd_env

def points_to_transforms(points):
    N = points.shape[0]
    transforms = np.repeat(np.eye(4)[np.newaxis, :, :], N, axis=0)
    transforms[:, :3, 3] = points
    return transforms

def apply_random_z_rotation(transforms):
    n = len(transforms)
    thetas = np.random.uniform(0, 2 * np.pi, size=n)
    cos_t = np.cos(thetas)
    sin_t = np.sin(thetas)
    
    # Create batch of rotation matrices shape (n, 3, 3)
    Rz = np.zeros((n, 3, 3))
    Rz[:, 0, 0] = cos_t
    Rz[:, 0, 1] = -sin_t
    Rz[:, 1, 0] = sin_t
    Rz[:, 1, 1] = cos_t
    Rz[:, 2, 2] = 1
    
    # Apply the rotations to the rotation parts of each transform
    # Assuming transforms is a (n, 4, 4) numpy array
    transforms[:, :3, :3] = Rz
    
    return transforms


def is_inside_convex_hull(hull: ConvexHull, points: np.ndarray) -> np.ndarray:
    A = hull.equations[:, :-1]
    b = hull.equations[:, -1]
    return np.all(A @ points.T + b[:, np.newaxis] <= 1e-8, axis=0)

def check_hull_containment(hull1: ConvexHull, hull2: ConvexHull, T: np.ndarray):
    """
    Checks if the transformed 2D hull1 is fully inside 2D hull2 using a 4x4 transformation matrix.
    The points are lifted to 3D with z=0, transformed in 3D, and projected back to 2D.
    """
    # (N, 2) → (N, 3) with z = 0
    points1 = hull1.points[hull1.vertices]
    points1_3d = np.hstack([points1, np.zeros((points1.shape[0], 1))])  # (N, 3)

    # Homogeneous: (x, y, z) → (x, y, z, 1)
    points1_hom = np.hstack([points1_3d, np.ones((points1.shape[0], 1))])  # (N, 4)

    # Apply 4x4 transformation
    transformed_3d = (T @ points1_hom.T).T  # (N, 4)

    # Project back to 2D
    transformed_2d = transformed_3d[:, :2]

    # Check containment
    inside_mask = is_inside_convex_hull(hull2, transformed_2d)
    return np.all(inside_mask), transformed_2d



def plot_2d_convex_hull_as_lineset(points_2d: np.ndarray, plane_model: np.ndarray, color=[1, 0, 0]) -> o3d.geometry.LineSet:
    """
    Given 2D points lying in a plane, computes the convex hull and draws it as a closed polygon in Open3D.

    Args:
        points_2d (np.ndarray): Nx2 array of points (assumed projected onto a plane)
        plane_model (a, b, c, d): coefficients of the ground plane (ax + by + cz + d = 0)
        color (list of 3 floats): RGB color

    Returns:
        o3d.geometry.LineSet: LineSet that draws the convex hull as a closed loop
    """
    # Step 1: Convex Hull in 2D
    hull = ConvexHull(points_2d)
    hull_vertices_2d = points_2d[hull.vertices]  # shape (M, 2)

    # Step 2: Project 2D points onto plane → 3D
    a, b, c, d = plane_model
    points_3d = []
    for x, y in hull_vertices_2d:
        z = -(a * x + b * y + d) / c
        points_3d.append([x, y, z])
    points_3d = np.array(points_3d)

    # Step 3: Create lines to connect the convex hull edges in a closed loop
    num_points = len(points_3d)
    lines = [[i, (i + 1) % num_points] for i in range(num_points)]

    # Step 4: Create Open3D LineSet
    line_set = o3d.geometry.LineSet()
    line_set.points = o3d.utility.Vector3dVector(points_3d)
    line_set.lines = o3d.utility.Vector2iVector(lines)
    line_set.paint_uniform_color(color)

    return line_set


def crop_and_simplify_mesh(env_mesh, environment: str = "shelf", placement_bounds: dict = None, plotting=False):
    """Crops and simplifies the environment mesh using per-environment bounds.

    Args:
        env_mesh: Open3D mesh for the environment.
        environment: Key to select which bounds to use (e.g., 'shelf', 'lower_shelf', 'bin').
        placement_bounds: Dict of environment bounds (required). Get from environment_config.py.
    """

    if placement_bounds is None:
        raise ValueError("placement_bounds must be provided. Get from environment_config.py")

    bounds = placement_bounds
    if environment not in bounds:
        raise ValueError(f"Unknown environment '{environment}' for placement bounds")

    env_bounds = bounds[environment]
    min_bound = env_bounds["min_bound"]
    max_bound = env_bounds["max_bound"]
    min_bound_shelf = env_bounds["min_bound_shelf"]
    max_bound_shelf = env_bounds["max_bound_shelf"]
    min_bound_placement = env_bounds["min_bound_placement"]
    max_bound_placement = env_bounds["max_bound_placement"]

    # Crop/detect the relevant area and simplify
    min_bound_crop, max_bound_crop = min_bound, max_bound

    
    aabb = o3d.geometry.AxisAlignedBoundingBox(min_bound_crop, max_bound_crop)
    
    
    cropped = env_mesh.crop(aabb)
    cropped = simplify_with_pyfqmr(cropped, aggressiveness=3)
    cropped = keep_large_components(cropped)
    
    if(environment=="shelf" or environment=="lower_shelf" or environment == "superlow_shelf"):
        shelf_mesh, shelf_mesh_notop = make_shelf(
            filled_mesh=cropped,
            min_bound=min_bound,
            max_bound=max_bound,
            min_bound_notop=min_bound_placement,   # optional
            max_bound_notop=max_bound_placement,   # optional
        )
        shelf_mesh_collision, _ = make_shelf(
            filled_mesh=cropped,
            min_bound=min_bound_shelf,
            max_bound=max_bound_shelf
        )
    elif(environment=="bin"):
        shelf_mesh, shelf_mesh_notop = make_bin(
            filled_mesh=cropped,
            min_bound=min_bound,
            max_bound=max_bound,
            min_bound_notop=min_bound_placement,   # optional
            max_bound_notop=max_bound_placement,   # optional
        )
        shelf_mesh_collision, _ = make_bin(
            filled_mesh=cropped,
            min_bound=min_bound_shelf,
            max_bound=max_bound_shelf
        )

    if(plotting):
        aabb_shelf = o3d.geometry.AxisAlignedBoundingBox(min_bound_shelf, max_bound_shelf)
        world = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.5)
        aabb.color = (1, 0, 0)
        #o3d.visualization.draw_geometries([env_mesh, aabb, world])
        o3d.visualization.draw_geometries([env_mesh, aabb_shelf, world])
        o3d.visualization.draw_geometries([shelf_mesh])
        
    
    return shelf_mesh, shelf_mesh_notop, shelf_mesh_collision
    

def _apply_inplace(mesh, method_name, *args, **kwargs):
    """Call an Open3D in-place method; if it returns a mesh (newer O3D) reassign."""
    m2 = getattr(mesh, method_name)(*args, **kwargs)
    return m2 if m2 is not None else mesh

def mesh_only_upward(env_mesh: o3d.geometry.TriangleMesh, max_tilt_deg=10.0):
    mesh = copy.deepcopy(env_mesh)
    mesh.compute_triangle_normals()

    z = np.array([0., 0., 1.])
    cos_thr = np.cos(np.deg2rad(max_tilt_deg))  # e.g. 10° -> ~0.985
    triN = np.asarray(mesh.triangle_normals)    # (T,3)
    keep = (triN @ z) >= cos_thr

    if keep.sum() == 0:
        raise RuntimeError("No upward-facing triangles found. Increase max_tilt_deg or check mesh orientation.")

    # --- Build a new mesh using only kept triangles (no in-place masking) ---
    tris = np.asarray(mesh.triangles)           # (T,3) int
    sel_tris = tris[keep]

    new_mesh = o3d.geometry.TriangleMesh()
    # Keep all vertices first; we'll drop unreferenced below
    new_mesh.vertices = copy.deepcopy(mesh.vertices)
    new_mesh.triangles = o3d.utility.Vector3iVector(sel_tris)

    # Cleanup (don’t rely on return values)
    new_mesh = _apply_inplace(new_mesh, "remove_unreferenced_vertices")
    new_mesh = _apply_inplace(new_mesh, "remove_degenerate_triangles")
    new_mesh = _apply_inplace(new_mesh, "remove_duplicated_triangles")
    new_mesh = _apply_inplace(new_mesh, "remove_duplicated_vertices")
    new_mesh = _apply_inplace(new_mesh, "remove_non_manifold_edges")
    return new_mesh

def sample_horizontal_points(env_mesh, number_of_poses, max_tilt_deg=10.0, oversample=2):
    horiz_mesh = mesh_only_upward(env_mesh, max_tilt_deg=max_tilt_deg)
    if len(horiz_mesh.triangles) == 0:
        raise RuntimeError("No triangles left after filtering to upward-facing surfaces.")

    # Sample only from horizontal submesh
    pcd = horiz_mesh.sample_points_poisson_disk(
        number_of_points=max(number_of_poses * oversample, 100), init_factor=2
    )

    # (Optional) extra normal check — do NOT flip normals to +Z here
    pcd.estimate_normals()
    z = np.array([0., 0., 1.])
    cos_thr = np.cos(np.deg2rad(max_tilt_deg))
    normals = np.asarray(pcd.normals)
    pts = np.asarray(pcd.points)
    mask = (normals @ z) >= cos_thr

    pts = pts[mask]
    if pts.shape[0] == 0:
        raise RuntimeError("No points passed the horizontal normal check; relax max_tilt_deg or inspect mesh.")
    return pts[:number_of_poses], pcd.select_by_index(np.where(mask)[0])



def get_placement_locations_multiple_orientations(
    obj_mesh,
    env_mesh,
    object_convex_hull,
    orientations,
    center_alignments,
    plotting=False,
    number_of_poses=1000,
    environment="shelf",
    placement_bounds=None,
):
    start_time_total = time.time()
    
    
    env_mesh, sampling_env_mesh, shelf_mesh_collision = crop_and_simplify_mesh(
        env_mesh=env_mesh,
        environment=environment,
        placement_bounds=placement_bounds,
        plotting=plotting,
    )
    sampled_points, pcd_env = sample_horizontal_points(sampling_env_mesh, number_of_poses, max_tilt_deg=10.0)

    ############################### CONVEX HULL - Placing Area #########################################

    plane_model, inliers = pcd_env.segment_plane(
        distance_threshold=0.01,
        ransac_n=3,
        num_iterations=1000
    )
    table_pcd = pcd_env.select_by_index(inliers)
    points_3d = np.asarray(table_pcd.points)
    points_2d = points_3d[:, :2]  # Only XY


    ############################### CONVEX HULL - Placing Area #########################################
    hull = ConvexHull(points_2d)
    hull_vertices = points_2d[hull.vertices]

    # Step 1: Create polygon from convex hull vertices
    poly = Polygon(hull_vertices)

    if poly.is_empty or not poly.is_valid:
        world_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
            size=0.1, origin=[0, 0, 0]
        )
        show_prob_points = o3d.geometry.PointCloud()
        show_prob_points.points = o3d.utility.Vector3dVector(points_3d)
        show_prob_points.paint_uniform_color([0, 1, 0])
        o3d.visualization.draw_geometries([show_prob_points, env_mesh, world_frame])
        raise ValueError("Placement polygon is empty or invalid")

    placement_coords = hull_vertices
    
    # --------------------------------- PLOT ------------------------------------------
    a, b, c, d = plane_model
    if(plotting):
        hull_points_3d = []
        for x, y in placement_coords:
            z = -(a * x + b * y + d) / c
            hull_points_3d.append([x, y, z])
        hull_points_3d = np.array(hull_points_3d)

        # Add line connections
        lines = [[i, (i + 1) % len(hull_points_3d)] for i in range(len(hull_points_3d))]

        line_set = o3d.geometry.LineSet()
        line_set.points = o3d.utility.Vector3dVector(hull_points_3d)
        line_set.lines = o3d.utility.Vector2iVector(lines)
        line_set.paint_uniform_color([1, 0, 0])  # red
    # --------------------------------- PLOT END ------------------------------------------


    ############################### Check which points are contained in convex hull #########################################
    print("SAMPLED POINTS SHAPE BEFORE: ",sampled_points.shape)
    # Create shapely Points
    shapely_points = [Point(xy) for xy in sampled_points[:, :2]]

    # Check which are inside the placement polygon
    mask_inside = np.array([poly.covers(p) for p in shapely_points])

    # Filter the original 3D points
    inside_points = sampled_points[mask_inside]
    outside_points = sampled_points[~mask_inside]

    sampled_points = inside_points
    
    print("SAMPLED POINTS SHAPE AFTER: ",sampled_points.shape)

    ############################### PLOTTING surface points #########################################
    if(plotting):
        # Convert numpy arrays to Open3D point clouds
        pcd_inside = o3d.geometry.PointCloud()
        pcd_inside.points = o3d.utility.Vector3dVector(inside_points)
        pcd_inside.paint_uniform_color([0, 1, 0])  # green

        pcd_outside = o3d.geometry.PointCloud()
        pcd_outside.points = o3d.utility.Vector3dVector(outside_points)
        pcd_outside.paint_uniform_color([1, 0, 0])  # red
    ########################################################################
        

    ################################## Check if Place area Convex hull contains object convex hull ######################################
    

    base_transforms = points_to_transforms(sampled_points)
    base_transforms = apply_random_z_rotation(base_transforms)
    
    
    print(f"Execution time collision checks: {time.time() - start_time_total:.6f} seconds")
    
    ##############################################################################################################################################################################################
    non_collision_Transform_list = []
    # iterate all possible orientations, here one could also use different sampled points or such for the sampling but that is disregarded for now TODO ?
    
    if(plotting):
        # plotting of outer line
        hull_points_3d = []
        for x, y in hull_vertices:
            z = -(a * x + b * y + d) / c
            hull_points_3d.append([x, y, z])
        hull_points_3d = np.array(hull_points_3d)
        # Step 3: Create line connections
        lines = [[i, (i + 1) % len(hull_points_3d)] for i in range(len(hull_points_3d))]
        # Step 4: Create LineSet
        line_set_old = o3d.geometry.LineSet()
        line_set_old.points = o3d.utility.Vector3dVector(hull_points_3d)
        line_set_old.lines = o3d.utility.Vector2iVector(lines)
        line_set_old.paint_uniform_color([0, 0, 1])
        # plotting of outer line END
    environment = o3d_mesh_to_klampt_geom(env_mesh)
    obj_mesh_klampt = o3d_mesh_to_klampt_geom(obj_mesh)
    
    
    for rot_idx in range(len(orientations)):
        start_con = time.time()
        contains = []
        convex_points = []
        for t_idx in range(base_transforms.shape[0]):
            #points1 = hull.points[hull.vertices]
            result, points = check_hull_containment(hull1=object_convex_hull[rot_idx], hull2=hull, T=base_transforms[t_idx])
            contains.append(result)
            convex_points.append(points)
        
        
        if len(contains) == 0:
            non_collision_Transform_list.append(np.empty((0, 4, 4), dtype=float))
            continue

        contains_mask = np.array(contains, dtype=bool)
        before_shape_removal = base_transforms.shape[0]
        Transforms = base_transforms[contains_mask]
        
        print(f"{before_shape_removal - Transforms.shape[0]} Objects to close to edge of convex hull removed")
        print(time.time() - start_con)

        if Transforms.shape[0] == 0:
            non_collision_Transform_list.append(np.empty((0, 4, 4), dtype=float))
            continue
        
        #----------------------------------------------------PLOTS-------------------------------------------------
        if(plotting):
            line_set_list = []
            out_idx, in_idx = 0, 0
            for cp in range(len(convex_points)):
                if(contains[cp] == True):
                    if(in_idx>=6):continue
                    in_idx+=1
                    line_set_iter = plot_2d_convex_hull_as_lineset(convex_points[cp], plane_model=plane_model, color=[0,1,0])
                else:
                    if(out_idx>=2):continue
                    out_idx+=1
                    line_set_iter = plot_2d_convex_hull_as_lineset(convex_points[cp], plane_model=plane_model, color=[1,0,0])
                line_set_list.append(line_set_iter)
                
            o3d.visualization.draw_geometries([line_set, line_set_old, env_mesh] + line_set_list)
        #----------------------------------------------------PLOTS END-------------------------------------------------
        
        
        #####################################################################################################
        # TODO rotate object mesh to correct orientation
        T_flip = np.eye(4)
        T_flip[:3,:3] = orientations[rot_idx].as_matrix()
        T_flip[:3,3] -= center_alignments[rot_idx]

        #################################### COLLISION CHECK ###############################################
        collision_flags = np.zeros(Transforms.shape[0], dtype=bool)
        for t_idx in range(Transforms.shape[0]):
            T_total = Transforms[t_idx] @ T_flip
            T_total[2,3] += 0.015 # lift points a bit to avoid collision with table
            R = T_total[:3, :3].T.flatten() #.ravel().tolist()  # Faster than reshape(-1)
            #R = T_total[:3, :3].ravel().tolist()  # Faster than reshape(-1)
            t = T_total[:3, 3].tolist() 
            obj_mesh_klampt.setCurrentTransform(R, t)
            #if obj_mesh_klampt.collides(environment): collision_flags[t_idx] = True
            res = obj_mesh_klampt.distance(environment)
            #res = environment.distance(obj_mesh_klampt)
            d = res.d 
            #print(d)
            if d <= 0.00:  # treat as collision
                collision_flags[t_idx] = True
        ##########################################################################################################

        #----------------------------------------------------PLOTS-------------------------------------------------
        if(plotting):
            o3d_meshes = []
            for t_idx in range(Transforms.shape[0]):
                T_total = Transforms[t_idx] @ T_flip
                T_total[2,3] += 0.015 # lift points a bit to avoid collision with table
                if(collision_flags[t_idx]==True):
                    mesh_o3d = klampt_geom_to_open3d(obj_mesh_klampt, T=T_total, color=[1.0, 0.0, 0.0])
                else:
                    mesh_o3d = klampt_geom_to_open3d(obj_mesh_klampt, T=T_total, color=[0.0, 0.5, 0.5])
                    o3d_meshes.append(mesh_o3d)
            o3d.visualization.draw_geometries(o3d_meshes + [env_mesh])
                
        #----------------------------------------------------PLOTS END-------------------------------------------------
    
        

        non_collision_Transforms = Transforms[~collision_flags] @ T_flip
        
        non_collision_Transform_list.append(non_collision_Transforms)
    
    
    return non_collision_Transform_list, shelf_mesh_collision


def make_o3d_mesh_object(data, voxel_size=0.01, alpha=0.05):
    """
    Accepts either a path to a .ply point cloud or an o3d.geometry.PointCloud object,
    and returns a mesh (using alpha shape reconstruction).
    """
    if isinstance(data, str):
        # Assume it's a path
        pcd = o3d.io.read_point_cloud(data)
    elif isinstance(data, o3d.geometry.PointCloud):
        # Already a point cloud
        pcd = data
    else:
        raise TypeError("Input must be a file path or an Open3D PointCloud object.")

    # Downsample if needed
    if voxel_size > 0:
        pcd = pcd.voxel_down_sample(voxel_size=voxel_size)

    # Estimate normals
    pcd.estimate_normals()

    # Create mesh using alpha shape
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd, alpha=alpha)

    # Optional cleanup (not always needed)
    mesh.remove_duplicated_vertices()
    mesh.remove_degenerate_triangles()
    mesh.remove_duplicated_triangles()
    mesh.remove_non_manifold_edges()

    return mesh