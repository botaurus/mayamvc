"""
:Danny Wynne
:dannywynne.com

Mean value coordinates implimatation prototype

DESCRIPTION: 
	This script is a python implimation of part of this paper:
		http://folk.uio.no/martinre/Publications/mv3d.pdf
	Theorems 1 and 2 at the top of page 4

	Helpful website to ease the maths:
		http://www.ams.org/samplings/feature-column/fcarc-harmonic

	The script also sets up the maya scene.

USAGE:
	put mayamvc folder into maya/scripts and run:

import mayamvc.main as mvc
reload(mvc)
mvc.main()

	turn on interactive playback or run mvc.update() after moving verts on the cage


"""
#import cgcg_rigging.lib.utils as u
import maya.OpenMaya as om
from math import *
import maya.cmds as cmds
import utils

reload(utils)

mvc_node = None

def ut(v,vi,tris):
	"""calculates the value that is used to get the barycentric coordinates
	Args:
		v(MPoint) = kernal of the starshaped polyhedron. this is the point that will be deformed
		vi(MPoint) = the current vert we are iterating over on the bounding polyhedron
		tris(list of MPoints) = all triangle facets on the polyhedron that vi is a member of
	"""
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
	
	def _ut(i,j,k):
		#floater's equation for ut
		vecvi = (v-i)
		vecvi.normalize()
		top = A(j,k) + A(i,j)*( N(i, j)*N(j, k) ) + A(k,i)*(N(k, i)*N(j, k))
		bot = 2*( vecvi*N(j,k) )
		return top/bot

	ri = v.distanceTo(vi)
	ut_sum = 0
	for t in tris:
		ut_sum += _ut(t[0], t[1], t[2])
	return ut_sum/ri

class MVC():
	def __init__(self, cage, loc):
		"""set weights and update mean value coordinates for a point in a cage
		Args:
			cage(MayaPolyWrapper) - deform this then call update to
		"""
		self.cage = cage
		self.loc = loc
		self.calculate_bary_coords()

	def update(self):
		#refresh the list p with the current location of the locators in maya
		pnts = self.cage.get_vert_pnts()

		x,y,z = 0,0,0
		for i in range(len(pnts)):
			x += pnts[i].x*self.bary[i]
			y += pnts[i].y*self.bary[i]
			z += pnts[i].z*self.bary[i]

		cmds.setAttr(self.loc+".t", x,y,z)
		

	def calculate_bary_coords(self):
		pnt_map = self.cage.get_poly_pnt_map()
		#calculate ut
		ut_values = []
		for m in pnt_map:
			tris= list(m[1])
			tris.reverse()
			ut_values.append(ut(utils.pnt(self.loc), m[0], tris))

		#barycentric coordinates
		bary=[]
		ut_sum = sum(ut_values)
		for u in ut_values:
			bary.append(u/ut_sum)

		self.bary = bary

class MayaPolyWrapper():
		"""interface wrapper for mvc to use maya polygons
	
		Args:
			poly_map [[vert, [all triangles that contain this vert],] - map of all verts
				in the poly and the tris they are a member of
		"""
		def __init__(self, poly_map):
			self.poly_map = poly_map

		def get_poly_pnt_map(self):
			"""return poly_map as MPoints
			"""
			pnt_map = []
			for m in self.poly_map:
				tris = []
				for t in m[1]:
					tris.append([utils.pnt(x) for x in t])
				pnt_map.append([utils.pnt(m[0]), tris])
			return pnt_map

		def get_vert_pnts(self):
			"""return list of verts pos as MPoints
			"""
			return [utils.pnt(x[0]) for x in self.poly_map]



def setup_scene():
	#manually create a simple tetrahedron 
	p1 = cmds.polyCreateFacet(p=[(0,0,0), (1,0,0), (0,0,1)])
	p2 = cmds.polyCreateFacet(p=[(0,0,0), (0,1,0), (1,0,0)])
	p3 = cmds.polyCreateFacet(p=[(0,0,0), (0,0,1), (0,1,0)])
	p4 = cmds.polyCreateFacet(p=[(0,0,1), (1,0,0), (0,1,0)])
	cmds.polyMergeVertex(cmds.polyUnite(p1,p2,p3,p4, ch=0, name = "cage"), ch=0)
	poly_map =[
		["cage.vtx[0]", [ 	("cage.vtx[0]","cage.vtx[2]","cage.vtx[3]"),
							("cage.vtx[0]","cage.vtx[3]","cage.vtx[1]"),
							("cage.vtx[0]","cage.vtx[1]","cage.vtx[2]"),
						]
		],
		["cage.vtx[1]", [ 	("cage.vtx[1]","cage.vtx[0]","cage.vtx[3]"),
							("cage.vtx[1]","cage.vtx[3]","cage.vtx[2]"),
							("cage.vtx[1]","cage.vtx[2]","cage.vtx[0]"),
						]
		],
		["cage.vtx[2]", [ 	("cage.vtx[2]","cage.vtx[3]","cage.vtx[0]"),
							("cage.vtx[2]","cage.vtx[1]","cage.vtx[3]"),
							("cage.vtx[2]","cage.vtx[0]","cage.vtx[1]"),
						]
		],
		["cage.vtx[3]", [ 	("cage.vtx[3]","cage.vtx[2]","cage.vtx[1]"),
							("cage.vtx[3]","cage.vtx[1]","cage.vtx[0]"),
							("cage.vtx[3]","cage.vtx[0]","cage.vtx[2]"),
						]
		]
		]
	#debug tetra
	"""
	for p in poly_map:
		tris = p[1]
		for t in tris:
			pnts = []
			for vert in t:
				pnt = utils.pnt(vert)
				pnts.append([pnt.x, pnt.y, pnt.z])
			cmds.polyCreateFacet(p=pnts)
	"""

	cage = MayaPolyWrapper(poly_map)
	loc = utils.loc([.1,.1,.1])
	return cage, loc


def main():
	global mvc_node
	cage, loc = setup_scene()
	mvc_node = MVC(cage, loc)
	cmds.expression(s='python("mvc.update()");')

def update():
	mvc_node.update()
