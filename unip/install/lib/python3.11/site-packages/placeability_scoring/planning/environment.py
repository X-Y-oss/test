import numpy as np
import open3d as o3d


DEFAULT_MIN_BOUND = (-1.23, -0.5, 1.06)
DEFAULT_MAX_BOUND = (-0.8, 0.26, 1.35)


def build_bbox_planes_for_cropped(
    aabb,
    pad_xy: float = 0.0,
    pad_z: float = 0.03,
    thickness: float = 0.01,
    top_extension: float = 0.5,
    bottom_extension: float = 0.0,
    faces=("top", "bottom", "xmin", "xmax", "ymin", "ymax"),
    color_map=None,
    inside_touch: bool = True,
):
    """
    Returns:
      planes: dict(face -> o3d.geometry.TriangleMesh)
      plane_equations: dict(face -> (n, d)) with n a 3-vector, d a scalar in n·x + d = 0
      cb: the AxisAlignedBoundingBox used
    """
    cb = aabb
    mn = cb.get_min_bound()
    mx = cb.get_max_bound()

    x0, y0, z0 = mn[0] - pad_xy, mn[1] - pad_xy, mn[2] - pad_z
    x1, y1, z1 = mx[0] + pad_xy, mx[1] + pad_xy, mx[2] + pad_z
    width_x = max(0.0, x1 - x0)
    depth_y = max(0.0, y1 - y0)
    height_z = max(0.0, z1 - z0)

    if color_map is None:
        color_map = {
            "top": (0.90, 0.90, 0.90),
            "bottom": (0.85, 0.85, 0.85),
            "xmin": (0.90, 0.70, 0.70),
            "xmax": (0.70, 0.90, 0.70),
            "ymin": (0.70, 0.70, 0.90),
            "ymax": (0.90, 0.90, 0.70),
        }

    planes = {}
    plane_equations = {}

    def add_plane(face, mesh, color, normal, point_on_plane):
        mesh.compute_vertex_normals()
        mesh.paint_uniform_color(color)
        planes[face] = mesh
        n = np.asarray(normal, dtype=float)
        p0 = np.asarray(point_on_plane, dtype=float)
        d = -float(n @ p0)
        plane_equations[face] = (n, d)

    if "top" in faces:
        z_base = (z1 - thickness) if inside_touch else z1
        top_depth = thickness + max(0.0, float(top_extension))
        plane = o3d.geometry.TriangleMesh.create_box(
            width=width_x, height=depth_y, depth=top_depth
        )
        plane.translate([x0, y0, z_base])
        add_plane("top", plane, color_map["top"], normal=(0, 0, 1), point_on_plane=(x0, y0, z1))

    if "bottom" in faces:
        bottom_depth = thickness + max(0.0, float(bottom_extension))
        # For inside_touch, keep the inner (top) face at z0 and extend downward.
        # For outside_touch, keep the outer (bottom) face at z0 and extend upward.
        z_base = (z0 - bottom_depth) if inside_touch else z0
        plane = o3d.geometry.TriangleMesh.create_box(width=width_x, height=depth_y, depth=bottom_depth)
        plane.translate([x0, y0, z_base])
        add_plane("bottom", plane, color_map["bottom"], normal=(0, 0, -1), point_on_plane=(x0, y0, z0))

    if "xmin" in faces:
        x_base = (x0 - thickness) if inside_touch else x0
        plane = o3d.geometry.TriangleMesh.create_box(width=thickness, height=depth_y, depth=height_z)
        plane.translate([x_base, y0, z0])
        add_plane("xmin", plane, color_map["xmin"], normal=(-1, 0, 0), point_on_plane=(x0, y0, z0))

    if "xmax" in faces:
        x_base = x1 if inside_touch else (x1 - thickness)
        plane = o3d.geometry.TriangleMesh.create_box(width=thickness, height=depth_y, depth=height_z)
        plane.translate([x_base, y0, z0])
        add_plane("xmax", plane, color_map["xmax"], normal=(1, 0, 0), point_on_plane=(x1, y0, z0))

    if "ymin" in faces:
        y_base = (y0 - thickness) if inside_touch else y0
        plane = o3d.geometry.TriangleMesh.create_box(width=width_x, height=thickness, depth=height_z)
        plane.translate([x0, y_base, z0])
        add_plane("ymin", plane, color_map["ymin"], normal=(0, -1, 0), point_on_plane=(x0, y0, z0))

    if "ymax" in faces:
        y_base = y1 if inside_touch else (y1 - thickness)
        plane = o3d.geometry.TriangleMesh.create_box(width=width_x, height=thickness, depth=height_z)
        plane.translate([x0, y_base, z0])
        add_plane("ymax", plane, color_map["ymax"], normal=(0, 1, 0), point_on_plane=(x0, y1, z0))

    return planes, plane_equations, cb

def merge_meshes(mesh_list, weld=True, recompute_normals=True):
    if not mesh_list:
        raise ValueError("merge_meshes: empty list")
    v_all, f_all, c_all = [], [], []
    v_ofs = 0
    for m in mesh_list:
        if(m is None): continue
        v = np.asarray(m.vertices)
        f = np.asarray(m.triangles)
        v_all.append(v)
        f_all.append(f + v_ofs)
        v_ofs += v.shape[0]
        if m.has_vertex_colors():
            c_all.append(np.asarray(m.vertex_colors))
    out = o3d.geometry.TriangleMesh()
    out.vertices = o3d.utility.Vector3dVector(np.vstack(v_all))
    out.triangles = o3d.utility.Vector3iVector(np.vstack(f_all))
    if c_all:
        out.vertex_colors = o3d.utility.Vector3dVector(np.vstack(c_all))
    if weld:
        out.remove_duplicated_vertices()
        out.remove_degenerate_triangles()
        out.remove_duplicated_triangles()
        out.remove_unreferenced_vertices()
    if recompute_normals:
        out.compute_vertex_normals()
    return out

def make_bin(top_extension=0.5, 
             bottom_extension=0.0, 
             filled_mesh=None,
             min_bound = np.array([-1.08, -0.39, 1.03]), # (x_min, y_min, z_min)
             max_bound = np.array([-0.67,  0.36,  1.37]),   # (x_max, y_max, z_max)
             min_bound_notop=None,
             max_bound_notop=None,
             ):
    min_bound = np.asarray(min_bound, dtype=float).reshape(3)
    max_bound = np.asarray(max_bound, dtype=float).reshape(3)
    if min_bound_notop is None:
        min_bound_notop = min_bound
    else:
        min_bound_notop = np.asarray(min_bound_notop, dtype=float).reshape(3)
    if max_bound_notop is None:
        max_bound_notop = max_bound
    else:
        max_bound_notop = np.asarray(max_bound_notop, dtype=float).reshape(3)

    aabb = o3d.geometry.AxisAlignedBoundingBox(min_bound, max_bound)
    planes, _, _ = build_bbox_planes_for_cropped(
        aabb=aabb,
        pad_xy=0.0,
        pad_z=0.0,
        thickness=0.03,
        top_extension=top_extension,
        bottom_extension=bottom_extension,
        faces=("bottom", "xmin", "xmax", "ymin", "ymax"),
        inside_touch=True,
    )
    bin_mesh = merge_meshes(
        [
            filled_mesh,
            planes["bottom"],
            planes["xmin"],
            planes["xmax"],
            planes["ymin"],
            planes["ymax"],
        ]
    )

    aabb_notop = o3d.geometry.AxisAlignedBoundingBox(min_bound_notop, max_bound_notop)
    planes_notop, _, _ = build_bbox_planes_for_cropped(
        aabb=aabb_notop,
        pad_xy=0.0,
        pad_z=0.0,
        thickness=0.03,
        top_extension=top_extension,
        bottom_extension=bottom_extension,
        faces=("bottom", "xmin", "xmax", "ymin", "ymax"),
        inside_touch=True,
    )

    filled_mesh_notop = filled_mesh
    if filled_mesh is not None and (
        np.any(min_bound_notop != min_bound) or np.any(max_bound_notop != max_bound)
    ):
        filled_mesh_notop = filled_mesh.crop(aabb_notop)

    bin_mesh_notop = merge_meshes(
        [
            filled_mesh_notop,
            planes_notop["bottom"],
            planes_notop["xmin"],
            planes_notop["xmax"],
            planes_notop["ymin"],
            planes_notop["ymax"],
        ]
    )

    return bin_mesh, bin_mesh_notop

def make_shelf(top_extension=0.5, 
               bottom_extension=0.0, 
               filled_mesh=None,
               min_bound = np.array([-1.08, -0.39, 1.03]), # (x_min, y_min, z_min)
               max_bound = np.array([-0.67,  0.36,  1.37]),   # (x_max, y_max, z_max)
               min_bound_notop=None,
               max_bound_notop=None,
               ):
      
    min_bound = np.asarray(min_bound, dtype=float).reshape(3)
    max_bound = np.asarray(max_bound, dtype=float).reshape(3)
    if min_bound_notop is None:
        min_bound_notop = min_bound
    else:
        min_bound_notop = np.asarray(min_bound_notop, dtype=float).reshape(3)
    if max_bound_notop is None:
        max_bound_notop = max_bound
    else:
        max_bound_notop = np.asarray(max_bound_notop, dtype=float).reshape(3)

    aabb = o3d.geometry.AxisAlignedBoundingBox(min_bound, max_bound)
    planes, _, _ = build_bbox_planes_for_cropped(
        aabb=aabb,
        pad_xy=0.0,
        pad_z=0.0,
        thickness=0.03,
        top_extension=top_extension,
        bottom_extension=bottom_extension,
        faces=("top", "bottom", "xmin", "xmax", "ymin", "ymax"),
        inside_touch=True,
    )
    shelf_mesh = merge_meshes(
        [
            filled_mesh,
            planes["top"],
            planes["bottom"],
            planes["xmin"],
            planes["ymin"],
            planes["ymax"],
        ]
    )

    aabb_notop = o3d.geometry.AxisAlignedBoundingBox(min_bound_notop, max_bound_notop)
    planes_notop, _, _ = build_bbox_planes_for_cropped(
        aabb=aabb_notop,
        pad_xy=0.0,
        pad_z=0.0,
        thickness=0.03,
        top_extension=top_extension,
        bottom_extension=bottom_extension,
        faces=("bottom", "xmin", "ymin", "ymax"),
        inside_touch=True,
    )

    filled_mesh_notop = filled_mesh
    if filled_mesh is not None and (
        np.any(min_bound_notop != min_bound) or np.any(max_bound_notop != max_bound)
    ):
        filled_mesh_notop = filled_mesh.crop(aabb_notop)

    shelf_mesh_notop = merge_meshes(
        [
            filled_mesh_notop,
            planes_notop["bottom"],
            planes_notop["xmin"],
            planes_notop["ymin"],
            planes_notop["ymax"],
        ]
    )
    
    return shelf_mesh, shelf_mesh_notop


def _to_aabb(bounding_box):
    if isinstance(bounding_box, o3d.geometry.AxisAlignedBoundingBox):
        return bounding_box

    if isinstance(bounding_box, o3d.geometry.OrientedBoundingBox):
        return bounding_box.get_axis_aligned_bounding_box()

    if isinstance(bounding_box, dict):
        if "min_bound" in bounding_box and "max_bound" in bounding_box:
            min_bound = np.asarray(bounding_box["min_bound"], dtype=float).reshape(3)
            max_bound = np.asarray(bounding_box["max_bound"], dtype=float).reshape(3)
            return o3d.geometry.AxisAlignedBoundingBox(min_bound, max_bound)
        if "min" in bounding_box and "max" in bounding_box:
            min_bound = np.asarray(bounding_box["min"], dtype=float).reshape(3)
            max_bound = np.asarray(bounding_box["max"], dtype=float).reshape(3)
            return o3d.geometry.AxisAlignedBoundingBox(min_bound, max_bound)
        raise ValueError(
            "bounding_box dict must contain ('min_bound','max_bound') or ('min','max')."
        )

    arr = np.asarray(bounding_box, dtype=float)
    if arr.shape == (2, 3):
        return o3d.geometry.AxisAlignedBoundingBox(arr[0], arr[1])
    if arr.shape == (6,):
        return o3d.geometry.AxisAlignedBoundingBox(arr[:3], arr[3:])

    raise ValueError(
        "bounding_box must be an Open3D bounding box, a dict with min/max, "
        "shape (2,3), or shape (6,)."
    )


def make_table(
    bounding_box,
    filled_mesh=None,
    thickness=0.02,
    top_extension=0.0,
    bottom_extension=0.0,
    faces=("top", "bottom", "xmin", "xmax", "ymin", "ymax"),
    inside_touch=True,
):
    """
    Build a closed table shell from a bounding box.

    Args:
        bounding_box:
            - o3d.geometry.AxisAlignedBoundingBox or OrientedBoundingBox
            - dict with {'min_bound','max_bound'} or {'min','max'}
            - array-like with shape (2,3): [[xmin,ymin,zmin],[xmax,ymax,zmax]]
            - array-like with shape (6,): [xmin,ymin,zmin,xmax,ymax,zmax]
        filled_mesh:
            Optional mesh to merge into the generated table shell.
    Returns:
        table_mesh, planes, plane_equations, aabb
    """
    aabb = _to_aabb(bounding_box)

    planes, plane_equations, _ = build_bbox_planes_for_cropped(
        aabb=aabb,
        pad_xy=0.0,
        pad_z=0.0,
        thickness=thickness,
        top_extension=top_extension,
        bottom_extension=bottom_extension,
        faces=faces,
        inside_touch=inside_touch,
    )

    #ordered_faces = [f for f in ("top", "bottom", "xmin", "xmax", "ymin", "ymax") if f in planes]
    ordered_faces = [f for f in ("top",) if f in planes]
    table_mesh = merge_meshes([filled_mesh] + [planes[f] for f in ordered_faces])
    table_mesh_noobj = merge_meshes([planes[f] for f in ordered_faces])
    return table_mesh, table_mesh_noobj


if __name__ == "__main__":
    table_bbox = np.array(
        [
            [-2.0, -2.0, -0.02],
            [2.0, 2.0, 0.0],
        ],
        dtype=float,
    )
    table_mesh, table_planes, table_plane_equations, table_aabb = make_table(
        bounding_box=table_bbox,
        thickness=0.02,
    )
    shelf_mesh, _ = make_shelf(
        top_extension=0.5,
        bottom_extension=0.5
    )
    print("Table vertices:", np.asarray(table_mesh.vertices).shape[0])
    print("Table triangles:", np.asarray(table_mesh.triangles).shape[0])
    print("Table AABB min:", table_aabb.get_min_bound())
    print("Table AABB max:", table_aabb.get_max_bound())
    print("Table faces:", list(table_planes.keys()))
    print("Table plane equations:", {k: (v[0].tolist(), v[1]) for k, v in table_plane_equations.items()})
    print("Shelf vertices:", np.asarray(shelf_mesh.vertices).shape[0])
    print("Shelf triangles:", np.asarray(shelf_mesh.triangles).shape[0])
    world = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.5)
    o3d.visualization.draw_geometries([world, table_mesh, shelf_mesh])
