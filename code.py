from adafruit_macropad import MacroPad
import board
import time
import terminalio
from adafruit_display_text import label
import displayio
import adafruit_imageload
import random

display = board.DISPLAY
macropad = MacroPad()

# Setup --------------------------

# Load splash image
macropad.display_image("game-of-life-splash.bmp")

# Load spritesheet
TILE_WIDTH = 4
TILE_HEIGHT = 4 
WIDTH = int(128 / TILE_WIDTH)
HEIGHT = int(64 / TILE_HEIGHT)
CENTER = WIDTH * int(HEIGHT/2) + int(WIDTH / 2) - 1

spritesheet, palette = adafruit_imageload.load("cells-and-selectors.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)

# create a sprite
sprite = displayio.TileGrid(spritesheet, pixel_shader=palette, width=WIDTH, height=HEIGHT, tile_width=TILE_WIDTH, tile_height=TILE_HEIGHT)

# create a group to hold the sprite
group = displayio.Group(scale=1)

# add the sprite to the group 
group.append(sprite)

# add the Group to the Display
#display.show(group)

# set sprite location 
group.x = 0
group.y = 0


# methods for determining the moore neighborhood of 
# a given cell. Here, we identify the left and right edges
# as well as the top and bottom, effectively representing a torus


def left_of_cell(cell, x_size, y_size):
    if(cell % x_size == 0):
        # cell is on far left of grid -> it's left side neighbor is on the far right
        return cell + (x_size - 1)
    else:
        return cell - 1


def right_of_cell(cell, x_size, y_size):
    if((cell + 1) % x_size == 0):
        # cell is on the right of the grid -> it's right side neighbor is on the far left
        return cell - (x_size - 1)
    else: 
        return cell + 1

def above_cell(cell, x_size, y_size):
    if(cell - x_size < 0):
        # cell is on the top row -> it's neighbor above is on the bottom 
        return cell + (x_size * y_size - (x_size))
    else: 
        return cell - x_size

def below_cell(cell, x_size, y_size):
    if(cell + x_size > (x_size*y_size - 1)):
        #cell is at bottom -> it's neighbor below is on the top
        return cell % x_size
    else: 
        return cell + x_size

# nest functions to get the corners

def upper_left_cell(cell, x_size, y_size):
    return above_cell(left_of_cell(cell, x_size, y_size), x_size, y_size)

def upper_right_cell(cell, x_size, y_size):
    return above_cell(right_of_cell(cell, x_size, y_size), x_size, y_size)

def lower_left_cell(cell, x_size, y_size):
    return below_cell(left_of_cell(cell, x_size, y_size), x_size, y_size)

def lower_right_cell(cell, x_size, y_size):
    return below_cell(right_of_cell(cell, x_size, y_size), x_size, y_size)



# This is just a helper method that draws the neighborhood of a given cell, regardless if the cell is on or off

def draw_neighbors(cell):
    sprite[left_of_cell(cell, WIDTH , HEIGHT)] = 1
    sprite[right_of_cell(cell, WIDTH, HEIGHT)] = 1
    sprite[above_cell(cell, WIDTH, HEIGHT )] = 1
    sprite[below_cell(cell, WIDTH, HEIGHT)] = 1
    sprite[upper_left_cell(cell,  WIDTH, HEIGHT)] = 1
    sprite[upper_right_cell(cell, WIDTH, HEIGHT)] = 1
    sprite[lower_left_cell(cell, WIDTH, HEIGHT)] = 1
    sprite[lower_right_cell(cell ,WIDTH, HEIGHT)] = 1


# this counts the moore neighborhood of the cell
def check_neighbors(cell, x_size, y_size, sprite):
    num_neighbors = 0
    if(sprite[left_of_cell(cell, x_size, y_size)] == 1):
        num_neighbors += 1
    if(sprite[right_of_cell(cell, x_size, y_size)] == 1):
        num_neighbors += 1
    if(sprite[above_cell(cell, x_size, y_size)] == 1):
        num_neighbors += 1
    if(sprite[below_cell(cell, x_size, y_size)] == 1):
        num_neighbors += 1
    if(sprite[upper_left_cell(cell, x_size, y_size)] == 1):
        num_neighbors += 1
    if(sprite[upper_right_cell(cell, x_size, y_size)] == 1):
        num_neighbors += 1
    if(sprite[lower_left_cell(cell, x_size, y_size)] == 1):
        num_neighbors += 1
    if(sprite[lower_right_cell(cell, x_size, y_size)] == 1):
        num_neighbors += 1

    return num_neighbors

def choose_selector_sprite(selector_pos):
    if(group[0][selector_pos] == 1):
        group[0][selector_pos] = 3
    if(group[0][selector_pos] == 2):
        group[0][selector_pos] = 0
    if(group[0][selector_pos] == 3):
        group[0][selector_pos] = 1



def game_of_life(sprite):
    next_generation = displayio.TileGrid(spritesheet, pixel_shader=palette, width=WIDTH, height=HEIGHT, tile_width=TILE_WIDTH, tile_height=TILE_HEIGHT)
    for cell in range(0, WIDTH * HEIGHT):
        neighbors = check_neighbors(cell, WIDTH, HEIGHT, sprite)
        if(sprite[cell] == 1):
            # if a cell is alive... 
            if(neighbors < 2):
                # and has fewer than 2 neighbors, it dies as by underpopulation
                next_generation[cell] = 0
            if(neighbors in (2, 3)):
                # or if it has 2 or 3 live neighbors it survives 
                next_generation[cell] = 1
            if(neighbors > 3):
                # or if it has greater than three live neighbors it dies, as if by overpopulation
                next_generation[cell] = 0
        else:
            # if a cell is not yet alive
            if(neighbors == 3): 
                # it becomes alive, as if by reproduction
                next_generation[cell] = 1
    # remove last generation and replace with the new one
    group.pop()
    group.append(next_generation)




# glider

# EXAMPLES -----------------------------------

def glider():
    # walks across the screen
    sprite[CENTER] = 1
    sprite[CENTER + 1] = 1
    sprite[CENTER - 1] = 1
    sprite[CENTER + 1 + WIDTH] = 1
    sprite[CENTER + 2*WIDTH] = 1

def randomtiles():
    # see what happens!
    for i in range(0, WIDTH*HEIGHT):
        sprite[i] = random.randint(0,1)


def pulsar():
    # Example of a repeating pattern
    # WARNING: this probably wont work with sprites that are greater than 4x4
    nw_center = CENTER - 3 - 3*WIDTH
    ne_center = CENTER + 3 - 3*WIDTH 
    sw_center = CENTER - 3 + 3*WIDTH
    se_center = CENTER + 3 + 3*WIDTH
    draw_neighbors(nw_center)
    draw_neighbors(ne_center)
    draw_neighbors(se_center)
    draw_neighbors(sw_center)


#pulsar()
#randomtiles()

# Start Button
macropad.pixels[11] = (10, 50, 15)
show = False
selector_pos = CENTER
play = False
counter = 0
game_start = 0
while True: 
    key_event = macropad.keys.events.get()
    if(key_event and key_event.pressed and show == False ):
        if(key_event.key_number == 11):
            display.show(group)
            show = True
    if(key_event and key_event.pressed and key_event.key_number == 11 and show and counter > 0 and play == False ):
        print(counter)
        for i in range(0, WIDTH*HEIGHT):
            if(group[0][i] == 2):
                group[0][i] = 0
            elif(group[0][i] == 3):
                group[0][i] = 1
        game_start = counter
        play = True
        macropad.pixels[11] = (50, 20, 20)
    if(key_event and key_event.pressed and key_event.key_number == 11 and show and counter > game_start and play == True):
        play = False
        macropad.pixels[11] = (10, 50, 15)
    if(key_event and key_event.pressed and key_event.key_number == 9 and show and counter > 0 and play == False):
        for cell in range(0, WIDTH*HEIGHT):
                group[0][cell] = 0
        group[0][selector_pos] = 2

    if(show):
        # Controls
        macropad.pixels[1] = (0, 0, 100)
        macropad.pixels[3] = (0, 0, 100)
        macropad.pixels[4] = (50, 40, 100)
        macropad.pixels[5] = (0, 0, 100)
        macropad.pixels[7] = (0, 0, 100)
        macropad.pixels[9] = (0, 0, 0)
        if(play == False):
            # show clear button only in edit mode
            macropad.pixels[9] = (20, 0, 0)

            if(group[0][selector_pos] == 0):
                # on a blank cell show blank selector
                group[0][selector_pos] = 2
            if(group[0][selector_pos] == 1):
                # on a filled cell show filled selector
                group[0][selector_pos] = 3
            if(key_event and key_event.pressed):
                if(key_event.key_number == 4):
                    if(group[0][selector_pos] == 2):
                        group[0][selector_pos] = 3
                    elif(group[0][selector_pos] == 3):
                        group[0][selector_pos] = 2

                choose_selector_sprite(selector_pos)
                new_selector_pos = selector_pos
                if(key_event.key_number == 3):
                    new_selector_pos = left_of_cell(selector_pos, WIDTH, HEIGHT)
                if(key_event.key_number == 1):
                    new_selector_pos = above_cell(selector_pos, WIDTH, HEIGHT)
                if(key_event.key_number == 5):
                    new_selector_pos = right_of_cell(selector_pos, WIDTH, HEIGHT)
                if(key_event.key_number == 7):
                    new_selector_pos = below_cell(selector_pos, WIDTH, HEIGHT)
                selector_pos = new_selector_pos

        if(play):
            game_of_life(group[0])
        counter += 1


