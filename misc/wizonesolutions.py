from talon.voice import Context, Key
from ..utils import capitalized_word, spoken_text
from .window_management import grid

ctx = Context('wizonesolutions')
ctx.keymap({
    'awesome <dgnwords>':          capitalized_word,
    'speak <dgndictation> [over]': spoken_text,
    "more <dgndictation> [over]":  [" ", spoken_text],

    'dub get':                     'wget ',
    'run cat':                     'cat ',
    'fast forward git':            'git pull --ff-only',
    'code tag':                    '<code></code>',
    'sparrow':                     '=>',
    'op sparrow':                  ' => ',
    'code tick':                   '```',
    'state is set':                'isset',

    'D dev S S H':                 ['ddev ssh', Key('enter')],
    'drewsh':                      'drush ',
    'drewsh enable':               'drush en ',
    'drewsh see are':              'drush cr',

    'snap wide screen':            grid(2, 1, 3, 6, 2, 5),
    'snap first short':            grid(1, 1, 3, 6, 1, 5),
    'snap mid short':              grid(2, 1, 3, 6, 1, 5),
    'snap third short':            grid(3, 1, 3, 6, 1, 5),
})
