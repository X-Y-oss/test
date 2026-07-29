import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from mpl_toolkits.mplot3d import Axes3D
#import table_edge_support as tes


def _ensure_numpy(x):
    """Ensures x is a (N, 3) numpy array. Handles Open3D PointClouds."""
    if isinstance(x, o3d.geometry.PointCloud):
        return np.asarray(x.points)
    x = np.asarray(x)
    return x

def sample_within_ellipse_2d(radius_x, radius_y, mean_x=0.0, mean_y=0.0, n_std=3, rng=None, std_scale=1.5):
    """
    Truncated Gaussian inside the ellipse centered at (mean_x, mean_y)
    with semi-axes (radius_x, radius_y). stds are radius/n_std.
    Returns a single (x, y) sample.
    """
    if radius_x <= 0 or radius_y <= 0:
        raise ValueError("radius_x and radius_y must be positive")
    if n_std <= 0:
        raise ValueError("n_std must be positive")

    rng = np.random.default_rng(rng)
    sx = (radius_x / n_std) * std_scale
    sy = (radius_y / n_std) * std_scale

    while True:
        x, y = rng.normal(loc=[mean_x, mean_y], scale=[sx, sy])
        if ((x - mean_x) / radius_x) ** 2 + ((y - mean_y) / radius_y) ** 2 <= 1.0:
            return x, y

def plot_support_polygon(ax, support_polygon, pointcloud):
    ax.clear()
    for simplex in support_polygon.simplices:
        simplex_points = support_polygon.points[simplex]
        ax.plot(simplex_points[:, 0], simplex_points[:, 1], np.min(pointcloud[:, 2]), 'b-', linewidth=1)  # Use ground Z
    plt.show()

    
def plot_stability(ax, pointcloud, middle_point, projected_middle_point, radius, support_polygons, sampled_com, stability_score, orientation_flag="", verbose=1):
    # clear old data
    ax.clear()
    
    # plot pointcloud TODO c = pointcloud[:,3] given value
    ax.scatter(pointcloud[:,0], pointcloud[:,1], pointcloud[:,2], marker='o', s=5, alpha=0.05)
    ax.scatter(middle_point[0], middle_point[1], middle_point[2], color='r', s=50, label="Center of Mass (CoM)")
    ax.scatter(*projected_middle_point, color='black', s=50, label="Projected CoM")
    
    normal_vector_end = [middle_point[0], middle_point[1], np.min(pointcloud[:,2])]
    ax.plot([middle_point[0], normal_vector_end[0]], [middle_point[1], normal_vector_end[1]], [middle_point[2], normal_vector_end[2]], color='g', lw=2, label="Normal Vector")
    
    # sampling sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x_sphere = middle_point[0] + radius[0] * np.outer(np.cos(u), np.sin(v))
    y_sphere = middle_point[1] + radius[1] * np.outer(np.sin(u), np.sin(v))
    ax.plot_surface(x_sphere, y_sphere, np.full_like(x_sphere, middle_point[2]), color='b', alpha=0.2)
    
    # Plot the support polygon in 3D by assuming all Z-values are on the ground plane
    for support_polygon in support_polygons:
        for simplex in support_polygon.simplices:
            simplex_points = support_polygon.points[simplex]
            ax.plot(simplex_points[:, 0], simplex_points[:, 1], np.min(pointcloud[:, 2]), 'b-', linewidth=1)  # Use ground Z
        
        
    #TODO sampled_com
    if(verbose>=1):
        for i in range(len(sampled_com)):
            ax.scatter(*sampled_com[i][0], color='orange', s=10, label="Gaussian sampled CoM" if i == 0 else "")
            ax.scatter(*sampled_com[i][1], color='gray' if sampled_com[i][2] else "red", s=10, label="Projected Gaussian CoM" if i == 0 else "")
    
    # TODO better generalization nessesary
    # ax.set_xlim([-0.15, 0.15])
    # ax.set_ylim([-0.15, 0.15])
    # ax.set_zlim([np.min(pointcloud[:,2]), 0.3])
    ax.set_xlim([-0.1, 0.1])
    ax.set_ylim([-0.1, 0.1])
    ax.set_zlim([np.min(pointcloud[:,2]), 0.2])
    # Labels
    # ax.set_xlabel("X Axis")
    # ax.set_ylabel("Y Axis")
    # ax.set_zlabel("Z Axis")
    # hide axes, grid, and background panes
    ax.set_axis_off()  # removes axes and ticks
    ax.grid(False)     # no grid lines
    ax.xaxis.pane.set_visible(False)
    ax.yaxis.pane.set_visible(False)
    ax.zaxis.pane.set_visible(False)
    
    leg = ax.legend(loc='upper left')
    for txt in leg.get_texts():
        txt.set_fontweight('bold')
    if orientation_flag == "":
        orientation_flag = ["I"]
    ax.set_title(f"Stability of orientation {orientation_flag[0]}: {stability_score}")

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
        return []
        raise ValueError("Not enough points to form a support polygon")

    return ConvexHull(ground_points[:, :2])

def project_com_to_ground(com, ground_plane):
    """
    Projects a center of mass onto the ground plane.

    Args:
        com (tuple): (x_c, y_c, z_c) - Center of Mass.
        ground_plane (tuple): (a, b, c, d) for ax + by + cz + d = 0.

    Returns:
        tuple: (x_p, y_p, 0) - Projected CoM.
    """
    a, b, c, d = ground_plane
    lambda_proj = (a * com[0] + b * com[1] + c * com[2] + d) / (a**2 + b**2 + c**2)
    x_p = com[0] - lambda_proj * a
    y_p = com[1] - lambda_proj * b
    return (x_p, y_p, 0)


def is_point_inside_convex_hull(hull, point):
    # Extract the half-space equations (A * x + b <= 0)
    A = hull.equations[:, :-1]
    b = hull.equations[:, -1]
    # Compute the dot product and check if it's less than or equal to zero
    return np.all(np.dot(A, point) + b <= 0)

def stability_sigmoid(p_in, k=15, c=0.7):
    """
    p_in : fraction inside [0,1]
    k    : slope of the logistic
    c    : center point where logistic=0.5
    """
    if p_in <= 0.5:
        return 0.0
    # logistic
    def sigma(x): return 1 / (1 + np.exp(-x))
    # normalize so that value=0 at 0.5 and value=1 at 1.0
    num = sigma(k*(p_in - c)) - sigma(k*(0.5 - c))
    den = sigma(k*(1.0 - c)) - sigma(k*(0.5 - c))
    return float(np.clip(num/den, 0, 1))



def compute_stability(pointcloud, n_samples=10, ground_threshold=0.02, compute_edge_evaluation=False): # Updated signature
        
    # ... (Keep all existing legacy code below) ...
    pointcloud = _ensure_numpy(pointcloud)
    # project z axis minimum on 0
    pointcloud[:, 2] -= np.min(pointcloud[:, 2])

    # Assume middle point is inside object. If this is not the case it would need to be projected
    middle_point = [np.mean(pointcloud[:,0]), np.mean(pointcloud[:,1]), np.mean(pointcloud[:,2])]
    
    # Take points close to middle point to build Convex Hull
    mask = np.abs(pointcloud[:,2] - middle_point[2]) < 0.02
    radius_calc = pointcloud[mask]
    
    # --- strip widths around the center in the *other* axis ---
    strip_half_width = 0.01  # +/- 1 cm; tune as needed
    tol = 1e-6
    cx, cy = middle_point[0], middle_point[1]

    # For x extent: only use points whose y is close to center (a vertical y-strip)
    mask_y_strip = np.abs(radius_calc[:, 1] - cy) <= strip_half_width
    if np.any(mask_y_strip):
        x_slice = radius_calc[mask_y_strip][:, 0]
        x_lo, x_hi = x_slice.min(), x_slice.max()
        # accept only if the strip extents straddle the center; else fallback
        if (x_lo < cx - tol) and (x_hi > cx + tol):
            x_min, x_max = x_lo, x_hi
        else:
            x_min, x_max = radius_calc[:, 0].min(), radius_calc[:, 0].max()
    else:
        # fallback: use all points in the z-slice
        x_min, x_max = radius_calc[:, 0].min(), radius_calc[:, 0].max()

    # For y extent: only use points whose x is close to center (a vertical x-strip)
    mask_x_strip = np.abs(radius_calc[:, 0] - cx) <= strip_half_width
    if np.any(mask_x_strip):
        y_slice = radius_calc[mask_x_strip][:, 1]
        y_lo, y_hi = y_slice.min(), y_slice.max()
        if (y_lo < cy - tol) and (y_hi > cy + tol):
            y_min, y_max = y_lo, y_hi
        else:
            y_min, y_max = radius_calc[:, 1].min(), radius_calc[:, 1].max()
    else:
        y_min, y_max = radius_calc[:, 1].min(), radius_calc[:, 1].max()

    x_radius = max(0.02, min(np.abs(x_min), np.abs(x_max)) - 0.01)
    y_radius = max(0.02, min(np.abs(y_min), np.abs(y_max)) - 0.01)
    radius = (x_radius, y_radius)
    
    # compute support polygon
    ground_plane = (0, 0, 1, 0)  # z=0 plane

    if(compute_edge_evaluation):
        support_polygons = tes.generater_table_edge(pointcloud, 0.094)
        print(len(support_polygons))
        #for s in support_polygons:
        #    fig = plt.figure(figsize=(16, 10))
        #    ax = fig.add_subplot(111, projection='3d')
        #    plot_support_polygon(ax, s, pointcloud)
    else:
        support_polygons = [compute_support_polygon(pointcloud, ground_plane, True, threshold=ground_threshold)]
    
    if(support_polygons[0] == []):
        print("No support polygon found")
        return 0.0, None, None

    print(f"Number of support polygons: {len(support_polygons)}")
    stability = []
    for support_polygon in support_polygons:
        # project middle point
        projected_middle_point = project_com_to_ground(middle_point, ground_plane)

        sampled_com = []
        outside = 0
        print(f"MEAN: x: {middle_point[0]} y: {middle_point[1]}")
        for i in range(n_samples):
            dx, dy = sample_within_ellipse_2d(radius_x=x_radius,radius_y=y_radius,mean_x=middle_point[0], mean_y=middle_point[1],n_std=3)
            #dx, dy = sample_within_radius_2d(radius, mean, std_dev)
            com_gauss = (dx, dy, middle_point[2])
            projected_com = project_com_to_ground((dx, dy, middle_point[2]), ground_plane)

            flag = is_point_inside_convex_hull(support_polygon, projected_com[:2])
            
            if not flag: outside+=1
            
            sampled_com.append((com_gauss, projected_com, flag))
        
        #stability_ = 1 - (outside/n_samples)
        p_in = (n_samples - outside) / max(1.0, n_samples)       # fraction inside
        print(f"Fraction inside: {p_in}")
        stability.append(stability_sigmoid(p_in)) #max(0.0, min(1.0, (p_in - 0.5) / 0.5))
        
    return stability, (middle_point, projected_middle_point, radius, support_polygons, sampled_com)