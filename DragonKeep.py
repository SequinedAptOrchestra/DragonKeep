from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
import pdb
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

#BG_WD = 6464
#BG_HT = 4829
BG_WD = 1600
BG_HT = 800
OBSTACLES = [[(-2926, -12), (-2247, -12)], [(-2239, -11), (-1931, -176)]]

testinfo = "s, q"
tags = "tilemap, collide_map, collider"


import pyglet
from pyglet.window import key
from pyglet.window import mouse

pyglet.resource.path.append(pyglet.resource.get_script_home())
pyglet.resource.reindex()

import cocos
from cocos import tiles, actions, layer, mapcolliders


class PlatformerController(actions.Action):
    on_ground = True
    MOVE_SPEED = 30
    JUMP_SPEED = 200
    GRAVITY = -80
    player_direction = key.RIGHT
    player_scale = 1

    def start(self):
        self.target.velocity = (0, 0)

    def step(self, dt):
        global keyboard, scroller
        if dt > 0.1:
            # a too big dt will move the player through walls
            # dt can be big at startup in slow hardware, as a raspi3
            # so do nothing on big dt
            return
        vx, vy = self.target.velocity
        #pdb.set_trace()

        if ((keyboard[key.RIGHT])  and (self.player_direction == key.LEFT)):
            #self.target.image = player_right
            self.player_direction = key.RIGHT

        if ((keyboard[key.LEFT]) and (self.player_direction == key.RIGHT)):
            #self.target.image = player_left
            self.player_direction = key.LEFT
                           
        # using the player controls, gravity and other acceleration influences
        # update the velocity
        vx = (keyboard[key.RIGHT] - keyboard[key.LEFT]) * self.MOVE_SPEED
        vy += self.GRAVITY * dt
        if self.on_ground and keyboard[key.SPACE]:
            vy = self.JUMP_SPEED

        # with the updated velocity calculate the (tentative) displacement
        dx = vx * dt
        dy = vy * dt

        # get the player's current bounding rectangle
        last = self.target.get_rect()

        # build the tentative displaced rect
        new = last.copy()
        new.x += dx
        new.y += dy

        # account for hitting obstacles, it will adjust new and vx, vy
        self.target.velocity = self.my_collision_handler(last, new, vx, vy)

        # update on_ground status
        self.on_ground = (new.y == last.y)

        # update player position; player position is anchored at the center of the image rect
        self.target.position = new.center

        # move the scrolling view to center on the player
        scroller.set_focus(*new.center)

    def my_collision_handler(self, last, new, vx, vy):
        this_vx = vx
        this_vy = vy
        #if (collision_y_detected == True):
        #    new.y = last.y
        #    this_vy = 0
        a = (vx, vy)
        return a

class DragonKeepScrollingLayer(layer.ScrollableLayer):
    is_event_handler = True
    
    def __init__( self ):
        super( layer.ScrollableLayer, self ).__init__()

    def on_mouse_release(self, x, y, buttons, modifiers):
        pdb.set_trace()
        print("mouse x{}, y{}".format(x, y))

    def on_key_press(self, key, modifier):
        print("scroll x{} y{}".format(x, y))

description = """
Dragon Keep: The Exploration Game

Original Art by Rachel Luc
Code Monkey: Ben Luc
"""
                                      
def main():
    global keyboard, tilemap, scroller, player_direction, player_right, player_left, my_start_x, ground_list, start_point
    from cocos.director import director
    director.init(width=BG_WD, height=BG_HT, autoscale=False)

    print(description)
    # create a layer to put the player in
    player_layer = layer.ScrollableLayer(1)
    # NOTE: the anchor for this sprite is in the CENTER (the cocos default)
    # which means all positioning must be done using the center of its rect
    player = cocos.sprite.Sprite('block_man.png')
    player.x = -2850
    player.y = 120
    
    dragon_keep_bg = cocos.sprite.Sprite('DragonKeepPNG.png')

    player_layer.add(dragon_keep_bg, z=1)
    player_layer.add(player, z=2)

    #test tmx object collision - no really good examples
    #points = [(3232, 2400), (4232, 2400), (4232, 2300), (3232, 2300)]
    #t = cocos.tiles.TmxObject('polygon', 'dragon', 3232, 2400, 1000, 10, None, None, None, 1, points)
    #lay = cocos.tiles.TmxObjectLayer('layer', (255, 0, 0, 255), [t], 1, 1, (3232, 2400))
    #i = 0
    #pdb.set_trace()
    #while (i < 10):
    #    player.x += 10
    #    player.y -= 10
    #    rect = player.get_rect()
    #    if (lay.collide(rect, 'layer')):
    #        print("True!")
    #    i+=1

    #tbd
    player.do(PlatformerController())
    
    scroller = layer.ScrollingManager()
    scroller.add(player_layer, z=2)

    # construct the scene with a background layer color and the scrolling layers
    platformer_scene = cocos.scene.Scene()
    platformer_scene.add(layer.ColorLayer(0, 0, 0, 255), z=0)
    platformer_scene.add(scroller, z=1)

    # track keyboard presses
    keyboard = key.KeyStateHandler()
    director.window.push_handlers(keyboard)
    my_start_x = 0
    ground_list = []
    start_point = []
    
    # allow display info about cells / tiles 
    def on_key_press(key, modifier):
        #pdb.set_trace()
        global player_direction
        if key == pyglet.window.key.LEFT:
            player.x -= 100
        if key == pyglet.window.key.RIGHT:
            player.x += 100
        if key == pyglet.window.key.UP:
            player.y += 100
        if key == pyglet.window.key.DOWN:
            player.y -= 100
        if key == pyglet.window.key.E:
            print(ground_list)

        scroller.set_focus(player.position[0], player.position[1])
        print(player.position)
        print("x{}, y{}".format(player.x, player.y))

    def on_mouse_release(x, y, buttons, modifiers):
        global my_start_x, start_point, ground_list
        t = scroller.screen_to_world(x, y)
        print("mouse x{}, y{}".format(x, y))
        print("mouse x{}, y{}".format(t[0], t[1]))
        if (my_start_x == 0):
            print("start_x = 0")
            my_start_x = 1
            start_point = t
        else:
            print("start_x = 1")
            my_start_x = 0
            ground_list.append([start_point, t])
        
             
    director.window.push_handlers(on_key_press)
    director.window.push_handlers(on_mouse_release)

    scroller.set_focus(player.position[0], player.position[1])

    # run the scene
    director.run(platformer_scene)


if __name__ == '__main__':
    main()
