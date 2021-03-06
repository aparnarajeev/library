'''
Created on Oct 4, 2011

@author: kykamath
'''
import datetime, math
import numpy as n
import matplotlib.pyplot as plt
from graphs import clusterUsingAffinityPropagation
from classes import GeneralMethods
from itertools import groupby
from operator import itemgetter

earthRadiusMiles = 3958.761
earthRadiusKMs = 6371.009
earthCircumferenceInMiles = 24901.55

def plotPointsOnUSMap(points, blueMarble=False, bkcolor='#85A6D9', returnBaseMapObject = False, pointLabels=[], *args, **kwargs):
    from mpl_toolkits.basemap import Basemap
    m = Basemap(llcrnrlon=-125.15625, llcrnrlat=20, urcrnrlon=-59.765625, urcrnrlat=49.61071, projection='mill', lat_1=24, lat_2=50, lon_0=-98, resolution='l', area_thresh=10000)
    m.drawmapboundary(fill_color='#85A6D9')
    
    if blueMarble: m.bluemarble()
    else:
        m.drawmapboundary(fill_color=bkcolor)
        m.fillcontinents(color='white',lake_color=bkcolor)
        m.drawcoastlines(color='#6D5F47', linewidth=.4)
        m.drawcountries(color='#6D5F47', linewidth=.4)
        m.drawstates(color='#6D5F47', linewidth=.4)
    
#    m.fillcontinents(color='white',lake_color='#85A6D9')
#    m.drawstates(color='#6D5F47', linewidth=.4)
#    m.drawcoastlines(color='#6D5F47', linewidth=.4)
#    m.drawcountries(color='#6D5F47', linewidth=.4)
    
#    m.drawmeridians(n.arange(-180, 180, 30), color='#bbbbbb')
#    m.drawparallels(n.arange(-90, 90, 30), color='#bbbbbb')
    lats, lngs = zip(*points)
    
    x,y = m(lngs,lats)
    scatterPlot = m.scatter(x, y, zorder = 2, *args, **kwargs)
    
    for population, xpt, ypt in zip(pointLabels, x, y):
        label_txt = str(population)
        plt.text( xpt, ypt, label_txt, color = 'black', size='small', horizontalalignment='center', verticalalignment='center', zorder = 3)
    if not returnBaseMapObject: return scatterPlot
    else: return (scatterPlot, m)
    
def plotPointsOnWorldMap(points, blueMarble=False, bkcolor='#85A6D9', returnBaseMapObject = False, pointLabels=[], resolution='l', *args, **kwargs):
    from mpl_toolkits.basemap import Basemap
    m = Basemap(projection='mill', llcrnrlon=-180. ,llcrnrlat=-60, urcrnrlon=180. ,urcrnrlat=80, resolution=resolution)
    if blueMarble: m.bluemarble()
    else:
        m.drawmapboundary(fill_color=bkcolor)
        m.fillcontinents(color='white',lake_color=bkcolor)
        m.drawcoastlines(color='#6D5F47', linewidth=.4)
        m.drawcountries(color='#6D5F47', linewidth=.4)
    
    lats, lngs = zip(*points)
    
    x,y = m(lngs,lats)
    scatterPlot = m.scatter(x, y, zorder = 2, *args, **kwargs)
    for population, xpt, ypt in zip(pointLabels, x, y):
        label_txt = str(population)
        plt.text( xpt, ypt, label_txt, color = 'black', size='small', horizontalalignment='center', verticalalignment='center', zorder = 3)
    if not returnBaseMapObject: return scatterPlot
    else: return (scatterPlot, m)

def plot_graph_clusters_on_world_map(graph, s=0, lw=0, alpha=0.6, bkcolor='#CFCFCF', *args, **kwargs):  
    no_of_clusters, tuples_of_location_and_cluster_id = clusterUsingAffinityPropagation(graph)
    map_from_location_to_cluster_id = dict(tuples_of_location_and_cluster_id)
    map_from_cluster_id_to_cluster_color = dict([(i, GeneralMethods.getRandomColor()) for i in range(no_of_clusters)])
    points, colors = zip(*map(lambda  location: (getLocationFromLid(location.replace('_', ' ')), map_from_cluster_id_to_cluster_color[map_from_location_to_cluster_id[location]]), graph.nodes()))
    _, m = plotPointsOnWorldMap(points, c=colors, s=s, lw=lw, returnBaseMapObject=True,  *args, **kwargs)
    for u, v, data in graph.edges(data=True):
        if map_from_location_to_cluster_id[u]==map_from_location_to_cluster_id[v]:
            color, u, v, w = map_from_cluster_id_to_cluster_color[map_from_location_to_cluster_id[u]], getLocationFromLid(u.replace('_', ' ')), getLocationFromLid(v.replace('_', ' ')), data['w']
            m.drawgreatcircle(u[1], u[0], v[1], v[0], color=color, alpha=alpha)
    return (no_of_clusters, tuples_of_location_and_cluster_id)
    
def parseData(line):
    data = line.strip().split('\t')
    if len(data)!=7: data.append(None) 
    if len(data)==7: return {'_id':id, 'u': int(data[0]), 'tw': int(data[1]), 'l': [float(data[2]), float(data[3])], 't': datetime.datetime.strptime(data[4], '%Y-%m-%d %H:%M:%S'), 'x': data[5], 'lid': data[6]}

def getLidFromLocation(location): return '%0.3f %0.3f'%(location[0], location[1])
def getLocationFromLid(lid): return [float(l) for l in lid.split()]
def convertMilesToRadians(miles): return miles/earthRadiusMiles
def convertRadiansToMiles(radians): return radians*earthRadiusMiles
def convertKMsToRadians(kms): return kms/earthRadiusKMs
def convertRadiansToKMs(radians): return radians*earthRadiusKMs
def isWithinBoundingBox(point, boundingBox):
    '''
    point [x,y]
    boundingBox = [[lower left][upper right]]
    '''
    lowerLeftPoint, upperRightPoint = boundingBox
    return lowerLeftPoint[0]<=point[0]<=upperRightPoint[0] and lowerLeftPoint[1]<=point[1]<=upperRightPoint[1]

def convexHull(points, smidgen=0.0075):
    '''Calculate subset of points that make a convex hull around points

        Recursively eliminates points that lie inside two neighbouring points until only convex hull is remaining.
        
        :Parameters:
            points : ndarray (2 x m)
                array of points for which to find hull
            smidgen : float
                offset for graphic number labels - useful values depend on your data range
        
        :Returns:
            hull_points : ndarray (2 x n)
                convex hull surrounding points
                
        Code obtained from: http://www.scipy.org/Cookbook/Finding_Convex_Hull
    '''
    def _angle_to_point(point, centre):
        '''calculate angle in 2-D between points and x axis'''
        delta = point - centre
        res = n.arctan(delta[1] / delta[0])
        if delta[0] < 0:
            res += n.pi
        return res
    def area_of_triangle(p1, p2, p3):
        '''calculate area of any triangle given co-ordinates of the corners'''
        return n.linalg.norm(n.cross((p2 - p1), (p3 - p1)))/2.
    n_pts = points.shape[1]
    assert(n_pts > 5)
    centre = points.mean(1)
    angles = n.apply_along_axis(_angle_to_point, 0, points, centre)
    pts_ord = points[:,angles.argsort()]
    pts = [x[0] for x in zip(pts_ord.transpose())]
    prev_pts = len(pts) + 1
    k = 0
    while prev_pts > n_pts:
        prev_pts = n_pts
        n_pts = len(pts)
        i = -2
        while i < (n_pts - 2):
            Aij = area_of_triangle(centre, pts[i],     pts[(i + 1) % n_pts])
            Ajk = area_of_triangle(centre, pts[(i + 1) % n_pts], \
                                   pts[(i + 2) % n_pts])
            Aik = area_of_triangle(centre, pts[i],     pts[(i + 2) % n_pts])
            if Aij + Ajk < Aik:
                del pts[i+1]
            i += 1
            n_pts = len(pts)
        k += 1
    return n.asarray(pts)

def geographicConvexHull(points): return convexHull(n.array(zip(*points)))

def getHaversineDistanceForLids(lid1, lid2, radius=earthRadiusMiles): return getHaversineDistance(getLocationFromLid(lid1), getLocationFromLid(lid2))
def getHaversineDistance((lon1, lat1), (lon2, lat2), radius=earthRadiusMiles):
    '''
    Got this code from
    '''
    try:
    #    print (lon1, lat1), (lon2, lat2)
        if str(lon1)==str(lon2) and str(lat1)==str(lat2): return 0.0
    #    if '%0.5f'%(lon1)=='%0.5f'%(lon2) and '%0.5f'%(lat1)=='%0.5f'%(lat2): return 0.0
        p1lat, p1lon = math.radians(lat1), math.radians(lon1)
        p2lat, p2lon = math.radians(lat2), math.radians(lon2)
        return radius * math.acos(math.sin(p1lat) * math.sin(p2lat) + math.cos(p1lat) * math.cos(p2lat) * math.cos(p2lon - p1lon))
    except: return 0.0
    
def getCenterOfMass(points, accuracy=10**-6, error=False): 
    com = getLattice(n.mean(points,0), accuracy=accuracy)
    if not error: return com
    else:
        meanDistance = n.mean([getHaversineDistance(com, p) for p in points])
        return (com, meanDistance)

def breakIntoLattice(boundingBox, latticeDimensions):
    '''latticeDimensions = [x,y] will break bounding box into x*y boxes
    '''
    lowerLeft, upperRight = boundingBox
    numberOfX, numberOfY = latticeDimensions
    y_length = n.abs(upperRight[0]-lowerLeft[0])
    x_length = n.abs(upperRight[1]-lowerLeft[1])
    yUnitLength, xUnitLength = y_length/float(numberOfY), x_length/float(numberOfX)
    yCoords = [lowerLeft[1]]
    for i in range(numberOfY): yCoords.append(yCoords[-1]+yUnitLength)
    xCoords = [lowerLeft[0]]
    for i in range(numberOfX): xCoords.append(xCoords[-1]+xUnitLength)
    i = 0
    ar = []
    for x in xCoords:
        tempAr = []
        for y in yCoords:
            tempAr.append([x,y])
        ar.append(tempAr)
    latticeBoundingBoxes = []
    for i in range(len(xCoords)):
        for j in range(len(yCoords)):
            if i+1<len(xCoords) and j+1<len(yCoords): 
                latticeBoundingBoxes.append([ar[i][j], ar[i+1][j+1]])
    return (latticeBoundingBoxes, xUnitLength, yUnitLength)

def getLatticeBoundingBoxFor(boundingBox, latticeDimensions, point):
    lowerLeft, upperRight = boundingBox
    numberOfX, numberOfY = latticeDimensions
    x_length = n.abs(upperRight[1]-lowerLeft[1])
    y_length = n.abs(upperRight[0]-lowerLeft[0])
    yUnitLength, xUnitLength = y_length/float(numberOfY), x_length/float(numberOfX)
    
def getRadiusOfGyration(points):
    if not points: return None
    centerOfMass = getCenterOfMass(points)
    return math.sqrt((sum(getHaversineDistance(centerOfMass, point)**2 for point in points))/len(points))

def getLattice(point, accuracy=0.0075):
    ''' Accuracy in miles getHaversineDistance([0, 0], [0, 0.0075])
    '''
    return [int(point[0]/accuracy)*accuracy, int(point[1]/accuracy)*accuracy]

def getLatticeLid(point, accuracy=0.0075):
    ''' Accuracy in miles getHaversineDistance([0, 0], [0, 0.0075])
    '''
    return '%0.4f_%0.4f'%(int(point[0]/accuracy)*accuracy, int(point[1]/accuracy)*accuracy)
def point_inside_polygon(x,y,poly):
    ''' Got this code from http://www.ariel.com.au/a/python-point-int-poly.html .
    poly = [[x1,y1], [x2, y2], ...]
    '''
    n = len(poly)
    inside =False
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside
#print breakIntoLattice([[0,-10], [10,0]], [2,2])
#getLatticeBoundingBoxFor([[0,-10], [10,0]], [2,2], [2.5, -7.5])
#print convertRadiansToMiles(49-24)
#print getLatticeLid([30.436834,-98.242493], 0.725)
#print getLatticeLid([30.259067,-97.695923], 0.725)
#print getLatticeLid([3.141545,101.691685], 0.725)
#print getLattice([37.073,-122.640381])
#print getHaversineDistance([0., 1.45], [0.,0.])
#print getHaversineDistance([37.699999999999996, -122.23499999999999], [37.700000000000003, -122.235])
#print getCenterOfMass([[-115.303551,36.181283],[-115.297509,36.181283],[-115.297509,36.186214],[-115.303551,36.186214]], error=True, accuracy=0.5)
#print getHaversineDistance((33.747123999999999, -84.379047), (33.747124669999998, -84.379047))
#print breakIntoLattice([[40.491, -74.356], [41.181, -72.612]], [250,100])[1:]
