mayamvc
=======

mean value coordinates implementation in Maya WIP

I've implimented Floater's Mean Value Coordinates theorem 1 and 2 in a python script as a prototype
next step is to write a c++ plugin

http://folk.uio.no/martinre/Publications/mv3d.pdf

put mayamvc folder into maya/scripts and run:

import mayamvc.main as mvc
reload(mvc)
mvc.main()

turn on interactive playback or run mvc.update() after moving verts on the cage
