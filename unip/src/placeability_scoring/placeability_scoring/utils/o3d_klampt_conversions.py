import open3d as o3d
import numpy as np
import pyfqmr
from klampt.model.geometry import TriangleMesh
from klampt import Geometry3D

def o3d_mesh_to_klampt_geom(o3d_mesh, downsample=False):
    """Transforms open3d mesh into klampt mesh for collision checking
    Args:
        o3d_mesh (o3dmesh)
    Returns:
        Klampt_mesh
    """
    if not o3d_mesh.has_vertex_normals():
        o3d_mesh.compute_vertex_normals()
    
    vertices = np.asarray(o3d_mesh.vertices)
    indices = np.asarray(o3d_mesh.triangles)
    if(downsample==True):
        mesh_simplifier = pyfqmr.Simplify()
        mesh_simplifier.setMesh(vertices, indices)
        mesh_simplifier.simplify_mesh(target_count=len(indices) / 100, aggressiveness=7, preserve_border=True,
                                        verbose=False)
        vertices, triangles, _ = mesh_simplifier.getMesh()
        invalid1 = triangles[:, 0] == triangles[:, 1]
        invalid2 = triangles[:, 0] == triangles[:, 2]
        invalid3 = triangles[:, 1] == triangles[:, 2]
        invalid = np.logical_or(invalid1, invalid2)
        invalid = np.logical_or(invalid, invalid3)
        indices = triangles[np.logical_not(invalid)]

    print("vertices shape", vertices.shape)
    klampt_mesh = TriangleMesh()
    klampt_mesh.vertices = vertices.tolist()
    klampt_mesh.indices = indices.tolist()

    geom = Geometry3D()
    geom.setTriangleMesh(klampt_mesh)
    return geom

def klampt_geom_to_open3d(geom, T=None, color=[0.5, 0.5, 0.5]):
    # Extract the underlying mesh
    if hasattr(geom, "getTriangleMesh"):
        mesh = geom.getTriangleMesh()
    else:
        mesh = geom  # Assume raw mesh

    vertices = np.array(mesh.vertices)
    triangles = np.array(mesh.indices)

    if T is not None:
        assert T.shape == (4, 4)
        verts_hom = np.hstack([vertices, np.ones((len(vertices), 1))])
        vertices = (T @ verts_hom.T).T[:, :3]

    mesh_o3d = o3d.geometry.TriangleMesh()
    mesh_o3d.vertices = o3d.utility.Vector3dVector(vertices)
    mesh_o3d.triangles = o3d.utility.Vector3iVector(triangles)
    mesh_o3d.paint_uniform_color(color)
    mesh_o3d.compute_vertex_normals()
    return mesh_o3d