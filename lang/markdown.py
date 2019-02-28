from os import system

from talon.voice import Context, Key, press, Str

from ..apps.atom import jump_to_bol
from ..utils import optional_numerals, is_filetype


FILETYPES = (".md",)

ctx = Context("markdown", func=is_filetype(FILETYPES))


def markdown_complete(m):
    if len(m._words) > 2:
        jump_to_bol(m)
    else:
        # lefty
        press("cmd-left")

    press("right")
    press("right")
    press("right")
    press("delete")
    Str("X")(None)


def markdown_incomplete(m):
    if len(m._words) > 2:
        jump_to_bol(m)
    else:
        # lefty
        press("cmd-left")

    press("right")
    press("right")
    press("right")
    press("delete")
    Str(" ")(None)


keymap = {
    "markdown check": "- [ ] ",
    "markdown complete" + optional_numerals: markdown_complete,
    "markdown incomplete" + optional_numerals: markdown_incomplete,
}

ctx.keymap(keymap)
