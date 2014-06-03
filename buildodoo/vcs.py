commands = {
    'noop': {
        'bzr': 'true',
        'git': 'true',
    },
    'checkout': {
        'bzr': 'bzr checkout --lightweight %(repo)s . %(rev)s',
        'git': 'git clone %(repo)s . %(rev)s',
    },
    'revno': {
        'bzr': 'bzr revno --tree',
        'git': 'git rev-parse HEAD',
    },
    'status': {
        'bzr': 'bzr status',
        'git': 'git status -s',
    },
}
