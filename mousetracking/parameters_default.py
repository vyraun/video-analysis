'''
Created on Aug 27, 2014

@author: zwicker

Provides a dictionary with default parameters for the mouse tracking
'''


PARAMETERS_DEFAULT = {
    # filename pattern used to look for videos
    'video/filename_pattern': 'raw_video/*',
    # number of initial frames to skip during analysis
    'video/ignore_initial_frames': 0,
    # radius of the blur filter to remove noise [in pixel]
    'video/blur_radius': 3,
    
    # folder to which the log file is written
    'logging/folder': None,
    
    # folder to which the YAML and HDF5 result files are written
    'output/result_folder': './results/',
    # folder to which debug videos are written
    'output/video/folder': './debug/',
    # file extension used for debug videos
    'output/video/extension': '.mov',
    # ffmpeg video codec used for debug videos
    'output/video/codec': 'libx264',
    # bitrate used for debug videos
    'output/video/bitrate': '2000k',
    
    # thresholds for cage dimension [in pixel]
    # These are only used to make a plausibility test of the results.
    # Setting the min to 0 and max to a large number should still allow the
    # algorithm to find a sensible cage approximation
    'cage/width_min': 650,
    'cage/width_max': 800,
    'cage/height_min': 400,
    'cage/height_max': 500,
                               
    # how often are the color estimates adapted [in frames]
    'colors/adaptation_interval': 1000,
                               
    # the rate at which the background is adapted [in 1/frames]
    'background/adaptation_rate': 0.01,
    # the rate at which the explored area is adapted [in 1/frames]
    'explored_area/adaptation_rate': 1e-5,
    
    # spacing of the support points describing the ground profile [in pixel]
    'ground/point_spacing': 20,
    # how often is the ground profile adapted [in frames]
    'ground/adaptation_interval': 100,
    # width of the ground profile ridge [in pixel]
    'ground/width': 5,
    
    # relative weight of distance vs. size of objects for matching them [dimensionless]
    'objects/matching_weigth': 0.5,
    # number of consecutive frames used for motion detection [in frames]
    'objects/matching_moving_window': 20,
    # threshold speed above which an object is said to be moving [in pixels/frame]
    'objects/matching_moving_threshold': 10,
        
    # `mouse.intensity_threshold` determines how much brighter than the
    # background (usually the sky) has the mouse to be. This value is
    # measured in terms of standard deviations of the sky color
    'mouse/intensity_threshold': 1,
    # radius of the mouse model [in pixel]
    'mouse/model_radius': 25,
    # minimal area of a feature to be considered in tracking [in pixel^2]
    'mouse/min_area': 100,
    # maximal speed of the mouse [in pixel per frame]
    # this is only used for the first-pass
    'mouse/max_speed': 30, 
    # maximal area change allowed between consecutive frames [dimensionless]
    'mouse/max_rel_area_change': 0.5,

    # how often are the burrow shapes adapted [in frames]
    'burrows/adaptation_interval': 100,
    # margin of a potential burrow to the cage boundary [in pixel]
    'burrows/cage_margin': 30,
    # what is a typical radius of a burrow [in pixel]
    'burrows/radius': 10,
    # minimal area a burrow cross section has to have [in pixel^2]
    'burrows/min_area': 1000,
    # maximal distance of ground profile to outline points that are considered exit points [in pixel]
    'burrows/ground_point_distance': 10,
    # length of a segment of the center line of a burrow [in pixel]
    'burrows/centerline_segment_length': 25,
    # the maximal radius of curvature the centerline is allowed to have
    'burrows/curvature_radius_max': 50,
    # the eccentricity above which burrows are refined by fitting [dimensionless]
    'burrows/fitting_eccentricity_threshold': 0.98,
    # the length above which burrows are refined by fitting [in pixel]
    'burrows/fitting_length_threshold': 75,
    # determines how much the burrow outline might be simplified. The quantity 
    # determines by what fraction the total outline length is allowed to change 
    'burrows/outline_simplification_threshold': 0.005,
    
    # minimal a track has to have in order to be considered a mouse for sure
    'tracking/min_length': 50, 
}
