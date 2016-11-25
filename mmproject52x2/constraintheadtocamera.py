'''
Constrain any in scene character's head to the main camera
instructions : just run script
written by Kevin Zimny; revised to Python by Elaine
last updated Nov. 10
'''

import maya.cmds as cmds

heads = cmds.ls('*:head_Sdk') #selects all the heads in the scene

if "cam:MainCAM" in cmds.ls('cam:MainCAM'):
	camera = 'cam:MainCAM' 
else: 
	raise ValueError("where is the main cam?!")

for head in heads: 
	cmds.aimConstraint(camera, head, offset=[0, 0, 0], weight=1, aimVector=[0, 0, 1], upVector=[0, 1, 0], worldUpType="object", worldUpObject="cam:MainCAM_up_loc")
