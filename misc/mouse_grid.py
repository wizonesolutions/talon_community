import math
import string
import time
# from talon import canvas, ui, ctrl
from talon import ui, ctrl
from talon.voice import Context, app
from talon.canvas import Canvas
from talon.skia import Rect

# from ..text.std import alpha_alt

# TODO:
'''
- [ ] fix number recognition: https://talonvoice.slack.com/archives/C7ENXA7C4/p1548458219733200
- [x] fix `squid up/down 6`
- [ ] simplify by not storing calculated data
- [ ] add object for each direction with associated metadata (instead of just an array with the names) so we are doing less hard coding
- [ ] 10 x 10 by default? or squares?
- [ ] opening the grid can "freeze" eye tracking
- [x] pop up on active window's screen
- [x] add numbers along edges as an alternative to inside the cell
- [ ] instead of moving the mouse cursor, optionally show a target/crosshairs
- [ ] with target/crosshairs enabled, all actions besides move mouse cursor to target will perform that action and immediately `go back`
- [ ] allow moving down, up, left, right by steps (calculate closest center, then move relative to that)
- [ ] add modal variant that turns off other commands so that you can just utter coordinate names without prefixes
- [ ] allow number arguments to be single digit pairs e.g. two one or three three instead of e.g. twenty one or thirty three
- [ ] make numbers along edges easier to use
  - [x] draw big numbers for every 10 x 10
  - [ ] add zebra stripes, alternating
  - [ ] add zebra stripes every 10
  - [ ] draw coordinate names at 10 x 10 intersections
- [ ] refactor
  - [ ] refactor draw big numbers for every 10 x 10
- [ ] performance
  - [ ] calculate only on `squid`/display configuration change
  - [ ] do NOT calculate if active screen is the same (will res or config change force "not same"?)
  - [ ] do we even need to repaint? just show and hide if same active screen!
  - [ ] replace `lines` with `centers`
- [ ] "clock" for precise movement (e.g., `clock 3 10` will move 10 units in 3 o'clock direction)
- [ ] fix vertical centering
- [ ] draw dot with draw_point()
  you might need to set the point size in the paint; its size is specified by the paint's stroke-width
- [ ] 0 pad big hints that are only one character? optionally?
- [ ] get alternate alphabet to work past 26 letters (two characters allowed? symbols?)
- [x] fix numbers along edges so that their position is not hardcoded
- [ ] fix numbers along edges so that they work on any size/resolution monitor
- [ ] fix numbers in cells so that they work on any size/resolution monitor
- [x] allow user to save last cursor position/coordinates
- [ ] allow user to save cursor position/coordinates in the named slot
- [ ] allow user to go back one cursor positionl
- [x] style some of the dots differently so it's easier to use numbers along edges
- [ ] allow `squid` to be "sticky" for a particular monitor, even when not showing
- [ ] allow `squid` to somehow show on active screen immediately, even if it is showing on another screen (close it)
- [ ] add option to disable other commands when grid is showing, so that you only have to say the coordinates
- [ ] calculate optimal number of columns and rows automatically based on dimensions/DPI etc
  - [ ] maybe take resolution and keep dividing both horizontal and vertical resolution until reaching a number below 100
- [x] show on active window only
- [x] hide/show overlay on `squid`
- [ ] squares, N x M cells = predictability in spacing, but not coordinate range; rectangles, always N x N cells = predictability in coordinate names, but not spacing
- [ ] handle screen configuration change
- [ ] add `click on <coordinates A> to <coordinates B>`
- [ ] add `double-click on <coordinates A> to <coordinates B>`
- [ ] add `right-click on <coordinates A> to <coordinates B>`
- [ ] add `(click and drag | select) from <coordinates A> to <coordinates B>`
- [ ] add `squid next`
- [ ] add `squid 3`, where 3 means screen 3
- [ ] eye tracking/mouse grid hybrid (look, freeze/adjust with mouse grid)
- [x] allow for dots instead of (or in addition to) boxes
- [x] double digits (or spacing) for both arguments
- [x] center text
- [ ] draw inner grid after outer grid is called out (diff # of rows/columns?)
- [ ] decide on storing calculations vs recalculating each time
- [ ] what events should force recalculate?
- [ ] add option to draw on all screens (what does this mean for naming cells? 
  calculate based on entire coordinate system?)
- [x] allow for using alphabet from std.py
  ALTERNATE_ALPHABET = False
- [x] allow for using both alphabet from std.py and normal alphabet
- [ ] allow for using more than one character/digit per name
- [ ] allow for "rainbow" instead of letter
- [ ] cells can either be squares or rectangles
  SQUARES = False
- [ ] allow user to reference one label instead of two
  TWO_D = True # False would behave more like Dragon's mouse grid where cells
               # are simply numbered 1-9 or similar
- [ ] display on all screens instead of just active screen
  ALL_SCREENS = False
'''

ALTERNATE_ALPHABET = False
SHOW_COORDINATES_IN_CELL = False
SHOW_COORDINATES_ON_EDGES = False
SHOW_COORDINATES_ON_DOTS = True
SHOW_FULL_COORDINATES_ON_DOTS = True
SHOW_CELL_OUTLINES = False
SHOW_CELL_CENTERS = True
SHOW_BIG_HINTS_IN_CELL = False
SHOW_BIG_HINTS_ON_EDGES = False

# TODO: auto calculate dimensions
# TODO: allow using pixels

# alpha
# NUMBER_OF_COLUMNS = 26
# NUMBER_OF_ROWS = 15

# numbers
NUMBER_OF_COLUMNS = 99
NUMBER_OF_ROWS = 51

TOTAL_NUMBER_OF_CELLS = NUMBER_OF_ROWS * NUMBER_OF_COLUMNS
CENTER_CELL_NUMBER = math.floor((TOTAL_NUMBER_OF_CELLS + 1) / 2)

# TODO: calc using screen dimensions/# of rows/cols
FONT_SIZE = 10
DOT_10S_NUMBER_FONT_SIZE = 14
HINT_FONT_SIZE = 50

# # colors
BACKGROUND_COLOR = 'FFFFFF66'
LINE_COLOR = '00000099'
TEXT_COLOR = '999900FF'
DOT_COLOR = '00000066'
DOT_HIGHLIGHT_COLOR = '00FFFFFF'
DOT_SEMIHIGHLIGHT_COLOR = '00999999'
DOT_HIGHLIGHT_10S_NUMBER_COLOR = '77FFFFFF'
EDGE_TEXT_COLOR = '00FFFFFF'
HINT_TEXT_COLOR = '00FFFF66'


def calculate_cells(s):
    screen = s.rect

    cells = []

    screenWidth = s.width
    screenHeight = s.height
    screenLeft = screen.left
    screenTop = screen.top

    # extra info?

    cellWidth = screenWidth / NUMBER_OF_COLUMNS
    cellHeight = screenHeight / NUMBER_OF_ROWS

    cellOffsetX = cellWidth / 2
    cellOffsetY = cellHeight / 2

    # columnIndex = adjustedCellNumber % NUMBER_OF_COLUMNS
    # rowIndex = math.floor(adjustedCellNumber / NUMBER_OF_ROWS)

    # upperLeftX = cellWidth * columnIndex
    # upperLeftY = cellHeight * rowIndex

    lines = {
        'vertical':   [],
        'horizontal': [],
    }

    centers = {
        'columns': [],
        'rows':    [],
    }

    for column_index in range(NUMBER_OF_COLUMNS - 1):
        x_position = screenLeft + screenWidth * ((column_index + 1) / NUMBER_OF_COLUMNS)
        lines['vertical'].append(x_position)

    for row_index in range(NUMBER_OF_ROWS - 1):
        y_position = screenTop + screenHeight * ((row_index + 1) / NUMBER_OF_ROWS)
        lines['horizontal'].append(y_position)

    # TODO: don't need to recalculate ... can pull from two arrays instead
    for row_index in range(NUMBER_OF_ROWS):
        cells.append([])
        center_y_position = screenTop + screenHeight * (row_index / NUMBER_OF_ROWS) + cellOffsetY

        for column_index in range(NUMBER_OF_COLUMNS):
            center_x_position = screenLeft + screenWidth * (column_index / NUMBER_OF_COLUMNS) + cellOffsetX
            cells[row_index].append({
                'center_x': center_x_position,
                'center_y': center_y_position,
            })

    # TODO: attempt to recalculate into two arrays (as mentioned above), replacing `lines`
    for column_index in range(NUMBER_OF_COLUMNS):
        center_x_position = screenLeft + screenWidth * (column_index / NUMBER_OF_COLUMNS) + cellOffsetX
        centers['columns'].append(center_x_position)

    for row_index in range(NUMBER_OF_ROWS):
        center_y_position = screenTop + screenHeight * (row_index / NUMBER_OF_ROWS) + cellOffsetY
        centers['rows'].append(center_y_position)

    return [lines, cells, centers]


def on_draw(canvas):
    # TODO: do we even need to repaint? just show and hide if same active screen!
    global destination_screen

    paint = canvas.paint
    paint.style = paint.Style.FILL

    # TODO: calculate only on `squid`/display configuration change?
    [lines, cells, centers] = calculate_cells(destination_screen)

    # draw background
    paint.color = BACKGROUND_COLOR
    destination = destination_screen.rect
    canvas.draw_rect(destination)

    # draw center dot
    paint.color = '00FFFFFF'
    # canvas.draw_circle(1280, 720, 1.5)  TODO: calculate this

    # draw lines
    if SHOW_CELL_OUTLINES:
        # TODO: store this with cells?
        screenWidth = destination_screen.width
        screenHeight = destination_screen.height
        paint.color = LINE_COLOR

        for x in lines['vertical']:
            canvas.draw_line(x, destination.top, x, destination.top + screenHeight)

        for y in lines['horizontal']:
            canvas.draw_line(destination.left, y, destination.left + screenWidth, y)

    if SHOW_BIG_HINTS_ON_EDGES:
        paint.textsize = HINT_FONT_SIZE
        paint.color = HINT_TEXT_COLOR
        column_centers = centers['columns']
        row_centers = centers['rows']

        for column_index, x in enumerate(column_centers):
            if column_index % 5 == 0 and column_index % 10 != 0:
                column_name = column_names[column_index]
                text = column_name[:-1]
                # # TODO: move display name/formatting out
                # if ALTERNATE_ALPHABET:
                #   column_name = column_name.upper()
                y = row_centers[0]
                draw_centered_text(text, x, y + 15, canvas)

        for row_index, y in enumerate(row_centers):
            if row_index % 5 == 0 and row_index % 10 != 0:
                row_name = row_names[row_index]
                text = row_name[:-1]
                x = column_centers[0]
                draw_centered_text(text, x + 25, y, canvas)

    if SHOW_COORDINATES_ON_EDGES:
        paint.textsize = FONT_SIZE
        paint.color = EDGE_TEXT_COLOR
        column_centers = centers['columns']
        row_centers = centers['rows']

        for column_index, x in enumerate(column_centers):
            column_name = column_names[column_index]

            # TODO: move display name/formatting out
            if ALTERNATE_ALPHABET:
                column_name = column_name.upper()
            y = row_centers[0]

            draw_centered_text(column_name, x, y, canvas)

        for row_index, y in enumerate(row_centers):
            row_name = row_names[row_index]
            x = column_centers[0]

            draw_centered_text(column_name, x, y, canvas)

    # draw coordinate names
    if SHOW_COORDINATES_IN_CELL:
        paint.textsize = FONT_SIZE
        paint.color = TEXT_COLOR

        for row_index, row in enumerate(cells):
            for column_index, cell in enumerate(row):
                x = cell['center_x']
                y = cell['center_y']

                column = column_names[column_index]
                if ALTERNATE_ALPHABET:
                    column = column.upper()
                column = column.ljust(2, ' ')

                row = row_names[row_index]
                row = row.rjust(2, ' ')

                text = column + ' ' + row
                draw_centered_text(text, x, y, canvas)

    # show dots
    if SHOW_CELL_CENTERS:
        for row_index, row in enumerate(cells):
            for column_index, cell in enumerate(row):
                paint.textsize = FONT_SIZE
                x = cell['center_x']
                y = cell['center_y']

                column = column_names[column_index]
                # if ALTERNATE_ALPHABET:
                #   column = column.upper()
                [column_prefix, column_end] = [column[:-1], column[-1]]
                row = row_names[row_index]
                [row_prefix, row_end] = [row[:-1], row[-1]]

                if row_index % 10 == 0 or column_index % 10 == 0:  # every 10
                    paint.color = DOT_HIGHLIGHT_COLOR
                    if SHOW_COORDINATES_ON_DOTS:
                        text = ''
                        if SHOW_FULL_COORDINATES_ON_DOTS:
                            if row_index % 10 == 0 and column_index % 10 == 0:
                                canvas.draw_circle(x, y, 1.5)
                            elif row_index % 10 == 0:
                                text = column
                            else:
                                text = row
                        else:
                            if row_index % 10 == 0 and column_index % 10 == 0:
                                paint.color = DOT_HIGHLIGHT_10S_NUMBER_COLOR
                                paint.textsize = DOT_10S_NUMBER_FONT_SIZE
                                draw_centered_text(column_prefix, x - 12, y - 2, canvas)
                                draw_centered_text(row_prefix, x, y - 12, canvas)
                                paint.textsize = FONT_SIZE
                                paint.color = DOT_HIGHLIGHT_COLOR
                                text = '0'
                            elif row_index % 10 == 0:
                                text = column_end
                            else:
                                text = row_end
                        draw_centered_text(text, x, y, canvas)
                    else:
                        canvas.draw_circle(x, y, 1.5)
                elif row_index % 10 == 5 and column_index % 10 == 5:  # in the center of every 10 x 10
                    paint.color = DOT_HIGHLIGHT_COLOR
                    if False:
                        draw_centered_text('*', x, y, canvas)
                    else:
                        canvas.draw_circle(x, y, 1.0)
                elif row_index % 10 == 5 or column_index % 10 == 5:  # intersecting the center of every 10 x 10
                    paint.color = DOT_SEMIHIGHLIGHT_COLOR
                    if False:
                        draw_centered_text('t', x, y, canvas)
                    else:
                        canvas.draw_circle(x, y, 1.5)
                else:  # all the other dots
                    paint.color = DOT_COLOR
                    if False:
                        draw_centered_text('.', x, y, canvas)
                    else:
                        canvas.draw_circle(x, y, 1.0)

                if row_index % 10 == 5 and column_index % 10 == 5:

                    # TODO: move this out
                    # TODO: a bit hacky? better to rely on own coords? or use % 10 == 0 instead?
                    # show big hints
                    if SHOW_BIG_HINTS_IN_CELL:
                        paint.color = HINT_TEXT_COLOR
                        paint.textsize = HINT_FONT_SIZE

                        column = column_names[column_index]
                        if ALTERNATE_ALPHABET:
                            column = column.upper()
                        column = column[:-1] + '_'

                        row = row_names[row_index]
                        row = row[:-1] + '_'

                        text = column + ', ' + row
                        draw_centered_text(text, x, y - 10, canvas)


def draw_centered_text(text, x, y, canvas):
    paint = canvas.paint
    width, rect = paint.measure_text(text)
    height = rect.height
    line_height = paint.get_fontmetrics(1)[0]
    canvas.draw_text(text, x - (width / 2), y + line_height - (height / 2))
    # columnIndex = adjustedCellNumber % NUMBER_OF_COLUMNS
    # rowIndex = math.floor(adjustedCellNumber / NUMBER_OF_ROWS)

    # upperLeftX = cellWidth * columnIndex
    # upperLeftY = cellHeight * rowIndex


# TODO: default to calculated screen in _GoToCell instead
# TODO: do not use global variable
# TODO: do not repeat code

def active_screen():
    # choose correct screen based off of active window
    if hasattr(ui.active_window(), 'screen'):
        return ui.active_window().screen
    return False


def is_same_screen(screen1, screen2):
    return screen1.x == screen2.x and screen1.y == screen2.y


destination_screen = {}


def set_screen(event, arg):
    global destination_screen
    if event in ('win_open', 'win_close'):
        destination_screen = active_screen()


# Set window on window changes (so we'll actually have a window).
ui.register('', set_screen)


def go_to_coord(m):
    print(m)
    move_absolute(m['mouse_grid.column'][0], m['mouse_grid.row'][0])


def GoToCell(off=1, num_spoken=1):
    def _GoToCell(m):
        # TODO: how to do this without having to explicitly pass in the number of words spoken?
        # from https://github.com/anonfunc/talon-user/blob/master/misc/mouse_snap9.py, possibly:
        '''
        def narrow(m):
        for d in m["mouseSnapNine.digits"]:
            mg.narrow(int(d))

        keymap = {
            "{mouseSnapNine.digits}+": narrow
        }

        digits = dict((str(n), n) for n in range(1, 11))
        ctx.keymap(keymap)
        ctx.set_list("digits", digits.keys())
        '''
        column = m._words[num_spoken]
        row = m._words[num_spoken + 1]
        move_absolute(column, row)

    return _GoToCell


def move_absolute(column, row):
    print(column, row)
    global destination_screen
    global x_old
    global y_old8

    [_, cells, centers] = calculate_cells(destination_screen)
    column_index = column_names_indices[column]
    row_index = row_names_indices[row]
    cell = cells[row_index][column_index]
    x = cell['center_x']
    y = cell['center_y']
    x_old, y_old = ctrl.mouse_pos()
    ctrl.mouse(x, y)


def toggle_grid(m):
    global grid_is_showing
    global destination_screen
    global grid_canvas

    def create_canvas_from_screen(screen):
        canvas = Canvas.from_screen(screen)
        canvas.register('draw', on_draw)
        canvas.hide()
        return canvas

    if grid_canvas is None:
        grid_canvas = create_canvas_from_screen(destination_screen)

    if grid_is_showing:
        # hide it
        grid_canvas.hide()
    else:
        # show it (on active screen)

        if not is_same_screen(destination_screen, active_screen()):
            # unregister handlers on old canvas
            grid_canvas.unregister('draw', on_draw)
            grid_canvas.close()
            # set up new canvas
            destination_screen = active_screen()
            grid_canvas = create_canvas_from_screen(destination_screen)

        # unhide it
        grid_canvas.show()
        # update it (trigger `draw` event)
        grid_canvas.freeze()

    # save toggle status
    grid_is_showing = not grid_is_showing


def Click():
    return lambda m: ctrl.mouse_click(0)


def Double_Click():
    return lambda m: (ctrl.mouse_click(x, y, button=button, times=times, wait=16000), time.sleep(0.032))


def Drag():
    def mouse_drag_2(m):
        ctrl.mouse_click(0, down=True)
        time.sleep(0.032)

    return mouse_drag_2


def Release():
    def mouse_release_2(m):
        ctrl.mouse_click(0, up=True)

    return mouse_release_2


def convert_list_to_grammar(list_argument):
    return '(' + ' | '.join(str(x) for x in list_argument) + ')'


def go_back(_):
    global x_old
    global y_old

    x = x_old
    y = y_old
    x_old, y_old = ctrl.mouse_pos()
    ctrl.mouse(x, y)


def move_relative(m):
    print('move relative')
    global destination_screen
    s = destination_screen

    for direction_word in m["mouse_grid.directions"]:
        for amount_word in m["mouse_grid.relative_numbers"]:
            direction = str(direction_word)
            amount = int(amount_word)
            print(direction)
            print(amount)

            cellWidth = s.width / NUMBER_OF_COLUMNS
            cellHeight = s.height / NUMBER_OF_ROWS

            if direction == 'left' or direction == 'right':
                amount = amount * cellWidth
            else:
                amount = amount * cellHeight

            if direction == 'up' or direction == 'left':
                amount = -amount

            # TODO: combine this with `move_absolute`
            # TODO: use centers instead?
            dx = amount if direction == 'left' or direction == 'right' else 0
            dy = amount if direction == 'up' or direction == 'down' else 0

            global x_old
            global y_old

            x_old, y_old = ctrl.mouse_pos()
            x = x_old
            y = y_old

            ctrl.mouse(x + dx, y + dy)


# TODO: generate these on the fly based on the screen dimensions etc

# characters
# column_names = alpha_alt if ALTERNATE_ALPHABET else list(string.ascii_uppercase)
# column_names = column_names[:NUMBER_OF_COLUMNS]

def grammar_or(list):
    return '(' + ' | '.join(list) + ')'


def grammar_optional(part):
    return '[' + str(part) + ']'


# numbers
ones = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
# ones = '(one | two | three | four | five | six | seven | eight | nine)'

teens = ['eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
# teens = '(eleven | twelve | thirteen | fourteen | fifteen | sixteen | seventeen | eighteen | nineteen)'
tens = ['ten', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
# tens = '(ten | twenty | thirty | forty | fifty | sixty | seventy | eighty | ninety)'

# TODO: start with numbers first, not the words2
spoken_to_index_map = {
    'zero': 0
}

for idx, word in enumerate(ones):
    spoken_to_index_map[word] = idx + 1
for idx, word in enumerate(teens):
    spoken_to_index_map[word] = (idx + 1) + 10
for idx, word in enumerate(tens):
    spoken_to_index_map[word] = (idx + 1) * 10
    for idx2, word2 in enumerate(ones):
        spoken_to_index_map[word + ' ' + word2] = (idx + 1) * 10 + (idx2 + 1)

print(spoken_to_index_map)
spoken_99 = spoken_to_index_map.keys()

# grammar approach
small_numbers = f'({grammar_or(tens)} [{grammar_or(ones)}] | {grammar_or(teens)})'
# hundreds = f'{small_numbers} hundred [and] [{small_numbers}]'
# huge_numbers = f'{hundreds} (thousand | million | billion | trillion)+ [and] [{hundreds}]'

column_names = [str(integer) for integer in list(range(NUMBER_OF_COLUMNS))]
row_names = [str(integer) for integer in list(range(NUMBER_OF_ROWS))]

column_names_indices = {v: i for i, v in enumerate(column_names)}
row_names_indices = {v: i for i, v in enumerate(row_names)}

grid_is_showing = False
grid_canvas = None

column_names_as_grammar = convert_list_to_grammar(column_names)
row_names_as_grammar = convert_list_to_grammar(row_names)
coordinates_as_grammar = column_names_as_grammar + ' ' + row_names_as_grammar

x_old, y_old = ctrl.mouse_pos()

directions = ['left', 'right', 'up', 'down']
relative_numbers = column_names if len(column_names) > len(row_names) else row_names

ctx = Context('mouse_grid')

ctx.set_list('directions', directions)
ctx.set_list('relative_numbers', relative_numbers)

# list + grammar approach
ctx.set_list('ones', ones)
ctx.set_list('teens', teens)
ctx.set_list('tens', tens)

small_numbers = '({tens} [{ones}] | {teens} | {ones})'
# drawback is: no named arguments

# list approach
ctx.set_list('column', spoken_99)
ctx.set_list('row', spoken_99)

column_names_indices = spoken_to_index_map
row_names_indices = spoken_to_index_map

# hundreds = '{small_numbers} hundred [and] [{small_numbers}]'
# huge_numbers = '{hundreds} (thousand | million | billion | trillion)+ [and] [{hundreds}]'

# TODO: reuse mouse commands somehow
# from https://github.com/anonfunc/talon-user/blob/master/misc/mouse_snap9.py, possibly:
'''
keymap.update({k: [v, mg.reset] for k, v in click_keymap.items()})
'''
ctx.keymap({
    'squid {mouse_grid.directions} {mouse_grid.relative_numbers}':                                  move_relative,
# e.g., `squid left 10`
    'squid {mouse_grid.column} {mouse_grid.row}':                                                   go_to_coord,
    # 'squid ' + coordinates_as_grammar: GoToCell(2),
    'squid':                                                                                        toggle_grid,
    'squid <dgndictation>':                                                                         lambda *args: None,
# prevent squid blabla from dismissing the grid
    'squid (click | chiff)' + coordinates_as_grammar:                                               [GoToCell(2, 2),
                                                                                                     Click()],
    'squid (dubclick | duke)' + coordinates_as_grammar:                                             [GoToCell(2, 2),
                                                                                                     Double_Click()],
    'squid (drag | pretzel)':                                                                       Drag(),
    'squid (drag | pretzel) ' + coordinates_as_grammar:                                             [GoToCell(2, 2),
                                                                                                     Drag()],
    'squid (release | relish)':                                                                     Release(),
    'squid (release | relish) ' + coordinates_as_grammar:                                           [GoToCell(2, 2),
                                                                                                     Release()],
    'squid (drag | pretzel) [from] ' + coordinates_as_grammar + ' until ' + coordinates_as_grammar: [GoToCell(2, 3),
                                                                                                     Drag(),
                                                                                                     GoToCell(2, 6),
                                                                                                     Release()],
# WIP: experimenting with combination drag/release
    'squid (drag | pretzel) (until | to) ' + coordinates_as_grammar:                                [Drag(),
                                                                                                     GoToCell(2, 3),
                                                                                                     Release()],
    'squid (release | relish) at ' + coordinates_as_grammar:                                        [GoToCell(2, 3),
                                                                                                     Release()],
    'squid go back':                                                                                go_back,
    'quids ' + coordinates_as_grammar:                                                              GoToCell(3)
})