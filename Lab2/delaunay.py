# -*- coding: ascii -*-
"""
Simple structured Delaunay triangulation in 2D with incremental(Bowyer-Watson) algorithm.
"""
import time

import matplotlib
import numpy as np
from math import sqrt

from matplotlib import pyplot as plt


class Delaunay:
    """
    Class to compute a Delaunay triangulation in 2D
    """

    def __init__(self, center=(0, 0), radius=9999):
        """
        Init and create a new frame to contain the triangulation
        center -- Optional position for the center of the frame. Default (0,0)
        radius -- Optional distance from corners to the center.
        """
        center = np.asarray(center)
        # Create coordinates for the corners of the frame
        self.coords = [center + radius * np.array((-1, -1)),
                       center + radius * np.array((+1, -1)),
                       center + radius * np.array((+1, +1)),
                       center + radius * np.array((-1, +1))]

        # Create two dicts to store triangle neighbours and circles.
        self.triangles = {}
        self.circles = {}

        # Create two CCW triangles for the frame
        T1 = (0, 1, 3)
        T2 = (2, 3, 1)
        self.triangles[T1] = [T2, None, None]
        self.triangles[T2] = [T1, None, None]

        # Compute circum-centers and circum-radius for each triangle
        for t in self.triangles:
            self.circles[t] = self.circum_center(t)

    def circum_center(self, tri):
        """
        Compute circum-center and circum-radius of a triangle.
        Uses an extension of the method described here:
        http://www.ics.uci.edu/~eppstein/junkyard/circumcenter.html
        """
        pts = np.asarray([self.coords[v] for v in tri])
        pts2 = np.dot(pts, pts.T)
        A = np.bmat([[2 * pts2, [[1],
                                 [1],
                                 [1]]],
                     [[[1, 1, 1, 0]]]])

        b = np.hstack((np.sum(pts * pts, axis=1), [1]))
        x = np.linalg.solve(A, b)
        bary_coords = x[:-1]
        center = np.dot(bary_coords, pts)

        # radius = np.linalg.norm(pts[0] - center) # euclidean distance
        radius = np.sum(np.square(pts[0] - center))  # squared distance
        return center, radius

    def in_circle(self, tri, p):
        """
        Check if point p is inside of precomputed circumcircle of tri.
        """
        center, radius = self.circles[tri]
        return np.sum(np.square(center - p)) <= radius

    def add_point(self, p):
        """
        Add a point to the current DT, and refine it using algorithm.
        """
        p = np.asarray(p)
        idx = len(self.coords)
        # print("coords[", idx,"] ->",p)
        self.coords.append(p)

        # Search the triangle(s) whose circum-circle contains p
        bad_triangles = []
        for T in self.triangles:
            # Choose one method: inCircleRobust(T, p) or inCircleFast(T, p)
            if self.in_circle(T, p):
                bad_triangles.append(T)

        # Find the CCW boundary (star shape) of the bad triangles,
        # expressed as a list of edges (point pairs) and the opposite
        # triangle to each edge.
        boundary = []
        # Choose a "random" triangle and edge
        T = bad_triangles[0]
        edge = 0
        # get the opposite triangle of this edge
        while True:
            # Check if edge of triangle T is on the boundary...
            # if opposite triangle of this edge is external to the list
            tri_op = self.triangles[T][edge]
            if tri_op not in bad_triangles:
                # Insert edge and external triangle into boundary list
                boundary.append((T[(edge + 1) % 3], T[(edge - 1) % 3], tri_op))

                # Move to next CCW edge in this triangle
                edge = (edge + 1) % 3

                # Check if boundary is a closed loop
                if boundary[0][0] == boundary[-1][1]:
                    break
            else:
                # Move to next CCW edge in opposite triangle
                edge = (self.triangles[tri_op].index(T) + 1) % 3
                T = tri_op

        # Remove triangles too near of point p of our solution
        for T in bad_triangles:
            del self.triangles[T]
            del self.circles[T]

        # Retriangle the hole left by bad_triangles
        new_triangles = []
        for (e0, e1, tri_op) in boundary:
            # Create a new triangle using point p and edge extremes
            T = (idx, e0, e1)

            # Store circum-center and circum-radius of the triangle
            self.circles[T] = self.circum_center(T)

            # Set opposite triangle of the edge as neighbour of T
            self.triangles[T] = [tri_op, None, None]

            # Try to set T as neighbour of the opposite triangle
            if tri_op:
                # search the neighbour of tri_op that use edge (e1, e0)
                for i, neigh in enumerate(self.triangles[tri_op]):
                    if neigh:
                        if e1 in neigh and e0 in neigh:
                            # change link to use our new triangle
                            self.triangles[tri_op][i] = T

            # Add triangle to a temporal list
            new_triangles.append(T)

        # Link the new triangles each another
        N = len(new_triangles)
        for i, T in enumerate(new_triangles):
            self.triangles[T][1] = new_triangles[(i + 1) % N]  # next
            self.triangles[T][2] = new_triangles[(i - 1) % N]  # previous

    def get_triangles(self):
        """
        Get the current list of Delaunay triangles
        """
        return [(a - 4, b - 4, c - 4)
                for (a, b, c) in self.triangles if a > 3 and b > 3 and c > 3]

    def export_voronoi_regions(self):
        """Export coordinates and regions of Voronoi diagram as indexed data.
        """
        # Remember to compute circumcircles if not done before
        # for t in self.triangles:
        #     self.circles[t] = self.circumcenter(t)
        useVertex = {i: [] for i in range(len(self.coords))}
        vor_coors = []
        index = {}
        # Build a list of coordinates and one index per triangle/region
        for tidx, (a, b, c) in enumerate(sorted(self.triangles)):
            vor_coors.append(self.circles[(a, b, c)][0])
            # Insert triangle, rotating it so the key is the "last" vertex
            useVertex[a] += [(b, c, a)]
            useVertex[b] += [(c, a, b)]
            useVertex[c] += [(a, b, c)]
            # Set tidx as the index to use with this triangle
            index[(a, b, c)] = tidx
            index[(c, a, b)] = tidx
            index[(b, c, a)] = tidx

        # init regions per coordinate dictionary
        regions = {}
        # Sort each region in a coherent order, and substitude each triangle
        # by its index
        for i in range(4, len(self.coords)):
            v = useVertex[i][0][0]  # Get a vertex of a triangle
            r = []
            for _ in range(len(useVertex[i])):
                # Search the triangle beginning with vertex v
                t = [t for t in useVertex[i] if t[0] == v][0]
                r.append(index[t])  # Add the index of this triangle to region
                v = t[1]  # Choose the next vertex to search
            regions[i - 4] = r  # Store region.

        return vor_coors, regions

    def exportCircles(self):
        """Export the circumcircles as a list of (center, radius)
        """
        # Remember to compute circumcircles if not done before
        # for t in self.triangles:
        #     self.circles[t] = self.circumcenter(t)

        # Filter out triangles with any vertex in the extended BBox
        # Do sqrt of radius before of return
        return [(self.circles[(a, b, c)][0], sqrt(self.circles[(a, b, c)][1]))
                for (a, b, c) in self.triangles if a > 3 and b > 3 and c > 3]


if __name__ == "__main__":
    numSeeds = 12
    radius_loc = 100
    seeds = radius_loc * np.random.random((numSeeds, 2))
    center_loc = np.mean(seeds, axis=0)

    dt2 = Delaunay(center_loc, 50 * radius_loc)
    for i, s in enumerate(seeds):
        print("Inserting seed", i, s)
        dt2.add_point(s)
        time.sleep(0.5)
        if i > 1:
            fig, ax = plt.subplots()
            ax.margins(0.1)
            ax.set_aspect('equal')
            plt.axis([-1, radius_loc + 1, -1, radius_loc + 1])
            for i, v in enumerate(seeds):
                plt.annotate(i, xy=v)  # Plot all seeds
            for t in dt2.get_triangles():
                polygon = [seeds[i] for i in t]  # Build polygon for each region
                plt.fill(*zip(*polygon), fill=False, color="b")  # Plot filled polygon
            for c, r in dt2.exportCircles():
                ax.add_artist(plt.Circle(c, r, color='k', fill=False, ls='dotted'))

            plt.show()

    # Create a plot with matplotlib.pyplot
    fig, ax = plt.subplots()
    ax.margins(0.1)
    ax.set_aspect('equal')
    plt.axis([-1, radius_loc + 1, -1, radius_loc + 1])

    # Plot our Delaunay triangulation (plot in blue)
    cx, cy = zip(*seeds)
    dt_tris = dt2.get_triangles()
    ax.triplot(matplotlib.tri.Triangulation(cx, cy, dt_tris), '-')


    # Build Voronoi diagram as a list of coordinates and regions
    vc, vr = dt2.export_voronoi_regions()

    # Plot voronoi diagram edges (in red)
    for r in vr:
        polygon = [vc[i] for i in vr[r]]  # Build polygon for each region
        plt.fill(*zip(*polygon), alpha=0.2)  # Plot filled polygon
        plt.annotate("r%d" % r, xy=np.average(polygon, axis=0))

    # Dump plot to file
    # plt.savefig('output-delaunay2D.png', dpi=96)
    # plt.savefig('output-delaunay2D.svg', dpi=96)

    plt.show()
