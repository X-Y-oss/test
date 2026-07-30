"""
Plotting Configuration Dictionary
================================
Centralized control for all plotting and visualization flags in UP4_Pipeline.
Modify these settings to enable/disable various visualization outputs.
"""

PLOTTING_CONFIG = {
    # === Main Control Flags ===
    "run_validation": False,        # Enable validation mode with interactive prompts and visualization
    "plotting": False,              # Enable general plotting outputs
    "show_colliding": False,        # Highlight colliding geometries in visualization
    
    # === Grasping Area Investigation ===
    "plot_grasp_mesh": False,       # Visualize the grasp mesh
    "plot_object_pointcloud": False, # Visualize filtered object pointcloud
    
    # === Placeability Calculation ===
    "plot_filter_object": False,    # Visualize object filtering process
    "plot_grasp_placeability": False, # Visualize grasp placeability analysis
    
    # === Placing Area Investigation ===
    "plot_place_mesh": False,       # Visualize the place mesh
    
    # === Grasp Validation ===
    "plot_grasp_collision_check": False, # Visualize grasp collision validation
    "plot_pointcloud_alignment": False,  # Verify pointcloud and mesh alignment
    
    # === OBB Alignment Filter ===
    "plot_obb_alignment": False,    # Visualize OBB-aligned grasp filtering
    "plot_obb_aligned_grasps": False, # Visualize OBB-aligned grasps with scores
    
    # === Placing Validation ===
    "plot_placements": False, # Visualize place collision validation
    "plot_placing_area_collisions": False, # Visualize collisions in placing area
    
    # === Reachability Maps ===
    "plot_reachability_grasping": True, # Visualize grasp reachability analysis
    "plot_reachability_placing": False,  # Visualize place reachability analysis
    
    # === Reasoning and Scoring ===
    "plot_scored_grasps": False,    # Visualize grasp scores and grasp mesh
    "plot_best_two_grasps": False,  # Compare best two grasp configurations
    "plot_best_three_grasps": False, # Compare best three grasp configurations
    
    # === Execution ===
    "plot_motion_plan": False,      # Visualize motion planning results
    "plot_grasp_transforms": False, # Show grasp and place frame transformations
    "plot_execution_preview": False, # Preview trajectory execution with geometries
}

def get_plotting_config():
    """Return the plotting configuration dictionary."""
    return PLOTTING_CONFIG

def update_plotting_config(**kwargs):
    """Update multiple plotting settings at once.
    
    Example:
        update_plotting_config(run_validation=True, plotting=True)
    """
    PLOTTING_CONFIG.update(kwargs)

def enable_all_plotting():
    """Enable all plotting flags."""
    for key in PLOTTING_CONFIG:
        PLOTTING_CONFIG[key] = True

def disable_all_plotting():
    """Disable all plotting flags."""
    for key in PLOTTING_CONFIG:
        PLOTTING_CONFIG[key] = False

def set_validation_mode(enabled=True):
    """Enable or disable validation mode (includes main flags and related visualizations)."""
    PLOTTING_CONFIG["run_validation"] = enabled
    PLOTTING_CONFIG["plotting"] = enabled
    if enabled:
        # Enable related visualizations when validation mode is on
        PLOTTING_CONFIG["plot_grasp_mesh"] = True
        PLOTTING_CONFIG["plot_object_pointcloud"] = True
        PLOTTING_CONFIG["plot_grasp_collision_check"] = True
        PLOTTING_CONFIG["plot_place_collision_check"] = True
