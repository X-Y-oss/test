import numpy as np
from scipy.spatial import cKDTree

def compute_graspability(grasps, pointcloud):
    """Infers the grasps to the points in the pointcloud
    This is mainly for visual output. The grasps are better to be Transformed which resolves in faster interference.

    Args:
        grasps (np.array(N_graspx17)): grasps from GPD 17 entries
        pointcloud (np.array Nx3)

    Returns:
        scores (N_pclx17): pointcloud associated with grasps, mostly 0
    """
    # Create the KDTree using the x, y, z coordinates
    kdtree = cKDTree(pointcloud)  # pointcloud is now an array of shape (N, 3)
    
    scores = np.zeros([len(pointcloud),17])
    
    for g in grasps:
        dist, idx = kdtree.query(g[14:])
        scores[idx] = g

    return scores