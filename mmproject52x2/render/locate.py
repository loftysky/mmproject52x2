import fnmatch
import glob
import os
import sys
import re

from sgfs import SGFS



def first_published_frame(publish, sgfs=None):

    sgfs = sgfs or SGFS()

    path = publish.fetch('path_to_frames')
    
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
        return

    names = sorted(os.listdir(path))
    names = [x for x in names if not x.startswith('.')]
    if not names:
        return

    path = os.path.join(path, names[0])
    return path


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
        result[shot_code] = first_published_frame(publish)

    return result


def newer(current_by_name):

    sgfs = SGFS()
    sg = sgfs.session

    pub_by_name = {}

    # Find everything that is a publish.
    for name, current_path in current_by_name.iteritems():
        print >> sys.stderr, name, current_path
        publishes = sgfs.entities_from_path(current_path, ['PublishEvent'])
        if publishes:
            pub_by_name[name] = publishes[0]
            print >> sys.stderr, '   ', publishes[0]
    print >> sys.stderr

    pubs = pub_by_name.values()
    sg.fetch(pubs, ['link', 'code', 'created_at', 'path_to_frames'])

    current_by_link = {p['link']: p for p in pubs if p['link']}

    # Find the most recent publishes for each link.
    newest_by_link = current_by_link.copy()
    for pub in sg.find('PublishEvent', [
        ('sg_type', 'is', 'maya_render'),
        ('link', 'in') + tuple(current_by_link.keys())
    ], ['created_at']):
        print >> sys.stderr, pub
        link = pub['link']
        newest = newest_by_link.get(link)
        if pub['created_at'] > newest['created_at']:
            print >> sys.stderr, '   newer!'
            newest_by_link[link] = pub

    res = []

    for name, current in sorted(current_by_name.iteritems()):
        
        pub = pub_by_name.get(name)
        if not pub:
            res.append(dict(name=name, type='nopublish'))
            continue

        link = pub['link']
        current = current_by_link[link]
        newest = newest_by_link[link]

        if current is newest:
            res.append(dict(name=name, type='nochange'))

        else:
            res.append(dict(name=name, type='newer', path=first_published_frame(newest)))

    return res

























