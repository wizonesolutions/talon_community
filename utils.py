import string
import collections

from talon import clip
from talon.voice import Str, press
from time import sleep
import json
import os

from .bundle_groups import TERMINAL_BUNDLES, FILETYPE_SENSITIVE_BUNDLES

VIM_IDENTIFIER = "(Vim)"

mapping = json.load(open(os.path.join(os.path.dirname(__file__), "replace_words.json")))
mappings = collections.defaultdict(dict)
for k, v in mapping.items():
    mappings[len(k.split(" "))][k] = v

punctuation = set(".,-!?")


def local_filename(file, name):
    return os.path.join(os.path.dirname(os.path.realpath(file)), name)


def parse_word(word, force_lowercase=True):
    if force_lowercase:
        word = word.lower()
    word = mapping.get(word, word)

    return word


def replace_words(words, mapping, count):
    if len(words) < count:
        return words

    new_words = []
    i = 0
    while i < len(words) - count + 1:
        phrase = words[i : i + count]
        key = " ".join(phrase)
        if key in mapping:
            new_words.append(mapping[key])
            i = i + count
        else:
            new_words.append(phrase[0])
            i = i + 1

    new_words.extend(words[i:])
    return new_words


def remove_dragon_junk(word):
    return str(word).lstrip("\\").split("\\", 1)[0]


def parse_words(m, natural=False):
    if isinstance(m, list):
        words = m
    elif hasattr(m, "dgndictation"):
        words = m.dgndictation[0]
    else:
        return []

    # split compound words like "pro forma" into two words.
    words = list(map(remove_dragon_junk, words))
    words = sum([word.split(" ") for word in words], [])
    words = list(map(lambda current_word: parse_word(current_word, not natural), words))
    words = replace_words(words, mappings[2], 2)
    words = replace_words(words, mappings[3], 3)
    words = replace_words(words, mappings[4], 4)
    return words


def join_words(words, sep=" "):
    out = ""
    for i, word in enumerate(words):
        if i > 0 and word not in punctuation:
            out += sep
        out += str(word)
    return out


def insert(s):
    Str(s)(None)


def text(m):
    insert(join_words(parse_words(m)).lower())


def spoken_text(m):
    insert(join_words(parse_words(m, True)))


def sentence_text(m):
    raw_sentence = join_words(parse_words(m, True))
    sentence = raw_sentence[0].upper() + raw_sentence[1:]
    insert(sentence)


def word(m):
    try:
        text = join_words(list(map(parse_word, m.dgnwords[0]._words)))
        insert(text.lower())
    except AttributeError:
        pass

def capitalized_word(m):
    try:
        text = join_words(list(map(parse_word, m.dgnwords[0]._words)))
        insert(text.capitalize())
    except AttributeError:
        pass

def surround(by):
    def func(i, word, last):
        if i == 0:
            word = by + word
        if last:
            word += by
        return word

    return func


def rot13(i, word, _):
    out = ""
    for c in word.lower():
        if c in string.ascii_lowercase:
            c = chr((((ord(c) - ord("a")) + 13) % 26) + ord("a"))
        out += c
    return out


numeral_map = dict((str(n), n) for n in range(0, 20))
for n in range(20, 101, 10):
    numeral_map[str(n)] = n
for n in range(100, 1001, 100):
    numeral_map[str(n)] = n
for n in range(1000, 10001, 1000):
    numeral_map[str(n)] = n
numeral_map["oh"] = 0  # synonym for zero
numeral_map["and"] = None  # drop me

numeral_list = sorted(numeral_map.keys())
numerals = " (" + " | ".join(numeral_list) + ")+"
optional_numerals = " (" + " | ".join(numeral_list) + ")*"


def text_to_number(words):
    tmp = [str(s).lower() for s in words]
    words = [parse_word(word) for word in tmp]

    result = 0
    factor = 1
    for word in reversed(words):
        print("{} {} {}".format(result, factor, word))
        if word not in numerals:
            raise Exception("not a number: {}".format(words))

        number = numeral_map[word]
        if number is None:
            continue

        number = int(number)
        if number > 10:
            result = result + number
        else:
            result = result + factor * number
        factor = (10 ** len(str(number))) * factor
    return result


def m_to_number(m):
    tmp = [str(s).lower() for s in m._words]
    words = [parse_word(word) for word in tmp]

    result = 0
    factor = 1
    for word in reversed(words):
        if word not in numerals:
            # we consumed all the numbers and only the command name is left.
            break

        result = result + factor * int(numeral_map[word])
        factor = 10 * factor

    return result


def text_to_range(words, delimiter="until"):
    tmp = [str(s).lower() for s in words]
    split = tmp.index(delimiter)
    start = text_to_number(words[:split])
    end = text_to_number(words[split + 1 :])
    return start, end


number_conversions = {"oh": "0"}  # 'oh' => zero
for i, w in enumerate(
    ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
):
    number_conversions[str(i)] = str(i)
    number_conversions[w] = str(i)
    number_conversions["%s\\number" % (w)] = str(i)


def parse_words_as_integer(words):
    # TODO: Once implemented, use number input value rather than manually
    # parsing number words with this function

    # Ignore any potential non-number words
    number_words = [w for w in words if str(w) in number_conversions]

    # Somehow, no numbers were detected
    if len(number_words) == 0:
        return None

    # Map number words to simple number values
    number_values = list(map(lambda w: number_conversions[w.word], number_words))

    # Filter out initial zero values
    normalized_number_values = []
    non_zero_found = False
    for n in number_values:
        if not non_zero_found and n == "0":
            continue
        non_zero_found = True
        normalized_number_values.append(n)

    # If the entire sequence was zeros, return single zero
    if len(normalized_number_values) == 0:
        normalized_number_values = ["0"]

    # Create merged number string and convert to int
    return int("".join(normalized_number_values))


def alternatives(options):
    return " (" + " | ".join(sorted(map(str, options))) + ")+"


def select_single(options):
    return " (" + " | ".join(sorted(map(str, options))) + ")"


def optional(options):
    return " (" + " | ".join(sorted(map(str, options))) + ")*"


def preserve_clipboard(fn):
    def wrapped_function(*args, **kwargs):
        old = clip.get()
        ret = fn(*args, **kwargs)
        sleep(0.1)
        clip.set(old)
        return ret

    return wrapped_function


# @preserve_clipboard
def paste_text(text):
    with clip.revert():
        clip.set(text)
        # sleep(0.1)
        press("cmd-v")
        sleep(0.1)


@preserve_clipboard
def copy_selected():
    press("cmd-c")
    sleep(0.25)
    return clip.get()


# The. following function is used to be able to repeat commands by following it by one or several numbers, e.g.:
# 'delete' + optional_numerals: repeat_function(1, 'delete'),
def repeat_function(numberOfWordsBeforeNumber, keyCode, delay=0):
    def repeater(m):
        line_number = parse_words_as_integer(m._words[numberOfWordsBeforeNumber:])

        if line_number is None:
            line_number = 1

        for i in range(0, line_number):
            sleep(delay)
            press(keyCode)

    return repeater


def delay(amount=0.1):
    return lambda _: sleep(amount)


def is_in_bundles(bundles):
    return lambda app, win: any(b in app.bundle for b in bundles)


def is_vim(app, win):
    if is_in_bundles(TERMINAL_BUNDLES)(app, win):
        if VIM_IDENTIFIER in win.title:
            return True
    return False


def is_not_vim(app, win):
    return not is_vim(app, win)


def is_filetype(extensions=()):
    def matcher(app, win):
        if is_in_bundles(FILETYPE_SENSITIVE_BUNDLES)(app, win):
            if any(ext in win.title for ext in extensions):
                return True
            else:
                return False
        return True

    return matcher


def extract_num_from_m(m):
    # loop identifies numbers in any message
    number_words = [w for w in m._words if w in numeral_list]
    if len(number_words) == 0:
        raise ValueError("No number found")
    return text_to_number(number_words)
