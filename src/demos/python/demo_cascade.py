#-------------------------------------------------------------------------------
# Name:        modulo1
# Purpose:
#
# Author:      tasora
#
# Created:     14/02/2012
# Copyright:   (c) tasora 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

def main():
    pass

if __name__ == '__main__':
    main()


import os
import math
import pychrono.core as chrono
import pychrono.irrlicht as chronoirr
import pychrono.cascade as cascade
from OCC.Core.TopoDS import TopoDS_Shape

print ("Example: create a system and visualize it in realtime 3D");

# ---------------------------------------------------------------------
#
#  Create the simulation system and add items
#

mysystem      = chrono.ChSystemNSC()

# Load a STEP file, containing a mechanism. The demo STEP file has been
# created using a 3D CAD (in this case, SolidEdge v.18).
#

# Create the ChCascadeDoc, a container that loads the STEP model
# and manages its subassembles
mydoc = cascade.ChCascadeDoc()

chrono.SetChronoDataPath("C:/tasora/code/projectchrono/chrono/data/")

# load the STEP model using this command:
load_ok = mydoc.Load_STEP(chrono.GetChronoDataFile("cascade/assembly.stp"));  # or specify abs.path: ("C:\\data\\cascade\\assembly.stp");

# print the contained shapes
#mydoc.Dump(chrono.GetLog())


CH_C_PI = 3.1456

# In most CADs the Y axis is horizontal, but we want it vertical.
# So define a root transformation for rotating all the imported objects.
rotation1 = chrono.ChQuaternionD()
rotation1.Q_from_AngAxis(-CH_C_PI / 2, chrono.ChVectorD(1, 0, 0));  # 1: rotate 90° on X axis
rotation2 = chrono.ChQuaternionD()
rotation2.Q_from_AngAxis(CH_C_PI, chrono.ChVectorD(0, 1, 0));  # 2: rotate 180° on vertical Y axis
tot_rotation = chrono.ChQuaternionD()
tot_rotation = rotation2 % rotation1     # rotate on 1 then on 2, using quaternion product
root_frame = chrono.ChFrameMovingD(chrono.ChVectorD(0, 0, 0), tot_rotation);

# Retrieve some sub shapes from the loaded model, using
# the GetNamedShape() function, that can use path/subpath/subsubpath/part
# syntax and * or ? wildcards, etc.

mrigidBody1 = 0
mrigidBody2 = 0

if load_ok: 
    
    shape1 = TopoDS_Shape()
    if (mydoc.GetNamedShape(shape1, "Assem1/body1")):
        
        mbody1 = mydoc.CreateBodyFromShape(shape1,1000, False, True)
        # or: mbody1 = cascade.ChBodyEasyCascade(shape1, 1000, False, True)
        mysystem.Add(mbody1)
        
        mbody1.SetBodyFixed(True) 
        
        # Move the body as for global displacement/rotation (also mbody1 %= root_frame; )
        mbody1.ConcatenatePreTransformation(root_frame);
        
        mrigidBody1= mbody1;
        
    else:
        print("Warning. Desired object not found in document \n")

    shape2 = TopoDS_Shape()
    if (mydoc.GetNamedShape(shape2, "Assem1/body2")): 
        
        mbody2 = mydoc.CreateBodyFromShape(shape2,1000, False, True)
        # or: mbody2 = cascade.ChBodyEasyCascade(shape2, 1000, False, True)
        mysystem.Add(mbody2)
        
        # Move the body as for global displacement/rotation  (also mbody2 %= root_frame; )
        mbody2.ConcatenatePreTransformation(root_frame);

        mrigidBody2= mbody2;
        
    else:
        print("Warning. Desired object not found in document \n")

else:
    print("Warning. Desired STEP file could not be opened/parsed \n")

# Create a revolute joint between the two parts
# as in a pendulum. We assume we already know in advance
# the aboslute position of the joint (ex. we used measuring tools in the 3D CAD)

measured_joint_pos_mm = chrono.ChVectorD(0, 48, 120);

scale = 1. / 1000.  # because we use meters instead of mm

joint_pos = chrono.ChVectorD(root_frame.TransformPointLocalToParent(measured_joint_pos_mm * scale)) 
                             # transform because we rotated everything

if (mrigidBody1 and mrigidBody2):
    my_link = chrono.ChLinkLockRevolute()
    my_link.Initialize(mrigidBody1, mrigidBody2, chrono.ChCoordsysD(joint_pos));
    mysystem.Add(my_link);


# Create a large cube as a floor.

mfloor = chrono.ChBodyEasyBox(1, 0.2, 1, 1000)
mfloor.SetPos(chrono.ChVectorD(0,-0.3,0))
mfloor.SetBodyFixed(True)
mysystem.Add(mfloor)

mcolor = chrono.ChColorAsset(0.3, 0.3, 0.8)
mfloor.AddAsset(mcolor)



# ---------------------------------------------------------------------
#
#  Create an Irrlicht application to visualize the system
#

myapplication = chronoirr.ChIrrApp(mysystem, 'Test', chronoirr.dimension2du(1024,768))

myapplication.AddTypicalSky(chrono.GetChronoDataPath() + 'skybox/')
myapplication.AddTypicalCamera(chronoirr.vector3df(0.2,0.2,-0.2))
myapplication.AddTypicalLights()

            # ==IMPORTANT!== Use this function for adding a ChIrrNodeAsset to all items
			# in the system. These ChIrrNodeAsset assets are 'proxies' to the Irrlicht meshes.
			# If you need a finer control on which item really needs a visualization proxy in
			# Irrlicht, just use application.AssetBind(myitem); on a per-item basis.

myapplication.AssetBindAll();

			# ==IMPORTANT!== Use this function for 'converting' into Irrlicht meshes the assets
			# that you added to the bodies into 3D shapes, they can be visualized by Irrlicht!

myapplication.AssetUpdateAll();


# ---------------------------------------------------------------------
#
#  Run the simulation
#


myapplication.SetTimestep(0.01)


while(myapplication.GetDevice().run()):
    myapplication.BeginScene()
    myapplication.DrawAll()
    myapplication.DoStep()
    myapplication.EndScene()





