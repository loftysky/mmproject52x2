import argparse
import os
import sys
import json


def log(msg, *args, **kwargs):
    if args or kwargs:
        msg = msg.format(*args, **kwargs)
    msg = '[mm52x2] ' + msg.strip() + '\n'
    sys.stderr.write(msg)
    sys.stderr.flush()

def send(msg=None, **kwargs):
    msg = dict(msg or {}).copy()
    msg.update(kwargs)
    encoded = json.dumps(msg, sort_keys=True)
    print >> sys.stderr, '[mm52x5] Send:', encoded
    sys.__stdout__.write(encoded + '\n')
    sys.__stdout__.flush()


NoResult = object()


handlers = {}

def register(func):
    name = func.__name__
    if name.startswith('on_'):
        name = name[3:]
    handlers[name] = func
    return func


@register
def on_hello(**kw):
    kw['type'] = 'elloh'
    return kw
@register
def on_elloh(**kw):
    return NoResult

@register
def on_ping(**kw):
    kw['type'] = 'pong'
    return kw
@register
def on_pong(**kw):
    return NoResult



def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    # We need to take over both stdout and stderr so that print statements
    # don't result in Premiere thinking it is getting a message back.
    if args.verbose:
        sys.stdout = sys.stderr
    else:
        sys.stdout = open('/tmp/mm52x2-premiere-runtime.log', 'a')
        sys.stderr = sys.stdout

    log('Starting.')

    send(
        type='hello',
        file=__file__,
    )

    while True:

        encoded = sys.stdin.readline()
        if not encoded:
            log('stdin closed.')
            return

        encoded = encoded.strip()
        if not encoded:
            continue

        log('Recv: {}', encoded)

        try:
            msg = json.loads(encoded)
        except ValueError as e:
            send(type='error', error='malformed message', detail='{}: {}'.format(e.__class__.__name__, e))
            continue

        if not isinstance(msg, dict):
            send(type='error', error='malformed message', detail='non-dict')
            continue

        type_ = msg.pop('type', None)
        id_ = msg.get('id')
        if not type_:
            send(type='error', error='malformed message', detail='no type')
            continue

        func = handlers.get(type_)
        if not func:
            send(type='error', error='unknown message type', detail=type_)
            continue

        try:
            res = func(**msg)
        except Exception as e:
            send(type='error', error='{}: {}'.format(e.__class__.__name__, e))
            continue
        
        if res is NoResult:
            continue

        if not isinstance(res, dict):
            res = {'value': res}
        res.setdefault('type', 'result')
        res.setdefault('id', id_)
        send(res)
            




if __name__ == '__main__':
    main()
