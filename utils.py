import maya.OpenMaya as om
import maya.cmds as cmds

def pnt(obj):
	return om.MPoint(*cmds.xform(obj, q=1,t=1, ws=1)[0:3])


def loc(pnt=None, scale=.1, color = None, name = "locator"):
	loc = cmds.spaceLocator(name=name)[0]

	if type(pnt).__name__ == "MPoint":
		cmds.setAttr(loc+".t", pnt.x, pnt.y, pnt.z)
	elif type(pnt).__name__ == "list" or type(pnt).__name__ == "tuple":
		cmds.setAttr(loc+".t", pnt[0], pnt[1], pnt[2])

	cmds.setAttr(loc+".localScale", scale, scale, scale)
	if color:
		if type(color).__name__ == "str":
			set_color(color, loc)
		else:
			cmds.setAttr(loc+".overrideEnabled", 1)
			cmds.setAttr(loc+".overrideColor", color)
	return loc