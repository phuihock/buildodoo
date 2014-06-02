commands = {
    'checkout': {
        'bzr': 'bzr checkout --lightweight %(repo)s . %(rev)s',
        'git': 'git clone %(repo)s . %(rev)s',
    },
    'revno': {
        'bzr': 'bzr revno',
        'git': 'git rev-parse HEAD',
    }
}
