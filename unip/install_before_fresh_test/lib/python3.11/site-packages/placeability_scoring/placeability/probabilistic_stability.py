import numpy as np
import open3d as o3d
import numpy as np
import open3d as o3d
from scipy.spatial import ConvexHull
from mpl_toolkits.mplot3d import Axes3D

def _ensure_numpy(x):
    """Ensures x is a (N, 3) numpy array. Handles Open3D PointClouds."""
    if isinstance(x, o3d.geometry.PointCloud):
        return np.asarray(x.points)
    x = np.asarray(x)
    return x



def conf_uncertainty_voxels(pcds, voxel=0.005, downsample=True):
    """
    pcds: list[o3d.geometry.PointCloud], already aligned
    voxel: voxel size in meters

    returns:
      centers (K,3) float64  voxel centers
      conf    (K,)  float64  occupancy frequency in [0,1]
      sigma   (K,)  float64  positional uncertainty per voxel (sqrt(trace(cov)))
    """
    M = len(pcds)
    vox = {}  # (ix,iy,iz) -> [count_frames_seen, pts_list, last_seen_frame]

    for fi, pcd in enumerate(pcds):
        if downsample:
            pcd = pcd.voxel_down_sample(voxel)
        pts = np.asarray(pcd.points)  # (N,3)

        keys = np.floor(pts / voxel).astype(np.int64)
        for k, p in zip(map(tuple, keys), pts):
            v = vox.get(k)
            if v is None:
                # frames_seen, pts, last_seen
                vox[k] = [1, [p], fi]
            else:
                # count frame once
                if v[2] != fi:
                    v[0] += 1
                    v[2] = fi
                v[1].append(p)

    K = len(vox)
    centers = np.empty((K, 3), np.float64)
    conf    = np.empty((K,), np.float64)
    sigma   = np.empty((K,), np.float64)

    for j, (k, (frames_seen, pts_list, _)) in enumerate(vox.items()):
        centers[j] = (np.array(k, np.float64) + 0.5) * voxel
        conf[j] = frames_seen / M
        pts = np.asarray(pts_list, np.float64)
        if len(pts) < 2:
            sigma[j] = 0.0
        else:
            C = np.cov(pts.T)              # 3x3
            sigma[j] = np.sqrt(np.trace(C))

    return centers, conf, sigma

def voxel_stats_to_point_uncertainty(
    centers: np.ndarray,
    conf: np.ndarray,
    sigma: np.ndarray,
    *,
    voxel: float = 0.005,
    alpha: float = 2.0,
    conf_min: float = 0.0,
    sigma0: float | None = None,
    w_max: float | None = None,
    eps: float = 1e-12,
):
    """
    Convert voxel agreement stats (from conf_uncertainty_voxels) into
    per-"point" (voxel center) variances and weights suitable for CoM estimation.

    Args:
        centers: (K,3) voxel centers.
        conf:    (K,)  occupancy frequency in [0,1].
        sigma:   (K,)  positional spread per voxel (sqrt(trace(cov))).
        voxel: voxel size used to generate centers.
        alpha: exponent for confidence; higher -> more aggressive downweighting of low conf.
        conf_min: discard voxels with conf < conf_min.
        sigma0: base positional noise floor. Default: voxel/2.
        w_max: optional cap on weights to prevent domination by a few voxels.
        eps: numerical stability.

    Returns:
        centers_f: (Kf,3) filtered centers
        variances: (Kf,)  isotropic variance per center (sigma_eff^2)
        weights:   (Kf,)  reliability weights (used in weighted average)
        conf_f:    (Kf,)  filtered conf (useful for debugging)
        sigma_f:   (Kf,)  filtered sigma (useful for debugging)
    """

    centers = np.asarray(centers, dtype=np.float64)
    conf = np.asarray(conf, dtype=np.float64).reshape(-1)
    sigma = np.asarray(sigma, dtype=np.float64).reshape(-1)

    if centers.ndim != 2 or centers.shape[1] != 3:
        raise ValueError(f"centers must be (K,3), got {centers.shape}")
    if conf.shape[0] != centers.shape[0] or sigma.shape[0] != centers.shape[0]:
        raise ValueError("centers/conf/sigma must have the same length")

    if sigma0 is None:
        sigma0 = 0.5 * float(voxel)

    # Filter by confidence
    mask = conf >= conf_min
    centers_f = centers[mask]
    conf_f = conf[mask]
    sigma_f = sigma[mask]

    if centers_f.shape[0] == 0:
        # Return empty arrays; caller should handle fallback.
        return centers_f, np.array([]), np.array([]), conf_f, sigma_f

    # Effective isotropic variance for each voxel center
    # sigma is already sqrt(trace(C)), so treat it as a length-scale of spread;
    # make it a variance and add a floor.
    sigma_eff = np.maximum(0.0, sigma_f)
    var = sigma_eff**2 + sigma0**2

    # Reliability weights:
    # - increase with agreement conf
    # - decrease with uncertainty var
    w = (np.maximum(conf_f, 0.0) ** alpha) / (var + eps)

    if w_max is not None:
        w = np.minimum(w, float(w_max))

    return centers_f, var, w, conf_f, sigma_f



def estimate_com_distribution_from_voxels(
    centers: np.ndarray,
    variances: np.ndarray,
    weights: np.ndarray,
    *,
    lambda_geom: float = 1.0,
    min_sum_w: float = 1e-12,
):
    """
    Estimate CoM Gaussian (mu_com, Sigma_com) from voxel centers with per-voxel
    isotropic variances + reliability weights.

    This decomposes uncertainty into:
      1) localization/measurement term (error of the weighted mean)
      2) geometric/completion-disagreement term (weighted covariance of centers)

    Args:
        centers: (K,3) voxel centers.
        variances: (K,) isotropic variance per center.
        weights: (K,) reliability weights.
        lambda_geom: scaling for geometric covariance term.
        min_sum_w: fallback threshold.

    Returns:
        mu_com: (3,)
        Sigma_com: (3,3)
    """
    centers = np.asarray(centers, dtype=np.float64)
    variances = np.asarray(variances, dtype=np.float64).reshape(-1)
    weights = np.asarray(weights, dtype=np.float64).reshape(-1)

    if centers.ndim != 2 or centers.shape[1] != 3:
        raise ValueError(f"centers must be (K,3), got {centers.shape}")
    if variances.shape[0] != centers.shape[0] or weights.shape[0] != centers.shape[0]:
        raise ValueError("centers/variances/weights must have same length")

    sum_w = float(np.sum(weights))
    if not np.isfinite(sum_w) or sum_w < min_sum_w:
        # conservative fallback
        mu = np.mean(centers, axis=0) if centers.shape[0] else np.zeros(3)
        return mu, np.eye(3) * 1e-3

    # Weighted mean
    mu = np.average(centers, axis=0, weights=weights)

    # 1) Localization / measurement term (error of weighted mean)
    # Var(mu) = sum( (w_i/sum_w)^2 * Var_i )
    norm_w = weights / sum_w
    combined_var = float(np.sum((norm_w**2) * variances))
    Sigma_loc = np.eye(3) * combined_var

    # 2) Geometric / disagreement term (weighted covariance of centers)
    diff = centers - mu[None, :]
    # weighted second moment: sum(w_i * diff_i diff_i^T) / sum_w
    Sigma_geom = (diff.T * weights) @ diff / sum_w

    Sigma = Sigma_loc + float(lambda_geom) * Sigma_geom
    return mu, Sigma


def estimate_com_from_completion_voxels(
    centers: np.ndarray,
    conf: np.ndarray,
    sigma: np.ndarray,
    *,
    voxel: float = 0.005,
    alpha: float = 2.0,
    conf_min: float = 0.2,
    sigma0: float | None = None,
    w_max: float | None = None,
    lambda_geom: float = 1.0,
):
    """
    End-to-end CoM estimator from voxel confidence stats.

    Args:
        centers/conf/sigma: output of conf_uncertainty_voxels(...)
        voxel: voxel size
        alpha/conf_min/sigma0/w_max: weighting controls
        lambda_geom: scales geometric covariance term

    Returns:
        mu_com: (3,)
        Sigma_com: (3,3)
        aux: dict of debug info (filtered counts, etc.)
    """
    centers_f, var, w, conf_f, sigma_f = voxel_stats_to_point_uncertainty(
        centers, conf, sigma,
        voxel=voxel, alpha=alpha, conf_min=conf_min, sigma0=sigma0, w_max=w_max
    )

    if centers_f.shape[0] < 3:
        # fallback to unfiltered or trivial
        mu = np.mean(centers, axis=0) if len(centers) else np.zeros(3)
        Sigma = np.eye(3) * 1e-3
        aux = {
            "n_voxels": int(len(centers)),
            "n_used": int(centers_f.shape[0]),
            "fallback": True,
        }
        return mu, Sigma, aux

    mu, Sigma = estimate_com_distribution_from_voxels(
        centers_f, var, w, lambda_geom=lambda_geom
    )

    aux = {
        "n_voxels": int(len(centers)),
        "n_used": int(centers_f.shape[0]),
        "conf_min": float(conf_min),
        "alpha": float(alpha),
        "lambda_geom": float(lambda_geom),
        "mean_conf_used": float(np.mean(conf_f)) if len(conf_f) else 0.0,
        "mean_sigma_used": float(np.mean(sigma_f)) if len(sigma_f) else 0.0,
        "fallback": False,
    }
    return mu, Sigma, aux


def get_point_uncertainty(points, weights=None, config=None):
    """
    Extracts or computes uncertainty (variance) for each point.

    Args:
        points (np.ndarray): Nx3 array of points.
        weights (np.ndarray, optional): Nx1 array of TSDF weights/confidence.
        config (dict, optional): Configuration dictionary. 
            - 'min_variance': Minimum variance to avoid division by zero (default: 1e-6).
            - 'default_variance': Variance to use if weights are missing (default: 0.001).
            - 'weight_scale': Scalar to scale weights before inversion (default: 1.0).

    Returns:
        tuple:
            - variances (np.ndarray): Nx1 array of variances (sigma^2).
            - weights (np.ndarray): Nx1 array of weights used for averaging (1/sigma^2).
    """
    if config is None:
        config = {}
    
    min_var = config.get('min_variance', 1e-6)
    default_var = config.get('default_variance', 0.001)
    epsilon = 1e-6

    if weights is not None:
        # TSDF weights are typically "confidence" or "count".
        # We model variance as inversely proportional to weight.
        # sigma^2 = 1 / (w + epsilon)
        
        # Ensure weights are positive and flat
        w = np.maximum(weights.flatten(), 0)
        
        # Calculate variance
        variances = 1.0 / (w + epsilon)
        
        # Clip variance to be sane
        variances = np.maximum(variances, min_var)
        
        # Recalculate weights from variances for consistency in downstream math
        # w_out = 1 / sigma^2
        out_weights = 1.0 / variances
        
    else:
        # Fallback to uniform uncertainty
        points = _ensure_numpy(points)
        N = points.shape[0]
        variances = np.full(N, default_var)
        out_weights = np.full(N, 1.0 / default_var)

    return variances, out_weights

def estimate_com_distribution(points, variances, weights, config=None):
    """
    Estimates the Center of Mass distribution (Mean and Covariance).
    
    Can combine "Measurement Uncertainty" (error of the mean, usually small)
    with "Geometric Uncertainty" (unknown mass distribution, usually large).

    Args:
        points (np.ndarray): Nx3 array of point coordinates.
        variances (np.ndarray): Nx1 array of point variances (isotropic assumption).
        weights (np.ndarray): Nx1 array of weights (1/variance).
        config (dict, optional): 
            - 'com_method': 'measurement' (default) or 'hybrid'
            - 'com_geo_scale': scaling factor for geometric sigma (default 1.0)

    Returns:
        tuple:
            - mu_com (np.ndarray): 3-element mean CoM.
            - sigma_com (np.ndarray): 3x3 Covariance matrix of the CoM.
    """
    if config is None: config = {}
    
    # Weighted Mean
    sum_w = np.sum(weights)
    if sum_w < 1e-9:
        return np.mean(points, axis=0), np.eye(3) * 1e-3

    mu_com = np.average(points, axis=0, weights=weights)

    # 1. Measurement Uncertainty (Error of the Mean)
    # Var(mu) = sum( (w_i / sum_w)^2 * Var(x_i) )
    norm_w = weights / sum_w
    combined_variance = np.sum((norm_w**2) * variances)
    sigma_meas = np.eye(3) * combined_variance

    sigma_com = sigma_meas

    # 2. Hybrid / Geometric Uncertainty
    # The legacy approach assumes CoM could be anywhere within a fraction of the object radius.
    # This models uncertainty due to non-uniform density (hollow objects, heavy batteries, etc).
    x_radius = 0
    y_radius = 0
    if config.get('com_method') == 'hybrid':
        # Calculate extents relative to mean
        # We use a simplified version of the notebook logic (min/max in X and Y)
        # Assumes points are roughly aligned or we interpret variance in principal axes
        
        diff = points - mu_com
        # 3 sigma ~ radius -> sigma = radius / 3
        # radius ~ min(abs(min), abs(max))
        
        # We calculate variance per axis
        # Heuristic: use raw std dev of points as a baseline for "radius"
        # Or stick to the legacy logic: "radius = min(abs(min), abs(max))"
        
        x_coords = diff[:, 0]
        y_coords = diff[:, 1]
        
        x_radius = max(0.01, min(np.abs(np.min(x_coords)), np.max(x_coords)))
        y_radius = max(0.01, min(np.abs(np.min(y_coords)), np.max(y_coords)))
        
        # Legacy used n_std=3, so sigma = radius / 3
        geo_scale = config.get('com_geo_scale', 1.0)
        sigma_x = (x_radius / 3.0) * geo_scale
        sigma_y = (y_radius / 3.0) * geo_scale
        # Z uncertainty? Legacy didn't vary Z much, let's keep it small or proportional
        sigma_z = (sigma_x + sigma_y) / 2.0 * 0.1 
        
        sigma_geo = np.diag([sigma_x**2, sigma_y**2, sigma_z**2])
        
        # Combine: variances add (convolution of uncertainties)
        sigma_com = sigma_meas + sigma_geo

    return mu_com, sigma_com, [x_radius, y_radius]

def sample_com(mu_com, sigma_com, n_samples=100, rng=None):
    """
    Samples CoM locations from the estimated Gaussian distribution.

    Args:
        mu_com (np.ndarray): Mean CoM (3,).
        sigma_com (np.ndarray): CoM Covariance (3,3).
        n_samples (int): Number of samples.
        rng (np.random.Generator, optional): Random number generator.

    Returns:
        np.ndarray: N x 3 array of sampled CoM points.
    """
    if rng is None:
        rng = np.random.default_rng()
    
    return rng.multivariate_normal(mu_com, sigma_com, size=n_samples)

def get_support_candidates(points, variances, config=None):
    """
    Identifies candidate points that could be in contact with the ground.
    
    Args:
        points (np.ndarray): Nx3, assumed aligned such that min(z) approx 0.
        variances (np.ndarray): Nx1 variances.
        config (dict):
            - 'ground_threshold': Distance from lowest point to consider candidates (default: 0.02).
            
    Returns:
        tuple:
            - candidates (np.ndarray): Mx3 array of candidate points.
            - candidate_vars (np.ndarray): Mx1 array of their variances.
    """
    if config is None: config = {}
    threshold = config.get('ground_threshold', 0.02)
    
    # We assume 'ground' is defined by the lowest Z points in the aligned cloud.
    # Note: notebook logic subtracts min(z), so min is exactly 0.
    min_z = np.min(points[:, 2])
    
    mask = (points[:, 2] - min_z) < threshold
    
    candidates = points[mask]
    candidate_vars = variances[mask]
    
    return candidates, candidate_vars

def estimate_contact_probabilities(candidate_vars, config=None):
    """
    Estimates probability that a candidate is a true contact point based on uncertainty.
    Lower uncertainty -> Higher probability.
    
    Args:
        candidate_vars (np.ndarray): Mx1 variances.
        config (dict):
            - 'tau': Temperature/scale parameter for probability mapping (default: 0.05).
            
    Returns:
        np.ndarray: Mx1 probabilities (sum to 1 for sampling, or independent probabilities).
        Here we normalize them to sum to 1 for use with np.random.choice.
    """
    if config is None: config = {}
    tau = config.get('tau', 0.01) # Small tau = sharp preference for low variance
    
    # p ~ exp(-sigma^2 / tau^2)
    # sigma^2 is variance
    logits = -candidate_vars / (tau**2)
    
    # Softmax stability
    max_logit = np.max(logits)
    exp_logits = np.exp(logits - max_logit)
    probs = exp_logits / np.sum(exp_logits)
    
    return probs

def sample_contacts(candidates, probs, rng=None, min_contacts=3):
    """
    Samples a set of contact points to form a polygon.
    
    Args:
        candidates (np.ndarray): Mx3
        probs (np.ndarray): Mx1 probabilities summing to 1.
        rng: Random generator.
        min_contacts: Minimum number of contacts to sample.
        
    Returns:
        np.ndarray: Kx3 sampled points.
    """
    if rng is None: rng = np.random.default_rng()
    n_candidates = len(candidates)
    
    if n_candidates < min_contacts:
        return candidates
    
    # Heuristic: Sample a number of points, say 10% of candidates or at least min_contacts
    n_sample = max(min_contacts, int(n_candidates * 0.1))
    n_sample = min(n_sample, 100) # Cap to avoid huge polygons
    
    indices = rng.choice(n_candidates, size=n_sample, replace=False, p=probs)
    return candidates[indices]

def build_support_polygon(contact_points):
    """
    Builds the convex hull of the contact points projected to Z=0.
    
    Args:
        contact_points (np.ndarray): Kx3 points.
        
    Returns:
        ConvexHull object or None if degenerate.
    """
    if len(contact_points) < 3:
        return None
        
    points_2d = contact_points[:, :2]
    try:
        hull = ConvexHull(points_2d)
        return hull
    except Exception:
        return None

def is_point_inside_hull(hull, point_2d):
    """
    Checks if point_2d is inside the ConvexHull.
    """
    if hull is None:
        return False
    # Using the equations: A*x + b <= 0
    # hull.equations is [A, b]
    eq = hull.equations
    val = np.dot(eq[:, :-1], point_2d) + eq[:, -1]
    return np.all(val <= 1e-6)



def hull_of_hulls(hulls, use_vertices_only=True, qhull_options=None):
    """
    hulls: list[scipy.spatial.ConvexHull]
    returns: ConvexHull of the union

    use_vertices_only=True is typically sufficient and faster.
    """
    if use_vertices_only:
        pts = np.vstack([h.points[h.vertices] for h in hulls])
    else:
        pts = np.vstack([h.points for h in hulls])

    # Optional: remove duplicate points (exact duplicates)
    pts = np.unique(pts, axis=0)

    # Compute combined hull
    return ConvexHull(pts, qhull_options=qhull_options)


def compute_stability_probabilistic(points, weights=None, config=None, use_completion_uncertainty=False):
    """
    Computes stability score using Monte Carlo sampling of CoM and Contacts.
    
    Args:
        points (np.ndarray): Nx3 point cloud.
        weights (np.ndarray, optional): Nx1 TSDF weights.
        config (dict): Configuration options.
        
    Returns:
        float: Stability probability [0.0, 1.0].
    """
    if config is None: config = {}
    n_mc_samples = config.get('n_mc_samples', 100)
    rng_seed = config.get('seed', None)
    rng = np.random.default_rng(rng_seed)


    if use_completion_uncertainty:
        # 1. Voxelize to get per-voxel stats
        centers, conf, sigma = conf_uncertainty_voxels(points, voxel=0.005)
        # 2. Convert to per-point variances and weights
        centers_f, variances, weights_calc, _, _ = voxel_stats_to_point_uncertainty(
            centers, conf, sigma, voxel=0.005, alpha=2.0, conf_min=0.2
        )
        
        # Use voxel centers as the nominal geometry
        points = centers_f
        
        # 3. Estimate CoM distribution from these per-point stats
        mu_com, sigma_com, radius = estimate_com_distribution(
            points, variances, weights_calc, config
        )
        
        # Override weights for visualization
        weights = weights_calc
        
    else:
        # 0. Sanitization
        points = _ensure_numpy(points)

        # 1. Uncertainty extraction
        variances, weights_calc = get_point_uncertainty(points, weights, config)
        
        # 2. CoM Distribution
        mu_com, sigma_com, radius = estimate_com_distribution(points, variances, weights_calc, config)
    
    # 3. Support Candidates
    candidates, candidate_vars = get_support_candidates(points, variances, config)
    
    if len(candidates) < 3:
        return 0.0
    
    contact_probs = estimate_contact_probabilities(candidate_vars, config)
    
    # 4. Monte Carlo Loop
    stable_count = 0
    
    # Pre-sample CoMs for efficiency
    com_samples = sample_com(mu_com, sigma_com, n_samples=n_mc_samples, rng=rng)
    
    # For visualization, store some polygons
    viz_hulls = []
    support_hulls = []
    
    for i in range(n_mc_samples):
        # Sample CoM
        com = com_samples[i]
        projected_com = com[:2] # Project to Z=0
        
        # Sample Support Polygon
        # We sample a new support polygon for each iteration effectively modeling
        # uncertainty in *which* points are contacts.
        contacts = sample_contacts(candidates, contact_probs, rng=rng)
        hull = build_support_polygon(contacts)
        
        if config.get('return_viz_data', False) and i < 20: # Keep first 20 for viz
            if hull is not None:
                # Store indices or points of simplex for plotting
                # Simplex points: hull.points[hull.vertices] usually gives ordered vertices for 2D hull
                # But ConvexHull in 2D: hull.vertices are indices into hull.points
                viz_hulls.append(hull.points[hull.vertices])
        
        if hull is not None:
            support_hulls.append(hull)
        
        # Check stability
        if is_point_inside_hull(hull, projected_com):
            stable_count += 1
            
    combined_support_hull = hull_of_hulls(support_hulls)
    probability = stable_count / n_mc_samples
    
    if config.get('return_viz_data', True):
        viz_data = {
            'mu_com': mu_com,
            'sigma_com': sigma_com,
            'com_samples': com_samples,
            'candidates': candidates,
            'contact_probs': contact_probs,
            'viz_hulls': viz_hulls,
            'stable_count': stable_count,
            'n_samples': n_mc_samples,
            'weights': weights,
            'radius': radius,
            'points': points
        }
        return probability, combined_support_hull, viz_data
        
    return probability, combined_support_hull


def plot_probabilistic_stability(ax, points, viz_data, orientation_flag=""):
    """
    Visualizes the probabilistic stability state.
    
    Args:
        ax: Matplotlib 3D axis.
        points: Scene point cloud (Nx3).
        viz_data: Dictionary returned by compute_stability_probabilistic.
    """
    # clear old data
    ax.clear()

    # Prioritize points from viz_data if present (e.g. voxel centers)
    if 'points' in viz_data:
        points = viz_data['points']
    
    # 1. Plot Point Cloud
    points = _ensure_numpy(points)
    weights = viz_data.get('weights')
    radius = viz_data.get('radius')

    # Subsample for performance if needed
    if weights is not None:
        # Plot with weights (colored)
        p = ax.scatter(points[:,0], points[:,1], points[:,2], marker='o',c=weights, cmap='viridis', s=5, alpha=0.05)
        ax.figure.colorbar(p, ax=ax, label='Weight', shrink=0.5)
    else:
        # Fallback (gray)
        ax.scatter(points[:,0], points[:,1], points[:,2], marker='o', s=5, alpha=0.05)    
    
    # 4. CoM Distribution (Mean)
    mu = viz_data['mu_com']
    z_ground = np.min(points[:,2])
    
    ax.scatter([mu[0]], [mu[1]], [mu[2]], color='r', s=50, label="Center of Mass (CoM)")
    ax.scatter([mu[0]], [mu[1]], [z_ground], color='black', s=50, label="Projected CoM")
    
    # Normal Vector (Approximate direction down to ground)
    normal_vector_end = [mu[0], mu[1], z_ground]
    ax.plot([mu[0], normal_vector_end[0]], [mu[1], normal_vector_end[1]], [mu[2], normal_vector_end[2]], 
            color='g', lw=2, label="Normal Vector")
    
    # sampling sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x_sphere = mu[0] + radius[0] * np.outer(np.cos(u), np.sin(v))
    y_sphere = mu[1] + radius[1] * np.outer(np.sin(u), np.sin(v))
    ax.plot_surface(x_sphere, y_sphere, np.full_like(x_sphere, mu[2]), color='b', alpha=0.2)


    # 2. Support Candidates
    # candidates = viz_data['candidates']
    # probs = viz_data['contact_probs']
    # p_norm = probs / np.max(probs)
    # ax.scatter(candidates[:,0], candidates[:,1], candidates[:,2], s=10, c=p_norm, cmap='viridis', label='Candidates')
    
    # 3. Support Polygons (Sampled) - Plot faint blueprints
    for poly_pts in viz_data['viz_hulls']:
        # poly_pts is (K, 2)
        xs = np.append(poly_pts[:,0], poly_pts[0,0])
        ys = np.append(poly_pts[:,1], poly_pts[0,1])
        zs = np.full_like(xs, z_ground)
        ax.plot(xs, ys, zs, 'b-', alpha=0.1, linewidth=1)
        
    # 4. CoM Samples
    samples = viz_data['com_samples']
    #if len(samples) > 200:
    #    samples = samples[:200]
        
    # Plot samples like "Gaussian sampled CoM"
    # We don't have per-sample projected stability in this loop easily unless we re-check, 
    # but the samples are just the CoM positions.
    ax.scatter(samples[:,0], samples[:,1], samples[:,2], color='orange', s=10, label="Gaussian sampled CoM")
    
    # Project Samples to Ground
    ax.scatter(samples[:,0], samples[:,1], np.full(len(samples), z_ground), color='gray', s=10, label="Projected Gaussian CoM")
    
    # Setup limits
    # Compute bounds from data
    min_xyz = np.min(points, axis=0)
    max_xyz = np.max(points, axis=0)
    center_xy = (min_xyz[:2] + max_xyz[:2]) / 2
    
    # Use 20cm window around center for XY
    ax.set_xlim([center_xy[0] - 0.1, center_xy[0] + 0.1])
    ax.set_ylim([center_xy[1] - 0.1, center_xy[1] + 0.1])
    
    # Use 20cm window above ground for Z
    ax.set_zlim([z_ground, z_ground + 0.2])
    
    # Hide axes
    ax.set_axis_off()
    ax.grid(False)
    ax.xaxis.pane.set_visible(False)
    ax.yaxis.pane.set_visible(False)
    ax.zaxis.pane.set_visible(False)
    
    leg = ax.legend(loc='upper left')
    for txt in leg.get_texts():
        txt.set_fontweight('bold')
    
    
    print(viz_data['stable_count'])
    print(viz_data['n_samples'])
    ax.set_title(f"Probabilistic Stability of orientation {orientation_flag}: {viz_data['stable_count']}/{viz_data['n_samples']}")

