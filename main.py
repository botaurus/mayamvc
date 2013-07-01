"""
:Danny Wynne
:dannywynne.com

Mean value coordinates implimatation prototype

DESCRIPTION: 
    This script is a python implimation of this paper:
        http://folk.uio.no/martinre/Publications/mv3d.pdf
    Helpful website to ease the maths:
        http://www.ams.org/samplings/feature-column/fcarc-harmonic

    The script also sets up the maya scene.

USAGE:
    usage

"""
import cgcg_rigging.lib.utils as u
import maya.OpenMaya as om
from math import *
import maya.cmds as cmds

def wi(v,vi,tris):
    #calculates the weights
    #v = kernal of the starshaped polyhedron. this is the point that will be deformed
    #vi = the current vert we are iterating over on the bounding polyhedron
    #tris = all triangle facets on the polyhedron that vi is a member of
    def A(vr,vs):
        #get an angle
        vec1 = vr-v
        vec2 = vs-v
        return vec1.angle(vec2)
    def N(vr, vs):
        #get the normal
        vecr = vr-v
        vecs = vs-v
        norm = vecr^vecs
        norm.normalize()
        return norm
    
    def ut(i,j,k):
        #floater's equation for ut
        vecvi = (v-i)
        vecvi.normalize()
        top = A(j,k) + A(i,j)*( N(i, j)*N(j, k) ) + A(k,i)*(N(k, i)*N(j, k))
        bot = 2*( vecvi*N(j,k) )
        return top/bot
    ''' 
    def ut(i,j,k):
        #this gets the area of a triangle, it is no more accurate than the above implimatation of Float's equation
        a, b, c = i.distanceTo(j), j.distanceTo(k), k.distanceTo(i)
        p = (a+b+c)/2
        return sqrt( p*(p-a)*(p-b)*(p-c) )
    ''' 
    ri = v.distanceTo(vi)
    ut_sum = 0
    for t in tris:
        ut_sum += ut(t[0], t[1], t[2])
    print "\n"
    return ut_sum/ri

class MVC():
    def __init__(self):
        #this is our main vert, the one that will be deformed
        self.v = u.pnt("v")
        self.bary = self.get_bary()

    def update(self):
        v = self.v
        #refresh the list p with the current location of the locators in maya
        p = [u.pnt("v0"), u.pnt("v1"), u.pnt("v2"), u.pnt("v3")]
        x,y,z = 0,0,0
        for i in range(len(p)):
            x += p[i].x*self.bary[i]
            y += p[i].y*self.bary[i]
            z += p[i].z*self.bary[i]
        #place a new locator at the deformed position
        u.loc(om.MPoint(x, y, z))

    def get_bary(self):
        v = self.v
        #get 4 points from maya that represent a polygon
        p = [u.pnt("v0"), u.pnt("v1"), u.pnt("v2"), u.pnt("v3")]
        #create a list of verts and all triangles that that vert is a memeber of
        #the triangels are i,j,k, going counter clock wise, and i = the associated vert that will be iterated over
        vert_tri=[
        [p[0], [(p[0], p[1], p[2]), (p[0], p[3], p[1]), (p[0], p[2], p[3]),]],
        [p[1], [(p[1], p[2], p[0]), (p[1], p[3], p[2]), (p[1], p[0], p[3]),]],
        [p[2], [(p[2], p[0], p[1]), (p[2], p[1], p[3]), (p[2], p[3], p[0]),]],
        [p[3], [(p[3], p[2], p[1]), (p[3], p[1], p[0]), (p[3], p[0], p[2]),]],
        ]

        #verify in maya that all triangles are counter clockwise, normal outward, and begin with the
        #same vert, the one that will be iterated over
        new_vert_tri = []
        for vt in vert_tri:
            new_triangles = []
            for tt in vt[1]:
                t= list(tt)
                #t.reverse()
                #_tmp = [t[2], t[0], t[1]]
                _tmp = t
                new_triangles.append(_tmp)
                v1,v2,v3 = _tmp[0],_tmp[1],_tmp[2]
                cmds.polyCreateFacet(p=[(v1.x, v1.y, v1.z), (v2.x, v2.y, v2.z), (v3.x, v3.y, v3.z)])
                print v1.x, v1.y, v1.z
            print vt[0].x, vt[0].y, vt[0].z
            print "\n"
            new_vert_tri.append([vt[0], new_triangles])

        #get the weight
        weights = []
        for vt in new_vert_tri:
            t= list(vt[1])
            t.reverse()
            weights.append(wi(v, vt[0], t))

        #get the bary weights
        bary_weights=[]
        weights_sum = sum(weights)
        for w in weights:
            bary_weights.append(w/weights_sum)
        return bary_weights