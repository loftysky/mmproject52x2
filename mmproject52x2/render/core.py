#!/usr/bin/env mayapy

import argparse
import datetime
import errno
import os
import socket
import subprocess
from fractions import Fraction  

from maya import cmds, standalone
from sgfs import SGFS
import farmsoup.client.models
from farmsoup.utils import shell_join

from mmpipeline.artifacts import to_shadow_dimension

from . import setup as setup_module


def submit(scene, start=None, end=None, out_dir=None, name=None, shadow_scene=None, **kwargs):

    sgfs = SGFS()

    if start is None or end is None:

        # This is likely handled by appinit, but it doesn't hurt.
        standalone.initialize() 
    
        # Load the file without references as we don't care about the contents at this point.
        cmds.file(scene, open=True, loadReferenceDepth='none')

        if start is None:
            start = int(cmds.playbackOptions(query=True, minTime=True))
        if end is None:
            end = int(cmds.playbackOptions(query=True, maxTime=True))

    name = name or os.path.splitext(os.path.basename(scene))[0]

    # Figure out where we will save the setup scene to.
    if not shadow_scene:
        shadow_scene = to_shadow_dimension(scene, make_parent=True)
        base, ext = os.path.splitext(shadow_scene)
        timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat('T').replace(':', '-')
        shadow_scene = '%s,%s%s' % (base, timestamp, ext)

    if not out_dir:
        tasks = sgfs.entities_from_path(scene, entity_type='Task')
        task_path = sgfs.path_for_entity(tasks[0])
        shadow_path = to_shadow_dimension(task_path)
        out_dir = os.path.join(shadow_path, 'maya', 'images')

    # TODO: Devmode without going into shebang cycle on Linux.
    setup_command = [
        #'vee', 'exec', '--bootstrap', # FIXME: For dev mode.
        'mm52x2-render', '--setup',
        '-s', str(start),
        '-e', str(end),
        '-o', out_dir,
        '-n', name,
        '--shadow-scene', shadow_scene,
        scene,
    ]
    # TODO: Remove hostname when farmsoup GUI scan identify the worker.
    setup_command = 'hostname; ' + shell_join(setup_command)
    setup_job = farmsoup.client.models.Job(
        name='Render setup.',
        label='setup',
    ).setup_subprocess(
        [setup_command],
        #extra_env={'VEE_EXEC_ARGS': os.environ.get('VEE_EXEC_ARGS', '')}, # FIXME.
        shell=True,
    )

    frames_dir = os.path.join(out_dir, name)
    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)
    render_command = ['Render',
        '-r', 'mr', 
        '-s', '__F',
        '-e', '__F_end',
        '-cam', 'cam:MainCAM',
        '-x', '1920', # These should already be set.
        '-y', '1080', # These should already be set.
        '-rd', frames_dir,
        '-im', name,
        '-fnc', 'name.#.ext',
        '-of', 'OpenEXR', # This should already be set.
        '-pad', '4',
        shadow_scene,
    ]
    # HACK: Get around escaping the variables.
    render_command = 'hostname; ' + shell_join(render_command).replace('__F', '$F')
    render_job = farmsoup.client.models.Job(
        name='Render.',
        label='render',
        requirements='jobs["setup"].status == "complete"',
    ).setup_subprocess(
        [render_command],
        shell=True,
    )
    render_job.expand_via_range('F=%d-%d/10' % (start, end))

    compress_job = farmsoup.client.models.Job(
        name='Compress.',
        label='compress',
        requirements='jobs["render"].status == "complete"',
    ).setup_subprocess(
        ['echo', u'Good job everyone!'],
        shell=True,
    )

    client = farmsoup.client.Client()
    group = client.submit(
        name='mm52x2-render :: %s' % name,
        jobs=[setup_job, render_job, compress_job],
    )

    print 'Submitted as', group.id


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
    global_args.add_argument('-o', '--out-dir',
        help="Base output directory.")
    global_args.add_argument('-n', '--name',
        help="Name of output within directory.")

    setup_args = parser.add_argument_group('Render setup options')
    setup_args.add_argument('--setup', action='store_true',
        help='Run render setup, and save the scene to the shadow dimension.')
    setup_args.add_argument('--shadow-scene',
        help='Where to save the setup scene.')

    parser.add_argument('scene')
    args = parser.parse_args()

    if args.setup:
        setup(**args.__dict__)
    else:
        submit(**args.__dict__)



if __name__ == "__main__":
    main()
