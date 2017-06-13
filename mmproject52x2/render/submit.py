#!/usr/bin/env mayapy

import argparse
import errno
import os
import socket
import subprocess
from fractions import Fraction  

from maya import cmds, standalone

from sgfs import SGFS 

from . import setup


#returns directory tree from args.scene and duplicates it on  CGartifacts
def to_shadow_dimension(path, mkdirs=True):
    path = os.path.abspath(path)
    rel_path = os.path.relpath(path, '/Volumes/CGroot')
    if rel_path.startswith('../'): 
        raise ValueError
    new_path = os.path.join('/Volumes/CGartifacts', rel_path)
    new_dir = os.path.dirname(new_path)
    print 'new_path_', new_path, 'new_dir', new_dir
    if mkdirs: 
        try:
            os.makedirs(new_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    return new_path
 

#using SGFS to find the parent task entity associated with the publish and creating the render directory in CGArtifacts 
def make_render_to_shadow_dimension(path_for_entity, args):
    sgfs = SGFS()
    entity_task = sgfs.entities_from_path(path_for_entity, entity_type='Task')
    task_path = sgfs.path_for_entity(entity_task[0])
    render = '/render'
    render_path = os.path.join(to_shadow_dimension(task_path), 'maya', 'images')
    if not os.path.isdir(render_path):
        os.makedirs(render_path)
        args.out_dir = render_path  
    if not args.out_dir:
        args.out_dir = render_path 


#saving maya scene to the CGArtifacts
def save_to_shadow_dimension(path, args):
    new_scene = to_shadow_dimension(path)
    original_filename = os.path.basename(new_scene)
    maya_type = 'mayaBinary' if '.mb' in original_filename else 'mayaAscii'
    cmds.file(rename=new_scene)
    cmds.file(save=True, type=maya_type)

    make_render_to_shadow_dimension(path, args)




def farmsoup_command(out_name, args):
#setting up Render command 
    cmd = ['Render',
        '-r', 'mr', 
        '-s', '$F',
        '-e', '$F__end',
    ]


    out_name = args.out or out_name
    out_dir  = os.path.join(args.out_dir, out_name) 

    cmd.extend((
        '-rd', out_dir,
        '-im', out_name,
        '-fnc', 'name.#.ext',
        '-of', 'tga',
        '-pad', '4',
    ))

    cmd.append(args.scene)
    print '# Running on', socket.gethostname()
    print '$', ' '.join(cmd)


    #Adding Farmsoup command
    cmd_farmsoup = ['farmsoup', 'submit']

    cmd_farmsoup.extend((
        '--shell',
        '--range',
        'F=%d-%d/10' % (args.start, args.end),
        ))

    fcmd = ' '.join(str(x) for x in cmd)
    cmd_farmsoup.append(fcmd)
    print cmd_farmsoup
    return cmd_farmsoup


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start', type=int)
    parser.add_argument('-e', '--end', type=int)
    parser.add_argument('--out-dir')
    parser.add_argument('-o', '--out')
    parser.add_argument('-n', '--name')
    parser.add_argument('scene')
    args = parser.parse_args()

    standalone.initialize()
    cmds.file(args.scene, open=True)
    startTime = cmds.playbackOptions(query=True, minTime=True)
    endTime = cmds.playbackOptions(query=True, maxTime=True)

    if not args.start:
        args.start = startTime
    if not args.end:
        args.end = endTime

    name = args.name or os.path.splitext(os.path.basename(args.scene))[0]
    out_name = name

    #call render setup
    setup.setup_all()
    save_to_shadow_dimension(args.scene, args)
    os.execvp('farmsoup', farmsoup_command(out_name, args))


if __name__ == "__main__":
    main()
