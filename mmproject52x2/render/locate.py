import fnmatch
import glob
import os
import sys
import re

from sgfs import SGFS



def by_glob(glob):

    stars = glob.count('*')

    filters = [
        ('sg_type', 'is', 'maya_render'),
        ('project.Project.id', 'is', 74),
    ]

    shot_code_key = 'link.Task.entity.Shot.code'

    if not stars:
        filters.append((shot_code_key, 'is', glob))
        glob = None
    elif stars == 1:
        if glob.startswith('*'):
            filters.append((shot_code_key, 'ends_with', glob[1:]))
            glob = None
        elif glob.endswith('*'):
            filters.append((shot_code_key, 'starts_with', glob[:-1]))
            glob = None

    print >> sys.stderr, filters

    sgfs = SGFS()
    sg = sgfs.session


    by_task = {}

    for publish in sg.find('PublishEvent', filters, [
        shot_code_key,
        'path_to_frames',
        'link',
        'created_at',
    ]):

        shot_code = publish[shot_code_key]
        if glob and not fnmatch.fnmatch(shot_code, glob):
            continue

        # We care about the latest one.
        task = publish['link']
        last = by_task.get(task)
        if last and last['created_at'] > publish['created_at']:
            continue
        by_task[task] = publish



    result = {}

    for publish in by_task.itervalues():

        shot_code = publish[shot_code_key]
        result[shot_code] = None

        path = publish['path_to_frames']
        if path:
            path = os.path.dirname(path)
            if not os.path.exists(path):
                path = None
        if not path:
            path = sgfs.path_for_entity(publish)
            if path:
                path = os.path.join(path, 'images')
                if not os.path.exists(path):
                    path = None

        if not path:
            missing.append(shot_code)
            continue

        names = sorted(os.listdir(path))
        names = [x for x in names if not x.startswith('.')]
        if not names:
            missing.append(shot_code)
            continue

        path = os.path.join(path, names[0])
        result[shot_code] = path

    return result
