commands = {
    'noop': {
        'bzr': 'true',
        'git': 'true',
    },
    'checkout': {
        'bzr': 'bzr checkout --lightweight %(repo)s . %(rev)s',
        'git': 'git clone %(repo)s . && git checkout -q %(rev)s',
    },
    'revno': {
        'bzr': 'bzr revno --tree',
        'git': 'git rev-parse HEAD',
    },
    'status': {
        'bzr': 'bzr status',
        'git': 'git status -s',
    },
    'export': {
        'bzr': 'mkdir -p %(root)s/build/%(relcwd)s && bzr export %(root)s/build/%(relcwd)s %(rev)s',
        'git': 'mkdir -p %(root)s/build/%(relcwd)s && git archive %(rev)s | tar -x -C  %(root)s/build/%(relcwd)s',
    }
}

revisions = {
    'last:1': {
        'bzr': '-r last:1',
        'git': 'HEAD',
    }
}
