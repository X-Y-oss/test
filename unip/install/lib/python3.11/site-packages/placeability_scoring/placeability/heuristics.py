import open3d as o3d
import numpy as np
from scipy.spatial import cKDTree


#########################################################################################################################################################
####################################################### PLOTTING HELPER #################################################################################
#########################################################################################################################################################

def _make_transformed_pcd(B_h: np.ndarray, T: np.ndarray, color=(0,1,0)) -> o3d.geometry.PointCloud:
    """Homogeneous points (M,4) * T -> PointCloud with color."""
    pts = (B_h @ T.T)[:, :3]
    p = o3d.geometry.PointCloud()
    p.points = o3d.utility.Vector3dVector(pts)
    p.paint_uniform_color(color)
    return p

def _pick_representative_indices(scores: np.ndarray,
                                 dmins: np.ndarray,
                                 tiny: float = 1e-3,
                                 mid_low: float = 0.43,
                                 mid_high: float = 0.57):
    """
    Return (idx_best, idx_med, idx_worst) with tie-breaking on distance.
      - Best  = argmax(score), tie -> max distance
      - Worst = argmin(score > tiny), tie -> min distance
      - Med   = first score in [mid_low, mid_high], tie -> max distance
                else fallback to closest-to-median score
    """
    n = scores.size
    if n == 1:
        return 0, 0, 0

    # --- best ---
    max_score = np.max(scores)
    best_candidates = np.where(scores == max_score)[0]
    if best_candidates.size > 1:
        idx_best = int(best_candidates[np.argmax(dmins[best_candidates])])
    else:
        idx_best = int(best_candidates[0])

    # --- worst (avoid ~0) ---
    valid_nonzero = np.where(scores > tiny)[0]
    if valid_nonzero.size > 0:
        min_score = np.min(scores[valid_nonzero])
        worst_candidates = valid_nonzero[scores[valid_nonzero] == min_score]
        if worst_candidates.size > 1:
            idx_worst = int(worst_candidates[np.argmin(dmins[worst_candidates])])
        else:
            idx_worst = int(worst_candidates[0])
    else:
        min_score = np.min(scores)
        worst_candidates = np.where(scores == min_score)[0]
        if worst_candidates.size > 1:
            idx_worst = int(worst_candidates[np.argmin(dmins[worst_candidates])])
        else:
            idx_worst = int(worst_candidates[0])

    # --- medium: prefer something around 0.5 ---
    mid_candidates = np.where((scores >= mid_low) & (scores <= mid_high))[0]
    idx_med = None
    if mid_candidates.size > 0:
        # pick one not equal to best/worst
        valid_mid = [j for j in mid_candidates if j not in (idx_best, idx_worst)]
        if valid_mid:
            idx_med = int(valid_mid[np.argmax(dmins[valid_mid])])
    if idx_med is None:
        # fallback: closest to median score
        med_val = float(np.median(scores))
        order = np.argsort(np.abs(scores - med_val))
        for j in order:
            if j not in (idx_best, idx_worst):
                idx_med = int(j)
                break
        if idx_med is None:
            idx_med = (idx_best + 1) % n

    return idx_best, idx_med, idx_worst

#########################################################################################################################################################
####################################################### PLOTTING HELPER END #############################################################################
#########################################################################################################################################################


def scores_from_dmins(dmins: np.ndarray,
                    threshold: float = 0.05,
                    decay_rate: float = 30.0,
                    collision_eps: float = 0.005,
                    mode: str = "clearance") -> np.ndarray:
    """
    mode = "dense_packing": closer (down to collision_eps) is better.
    mode = "clearance": farther than threshold keeps score 1; closer decays.
    """
    scores = np.ones_like(dmins, dtype=float)

    # 1) collisions or near-collisions → 0
    coll = dmins < collision_eps
    scores[coll] = 0.0

    if mode == "dense_packing":
        # 2a) dense packing: ideal if d in [collision_eps, threshold]
        # farther than threshold → exponential decay
        far = dmins > threshold
        scores[far] = np.exp(-decay_rate * (dmins[far] - threshold))

    elif mode == "clearance":
        # 2b) clearance: ideal if d >= threshold; closer than threshold → decay
        close = (dmins < threshold) & (~coll)
        # decay from threshold downward (flip sign)
        scores[close] = np.exp(-decay_rate * (threshold - dmins[close]))
        # far stays at 1

    else:
        raise ValueError("mode must be 'dense' or 'clearance'")

    # numerical hygiene
    return np.clip(scores, 0.0, 1.0)

def dense_packing(
        self,
        pcd_A: o3d.geometry.PointCloud,
        pcd_B: o3d.geometry.PointCloud,
        transforms: np.ndarray,           # shape (N,4,4) or list of 4x4
        mode="dense_packing", #"clearance"  "dense_packing"
        subsample_fraction=1.0,
        mesh=None,
    ) -> np.ndarray:
        """
        For each pose T in `transforms`, compute min_{b in (T*B)} min_{a in A} ||a - b||.

        Returns:
            dmins: (N,) minimal distances, one per transform.
        """
        # --- static KD-tree on A ---
        points_A = np.asarray(pcd_A.points)
        # --- subsample (e.g. 20% of points) ---
        if(subsample_fraction != 1.0):
            n = points_A.shape[0]
            k = max(1, int(subsample_fraction * n))               # number of points to keep
            idx = np.random.choice(n, size=k, replace=False)
            points_A = points_A[idx]
        
        if points_A.size == 0:
            raise ValueError("pcd_A is empty.")
        
        treeA = cKDTree(points_A)

        # --- B points once (homogeneous for cheap transforms) ---
        B = np.asarray(pcd_B.points)
        if B.size == 0:
            raise ValueError("pcd_B is empty.")
        B_h = np.hstack([B, np.ones((B.shape[0], 1))])  # (M,4)

        # normalize transforms into (N,4,4)
        if isinstance(transforms, (list, tuple)):
            transforms = np.stack(transforms, axis=0)
        if transforms.ndim != 3 or transforms.shape[1:] != (4, 4):
            raise ValueError("`transforms` must have shape (N,4,4).")

        N = transforms.shape[0]
        dmins = np.empty(N, dtype=float)

        print("Looping poses")
        for i in range(N):
            T = transforms[i]
            B_world = (B_h @ T.T)[:, :3]          # (M,3) — no O3D in-place ops
            dists, _ = treeA.query(B_world, k=1)  # nearest A-point for every transformed B-point
            dmins[i] = float(dists.min())

        score = scores_from_dmins(dmins=dmins, mode=mode)
        
        ####################################################### PLOTTING #################################################################################
        if mesh is not None:
            print("Now plotting")
            geoms = []

            # scene cloud A in gray
            pA = o3d.geometry.PointCloud(pcd_A)  # shallow copy
            pA.paint_uniform_color([0, 0, 1.])
            geoms.append(pA)

            # optional mesh (environment)
            if isinstance(mesh, o3d.geometry.TriangleMesh):
                m = o3d.geometry.TriangleMesh(mesh)  # shallow copy
                m.compute_vertex_normals()
                #m.paint_uniform_color([0.5, 0.5, 0.5])
                geoms.append(m)

            # choose indices
            i_best, i_med, i_worst = _pick_representative_indices(score, dmins)

            colors = {
                "best":  (0.0, 0.9, 0.0),   # bright green
                "med":   (1.0, 0.75, 0.0), # magenta-ish (middle point)
                "worst": (1.0, 0.0, 1.0),   # full magenta
            }
            # build transformed candidate clouds
            geoms.append(_make_transformed_pcd(B_h, transforms[i_best],  colors["best"]))
            geoms.append(_make_transformed_pcd(B_h, transforms[i_med],   colors["med"]))
            geoms.append(_make_transformed_pcd(B_h, transforms[i_worst], colors["worst"]))

            # small world frame for reference
            geoms.append(o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1))

            print(f"[viz] best idx={i_best}, score={score[i_best]:.4f}  "
                f"med idx={i_med}, score={score[i_med]:.4f}  "
                f"worst idx={i_worst}, score={score[i_worst]:.4f}")

            o3d.visualization.draw_geometries(geoms)

        return score