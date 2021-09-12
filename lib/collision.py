import numpy as np
from math import acos, atan2, degrees, sqrt
from matplotlib.patches import Ellipse

def locusCollision(plt, axs, polys):
    # Despite the waves, collision height is static at 75, so we can cope with all polys
    # Draws them overlapping coz cba and actually it looks pretty cool now
    # Returns the list of positions for use in the checkpointing code

    ellipseCentres = []

    # Gather points with the polys that they belong to
    polysFor = dict()
    normals = []

    for i,poly in enumerate(polys):
        for pnt in poly:
            l = polysFor[pnt] = polysFor.get(pnt, [])
            l.append(i)

        a,b,c,d = poly
        n = np.cross(np.subtract(b,a), np.subtract(c,a))
        normals.append(n)

    # Restructure into a map (poly, poly) -> (point, point) of intersection
    intersection = dict()

    for pnt,polyPair in polysFor.items():
        assert len(polyPair) == 2
        polyPair.sort()
        polyPair = tuple(polyPair)
        l = intersection[polyPair] = intersection.get(polyPair, [])
        l.append(pnt)

    polyVerticals = [[] for _ in polys]

    # Make our cylinders, draw our ellipses
    for (i,j),pnts in intersection.items():
        assert len(pnts) == 2

        # Arrange AB upwards
        a,b = pnts
        AB = np.subtract(b,a)
        y = AB[1]
        if y < 0:
            AB = np.multiply(AB, -1)
            a,b = b,a

        # Store the verticals for use below
        polyVerticals[i].append((a,b))
        polyVerticals[j].append((a,b))

        # Find the point which is at the collision height, 75
        assert a[1] < 75 < b[1]
        c = np.add(a, np.multiply(AB, (75-a[1]) / AB[1]))
        c = c[::2]
        ellipseCentres.append(c)

        # Draw the ellipse
        x,y,z = AB
        cosA = y / np.linalg.norm(AB)
        ang = degrees(atan2(x,-z))

        x,z = c
        axs.add_artist(Ellipse(xy=(x,-z),
                        width=200/cosA, height=200,
                        angle=90-ang,lw=1,edgecolor='r',fill=False))

        
    # And then draw the straight edges
    # Note that our 'lean' is different to the intersection! This was our issue
    for verticals,poly,n in zip(polyVerticals, polys, normals):
        y = n[1]
        if y < 0:
            n = np.multiply(n, -1)

        # Compute the seperation at this point BELOW the collision height which we're nearest
        sinA = y / np.linalg.norm(n)    
        cosA = sqrt(1 - sinA*sinA)      # != cosA for the cylinders, even if all quads are leant equally

        xz_sep = 100 * cosA

        # Find this point at each end
        h = 75 - (100 * sinA)
        edge = []
        atCollHeight = []
        for (a,b) in verticals:
            assert a[1] < h < b[1]
            v = np.subtract(b,a)
            edge.append( np.add(a, np.multiply(v, (h-a[1]) / v[1] )))
            assert np.isclose(edge[-1][1], h)
            edge[-1] = edge[-1][::2]
            atCollHeight.append( np.add(a[::2], np.multiply(v[::2], (75-a[1]) / v[1] )))
        
        # Flatten and scale
        n = n[::2]
        n = np.multiply(n, 1 / np.linalg.norm(n))

        
        # Draw the line at the collision height just for reference
        xs, zs = zip(*atCollHeight)
        zs = [-z for z in zs]
        plt.plot(xs, zs, linewidth=0.5, color='k')

        # Edge just on the near side (ASSUMES leant outwards)
        # NOTE that the outer edge will be too far in as we draw it,
        #   since we'd need to use the point above the collision height
        # but we don't care about that :P so we just omit drawing it
        inner_edge = [np.add(p,np.multiply(n, xz_sep)) for p in edge]
        xs, zs = zip(*inner_edge)
        zs = [-z for z in zs]
        plt.plot(xs, zs, linewidth=1, color='r')


    return ellipseCentres