#!/usr/bin/env mayapy

from fractions import Fraction  
import argparse
import datetime
import errno
import math
import os
import socket
import subprocess

from farmsoup.utils import shell_join
from maya import cmds, mel, standalone
from mayatools.sound import get_active_sound_node
from mayatools.units import get_fps
from sgfs import SGFS
import farmsoup.client.models

from mmpipeline.artifacts import to_shadow_dimension, from_shadow_dimension

from . import setup as setup_module


def pick_name(scene):
    return os.path.splitext(os.path.basename(scene))[0]

def pick_shadow_scene(scene):
    shadow_scene = to_shadow_dimension(scene, make_parent=True)
    base, ext = os.path.splitext(shadow_scene)
    timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat('T').replace(':', '-')
    shadow_scene = '%s,%s%s' % (base, timestamp, ext)
    return shadow_scene

def pick_out_base(scene):
    sgfs = SGFS()
    tasks = sgfs.entities_from_path(scene, entity_type='Task')
    task_path = sgfs.path_for_entity(tasks[0])
    shadow_path = to_shadow_dimension(task_path)
    out_dir = os.path.join(shadow_path, 'maya', 'images')
    return out_dir


def get_render_range(sgfs=None):
    """Determine the ideal start/end frame ranges in 24fps."""

    fps = get_fps()
    if fps not in (12, 24):
        raise ValueError("FPS is non-standard {}".format(fps))

    sound_node = get_active_sound_node()
    if sound_node:
        print "Taking sound from active node {}.".format(sound_node)
        sound_nodes = [sound_node]
    else:
        sound_nodes = cmds.ls(type='audio') or ()

    if not sound_nodes:
        raise ValueError("There is no sound in the scene.")

    if len(sound_nodes) == 1:
        sound_node = sound_nodes[0]

    else:

        print "Comparing audio_proxy publishes to pick best sound."

        sgfs = sgfs or SGFS()
        task = None
        latest = None

        for node in sound_nodes:
            
            path = cmds.sound(node, q=True, file=True)
            
            publish = sgfs.entities_from_path(path, 'PublishEvent')
            if not publish:
                raise ValueError("Sound file '{}' from node {} is not a publish, so we can't tell them apart.".format(path, node))
            
            # We're looking at created_at instead of version, because I want
            # versions to be less meaningful in the future.
            type_, this_task, created_at = publish.fetch('sg_type', 'link', 'created_at')

            if type_ != 'audio_proxy':
                raise ValueError("Sound file '{}' from node {} is not an 'audio_proxy' publish.".format(path, node))

            if task and task is not this_task:
                raise ValueError("Sound files are from different tasks: {} and {}.".format(task, this_task))
            task = task or this_task

            if not latest or created_at > latest:
                sound_node = node
                latest = created_at

    print "Taking timing from sound file '{}' from node {}.".format(cmds.sound(sound_node, q=True, file=True), sound_node)


    offset = cmds.getAttr(sound_node + '.offset')
    source_start = cmds.getAttr(sound_node + '.sourceStart')
    source_end   = cmds.getAttr(sound_node + '.sourceEnd')

    # N.B. Maya's API is returning `sourceEnd` and `endFrame` as being 1 higher
    # than the UI is reporting. There may be some different behaviour if it
    # is in 12/24 fps (or maybe in the same/different fps as the sound was
    # importer). Either way, we're going to let is slide as it only results
    # in more frames being rendered, which isn't a big deal.

    if source_start:
        cmds.warning("Sound has a source start; this may mess up timing.")

    start = offset
    end = offset + source_end - source_start

    if start and float(start) != 1.0:
        cmds.warning('Sound sourceStart is %s; resetting to 1.' % start)
        start = 1.0

    # We leave start where it is, because Kevin has request that we start
    # rendering at frame 1 even though the animator's frame 1 would be
    # frame 2.
    start = int(math.ceil(start))
    end   = int(math.ceil(end * (24 / fps)))

    return start, end




def submit(scene, start=None, end=None, out_base=None, out_dir=None, name=None, shadow_scene=None, verbose=True, dry_run=False, **kwargs):

    if start is None or end is None:

        # This is likely handled by appinit, but it doesn't hurt.
        standalone.initialize() 
    
        # Load the file without references as we don't care about the contents at this point.
        cmds.file(scene, open=True, loadReferenceDepth='none')

        ideal_start, ideal_end = get_render_range()
        if start is None:
            start = ideal_start
        if end is None:
            end = ideal_end

    name = name or pick_name(scene)
    shadow_scene = shadow_scene or pick_shadow_scene(scene)

    if not out_dir:
        if not out_base:
            out_base = pick_out_base(scene)
        out_dir = os.path.join(out_base, name)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # TODO: Devmode without going into shebang cycle on Linux.
    setup_command = [
        #'vee', 'exec', '--bootstrap', # FIXME: For dev mode.
        'mm52x2-render', '--setup',
        '--start', str(start),
        '--end', str(end),
        '--out-dir', out_dir,
        '--name', name,
        '--shadow-scene', shadow_scene,
        scene,
    ]
    setup_command = shell_join(setup_command)
    if verbose:
        print 'setup command:', setup_command
    setup_job = farmsoup.client.models.Job(
        name='Render setup.',
        label='setup',
    ).setup_as_subprocess(
        # TODO: Remove hostname when farmsoup GUI scan identify the worker.
        ['hostname; ' + setup_command],
        #extra_env={'VEE_EXEC_ARGS': os.environ.get('VEE_EXEC_ARGS', '')}, # FIXME.
        shell=True,
    )

    render_command = ['Render', 

        '-r', 'mr', # mr -> mentalray

        '-s', '__F', # These get replaced with $F later.
        '-e', '__F_end',

        # The camera is not set to be renderable.
        '-cam', 'cam:MainCAM',

        '-x', '1920', # These should already be set.
        '-y', '1080', # These should already be set.
        
        '-rd', out_dir,
        '-im', name,
        '-fnc', 'name.#.ext',
        
        # We can't seem to explicitly set EXR here. It always renders as .iff.
        # We've tried 'OpenEXR', 'exr', and 'EXR'.
        # Just assume it was setup to be EXR.
        #'-of', 'OpenEXR',

        '-pad', '4',
        shadow_scene,
    ]
    # HACK: Get around escaping the variables.
    render_command = shell_join(render_command).replace('__F', '$F')
    if verbose:
        print 'render command:', render_command

    render_job = farmsoup.client.models.Job(
        name='Render.',
        label='render',
        requirements='jobs["setup"].status == "complete"',
    ).setup_as_subprocess(
        ['hostname; ' + render_command],
        shell=True,
    )
    render_job.expand_via_range('F=%d-%d/10' % (start, end))

    # compress_job = farmsoup.client.models.Job(
    #     name='Compress.',
    #     label='compress',
    #     requirements='jobs["render"].status == "complete"',
    # ).setup_as_subprocess(
    #     ['echo', u'Good job everyone!'],
    #     shell=True,
    # )

    if not dry_run:
        client = farmsoup.client.Client()
        group = client.submit(
            id=int(os.environ.get('FARMSOUP_JOB_GROUP_ID', '0')) or None,
            name='mm52x2-render :: %s' % name,
            jobs=[setup_job, render_job],
        )
        print 'group id:', group.id


def setup(scene, shadow_scene, **kwargs):

    # This is likely handled by appinit, but it doesn't hurt.
    standalone.initialize() 
    
    cmds.file(scene, open=True)
    
    # Immediately rename file in case something somewhere decides to save the file.
    cmds.file(rename=shadow_scene)

    # Do the thing!
    setup_module.setup_all()

    # Finally save to the new location.
    ext = os.path.splitext(shadow_scene)[1]
    maya_type = 'mayaBinary' if ext == '.mb' in ext else 'mayaAscii'
    cmds.file(save=True, type=maya_type)


def main():

    parser = argparse.ArgumentParser()

    global_args = parser.add_argument_group('Global options')
    global_args.add_argument('-s', '--start', type=int,
        help="First frame.")
    global_args.add_argument('-e', '--end', type=int,
        help="Last frame.")
    global_args.add_argument('-o', '--out-base',
        help="Base output directory.")
    global_args.add_argument('-O', '--out-dir',
        help="Actual output directory.")
    global_args.add_argument('-n', '--name', # TODO: Rename this to -N when they are off the farm.
        help="Name of output within directory.")

    setup_args = parser.add_argument_group('Render setup options')
    setup_args.add_argument('--setup', action='store_true',
        help='Run render setup, and save the scene to the shadow dimension.')
    setup_args.add_argument('--shadow-scene',
        help='Where to save the setup scene.')

    runtime_args = parser.add_argument_group('Runtime options')
    runtime_args.add_argument('-v', '--verbose', action='store_true')
    runtime_args.add_argument('--dry-run', action='store_true')

    parser.add_argument('scene')
    args = parser.parse_args()

    if args.setup:
        setup(**args.__dict__)
    else:
        submit(**args.__dict__)



if __name__ == "__main__":
    main()
