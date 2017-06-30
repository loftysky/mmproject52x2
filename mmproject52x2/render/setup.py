import os

from mayatools import context
from mayatools import units
from sgfs import SGFS
from sgpublish.check import check_paths

from maya import cmds


steps = []
def _step(func):
    steps.append(func)
    return func


def _get_reference(namespace):
    """Get the (ref_node, filename) for a reference with the given namespace.

    :raises: ``ValueError`` if no reference exists with the given namespace.

    """

    namespace = ':' + namespace.strip(':')

    for filename in cmds.file(query=True, reference=True) or ():
        try:
            this_namespace = cmds.referenceQuery(filename, namespace=True)
        except RuntimeError as e:
            # We need a namespace, so screw it.
            continue
        if namespace == this_namespace:
            node = cmds.referenceQuery(filename, referenceNode=True)
            return node, filename

    raise ValueError(namespace)


@_step
def disable_hud_expressions():
    for node in cmds.ls(type='expression') or ():
        expr = cmds.getAttr(node + '.expression') or ''
        if expr.strip().startswith('headsUpDisplay'):
            print 'Deleting', node
            cmds.delete(node)


@_step
def fetch_newest_camera():
    """Update the camera rig to the newest version in Shotgun."""

    # Note that we need to do this manually because there are a pile of shots
    # that do not have the camera referenced at all.

    try:
        cam_ref_node, current_cam_path = _get_reference(':cam')
    except ValueError:
        raise ValueError("No \"cam\" namespace.")

    sgfs = SGFS()

    path = '/Volumes/CGroot/Projects/MM52x2/assets/utilities/Camera_rig/rig/published/maya_scene/camera_rig/'
    found = sgfs.entities_in_directory(path, entity_type='PublishEvent')
    if not found:
        raise ValueError("No camera publishes?!")

    publishes = [e for path, e in found]
    sgfs.session.fetch(publishes, ['path', 'created_at'])
    publishes.sort(key=lambda e: e['created_at'])
    latest_cam_path = publishes[-1].fetch('path')

    if current_cam_path == latest_cam_path:
        print '    Up to date.'
        return
    
    print '    Updating to', latest_cam_path     
    type_ = 'mayaAscii' if latest_cam_path.endswith('.ma') else 'mayaBinary'
    cmds.file(latest_cam_path, loadReference=cam_ref_node, type=type_)

@_step
def update_references():

    references = cmds.file(q=True, reference=True)
    references = [path for path in references if cmds.referenceQuery(path, isLoaded=True)]

    for status in check_paths(references):

        print status.path
        if status.is_latest:
            print '    Up to date.'
            continue

        new_path = status.latest['sg_path']
        ext = os.path.splitext(new_path)[1]
        if ext not in ('.ma', '.mb'):
            cmds.warning('PublishEvent.sg_path is not a maya file: {}'.format(new_path))
            continue

        print '   Updating to', new_path

        type_ = 'mayaAscii' if ext == '.ma' else 'mayaBinary'
        node = cmds.referenceQuery(status.path, referenceNode=True)
        cmds.file(new_path, loadReference=node, type=type_)


def _bake(things):

    minTime = cmds.playbackOptions(query=True, minTime=True)
    maxTime = cmds.playbackOptions(query=True, maxTime=True)

    # Hide poly for faster simulation.
    # TODO: Query the API to figure out which panel this is for sure.
    with context.command(cmds.modelEditor, 'modelPanel4', edit=True, polymeshes=False), context.selection(things, replace=True):

        cmds.BakeSimulation(time='%s:%s' % (minTime, maxTime))

        # Set the out-tangent; in-tangent cannot be set to "step".
        cmds.keyTangent(edit=True, outTangentType="step")


@_step
def bake_dynamic_joints():

    # Select all joints (with the suffix "dynbake").
    all_joints = cmds.ls('*dynbake*', recursive=True)
    if not all_joints:
        print("No '*dynbake*' found; no dynamic joints to bake.")
        return

    _bake(all_joints)


@_step
def bake_controls():
    """Bakes controls (at 12fps) so we can transition to 24fps."""

    fps = units.get_fps()
    if fps != 12:
        raise ValueError('Must bake controls at 12fps; currently %s.' % fps)

    #select bake objects ie. ("*:*" + "*_Ctrl") and delects the flexi ctrls
    controls = cmds.ls('*:*_Ctrl') or ()
    controls = [x for x in controls if 'Flexi' not in x]

    if not controls:
        raise ValueError("There are no '*:*_Ctrl' objects to bake.")

    _bake(controls)
   

@_step
def shift_time():
    """Convert from 12 to 24fps."""
    fps = units.get_fps()
    if fps == 24:
        return
    if fps != 12:
        cmds.warning('We expect FPS to be 12, but it is currently %s.' % fps)
    units.set_fps(24)


@_step
def smooth_geo():
    """Set smooth level in viewport to 1 and render time smoothing to 3 divisions."""

    groups = cmds.ls("*:threeD_geo_grp") or ()
    if not groups:
        cmds.warning("No '*:threeD_geo_grp' groups.")
        return

    all_polygons = set()
    for group in groups:
        children = cmds.listRelatives(group, allDescendents=True, fullPath=True) or ()
        for child in children:
            polygons = cmds.filterExpand(child, selectionMask=12, fullPath=True) # 12 -> polygons (polymesh?)
            all_polygons.update(polygons or ())

    if not all_polygons:
        raise ValueError("No polygons under '*:threeD_geo_grp' groups.")

    for poly in all_polygons:
        cmds.setAttr(poly + ".useSmoothPreviewForRender", 0)
        cmds.setAttr(poly + ".smoothLevel", 0) # Preview.
        cmds.setAttr(poly + ".displaySmoothMesh", 1)
        cmds.setAttr(poly + ".renderSmoothLevel", 3)


#@_step
def constrain_head():
    """Constrain any in scene character's head to the main camera."""

    cmds.warning("You shouldn't need to constrain heads anymore. What are you calling this for?!")

    heads = cmds.ls('*:head_Sdk')
    if not heads:
        cmds.warning("There are no '*:head_Sdk' to constrain.")
        return

    if not cmds.objExists('cam:MainCAM'):
        raise ValueError("No 'cam:MainCAM'.")

    camera = 'cam:MainCAM'
    for head in heads: 
        cmds.aimConstraint(camera, head,
            offset=[0, 0, 0],
            weight=1,
            aimVector=[0, 0, 1],
            upVector=[0, 1, 0],
            worldUpType="object",
            worldUpObject="cam:MainCAM_up_loc",
        )


@_step
def shadow_light_linker():
    """Light links character shadow lights to the set group."""

    lights = cmds.ls("*:shadowLight_light")
    light_sets = cmds.ls("*_lightLink*")

    if not lights:
        cmds.warning("No '*:shadowLight_light' in scene.")
        return
    if not light_sets:
        cmds.warning("No '*_lightLink*' in scene.")
        return

    for light in lights: 
        for light_set in light_sets: 
            cmds.lightlink(light=light, object=light_set)


@_step
def set_shadow_switch():
    """Set god_ctrl switch depending on if the set is interior or not."""

    # Find the set.
    # TODO: Moar SGFS.
    files_referenced = cmds.file(query=True, list=True) or ()
    for path in files_referenced:
        if '/assets/sets/' not in path:
            continue
        if '/model/' not in path:
            continue
        break
    else:
        raise ValueError("Could not identify the set reference.")

    # HACK: ...
    is_interior = 'Interior' in path
    print 'We have decided that the set is %san interior.' % ('' if is_interior else 'not ')
    
    # Find all the "switch"es on god controls, and turn them on if interior,
    # and off otherwise.
    god_ctrls = cmds.ls('*:God_Ctrl') or ()
    for god_ctrl in god_ctrls:

        switch = god_ctrl + '.switch'
        if not cmds.objExists(switch):
            continue # because not all gods have switches.

        cmds.setAttr(switch, 1 if is_interior else 0)


@_step
def manage_colours():

    cmds.colorManagementPrefs(e=True, cmEnabled=True)
    cmds.colorManagementPrefs(e=True, cmConfigFileEnabled=False)

    # These should be overkill together.
    cmds.colorManagementPrefs(e=True, outputTransformEnabled=False)
    cmds.colorManagementPrefs(e=True, outputTransformName='Raw')

    cmds.colorManagementPrefs(e=True, renderingSpaceName='scene-linear Rec 709/sRGB')


@_step
def config_mentalray():
    # Load mentalRay if not yet active.
    if 'Mayatomr' not in cmds.pluginInfo(q=True, listPlugins=True):
        cmds.loadPlugin('Mayatomr') 
    
    # Set Renderer to MentalRay.
    cmds.setAttr('defaultRenderGlobals.currentRenderer', 'mentalRay', type='string')

    # Set quality settings.
    # Kevin wanted "Production", but lets just straight to "FinalFrameEXR"
    # (also because 'defaultRenderGlobals' has no "Production").
    cmds.nodePreset(load=('defaultRenderGlobals', 'FinalFrameEXR'))
    cmds.nodePreset(load=('miDefaultOptions', 'FinalFrameEXR'))


def setup_all():
    for step in steps:
        print '=>', step.__name__
        step()


