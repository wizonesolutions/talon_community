from talon.voice import Word, Key, Context, Str, press
import string

from ..utils import numerals, parse_words, text

# TODO: move application specific commands into their own files: git, apt-get, etc

terminals = ("com.apple.Terminal", "com.googlecode.iterm2")
ctx = Context("terminal", func=lambda app, win: any(t in app.bundle for t in terminals))

mapping = {"semicolon": ";", r"new-line": "\n", r"new-paragraph": "\n\n"}


def parse_word(word):
    word = word.lstrip("\\").split("\\", 1)[0]
    word = mapping.get(word, word)
    return word


def dash(m):
    words = parse_words(m)
    press(" ")
    if len(words) == 1 and len(words[0]) == 1:
        press("-")
        Str(words[0])(None)
    else:
        press("-")
        press("-")
        Str("-".join(words))(None)

KUBERNETES_PREFIX = "(cube | cube control)"

keymap = {
    "(pain new | split vertical)": Key("cmd-d"),
    # talon
    "tail talon": "tail -f .talon/talon.log",
    # some habits die hard
    "troll char": Key("ctrl-c"),
    "reverse": Key("ctrl-r"),
    "cd": ["cd ; ls", Key("left"), Key("left"), Key("left"), Key("left")],
    "cd wild": [
        "cd **; ls",
        Key("left"),
        Key("left"),
        Key("left"),
        Key("left"),
        Key("left"),
    ],
    "cd wild [<dgndictation>]": [
        "cd **; ls",
        Key("left"),
        Key("left"),
        Key("left"),
        Key("left"),
        Key("left"),
        text,
    ],
    "(ls | run ellis | run alice)": "ls\n",
    "(la | run la)": "ls -la\n",
    "durrup": "cd ..; ls\n",
    "go back": "cd -\n",
    "dash <dgndictation> [over]": dash,
    "pseudo": "sudo ",
    "shell C H mod": "chmod ",
    "shell clear": [Key("ctrl-c"), "clear\n"],
    "shell copy [<dgndictation>]": ["cp ", text],
    "shell copy (recursive | curse) [<dgndictation>]": ["cp -r", text],
    "shell kill": Key("ctrl-c"),
    "shell list [<dgndictation>]": ["ls ", text],
    "shell list all [<dgndictation>]": ["ls -la ", text],
    "shell make (durr | dear | directory) [<dgndictation>]": ["mkdir ", text],
    "shell mipple [<dgndictation>]": ["mkdir -p ", text],
    "shell move [<dgndictation>]": ["mv ", text],
    "shell remove [<dgndictation>]": ["rm ", text],
    "shell remove (recursive | curse) [<dgndictation>]": ["rm -rf ", text],
    "shell enter": "ag -l | entr ",
    "shell enter 1": "ag -l . .. | entr ",
    "shell enter 2": "ag -l . ../.. | entr ",
    "shell less [<dgndictation>]": ["less ", text],
    "shell cat [<dgndictation>]": ["cat ", text],
    "shell X args [<dgndictation>]": ["xargs ", text],
    "shell mosh": "mosh ",
    "shell M player": "mplayer ",
    "shell nvidia S M I": "nvidia-smi ",
    "shell R sync": "./src/dotfiles/sync_rsync ",
    # python
    "create virtual environment": ["virtualenv -p python3 venv", Key("enter")],
    "activate virtual environment": [
        "source `find . | grep bin/activate$`",
        Key("enter"),
    ],
    # apt-get
    "apt get": "apt-get ",
    "apt get install": "apt-get install ",
    "apt get update": "apt-get update ",
    "apt get upgrade": "apt-get upgrade ",
    # git
    "jet [<dgndictation>]": ["git ", text],
    "jet add [<dgndictation>]": ["git add ", text],
    "jet branch": "git branch",
    "jet branch delete [<dgndictation>]": ["git branch -D ", text],
    "jet branch all [<dgndictation>]": ["git branch -a ", text],
    "jet clone [<dgndictation>]": ["git clone ", text],
    "jet checkout master": "git checkout master",
    "jet checkout [<dgndictation>]": ["git checkout ", text],
    "jet checkout branch [<dgndictation>]": ["git checkout -B ", text],
    "jet cherry pick [<dgndictation>]": ["git cherry-pick ", text],
    "jet commit [<dgndictation>]": ['git commit -m ""', Key("left"), text],
    "jet commit amend [<dgndictation>]": [
        'git commit --amend -m ""',
        Key("left"),
        text,
    ],
    "jet commit all [<dgndictation>]": ['git commit -a -m ""', Key("left"), text],
    "jet config [<dgndictation>]": ["git config ", text],
    "jet config list [<dgndictation>]": ["git config --list ", text],
    "jet diff [<dgndictation>]": ["git diff ", text],
    "jet history": "git hist ",
    "jet (init | initialize)": "git init ",
    "jet log": "git log ",
    "jet merge [<dgndictation>]": ["git merge ", text],
    "jet move [<dgndictation>]": ["git mv ", text],
    "jet pull [<dgndictation>]": ["git pull ", text],
    "jet pull (base | re-base | rebase | re base) [<dgndictation>]": [
        "git pull --rebase ",
        text,
    ],
    "jet push [<dgndictation>]": ["git push ", text],
    "jet push force [<dgndictation>]": ["git push --force ", text],
    "jet push set up stream [<dgndictation>]": ["git push --set-upstream ", text],
    "jet rebase continue": "git rebase --continue",
    "jet rebase [<dgndictation>]": ["git rebase ", text],
    "jet remove [<dgndictation>]": ["git rm ", text],
    "jet reset": "git reset ",
    "jet reset hard": "git reset --hard ",
    "jet show": "git show ",
    "jet stash": "git stash ",
    "jet stash apply": "git stash apply ",
    "jet stash pop": "git stash pop ",
    "jet status": "git status ",
    # Tools
    "(grep | grip)": ["grep  .", Key("left left")],
    "gripper": ["grep -r  .", Key("left left")],
    "pee socks": "ps aux ",
    "vi": "vi ",
    # python
    "pip": "pip",
    "pip install": "pip install ",
    "pip install requirements": "pip install -r ",
    "pip install editable": "pip install -e ",
    "pip install this": "pip install -e .",
    "pip install local": "pip install -e .",
    "pip [install] upgrade": "pip install --upgrade ",
    "pip uninstall": "pip uninstall ",
    "pip list": "pip list",
    # kubectl
    KUBERNETES_PREFIX + "control": "kubectl ",
    KUBERNETES_PREFIX + "create": "kubectl create ",
    KUBERNETES_PREFIX + "expose": "kubectl expose ",
    KUBERNETES_PREFIX + "run": "kubectl run ",
    KUBERNETES_PREFIX + "set": "kubectl set ",
    KUBERNETES_PREFIX + "run-container": "kubectl run-container ",
    KUBERNETES_PREFIX + "get": "kubectl get ",
    KUBERNETES_PREFIX + "explain": "kubectl explain ",
    KUBERNETES_PREFIX + "edit": "kubectl edit ",
    KUBERNETES_PREFIX + "delete": "kubectl delete ",
    KUBERNETES_PREFIX + "rollout": "kubectl rollout ",
    KUBERNETES_PREFIX + "rolling-update": "kubectl rolling-update ",
    KUBERNETES_PREFIX + "scale": "kubectl scale ",
    KUBERNETES_PREFIX + "autoscale": "kubectl autoscale ",
    KUBERNETES_PREFIX + "certificate": "kubectl certificate ",
    KUBERNETES_PREFIX + "cluster-info": "kubectl cluster-info ",
    KUBERNETES_PREFIX + "top": "kubectl top ",
    KUBERNETES_PREFIX + "cordon": "kubectl cordon ",
    KUBERNETES_PREFIX + "uncordon": "kubectl uncordon ",
    KUBERNETES_PREFIX + "drain": "kubectl drain ",
    KUBERNETES_PREFIX + "taint": "kubectl taint ",
    KUBERNETES_PREFIX + "describe": "kubectl describe ",
    KUBERNETES_PREFIX + "logs": "kubectl logs ",
    KUBERNETES_PREFIX + "attach": "kubectl attach ",
    KUBERNETES_PREFIX + "exec": "kubectl exec ",
    KUBERNETES_PREFIX + "port-forward": "kubectl port-forward ",
    KUBERNETES_PREFIX + "proxy": "kubectl proxy ",
    KUBERNETES_PREFIX + "cp": "kubectl cp ",
    KUBERNETES_PREFIX + "auth": "kubectl auth ",
    KUBERNETES_PREFIX + "apply": "kubectl apply ",
    KUBERNETES_PREFIX + "patch": "kubectl patch ",
    KUBERNETES_PREFIX + "replace": "kubectl replace ",
    KUBERNETES_PREFIX + "convert": "kubectl convert ",
    KUBERNETES_PREFIX + "label": "kubectl label ",
    KUBERNETES_PREFIX + "annotate": "kubectl annotate ",
    KUBERNETES_PREFIX + "completion": "kubectl completion ",
    KUBERNETES_PREFIX + "api": "kubectl api ",
    KUBERNETES_PREFIX + "config": "kubectl config ",
    KUBERNETES_PREFIX + "help": "kubectl help ",
    KUBERNETES_PREFIX + "plugin": "kubectl plugin ",
    KUBERNETES_PREFIX + "version": "kubectl version ",
    # conda
    "conda install": "conda install ",
    "conda list": "conda list ",
    # tmux
    "T mux new session": "tmux ",
    "T mux scroll": [Key('ctrl-b'), Key('[')],
}

for action in ('get', 'delete', 'describe'):
    for object in ('nodes', 'jobs', 'pods', ''):
        if object:
            object = object + ' '
        command = f'{KUBERNETES_PREFIX} {action} {object}'
        typed = f'kubectl {action} {object}'
        keymap.update({command: typed})

keymap.update({"pain " + str(i): Key("alt-" + str(i)) for i in range(10)})

ctx.keymap(keymap)


# module.exports = {
#   permissions: "chmod "
#   access: "chmod "
#   ownership: "chown "
#   "change own": "chown "
#   "change group": "chgrp "
#   cat: "cat "
#   chat: "cat " # dragon doesn't like the word 'cat'
#   copy: "cp "
#   "copy recursive": "cp -r "
#   move: "mv "
#   remove: "rm "
#   "remove recursive": "rm -rf "
#   "remove directory": "rmdir "
#   "make directory": "mkdir "
#   link: "ln "
#   man: "man "
#   list: "ls "
#   "list all": "ls -al "
#   ls: "ls "
#
#   "python reformat": "yapf -i "
#   "enter": "ag -l | entr "
#   "enter to": "ag -l . ../.. | entr "
# }
