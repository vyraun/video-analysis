'''
Created on Feb 4, 2015

@author: David Zwicker <dzwicker@seas.harvard.edu>

This module provides some classes for geometric shapes for convenience. These
classes are not implemented with very high speed in mind, but rather serve to
ease implementations of geometric calculations.
'''

from __future__ import division

import cv2
import numpy as np
from scipy import interpolate, spatial
from shapely import geometry

from utils.data_structures.cache import cached_property
import curves
import image



class Point(object):
    """ class that represents a single point """
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        
    def __repr__(self):
        return ("%s(x=%g, y=%g)" % (self.__class__.__name__, self.x, self.y))
        
     
    @property
    def coords(self):
        return (self.x, self.y)

    
    def translate(self, x, y):
        """ moves the point """
        self.x += x
        self.y += y
        return self
    


class Rectangle(object):
    """ class that represents a rectangle """
    
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        
    @classmethod
    def from_points(cls, p1, p2):
        x1, x2 = min(p1[0], p2[0]), max(p1[0], p2[0])
        y1, y2 = min(p1[1], p2[1]), max(p1[1], p2[1])
        return cls(x1, y1, x2 - x1, y2 - y1)
    
    
    @classmethod
    def from_centerpoint(cls, centerpoint, width, height):
        x = centerpoint[0] - width/2
        y = centerpoint[1] - height/2
        return cls(x, y, width, height)
    
    
    @classmethod
    def from_list(cls, data):
        return cls(*data)
    
    
    def to_list(self):
        return [self.x, self.y, self.width, self.height]


    @classmethod
    def from_array(cls, data):
        return cls(*data)
    
    
    def to_array(self):
        return np.array(self.to_list())
    
    
    def copy(self):
        return self.__class__(self.x, self.y, self.width, self.height)
        
        
    def __repr__(self):
        return ("%s(x=%g, y=%g, width=%g, height=%g)"
                % (self.__class__.__name__, self.x, self.y, self.width,
                   self.height))
            
            
    @property
    def data(self):
        return self.x, self.y, self.width, self.height
    
    
    @property
    def data_int(self):
        return (int(self.x), int(self.y),
                int(self.width), int(self.height))
    
    
    @property
    def left(self):
        return self.x
    
    @left.setter
    def left(self, value):
        self.x = value
    
    
    @property
    def right(self):
        return self.x + self.width
    
    @right.setter
    def right(self, value):
        self.width = value - self.x
    
    
    @property
    def top(self):
        return self.y
    
    @top.setter
    def top(self, value):
        self.y = value
    
    
    @property
    def bottom(self):
        return self.y + self.height
    
    @bottom.setter
    def bottom(self, value):
        self.height = value - self.y        


    def set_corners(self, p1, p2):
        x1, x2 = min(p1[0], p2[0]), max(p1[0], p2[0])
        y1, y2 = min(p1[1], p2[1]), max(p1[1], p2[1])
        self.x = x1
        self.y = y1
        self.width = x2 - x1
        self.height = y2 - y1 
            
            
    @property
    def corners(self):
        return (self.x, self.y), (self.x + self.width, self.y + self.height)
    
    @corners.setter
    def corners(self, ps):
        self.set_corners(ps[0], ps[1])
        
        
    @property
    def contour(self):
        x2, y2 = self.x + self.width, self.y + self.height
        return ((self.x, self.y),
                (x2, self.y),
                (x2, y2),
                (self.x, y2))
    
    
    @property
    def slices(self):
        slice_x = slice(int(self.x), int(self.x + self.width))
        slice_y = slice(int(self.y), int(self.y + self.height))
        return slice_x, slice_y


    @property
    def p1(self):
        return (self.x, self.y)
    
    @p1.setter
    def p1(self, p):
        self.set_corners(p, self.p2)
           
           
    @property
    def p2(self):
        return (self.x + self.width, self.y + self.height)
    
    @p2.setter
    def p2(self, p):
        self.set_corners(self.p1, p)
        
        
    @property
    def centroid(self):
        return (self.x + self.width/2, self.y + self.height/2)
        
        
    def buffer(self, amount):
        """ dilate the rectangle by a certain amount in all directions """
        self.x -= amount
        self.y -= amount
        self.width += 2*amount
        self.height += 2*amount
    
    
    def intersect(self, other):
        """ intersects this rectangle with another one """
        self.left = max(self.left, other.left) 
        self.right = min(self.right, other.right)
        self.top = max(self.top, other.top)
        self.bottom = min(self.bottom, other.bottom)
        
        
    def intersection(self, other):
        """ return the intersection between this rectangle and the other """
        left = max(self.left, other.left) 
        right = min(self.right, other.right)
        top = max(self.top, other.top)
        bottom = min(self.bottom, other.bottom)
        return Rectangle.from_points((left, top), (right, bottom))
        
        
    @property
    def area(self):
        return self.width * self.height
    
    
    def points_inside(self, points):
        """ returns a boolean array indicating which of the points are inside
        this rectangle """
        return ((self.left <= points[:, 0]) & (points[:, 0] <= self.right) &
                (self.top  <= points[:, 1]) & (points[:, 1] <= self.bottom))
        
        
    @property
    def contour_ring(self):
        """ return the linear ring of the polygon contour """
        return geometry.LinearRing(self.contour)
    
    @property
    def polygon(self):
        """ return the shapely polygon """
        return geometry.Polygon(self.contour)



class Circle(object):
    """ class that represents a circle """

    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        
    
    def __repr__(self):
        return ('%s(x=%r, y=%r, radius=%r)' %
                (self.__class__.__name__, self.x, self.y, self.radius))
       
       
    @property
    def perimeter(self):
        return 2*np.pi*self.radius
    
       
    @property
    def centroid(self):
        return np.array((self.x, self.y))
    
    
    @property
    def area(self):
        return 4*np.pi*self.radius**2
       
    
    @property
    def bounds(self):
        r = self.radius
        return Rectangle(self.x - r, self.y - r, 2*r, 2*r)
       
           
    def get_theta(self, x, y):
        """ returns the angle associated with a point """
        return np.arctan2(y - self.y, x - self.x)
       

    def get_point(self, angle):
        """ returns the point at the given angle """
        x = self.x + self.radius * np.cos(angle)
        y = self.y + self.radius * np.sin(angle)
        return np.squeeze(np.c_[x, y])
        
        
    def get_points(self, spacing=1):
        """ returns points on the perimeter of the circle """
        num_points = max(4, int(self.perimeter/spacing))
        theta = np.linspace(0, 2*np.pi, num_points, endpoint=False)
        return self.get_point(theta)
    
    
    def get_tangent(self, angle):
        """ returns the tangent vector at the angle """
        return np.squeeze(np.c_[np.cos(angle), np.sin(angle)])
    
    
    
class Arc(Circle):
    """ class that represents a circular arc """

    def __init__(self, x, y, radius, start, end):
        """
        `x` and `y` determine the center of the arc
        `radius` is the radius
        `start` and `end` set the start and end angle in radians
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.start = start
        self.end = end
        if self.start < self.end:
            self._end = self.end
        else:
            self._end = self.end + 2*np.pi
        
    
    def __repr__(self):
        return ('%s(x=%r, y=%r, radius=%r, start=%r, end=%r)' %
                (self.__class__.__name__, self.x, self.y, self.radius,
                 self.start, self.end))
       
       
    @classmethod
    def from_circle(cls, circle, start, end):
        """
        `start` and `end` set the start and end of the arc.
            They can either be given as radians or as points, in which case
            the associated radians will be calculated automatically.
        """ 
        try:
            start = np.arctan2(start[1] - circle.y, start[0] - circle.x)
        except TypeError:
            pass
        try:
            end = np.arctan2(end[1] - circle.y, end[0] - circle.x)
        except TypeError:
            pass
        return cls(circle.x, circle.y, circle.radius, start, end)
    
    
    @property
    def opening_angle(self):
        return (self._end - self.start)
       
       
    @property
    def perimeter(self):
        return self.opening_angle * self.radius
    
    
    @property
    def centroid(self):
        """ centroid of the circular arc """
        theta_c = 0.5*(self.start + self._end)
        angle_o2 = 0.5*self.opening_angle
        radius_c = self.radius*np.sin(angle_o2)/angle_o2
        x = self.x + radius_c*np.cos(theta_c) 
        y = self.y + radius_c*np.sin(theta_c)
        return x, y 
    
    
    @property
    def area(self):
        return 2 * self.opening_angle * self.radius**2
    
    
    @property
    def bounds(self):
        """ return bounding rect of the arc """
        # determine all angles pointing in possible extreme directions
        thetas = [t for t in np.linspace(0, 4*np.pi, 9)
                  if self.start < t < self._end]
        thetas.append(self.start)
        thetas.append(self.end)
        # determine the bounding rect for all these points
        points = geometry.asMultiPoint(self.get_point(thetas))
        bounds = points.bounds
        return Rectangle.from_points(bounds[:2], bounds[2:])
       
        
    def get_points(self, spacing=1):
        """ returns points on the perimeter of the arc """
        num = max(2, int(self.perimeter/spacing))
        theta = np.linspace(self.start, self._end, num)
        return self.get_point(theta)
    
    
    @property
    def start_point(self):
        return self.get_point(self.start) 
    
    @property
    def end_point(self):
        return self.get_point(self.end)     
    
    @property
    def mid_point(self):
        return self.get_point(0.5*(self.start + self._end))     
    


class Polygon(object):
    """ class that represents a single polygon """
    
    def __init__(self, data):
        """ create polygon from list of points or shapely geometry """
        if isinstance(data, geometry.Polygon):
            if data.is_simple:
                data = data.boundary.coords
            else:
                raise ValueError('Only simple polygons are supported') 
        
        # assume that `data` contains a list of points
        if len(data) < 3:
            raise ValueError("Polygon must have at least three points.")
        self.contour = np.asarray(data, np.double)


    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.contour)


    def copy(self):
        """ create copy of the current object """
        return self.__class__(self.contour.copy())


    def clear_cache(self):
        """ clears the internal cache """
        self._cache = {}
        
        
    def __getstate__(self):
        """ do not save the cache to the pickled state """
        state = self.__dict__.copy()
        del state['_cache'] #< don't save the cache when pickling
        return state


    def __setstate__(self, state):
        """ set a clear cache on unpickling """
        self.__dict__ = state
        self.clear_cache()


    @property
    def contour(self):
        return self._contour
    
    @contour.setter 
    def contour(self, points):
        """ set the contour of the polygon.
        `point_list` can be a list/array of points or a shapely LinearRing
        """ 
        if points is None:
            self._contour = None
        else:
            if isinstance(points, geometry.LinearRing):
                ring = points
            else:
                ring = geometry.LinearRing(points)
                
            # make sure that the contour is given in clockwise direction
            self._contour = np.array(points, np.double)
            if ring.is_ccw:
                self._contour = self._contour[::-1]
            
        self.clear_cache()

        
    def scale(self, scale_factor):
        """ scales the polygon by a factor """
        self._contour *= scale_factor
        self.clear_cache()
        
        
    @cached_property
    def contour_ring(self):
        """ return the linear ring of the polygon contour """
        return geometry.LinearRing(self.contour)
    
        
    @cached_property
    def polygon(self):
        """ return the shapely polygon """
        return geometry.Polygon(self.contour)
    
    
    @cached_property
    def centroid(self):
        return np.array(self.polygon.centroid)
    
    
    @cached_property
    def position(self):
        return np.array(self.polygon.representative_point())
    
    
    @cached_property
    def area(self):
        """ return the area of the polygon """
        return self.polygon.area
    
    
    @cached_property
    def perimeter(self):
        """ return the perimeter of the polygon """
        return self.contour_ring.length
    
    
    @cached_property
    def moments(self):
        """ return all moments of the polygon up to third order. """
        # cv2.moments only supports np.int or np.float32, otherwise the
        # coordinate sequence is interpreted as an image, see
        #     https://github.com/Itseez/opencv/issues/6643
        return cv2.moments(np.asarray(self.contour, np.float32))
    
    
    @cached_property
    def eccentricity(self):
        """ return the eccentricity of the polygon
        The eccentricity will be between 0 and 1, corresponding to a circle
        and a straight line, respectively.
        """
        m = self.moments
        a, b, c = m['mu20'], -m['mu11'], m['mu02']
        e1 = (a + c) + np.sqrt(4*b**2 + (a - c)**2)
        e2 = (a + c) - np.sqrt(4*b**2 + (a - c)**2)
        if e1 == 0:
            return 0
        else:
            return np.sqrt(1 - e2/e1)
    
                
    def contains(self, point):
        """ returns True if the point is inside the polygon """
        return self.polygon.contains(geometry.Point(point))
    
    
    @cached_property
    def bounds(self):
        bounds = geometry.MultiPoint(self.contour).bounds
        return Rectangle.from_points(bounds[:2], bounds[2:])

    
    def regularize(self):
        """ regularize the current polygon """
        import regions #< lazy import to prevent circular dependencies
        self.contour = regions.regularize_contour_points(self.contour)
        
    
    def get_bounding_rect(self, margin=0):
        """ returns the bounding rectangle of the polygon """
        bound_rect = self.bounds
        if margin:
            bound_rect.buffer(margin)
        return np.asarray(bound_rect.data, np.int)
            
        
    def get_mask(self, margin=0, dtype=np.uint8, ret_offset=False):
        """ builds a mask of the polygon.
        
        `margin` adds an extra margin to the boundary
        `dtype` determines the dtype of the output
        `ret_offset` determines whether the coordinates of the upper left point
            of the mask are returned
        """
        # prepare the array to store the mask into
        rect = self.get_bounding_rect(margin=margin)
        mask = np.zeros((rect[3], rect[2]), dtype)

        # draw the polygon into the mask
        contour = np.asarray(self.contour, np.int)
        offset = (-rect[0], -rect[1])
        cv2.fillPoly(mask, [contour], color=1, offset=offset)
        
        if ret_offset:
            return mask, (-offset[0], -offset[1])
        else:
            return mask

        
    def get_skeleton(self, ret_offset=False):
        """ gets the binary skeleton image of the polygon

        `ret_offset` determines whether the coordinates of the upper left point
            of the skeleton mask are returned
        """
        if ret_offset:
            mask, offset = self.get_mask(margin=5, ret_offset=True)
        else:
            mask = self.get_mask(ret_offset=False)
        
        skeleton = image.mask_thinning(mask)
        
        if ret_offset:
            return skeleton, offset
        else:
            return skeleton
        
        
    def get_skeleton_points(self):
        """ returns points along the skeleton of the shape """
        skeleton, offset = self.get_skeleton(ret_offset=True)
        
        # determine the coordinates on the skeleton
        y, x = np.nonzero(skeleton)
        return np.c_[x, y] + offset
        
        
    def get_morphological_graph(self, simplify_epsilon=0.1):
        """ gets the graph representing the skeleton of the polygon """
        # skeletonize the polygon
        skeleton, offset = self.get_skeleton(ret_offset=True)
        
        # lazy import to prevent circular imports
        from morphological_graph import MorphologicalGraph
        
        # build the morphological graph from the skeleton
        graph = MorphologicalGraph.from_skeleton(skeleton, copy=False)
        
        # simplify the curves describing the edges, if requested
        if simplify_epsilon > 0:
            graph.simplify(simplify_epsilon)

        # move the graph to the global coordinate system
        graph.translate(*offset)
        
        return graph
        
        
    def get_centerline_estimate(self, end_points=None):
        """ determines an estimate to a center line of the polygon
        `end_points` can either be None, a single point, or two points.
        """
        import regions #< lazy import to prevent circular dependencies
        
        def _find_point_connection(p1, p2=None, maximize_distance=False):
            """ estimate centerline between the one or two points """
            mask, offset = self.get_mask(margin=2, dtype=np.int32,
                                         ret_offset=True)

            p1 = (p1[0] - offset[0], p1[1] - offset[1])

            if maximize_distance or p2 is None:
                dist_prev = 0 if maximize_distance else np.inf
                # iterate until second point is found
                while True:
                    # make distance map starting from point p1
                    distance_map = mask.copy()
                    regions.make_distance_map(distance_map, start_points=(p1,))
                    # find point farthest point away from p1
                    idx_max = np.unravel_index(distance_map.argmax(),
                                               distance_map.shape)
                    dist = distance_map[idx_max]
                    p2 = idx_max[1], idx_max[0]

                    if dist <= dist_prev:
                        break
                    dist_prev = dist
                    # take farthest point as new start point
                    p1 = p2
            else:
                # locate the centerline between the two given points
                p2 = (p2[0] - offset[0], p2[1] - offset[1])
                distance_map = mask
                regions.make_distance_map(distance_map,
                                          start_points=(p1,), end_points=(p2,))
                
            # find path between p1 and p2
            path = regions.shortest_path_in_distance_map(distance_map, p2)
            return curves.translate_points(path, *offset)
        
        
        if end_points is None:
            # determine both end points
            path = _find_point_connection(np.array(self.position),
                                          maximize_distance=True)
        else:
            end_points = np.squeeze(end_points)

            if end_points.shape == (2, ):
                # determine one end point
                path = _find_point_connection(end_points,
                                              maximize_distance=False)
            elif end_points.shape == (2, 2):
                # both end points are already determined
                path = _find_point_connection(end_points[0], end_points[1])
                
            elif end_points.ndim == 2 and end_points.shape[1] == 2:
                # multiple end points found => we have to find the end points
                # that are farthest apart
                longest_path, length = None, 0
                for k_1, p_1 in enumerate(end_points):
                    for p_2 in end_points[:k_1]:
                        path = _find_point_connection(p_1, p_2)
                        path_len = curves.curve_length(path)
                        if path_len > length:
                            longest_path, length = path, path_len
                        
                path = longest_path
                
            else:
                raise TypeError('`end_points` must have shape (2,) or (n, 2), '
                                'but we found %s' % str(end_points.shape))
            
        return path
        
        
    def get_centerline_optimized(self, alpha=1e3, beta=1e6, gamma=0.01,
                                 spacing=20, max_iterations=1000,
                                 endpoints=None):
        """ determines the center line of the polygon using an active contour
        algorithm """
        # lazy import to prevent circular imports
        from active_contour import ActiveContour
        
        # use an active contour algorithm to find centerline
        ac = ActiveContour(blur_radius=1, alpha=alpha, beta=beta,
                           gamma=gamma, closed_loop=False)
        ac.max_iterations = max_iterations

        # set the potential from the  distance map
        mask, offset = self.get_mask(1, ret_offset=True)
        potential = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
        ac.set_potential(potential)
        
        # initialize the centerline from the estimate
        points = self.get_centerline_estimate(endpoints)
        points = curves.make_curve_equidistant(points, spacing=spacing)        
        points = curves.translate_points(points, -offset[0], -offset[1])
        # anchor the end points
        anchor = np.zeros(len(points), np.bool)
        anchor[0] = anchor[-1] = True
        
        # find the best contour
        points = ac.find_contour(points, anchor, anchor)
        
        points = curves.make_curve_equidistant(points, spacing=spacing)        
        return curves.translate_points(points, *offset)
        

    def get_centerline_smoothed(self, points=None, spacing=10, skip_length=90,
                                **kwargs):
        """ determines the center line of the polygon using an active contour
        algorithm. If `points` are given, they are used for getting the
        smoothed centerline. Otherwise, we determine the optimized centerline
        influenced by the additional keyword arguments.
        `skip_length` is the length that is skipped at either end of the center
            line when the smoothed variant is calculated
        """
        if points is None:
            points = self.get_centerline_optimized(spacing=spacing, **kwargs)
        
        # get properties of the line
        length = curves.curve_length(points)
        endpoints = points[0], points[-1]
        
        # get the points to interpolate
        points = curves.make_curve_equidistant(points, spacing=spacing)
        skip_points = int(skip_length / spacing)
        points = points[skip_points:-skip_points]
        
        # do spline fitting to smooth the line
        smoothing_condition = length
        spline_degree = 3
        try:
            tck, _ = interpolate.splprep(np.transpose(points), k=spline_degree,
                                         s=smoothing_condition)
        except (ValueError, TypeError):
            # do not interpolate if there are problems
            pass
        else:
            # extend the center line in both directions to make sure that it
            # crosses the outline
            overshoot = 20*skip_length #< absolute overshoot
            num_points = (length + 2*overshoot)/spacing
            overshoot /= length #< overshoot relative to total length
            s = np.linspace(-overshoot, 1 + overshoot, num_points)
            points = interpolate.splev(s, tck)
            points = zip(*points) #< transpose list
        
            # restrict center line to the section between the end points
            dists = spatial.distance.cdist(endpoints, points)
            ks = sorted(np.argmin(dists, axis=1))
            cline = geometry.LineString(points[ks[0] : ks[1]+1])
            
            if isinstance(cline, geometry.MultiLineString):
                points = max(cline, key=lambda obj: obj.length).coords
            else:
                points = np.array(cline.coords)
        
        return points
    
    
    def get_centerline(self, method='smoothed', **kwargs):
        """ get the centerline of the polygon """
        if method == 'smoothed':
            return self.get_centerline_smoothed(**kwargs)
        elif method == 'optimized':
            return self.get_centerline_optimized(**kwargs)
        elif method == 'estimate':
            return self.get_centerline_estimate(**kwargs)
        else:
            raise ValueError('Unknown method `%s`' % method)
    