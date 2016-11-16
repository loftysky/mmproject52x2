import maya.cmds as cmds



def camRigSetup():
	#camera rig setup

	if cmds.referenceQuery('camRN', filename=True) != "/Volumes/CGroot/Projects/MM52x2/assets/utilities/Camera_rig/rig/published/maya_scene/camera_rig/v0005/Camera_rig,rig,v0005.ma":
	    cmds.file("/Volumes/CGroot/Projects/MM52x2/assets/utilities/Camera_rig/rig/published/maya_scene/camera_rig/v0005/Camera_rig,rig,v0005.ma", loadReference="camRN", type="mayaAscii", options="v=0;")


 def bakeDynamicJoints():
 	#bake dynamic joints
	#written by Mike Waldrum
	#last updated by Kevin Zimny 
	#dated Nov 15/2016
	#find the start and end frame of the timeslider
	minTime = cmds.playbackOptions(query=True, minTime=True)
	maxTime = cmds.playbackOptions(query=True, maxTime=True)

	    
	#hide poly for faster simulation
	cmds.modelEditor('modelPanel4', edit=True, polymeshes=False)

	#select all joints with the suffix "dynbake"
	allJoints = cmds.select(cmds.ls('*dynbake*', recursive=True))    

	#bake 
	cmds.BakeSimulation(allJoints, time=(str(minTime)+":"+str(maxTime)))
	    
	 #Set the in-tangent and out-tangent on selection
	cmds.keyTangent(edit=True, outTangentType="step")
	    
	#show poly
	cmds.modelEditor('modelPanel4', edit=True, polymeshes=True)
	cmds.select(clear=True)
	    
	
def timeShift():
	#12 fps to 24 fps
	#written By kevin Zimny
	#last updated Nov 11 2016 
	#instructions : just run script

	#ind the start and end frame of the timeslider
	minTime = cmds.playbackOptions(query=True, minTime=True)
	maxTime = cmds.playbackOptions(query=True, maxTime=True)

	#hide poly for faster simulation
	cmds.modelEditor('modelPanel4', edit=True, polymeshes=False)

	    
	#select bake objects ie. ("*:*" + "*_Ctrl")
	bakeObjects = cmds.ls('*_Ctrl')
	    
	#bake 
	cmds.BakeSimulation(bakeObjects, time=(str(minTime)+":"+str(maxTime)))
	    
	#show poly
	cmds.modelEditor('modelPanel4', edit=True, polymeshes=True)

	#Set the in-tangent and out-tangent on selection
	cmds.keyTangent(edit=True, outTangentType="step")
	    
	#set to 24 fps
	cmds.currentUnit(time='film')
	    
	#set startframe to 1
	cmds.playbackOptions(query=True, minTime=True)
	cmds.select(clear=True)


'''
  //smooth geo
    //written by Kevin Zimny
    //last updated : Nov 3 /2016
    //selects all geometry, sets smooth level in viewport to 1 and render time smoothing to 3 divisions.
 '''

def smoothGeo():

#select threeD geo group , because face planes can not be smoothed
	cmds.select("*:threeD_geo_grp", hierarchy=True)

	transforms = cmds.ls(selection=True, transforms=True)
	polyMeshes = cmds.filterExpand(transforms, selectionMask=12)

#for everything selected sets smooth level in viewport to 1 and render time smoothing to 3 divisions.
	for item in polyMeshes:
	    cmds.setAttr(str(item) + ".smoothLevel", 0)
	    cmds.setAttr(str(item) + ".displaySmoothMesh", 1)
	    cmds.setAttr(str(item) + ".renderSmoothLevel", 3)

	cmds.select(clear=True)

#set render settings
#color management off
    
	cmds.colorManagementPrefs(edit=True, cmEnabled=False)
    
#Loads mentalRay if not yet active
     
	if 'Mayatomr' not in cmds.pluginInfo( query=True, listPlugins=True ):
    	cmds.loadPlugin("Mayatomr") 
 
  
     
#sets Renderer to MentalRay
    cmds.setAttr('defaultRenderGlobals.currentRenderer', 'mentalRay', type="string")
