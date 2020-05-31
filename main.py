import pygame as pg
import sys
from settings import *
from sprites import *
import matplotlib.pyplot as plt
vec = pg.math.Vector2

class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        self.x = -target.rect.centerx + int(WIDTH / 2) + 70
        self.y = -target.rect.centery + int(HEIGHT / 2)

        #limit for map size
        #x = min(0, x)
        #y = min(0, y)
        #x = max(-(self.width  - WIDTH), x)
        #y = max(-(self.height - HEIGHT), y)
        self.camera = pg.Rect(self.x, self.y, self.width, self.height)

class Simulation:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH,HEIGHT))
        self.pathscreen = pg.display.set_mode((WIDTH,HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()

    def kill(self):
        pygame.sprite.Sprite.kill(self)

    def draw_text(self, text, font, colour, x, y):
        text_surface = font.render(text, True, colour)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x,y)
        self.screen.blit(text_surface, text_rect)

    def new(self):
        # VARIABLES FOR NEW SIMULATION #
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.planets = pg.sprite.Group()
        self.buttons = pg.sprite.Group()
        self.clicksprite = pg.sprite.Group()
        self.paused = True
        self.draw_lines = False
        self.font = pg.font.SysFont("FONT", 25)
        self.title_font = pg.font.SysFont("FONT", 60)
        self.V = 0
        self.rot = 0
        self.time_step = 0
        self.time_steps = []
        self.planet_numbers = []
        self.energys = []
        self.total_energy = 0
        #Planet(self, WIDTH/2 - 500, HEIGHT/2, 5, 0, 1)
        #Planet(self, WIDTH/2 + 100, HEIGHT/2, 5, 180, 1)
        #Planet(self, WIDTH/2, HEIGHT/2, 0 ,0, 2000)
        x = 140 + (WIDTH - 140)/2
        self.player = Player(self, WIDTH/2, HEIGHT/2)
        Button(self, 20, 20, 100, 50, D_GREEN, M_GREEN, 1)
        Button(self, 20, 90, 100, 50, D_YELLOW, M_YELLOW, 2)
        Button(self, 15, 220, 35, 50, D_RED, RED, 3)
        Button(self, 80, 220, 35, 50, D_RED, RED, 4)
        Button(self, 15, 290, 35, 50, D_BLUE, BLUE, 5)
        Button(self, 80, 290, 35, 50, D_BLUE, BLUE, 6)
        Button(self, 20, 350, 100, 50, D_RED, RED, 7)
        Button(self, 20, 400, 100, 50, D_GREEN, GREEN, 8)
        Button(self, 20, 470, 100, 50, D_GREEN, GREEN, 9)

        self.camera = Camera(WIDTH, HEIGHT)

    def run(self):
        # SIMULATION LOOP #
        self.simulating = True
        while self.simulating:
            self.dt = self.clock.tick(FPS) / 1000
            if self.paused == False:
                self.time_step += 1
                self.time_steps.append(self.time_step)
                self.planet_numbers.append(len(self.planets))
                self.total_energy = 0
                #i = 0
                #for planet in self.planets:
                    #self.total_energy += planet.kenergy
                    #if i == 0:
                        #print(planet.penergy, planet.kenergy)
                        #self.total_energy += planet.penergy

                self.energys.append(self.total_energy)

            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # UPDATE THE SIMULATION #
        self.all_sprites.update()
        if self.player != None:
            self.camera.update(self.player)
        else:
            self.camera = Camera(WIDTH, HEIGHT)
        if( len(self.planets) == 1):
            print("Time steps to get to 1 body", self.time_step)
            self.quit()
        plans_x = []
        plans_y = []
        plans_mom = []
        plans_rot = []
        plans_mass = []
        n = 0
        ii = 0
        player = False
        for planet in self.planets:
            collides = pg.sprite.Group()
            for target in planet.targets:
                dist = planet.pos - target.pos
                if  dist.length() <= planet.radius/1.5:
                    collides.add(target)
            #hits = pg.sprite.spritecollide(planet, planet.targets, False)
            if collides:
                n+=1
                pos = vec(0,0)
                mom = vec(0,0)
                mass = 0
                n = len(collides)
                for hit in collides:
                    pos += hit.pos
                    mom += hit.mom
                    mass += hit.mass
                    if self.player == hit:
                        player = True
                        ii = n-1
                    hit.kill()
                new_mass = planet.mass + mass
                pos = pos/n
                new_pos = (pos - planet.pos)*(mass/(new_mass)) + planet.pos
                new_mom = mom + planet.mom
                mom_mag = (new_mom.x**2 + new_mom.y**2)**0.5
                rot = new_mom.angle_to(vec(1,0))
                if self.player == planet:
                    player = True
                    ii = n-1
                planet.kill()
                plans_x.append(new_pos.x)
                plans_y.append(new_pos.y)
                plans_mom.append(mom_mag)
                plans_rot.append(rot)
                plans_mass.append(new_mass)

            hits = pg.sprite.spritecollide(planet, self.clicksprite, False)
            for hit in hits:
                self.player = planet
                hit.kill()
        for i in range(0, len(plans_x)):
            if i == ii and player == True:
                self.player = Planet(self, plans_x[i], plans_y[i], plans_mom[i]/plans_mass[i], plans_rot[i], plans_mass[i])
            else:
                Planet(self, plans_x[i], plans_y[i], plans_mom[i]/plans_mass[i], plans_rot[i], plans_mass[i])
    def events(self):
        # CATCH ALL EVENTS HERE #
        mouse = pg.mouse.get_pos()
        x = mouse[0] - self.camera.x
        y = mouse[1] - self.camera.y
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_p:
                    self.paused = not self.paused
                if event.key == pg.K_l:
                    self.draw_lines = not self.draw_lines
            if event.type == pg.MOUSEBUTTONDOWN and mouse[0] > 140:
                for butt in self.buttons:
                    if butt.active:
                        if butt.action == 1:
                            butt.action1(self, x, y, self.V, self.rot)
                        if butt.action == 2:
                            butt.action2(self, x, y, self.V, self.rot)
                        if butt.action == 9:
                            Clicksprite(self, x, y)

    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.fill(BGCOLOUR)
        pg.draw.rect(self.screen, BLACK, (0,0, 140, HEIGHT))
        self.screen.blit(self.pathscreen, (0,0))
        self.buttons.draw(self.screen)
        for sprite in self.planets:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        if self.draw_lines:
            for planet in self.planets:
                pos = (planet.pos.x + self.camera.x, planet.pos.y + self.camera.y)
                pg.draw.line(self.screen, RED, pos, (pos + planet.vel))
                pg.draw.line(self.screen, BLUE, pos, (pos + planet.acc))
                #pg.draw.line(self.pathscreen, GREY, pos, pos)
        for butt in self.buttons:
            self.screen.blit(butt.text_surface, butt.text_rect)
        #self.screen.blit(self.player.image, self.camera.apply(self.player))
        if self.paused:
            self.draw_text("P", self.title_font, RED, 60, 600)
        self.draw_text("Initial Cond: ", self.font, RED, 10, 160)
        self.draw_text("{}".format(self.V), self.font, RED, 45, 180)
        self.draw_text("{}".format(self.rot), self.font, RED, 45, 200)
        self.draw_text("{}".format(self.time_step), self.font, BLACK, 150, 40)
        self.draw_text("Time Steps: ", self.font, BLACK, 150, 20)
        self.draw_text("# of Objects: ", self.font, BLACK, 150, 70)
        self.draw_text("{}".format(len(self.planets)), self.font, BLACK, 150, 90)
        pg.display.flip()

    def show_start_screen(self):
        pass

sim = Simulation()
sim.show_start_screen()
while True:
    sim.new()
    sim.run()
    sim.show_over_screen()
