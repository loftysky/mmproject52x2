import maya.cmds as cmds
from sgfs import SGFS


minTime = cmds.playbackOptions(query=True, minTime=True)
maxTime = cmds.playbackOptions(query=True, maxTime=True)
currentTime = cmds.currentTime(1)
#hide poly for faster simulation
hidePoly = cmds.modelEditor('modelPanel4', edit=True, polymeshes=False)

def camRigSetup():
    """
    looks through shotgun for path of latest camera rig set-up.
    """
    sgfs = SGFS()
    sg = sgfs.session
    path = '/Volumes/CGroot/Projects/MM52x2/assets/utilities/Camera_rig/rig/published/maya_scene/camera_rig/'
    cam_entities = sgfs.entities_in_directory(path, entity_type='PublishEvent')
    version = 0
    for i in cam_entities:
        if i[1].fetch('version') > version: 
            version = i[1].fetch('version')
            latest_cam = i[1]
    cam_path = latest_cam.fetch('path')

    if cmds.ls('camRN') == []:
        raise ValueError("no camera called camRN")
    else: 
        if cmds.referenceQuery('camRN', filename=True) != cam_path:
            try: 
                cmds.file(cam_path, loadReference="camRN", type="mayaAscii", options='v=0;')
            except: 
                raise ValueError("Error, no file found.") 

def bakeDynamicJoints():
    """
    bake dynamic joints
    written by Mike Waldrum
    last updated by Kevin Zimny 
    dated Nov 15/2016
    """

    #hide poly for faster simulation
    hidePoly
        
    #select all joints with the suffix "dynbake"
    try: 
        allJoints = cmds.select(cmds.ls('*dynbake*', recursive=True))
    except: 
        print ("no dynbakes found")    

    else:     
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


    #hide poly for faster simulation
    hidePoly

        
    #select bake objects ie. ("*:*" + "*_Ctrl") and delects the flexi ctrls
    try: 
        allBakedObjects = cmds.ls('*:*_Ctrl')

    except: 
        raise ValueError("no Ctrl objects found")

    else: 
        bakedObjects = []
        
        for item in allBakedObjects:
            if 'Flexi' not in item:
                bakedObjects.append(item)

        cmds.select(bakedObjects)
        #bake 
        cmds.BakeSimulation(bakedObjects, time=(str(minTime)+":"+str(maxTime)))
               
        #show poly
        cmds.modelEditor('modelPanel4', edit=True, polymeshes=True)

        #Set the in-tangent and out-tangent on selection
        cmds.keyTangent(edit=True, outTangentType="step")
            
        #set to 24 fps
        cmds.currentUnit(time='film')
        cmds.select(clear=True)

    
def smoothGeo():
    '''
    smooth geo
    written by Kevin Zimny
    last updated : Nov 3 /2016
    selects all geometry, sets smooth level in viewport to 1 and render time smoothing to 3 divisions.
    '''

    #select threeD geo group , because face planes can not be smoothed
    try: 
        cmds.select("*:threeD_geo_grp", hierarchy=True)

    except: 
        raise Exception("no threeD_geo_grp")

    else: 
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

def constrainHead():
    '''
    Constrain any in scene character's head to the main camera
    instructions : just run script
    written by Kevin Zimny
    last updated Nov. 10
    '''

    #selects all the heads in the scene
    try:
        heads = cmds.ls('*:head_Sdk') 
    except:
        raise Exception("no heads!") 
    else:     
        if "cam:MainCAM" in cmds.ls('cam:MainCAM'):
            camera = 'cam:MainCAM'
            for head in heads: 
                cmds.aimConstraint(camera, head, offset=[0, 0, 0], weight=1, aimVector=[0, 0, 1], upVector=[0, 1, 0], worldUpType="object", worldUpObject="cam:MainCAM_up_loc")
        else: 
            raise ValueError("where is the main cam?!")

def shadowLightLinker():
    '''
    shadow light linker
    written by Kevin Zimny
    last updated Nov 16/2016
    select's any character shadow lights light links them to the set group.
    '''

    #select all existing shadow lights and attach to an array
    lights = cmds.ls("*:shadowLight_light")
    lightSets = cmds.ls("*_lightLink*")

    for light in lights: 
        for lightSet in lightSets: 
            cmds.lightlink(light=light, object=lightSet)



def setRender():

    """
    all the functions
    """

    camRigSetup()
    bakeDynamicJoints()
    timeShift()
    smoothGeo()
    constrainHead()
    shadowLightLinker()
