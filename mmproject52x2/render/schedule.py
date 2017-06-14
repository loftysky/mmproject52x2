import argparse
import os

from sgfs import SGFS
from sgpublish import Publisher
from farmsoup.client import Client

from mmpipeline import artifacts


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-P', '--project', default='/Volumes/CGroot/Projects/MM52x2')
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-c', '--count', type=int)
    #parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    sgfs = SGFS()
    proj = sgfs.parse_user_input(args.project, entity_types=['Project'])

    # Find all the render tasks.
    print 'Loading all render tests.'
    render_tasks = {}
    for task in sgfs.session.find('Task', [
        ('project', 'is', proj),
        ('step.Step.code', 'is', 'render')
    ], ['entity']):
        shot = task['entity']
        render_tasks[shot] = task

    # Find all the anim and render publishes in the project so we may compare them.
    print 'Loading all anim/render publishes.'
    publishes = sgfs.session.find('PublishEvent', [
        ('project', 'is', proj),
        ('link.Task.step.Step.code', 'in', 'anim', 'render'),
    ], [
        'link.Task.entity',
        'link.Task.sg_status_list',
        'link.Task.step.Step.code',
        'sg_type',
        'source_publish',
        'source_publishes',
        'status_list',
        'version',
        'path'
    ])

    latest_anim = {}
    latest_render = {}

    for publish in publishes:

        if publish['link.Task.step.Step.code'] == 'anim':
            if publish['sg_type'] != 'maya_scene':
                continue
            latest_dict = latest_anim
        else:
            if publish['sg_type'] != 'maya_render':
                continue
            latest_dict = latest_render

        shot = publish['link.Task.entity']
        last = latest_dict.get(shot)
        if last is None or publish['updated_at'] > last['updated_at']:
            latest_dict[shot] = publish

    client = Client()
    job = client.job(
        name='mm52x2-render-all',
    )

    for i, (shot, anim_publish) in enumerate(sorted(latest_anim.iteritems(), key=lambda (s, a): s['name'])):

        if args.count and i >= args.count:
            continue

        render_publish = latest_render.get(shot)
        render_task = render_tasks.get(shot)

        print
        print shot['code']
        print '-' * 40
        print 'anim publish:', anim_publish
        print 'render publish:', render_publish
        print 'render task:', render_task

        if not render_task:
            print 'ERROR: Cannot continue without render task.'
            continue

        if render_publish:
            render_sources = [render_publish['source_publish']] + render_publish['source_publishes']
            if anim in render_sources:
                print 'Render is up to date; skipping.'
                continue
            else:
                print 'Render is out of date.'

        anim_scene = anim_publish['path']
        print 'anim scene:', anim_scene

        with Publisher(link=render_task, type='maya_render', name=shot['code'],
            template=anim_publish, review_version_fields={},
            defer_entities=True, makedirs=False, # So we can move it to artifacts.
        ) as publisher:

            publisher.extra_fields['sg_status_list'] = 'ip' # In Progress
            publisher.review_version_fields['sg_status_list'] = 'na'

            for dir_ in publisher.iter_potential_directories():
                dir_ = artifacts.to_shadow_dimension(dir_)
                try:
                    os.makedirs(dir_)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise
                else:
                    break

            publisher.directory = dir_

            scene = publisher.add_file(anim_scene)

            publisher.path_to_frames = os.path.join(dir_, 'images')

        name = shot['code'] + '_v%04d' % publisher.version
        base, ext = os.path.splitext(scene)
        shadow_scene = base + '.to-render' + ext

        command = [
            'mm52x2-render',
            '--name', name,
            '--out-dir', publisher.path_to_frames,
            '--shadow-scene', shadow_scene,
            scene
        ]

        print 'command: $', ' '.join(command)
        continue

        job.add_subprocess(command,
            name=name,
        )

    #group = client.submit(jobs=[job])
    #print 'Submitted as', group.id








