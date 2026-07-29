import open3d as o3d
import numpy as np


def inverse_cropping(mesh, min_xyz, max_xyz):
    # Define an axis-aligned bounding boxes (AABB)
    high_value = 5.0
    
    # Assume OO is the to be removed bounding box
    #                       🧱🧱🧱 <- Higher than max X
    # Smaller than min Y -> 🧱OO🧱 <- Higher than max Y
    #                       🧱🧱🧱 <- Smaller than min X
    # Under and Above Z are above and below object, one can add the area behind box aswell.
    
    # Higher than max X
    environment_cropped = mesh.crop(o3d.geometry.AxisAlignedBoundingBox(min_bound=[max_xyz[0], -high_value, 0.02], max_bound=[high_value, high_value, 2.0]))
    # Smaller than min X
    environment_cropped += mesh.crop(o3d.geometry.AxisAlignedBoundingBox(min_bound=[-high_value, -high_value, 0.02], max_bound=[min_xyz[0], high_value, 2.0]))
    # Higher than max Y
    environment_cropped += mesh.crop(o3d.geometry.AxisAlignedBoundingBox(min_bound=[min_xyz[0], max_xyz[1], 0.02], max_bound=[max_xyz[0], high_value, 2.0]))
    # Smaller than min Y
    environment_cropped += mesh.crop(o3d.geometry.AxisAlignedBoundingBox(min_bound=[min_xyz[0], -high_value, 0.02], max_bound=[max_xyz[0], min_xyz[1], 2.0]))
    # Under min Z
    try:
        environment_cropped += mesh.crop(o3d.geometry.AxisAlignedBoundingBox(min_bound=[min_xyz[0], min_xyz[1], 0.02], max_bound=[max_xyz[0], max_xyz[1], min_xyz[2]]))
    except:print("No mesh below cropped region")
    # Above max Z
    environment_cropped += mesh.crop(o3d.geometry.AxisAlignedBoundingBox(min_bound=[min_xyz[0], min_xyz[1], max_xyz[2]], max_bound=[max_xyz[0], max_xyz[1], 2.0]))
            
    return environment_cropped


def remove_object(mesh, object_of_interest, plotting=False, plane_adjustment=-0.03):
    aabb = object_of_interest.get_axis_aligned_bounding_box()
    inflated_aabb = aabb
    min_bound = np.array(inflated_aabb.min_bound)
    max_bound = np.array(inflated_aabb.max_bound)
    
    min_bound -= 0.1
    max_bound += 0.1
    
    env_mesh = inverse_cropping(mesh=mesh, min_xyz=min_bound, max_xyz=max_bound)
    
    plane_z = aabb.min_bound[2] - plane_adjustment  # 1.5 cm below object's lowest point

    # Set plane dimensions (e.g., size of bounding box in x/y with margin)
    plane_length = max_bound[0] - min_bound[0]
    plane_width  = max_bound[1] - min_bound[1]
    plane = o3d.geometry.TriangleMesh.create_box(width=plane_length,
                                                 height=plane_width,
                                                 depth=0.001)
    plane.translate([min_bound[0], min_bound[1], plane_z])
    
    env_mesh += plane
    
    if(plotting==True):
        plane.paint_uniform_color([0.8, 0.1, 0.1])  # optional: red plane
        o3d.visualization.draw_geometries([env_mesh, object_of_interest])
    
    return env_mesh

def remove_object_with_shrunken_cylinder(
    mesh,
    object_of_interest,
    plotting=False,
    plane_adjustment=0.01,
    margin=0.1,
    shrink_xy_abs=0.015,   # 1.5 cm
    fallback_ratio=0.5,    # if too small, use 50%
    min_radius=0.005,
    min_height=0.01,
    cyl_resolution=24,
):
    """
    Remove region around object, add a shrunken cylinder proxy at object location.
    """
    aabb = object_of_interest.get_axis_aligned_bounding_box()
    min_bound = np.asarray(aabb.min_bound, dtype=float)
    max_bound = np.asarray(aabb.max_bound, dtype=float)

    # 1) Remove around object (same idea as remove_object)
    crop_min = min_bound - margin
    crop_max = max_bound + margin
    env_mesh = inverse_cropping(mesh=mesh, min_xyz=crop_min, max_xyz=crop_max)

    # Optional support plane (same as remove_object)
    plane_z = min_bound[2] - plane_adjustment
    plane = o3d.geometry.TriangleMesh.create_box(
        width=(crop_max[0] - crop_min[0]),
        height=(crop_max[1] - crop_min[1]),
        depth=0.001,
    )
    plane.translate([crop_min[0], crop_min[1], plane_z])
    env_mesh += plane

    # 2) Build shrunken XY cylinder proxy
    extent = max_bound - min_bound
    rx = 0.5 * extent[0]
    ry = 0.5 * extent[1]
    h = max(extent[2], min_height)

    rx_new = (rx - shrink_xy_abs) if (rx > 2.0 * shrink_xy_abs) else (rx * fallback_ratio)
    ry_new = (ry - shrink_xy_abs) if (ry > 2.0 * shrink_xy_abs) else (ry * fallback_ratio)
    radius = max(min(rx_new, ry_new), min_radius)

    cyl = o3d.geometry.TriangleMesh.create_cylinder(
        radius=radius, height=h, resolution=cyl_resolution
    )

    # move cylinder center to object AABB center
    target_center = aabb.get_center()
    cyl_center = cyl.get_axis_aligned_bounding_box().get_center()
    cyl.translate(target_center - cyl_center)

    env_mesh_withcyl = env_mesh + cyl

    if plotting:
        cyl.paint_uniform_color([0.1, 0.7, 0.1])
        plane.paint_uniform_color([0.8, 0.1, 0.1])
        o3d.visualization.draw_geometries([env_mesh, object_of_interest])

    return env_mesh_withcyl, env_mesh

def make_surface(z_height, area, color=[0.2, 0.8, 0.8], thickness=0.001):
    """
    Create a rectangular horizontal surface mesh at a given z-height.
    
    Args:
        z_height (float): Height of the plane along the z-axis.
        area (list or tuple): [x_min, x_max, y_min, y_max].
        color (list): RGB color of the surface (default: turquoise).
        thickness (float): Thickness of the plane for visibility (default: 1 mm).
    
    Returns:
        o3d.geometry.TriangleMesh: The surface mesh.
    """
    x_min, x_max, y_min, y_max = area

    # Define 8 vertices of a thin box
    vertices = np.array([
        [x_min, y_min, z_height - thickness/2],
        [x_max, y_min, z_height - thickness/2],
        [x_max, y_max, z_height - thickness/2],
        [x_min, y_max, z_height - thickness/2],
        [x_min, y_min, z_height + thickness/2],
        [x_max, y_min, z_height + thickness/2],
        [x_max, y_max, z_height + thickness/2],
        [x_min, y_max, z_height + thickness/2],
    ])

    # 12 triangles for a box
    triangles = np.array([
        [0, 1, 2], [0, 2, 3],   # bottom
        [4, 5, 6], [4, 6, 7],   # top
        [0, 1, 5], [0, 5, 4],   # front
        [1, 2, 6], [1, 6, 5],   # right
        [2, 3, 7], [2, 7, 6],   # back
        [3, 0, 4], [3, 4, 7],   # left
    ])

    # Create mesh
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(triangles)
    mesh.paint_uniform_color(color)
    mesh.compute_vertex_normals()
    
    return mesh


def remove_object_with_obb(
    mesh,
    object_of_interest,
    plotting=False,
    plane_adjustment=0.01,
    margin=0.1,                 # cropping only
    plane_size_xy=(0.8, 0.8),   # fixed plane size in meters
    min_height=0.01,
):
    """
    Remove region around object, then add back an unshrunk OBB proxy.
    Returns:
        env_mesh_withobb, env_mesh_without_proxy
    """
    # Use AABB for robust removal window
    aabb = object_of_interest.get_axis_aligned_bounding_box()
    min_bound = np.asarray(aabb.min_bound, dtype=float)
    max_bound = np.asarray(aabb.max_bound, dtype=float)

    crop_min = min_bound - margin
    crop_max = max_bound + margin
    env_mesh = inverse_cropping(mesh=mesh, min_xyz=crop_min, max_xyz=crop_max)

    # Optional support plane
    plane_z = min_bound[2] - plane_adjustment
    # plane = o3d.geometry.TriangleMesh.create_box(
    #     width=(crop_max[0] - crop_min[0]),
    #     height=(crop_max[1] - crop_min[1]),
    #     depth=0.001,
    # )
    plane_w, plane_h = plane_size_xy
    center_xy = 0.5 * (min_bound[:2] + max_bound[:2])
    plane_min_xy = center_xy - np.array([plane_w, plane_h]) / 2.0

    plane = o3d.geometry.TriangleMesh.create_box(
        width=plane_w,
        height=plane_h,
        depth=0.001,
    )
    #plane.translate([crop_min[0], crop_min[1], plane_z])
    plane.translate([plane_min_xy[0], plane_min_xy[1], plane_z])
    
    env_mesh += plane

    # Build unshrunk OBB proxy
    obb = object_of_interest.get_minimal_oriented_bounding_box()
    ext = np.asarray(obb.extent, dtype=float)  # full lengths [x, y, z]
    sx, sy, sz = ext[0], ext[1], max(ext[2], min_height)

    # Local box centered at origin
    obb_proxy = o3d.geometry.TriangleMesh.create_box(width=sx, height=sy, depth=sz)
    obb_proxy.translate([-sx / 2.0, -sy / 2.0, -sz / 2.0])

    # Orient/position like original OBB
    obb_proxy.rotate(np.asarray(obb.R, dtype=float), center=(0.0, 0.0, 0.0))
    obb_proxy.translate(np.asarray(obb.center, dtype=float))

    env_mesh_withobb = env_mesh + obb_proxy

    if plotting:
        obb_proxy.paint_uniform_color([0.1, 0.7, 0.1])
        plane.paint_uniform_color([0.8, 0.1, 0.1])
        o3d.visualization.draw_geometries([env_mesh_withobb, object_of_interest])

    return env_mesh_withobb, env_mesh, obb_proxy

# Example usage:
if __name__ == "__main__":
    object_area = [-0.4, 0.4, 0.1, 1.1]
    z_height = 0.73

    table_mesh = make_surface(z_height, object_area)
    frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1)

    o3d.visualization.draw_geometries(
        [table_mesh, frame],
        window_name="Surface at z=0.73",
        mesh_show_back_face=True,
    )
