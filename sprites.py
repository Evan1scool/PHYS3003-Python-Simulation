import pygame as pg
import pygame.gfxdraw
import math
from settings import *
from random import random, choice, randrange
import matplotlib.pyplot as plt
import numpy as np
vec = pg.math.Vector2

#PLANET_IMG = pg.Surface((30, 30), pg.SRCALPHA)
#pg.gfxdraw.aacircle(PLANET_IMG, 20, 15, RADIUS, (0,255,0))
#pg.gfxdraw.filled_circle(PLANET_IMG, 20, 15, RADIUS, (0,255,0))

def plot_data(L1, L2):
    fig, axs = plt.subplots(1) #creating axis
    #print("creating plot")
    fig.suptitle('Maxwell-Boltzmann Distribution')
    axs.plot(L1,L2)
    axs.set_ylabel('Number of Bodys')
    axs.set_xlabel('Speed')
    plt.show()


class Clicksprite(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.layer = 0
        self.groups = game.all_sprites, game.clicksprite
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((5,5))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    def update(self):
        pass

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.layer = PLANET_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((20,20))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.vel = vec(0,0)
        self.pos = vec(x,y)

    def get_keys(self):
        #print('Getting keys')
        self.vel = vec(0,0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.vel.x -= cam_speed
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vel.x += cam_speed
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel.y -= cam_speed
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel.y += cam_speed

    def update(self):
        self.rect.center = self.pos
        self.get_keys()
        #print("updating, got keys")
        #print('Pos:', self.pos)
        self.pos += self.vel * self.game.dt
        #print(self.pos)

class Planet(pg.sprite.Sprite):
    def __init__(self, game, x, y, v, rot, m):
        layer = PLANET_LAYER
        self.groups = game.all_sprites, game.planets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.radius = round(RADIUS*(m**0.2))
        self.image = pg.Surface((self.radius,self.radius))
        if m<75:
            col = (m*255/75,0,0)
        elif 74<m<150:
            col = (255,m*255/150,0)
        elif m < 225:
            col = (255,255,m*255/225)
        else:
            col = (255,255,255)
        self.image.fill(col)
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.rect.center = (x,y)
        self.acc = vec(0,0)
        self.rot = rot
        self.vel = vec(1,0).rotate(-self.rot)
        self.vel.scale_to_length(v)
        self.pos = vec(x,y)
        ##self.kenergy = 0
        self.penergy = 0
        #if self.pos.x < (WIDTH+140)/2:
            #self.vel.y += 0.1*(((WIDTH+140)/2)-self.pos.x)
        #else:
            #self.vel.y -= (self.pos.x - (WIDTH+140)/2)*0.1
        self.mom = vec(0,0)
        self.poss_diff = 0
        self.mass = m
        self.targets = pg.sprite.Group()
        self.force = vec(0,0)
        self.force_total = vec(0,0)
        self.text_surf = self.game.font.render("{}".format(self.mass), True, BLACK)

    def find_target(self):
        for planet in self.game.planets:
            if planet != self:
                found = False
                for p in self.targets:
                    if p == planet:
                        found = True
                if found == False:
                    self.targets.add(planet)

    def update(self):
        if self.game.paused == False:
            self.find_target()
            self.rect.center = self.pos
            self.force_total = vec(0,0)
            #self.kenergy = 0
            #self.penergy = 0
            self.force = vec(0,0)
            for target in self.targets:
                target_dist = (target.pos - self.pos)
                self.rot = target_dist.angle_to(vec(1,0))
                dist_mag = pg.math.Vector2.magnitude(target_dist)
                if dist_mag != 0:
                    self.force_mag = F_MULT*(self.mass*target.mass)/(dist_mag**2)
                    self.force = vec(1,0).rotate(-self.rot)
                    self.force.scale_to_length(self.force_mag)
                    self.force_total += self.force
                    #self.penergy = -self.force_mag * dist_mag
                    #print("Gravitational Potential",-self.force_mag * dist_mag)
            self.rot = self.force_total.angle_to(vec(1,0))
            self.acc = vec(1,0).rotate(-self.rot)
            self.acc.scale_to_length(pg.math.Vector2.magnitude(self.force_total)/self.mass)
            self.vel += self.acc * self.game.dt
            if self.vel.x != 0 and self.vel.y !=0:
                self.mom = vec(1,0).rotate(-self.vel.angle_to(vec(1,0)))
                self.mom.scale_to_length(self.mass*pg.math.Vector2.magnitude(self.vel))
            self.pos_diff = self.vel * self.game.dt * 0.5 + self.acc * self.game.dt ** 2
            self.pos += self.pos_diff
            #self.kenergy = 0.5*self.mass*(pg.math.Vector2.magnitude(self.vel)**2)
            #print("Kinetic", 0.5*self.mass*(pg.math.Vector2.magnitude(self.vel)**2))
            self.topleft = vec(self.rect.topleft)
            self.game.draw_text("{}".format(self.mass), self.game.font, BLACK, self.topleft.x, self.topleft.y)

class Button(pg.sprite.Sprite):
    def __init__(self, game, x, y, W, H, ac, bc, action=None):
        self.layer = BUTTON_LAYER
        self.groups = game.all_sprites, game.buttons
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((W,H))
        self.image.fill(bc)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.x = x
        self.y = y
        self.width = W
        self.height = H
        self.ac = ac
        self.bc = bc
        self.action = action
        self.active = False
        self.font = self.game.font
        if action == 1:
            self.text = "New Planet"
        if action == 2:
            self.text = "New Sun"
        if action == 3:
            self.text = "+Vel"
        if action == 4:
            self.text = "+Rot"
        if action == 5:
            self.text = "-V"
        if action == 6:
            self.text = "-Rot"
        if action == 7:
            self.text = "CLEAR"
        if action == 8:
            self.text = "N-Body"
        if action == 9:
            self.text = "Select"
        self.text_surface = self.font.render(self.text, True, WHITE)
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.midtop = (self.x +(W/2), self.y)

    def get_boltz(self, T, m, n):
        speed = 0
        p_num = 0
        p_numbers = []
        p_tot = 0
        while True:
            p_num = 100*((m**3)**0.5)*(speed*speed)*math.exp(-m*speed*speed/T)
            p_numbers.append(p_num)
            speed+=1
            p_tot += p_num
            if speed > 100:
                break
        prob = np.zeros(len(p_numbers), int)
        prob_num = 0
        for i in range(0,len(p_numbers)):
            prob[i] = round(p_numbers[i]*n/p_tot)
            prob_num += prob[i]
        #print(prob, prob_num)
        return prob

    def action1(self, game, x, y, v1, v2):
        Planet(self.game, x, y, v1, v2, 1)
    def action2(self, game, x, y, v1, v2):
        Planet(self.game, x, y, v1, v2, 1000)
    def action3(self):
        self.game.V += 5
    def action4(self):
        self.game.rot += 10
    def action5(self):
        self.game.V -= 5
    def action6(self):
        self.game.rot -= 10
    def action7(self):
        for sprite in self.game.planets:
            sprite.kill()
        self.game.player = Player(self.game, WIDTH/2, HEIGHT/2)
        #print("Time: steps:", self.game.time_steps)
        #print("Planet Numbers:", self.game.planet_numbers)
        plot_data(self.game.time_steps, self.game.planet_numbers)
        #plot_data(self.game.time_steps, self.game.energys)
        self.game.time_step = 0
        self.game.time_steps = []
        self.game.planet_numbers = []
        self.game.energys = []
    def action8(self):
        for sprite in self.game.planets:
            sprite.kill()
        self.game.paused = True
        self.game.player = Player(self.game, WIDTH/2, HEIGHT/2)
        n = NUMBER
        m = MASS
        T = TEMPERATURE
        boltz = self.get_boltz(T, m, n)
        for i in range(0, len(boltz)):
            if boltz[i] != 0:
                for ii in range (0, boltz[i]):
                    x = randrange(140, WIDTH)
                    y = randrange(0, HEIGHT)
                    speed = i
                    rot = randrange(0,360)
                    Planet(self.game, x, y, speed, rot, m)
        self.game.time_step = 0
        self.game.time_steps = []
        self.game.planet_numbers = []
        self.game.energys = []
            #Planet(self.game, x, y, vx, vy, m, GREEN)

    def update(self):
        self.mouse = pg.mouse.get_pos()
        self.click = pg.mouse.get_pressed()
        #print(pg.mouse.get_pos())
        if self.x < self.mouse[0] < self.x + self.width and self.y < self.mouse[1] < self.y+self.height :
            self.col = self.ac
            #print(self.click, self.action)
            if self.click[0] == 1:
                self.active = True
                for butt in self.game.buttons:
                    if butt != self:
                        butt.active = False
                if self.action == 3:
                    self.action3()
                if self.action == 4:
                    self.action4()
                if self.action == 5:
                    self.action5()
                if self.action == 6:
                    self.action6()
                if self.action ==7:
                    self.action7()
                if self.action == 8:
                    self.action8()
        else:
            self.col = self.bc
        self.image.fill(self.col)
