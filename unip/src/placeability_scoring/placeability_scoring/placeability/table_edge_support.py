from scipy.spatial import ConvexHull
import numpy as np
import open3d as o3d

def compute_support_polygon(point_cloud, ground_plane, just_z = True, threshold=0.01):
    """
    Computes the support polygon (convex hull) from ground-contact points.
    
    Args:
        point_cloud (numpy array): Nx3 array of (x, y, z) points.
        ground_plane (tuple): (a, b, c, d) for ax + by + cz + d = 0.

    Returns:
        ConvexHull: Convex hull of the support polygon.
    """
    if(just_z):
        ground_points = point_cloud[np.abs(point_cloud[:, 2]) < threshold]
        
    else:
        a, b, c, d = ground_plane  # Ground plane equation

        # Filter points that are close to the ground plane
        ground_points = point_cloud[np.abs(a * point_cloud[:, 0] + b * point_cloud[:, 1] + c * point_cloud[:, 2] + d) < threshold]

    # Convex hull of (x, y) points
    print(ground_points.shape[0])
    if ground_points.shape[0] < 3:
        raise ValueError("Not enough points to form a support polygon")

    return ConvexHull(ground_points[:, :2]), ground_points

def convex_hull_polygon(points_xy):
    """
    Return convex polygon (k,2) of the hull of points_xy. If <3 points, returns input.
    """
    pts = np.asarray(points_xy, dtype=np.float64)
    if pts.shape[0] < 3:
        return pts
    try:
        H = ConvexHull(pts)
        return pts[H.vertices]
    except Exception:
        return pts


def clip_polygon_to_aabb(poly_xy, x_min, x_max, y_min, y_max):
    """
    poly_xy: (N,2) polygon vertices in order (not necessarily closed).
    Returns (M,2) clipped polygon (may be empty).
    """
    if len(poly_xy) == 0:
        return np.empty((0,2))
    def inside_left(p):  return p[0] >= x_min
    def inside_right(p): return p[0] <= x_max
    def inside_bottom(p):return p[1] >= y_min
    def inside_top(p):   return p[1] <= y_max

    def intersect(p1, p2, edge):
        x1,y1 = p1; x2,y2 = p2
        if edge == 'left':   xE = x_min; t = (xE - x1)/(x2 - x1); return np.array([xE, y1 + t*(y2 - y1)])
        if edge == 'right':  xE = x_max; t = (xE - x1)/(x2 - x1); return np.array([xE, y1 + t*(y2 - y1)])
        if edge == 'bottom': yE = y_min; t = (yE - y1)/(y2 - y1); return np.array([x1 + t*(x2 - x1), yE])
        if edge == 'top':    yE = y_max; t = (yE - y1)/(y2 - y1); return np.array([x1 + t*(x2 - x1), yE])

    def clip_against(edge, keep_fn, pts):
        if len(pts) == 0: 
            return []
        res = []
        S = pts[-1]
        for E in pts:
            Ein, Sin = keep_fn(E), keep_fn(S)
            if Ein and Sin:            # in->in
                res.append(E)
            elif not Ein and Sin:      # in->out
                res.append(intersect(S, E, edge))
            elif Ein and not Sin:      # out->in
                res.append(intersect(S, E, edge))
                res.append(E)
            S = E
        return res

    out = list(map(np.asarray, poly_xy.tolist()))
    for edge, fn in [('left',inside_left), ('right',inside_right),
                     ('bottom',inside_bottom), ('top',inside_top)]:
        out = clip_against(edge, fn, out)
        if len(out) == 0:
            break
    return np.array(out, dtype=np.float64)


def support_polygon_over_boxes(hull_xy, rects):
    """
    hull_xy: (N,2) convex polygon of object's bottom footprint (in XY at support plane).
    rects: list of axis-aligned rectangles, each as (x_min,x_max,y_min,y_max)
    Returns:
      patches: list of clipped polygons (each (Mi,2))
      support_xy: (K,2) convex hull of the union of all patches' vertices (may be empty/degenerate)
    """
    patches = []
    verts = []
    for (x_min,x_max,y_min,y_max) in rects:
        clipped = clip_polygon_to_aabb(hull_xy, x_min, x_max, y_min, y_max)
        if len(clipped) > 0:
            patches.append(clipped)
            verts.append(clipped)
    if len(verts) == 0:
        return patches, np.empty((0,2))
    union_pts = np.vstack(verts)
    # Optionally, dedupe nearly-equal points to help Qhull
    if union_pts.shape[0] > 1:
        union_pts = np.unique(np.round(union_pts, decimals=8), axis=0)
    support_xy = convex_hull_polygon(union_pts)
    return patches, support_xy


def aabb_from_support_hull(support_hull: ConvexHull, ground_points_xy: np.ndarray):
    """
    support_hull: ConvexHull built on ground_points_xy (shape (N,2))
    ground_points_xy: the 2D points used to build the hull (shape (N,2))
    """
    hull_xy = ground_points_xy[support_hull.vertices]      # ordered polygon (K,2)
    xmin, ymin = hull_xy.min(axis=0)
    xmax, ymax = hull_xy.max(axis=0)
    return (xmin, xmax, ymin, ymax), hull_xy


def make_box(center, size_xy, thickness, color=(0.2, 0.2, 0.2)):
    w,h = size_xy
    mesh = o3d.geometry.TriangleMesh.create_box(width=w, height=h, depth=thickness)
    mesh.translate(center - np.array([w/2, h/2, thickness/2]))
    mesh.compute_vertex_normals()
    mesh.paint_uniform_color(color)
    # rectangle bounds (top face) for clipping:
    x_min = center[0] - w/2
    x_max = center[0] + w/2
    y_min = center[1] - h/2
    y_max = center[1] + h/2
    return mesh, (x_min, x_max, y_min, y_max)


def generater_table_edge(pointcloud, object_length_x_axis, percentage_shift=1, ground_threshold=0.002):
    # Environment "platform" box (we will shift it in +x)

    ground_plane = (0, 0, 1, 0)  # z=0 plane
    support_polygon, ground_points = compute_support_polygon(
        pointcloud, ground_plane, just_z=True, threshold=ground_threshold
    )

    pts_xy = ground_points[:, :2]
    hull_xy = pts_xy[support_polygon.vertices]
    (rect_xmin, rect_xmax, rect_ymin, rect_ymax), hull_xy = aabb_from_support_hull(support_polygon, pts_xy)

    thickness = 0.05
    w = rect_xmax - rect_xmin
    h = rect_ymax - rect_ymin
    center = np.array([(rect_xmin + rect_xmax) / 2.0,
                       (rect_ymin + rect_ymax) / 2.0,
                       -thickness / 2.0], dtype=np.float64)

    stability_list = []
    percentage_shifted = []
    percentage_in = []
    new_support_polygones = []

    for x_shifts in range(0, 101, percentage_shift):
        percentage_shifted.append(x_shifts)

        boxA, rectA = make_box(center, (w, h), thickness)
        curr_x_shift = object_length_x_axis * (x_shifts / 100.0)


        T = np.eye(4)
        T[:3, 3] = [curr_x_shift, 0.0, 0.0]
        boxA.transform(T)

        tx, ty, tz = T[:3, 3]
        xmin, xmax, ymin, ymax = rectA
        rectA = (xmin + tx, xmax + tx, ymin + ty, ymax + ty)

        # Clip support hull against shifted platform rectangle
        patches, support_xy = support_polygon_over_boxes(hull_xy, [rectA])
        if support_xy.shape[0] >= 3:
            new_support_polygones.append(ConvexHull(support_xy))
    return new_support_polygones