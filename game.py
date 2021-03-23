#importing the libraries
import pygame
import random 
import time
import tkinter as tk
from tkinter import messagebox
import time
import os
from pygame import mixer
pygame.font.init()
 
#set up the window
width = 900
height = 650
dim = (width, height)
win = pygame.display.set_mode(dim) 

# Title and Icon 
pygame.display.set_caption("SPACE SHOOTER GAME") 

#import the main player and enemy ship images
main_player = pygame.image.load(os.path.join("game_images","pixel_ship_yellow.png"))         #denotes the player ship(us)

#enemy ships
blue_enemy = pygame.image.load(os.path.join("game_images","pixel_ship_blue_small.png"))
red_enemy = pygame.image.load(os.path.join("game_images","pixel_ship_red_small.png"))
green_enemy = pygame.image.load(os.path.join("game_images","pixel_ship_green_small.png"))

#import the laser images
yellow_laser = pygame.image.load(os.path.join("game_images","pixel_laser_yellow.png"))
blue_laser = pygame.image.load(os.path.join("game_images","pixel_laser_blue.png"))
red_laser = pygame.image.load(os.path.join("game_images","pixel_laser_red.png"))
green_laser = pygame.image.load(os.path.join("game_images","pixel_laser_green.png"))

#import background image and scaling it to the pygame window size
background = pygame.transform.scale(pygame.image.load(os.path.join("game_images", "background-black.png")), (width, height))   #transforming the image so that the background image is fit to the screen

class Ship:
    buffer = 30            #buffer denotes 30 seconds as the waiting period before shooting another laser
    def __init__(self, x,y):
        self.x=x     
        self.y=y
        self.ship_img = None
        self.laser_img = None
        self.lasers=[]           #array for storing the elements
        self.buffer_timer=0

    def draw(self, win):
        win.blit(self.ship_img, (self.x, self.y))
        for shot in self.lasers:
            shot.draw(win)

    #returns height of the ship object        
    def height(self):
        return self.ship_img.get_height()

    #returns width of the ship object
    def width(self):
        return self.ship_img.get_width()

    def shoot(self):
            if self.buffer_timer == 0:
                laser = Laser(self.x, self.y, self.laser_img)
                self.lasers.append(laser)
                self.buffer_timer = 1

    def waiting_period(self):
        if self.buffer_timer >= self.buffer:
            self.buffer_timer = 0
        elif self.buffer_timer > 0:
            self.buffer_timer += 1

        
class Laser:
    def __init__(self, x,y,laser_img):
        self.x=x
        self.y=y
        self.laser_img=laser_img
        self.mask = pygame.mask.from_surface(self.laser_img)
        
    def draw(self, win):
        win.blit(self.laser_img, (self.x, self.y))
        
    def move(self,vel):
        self.y+=vel
        
    def collision(self, enemy):
        return collide(self, enemy)  
        
#hierarchical inheritance where Player is child class of Ship class        
class Player(Ship):
    def __init__(self,x,y,score=0, health_points=100):
        super().__init__(x,y)
        self.ship_img = main_player
        self.laser_img = yellow_laser
        self.score = score
        self.health = health_points
        self.mask = pygame.mask.from_surface(self.ship_img)
        
    def move_lasers(self, vel, enemies):
        self.waiting_period()
        for laser in self.lasers:
            laser.move(vel)
            if (laser.y + vel) <= 0:
                self.lasers.remove(laser)
            else:
                for enemy in enemies:
                    if laser.collision(enemy):
                        enemies.remove(enemy)
                        self.score+=20
                        if laser in self.lasers:
                            self.lasers.remove(laser)        

#hierarchical inheritance where Enemy is child class of Ship class
class Enemy(Ship):
    #creating a dictionary where the ship color maps to it's respective ship image and laser color
    mappings = {"red":(red_enemy, red_laser),"green":(green_enemy, green_laser)}
    def __init__(self,x,y,color):
        super().__init__(x,y)
        self.ship_img, self.laser_img = self.mappings[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        
    def move(self, vel):
        self.y+=vel

    def shoot(self):
        if self.buffer_timer==0:
            shot = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(shot)
            self.buffer_timer=1

    def move_lasers(self, vel, player):
        self.waiting_period()
        for laser in self.lasers:
            laser.move(vel)
            if laser.collision(player):
                player.health -= 10
                self.lasers.remove(laser)

    
#a tkinter window popup just in case we run out of lives or the player health becomes 0
def popup():
    root = tk.Tk()
    root.withdraw()
    messagebox.askokcancel("Game Over","You have run out of lives !!! Press Enter to quit the game")    

def collide(o1, o2):
    offset_x = o2.x - o1.x
    offset_y = o2.y - o1.y
    #checking for pixel-perfect collision by using the offset
    return o1.mask.overlap(o2.mask, (offset_x, offset_y)) != None  


def main():
    enemies=[]
    no_of_enemies=5
    run=True
    lives=5
    level=0
    speed=5    #player speed
    enemy_vel=1      #speed at which enemy ships come down
    enemy_laser_speed=5   #speed of enemy laser
    x=15
    lost=False
    player=Player(300,600)
    clock = pygame.time.Clock()
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 80)

    def replot_contents():
        win.blit(background,(0,0))
        lives_label = main_font.render(f"Lives Left: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        health_label = main_font.render(f"Health: {player.health}", 1, (255,255,255))
        score_label = main_font.render(f"Score: {player.score}", 1, (255,255,255))
        game_over = lost_font.render("Game   Over", 1, (255,255,255))
        win.blit(lives_label, (10, 10))
        win.blit(level_label, (width - level_label.get_width() - 50, 10))
        win.blit(health_label, (10, 10 + level_label.get_height()))
        win.blit(score_label, (width - level_label.get_width() - 50, 10 + level_label.get_height()))     #
        for enemy in enemies:
            enemy.draw(win)
        player.draw(win)
        if lost:
            win.blit(game_over, (450 - game_over.get_width()/2, 325))
            pygame.display.update()
            pygame.time.delay(500)
            popup()
            quit()       #quit the game once game is over
        pygame.display.update()
    
    while run:
        clock.tick(60)                           #clock rate is set as 60 so that the game moves at the same pace regardless of the computer this code is run on
        replot_contents() 
        if lives==0 or player.health==0:
            lost=True
        if not len(enemies):
            level+=1
            no_of_enemies+=5
            x-=0.5
            for i in range(no_of_enemies):
                #instantiating the enemy class by creating multiple enemies and storing them in the array. 
                enemy = Enemy(random.randrange(50, width-50), random.randrange(-1000,-200), random.choice(["red","green"]))
                enemies.append(enemy)
        for event in pygame.event.get():
           if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x > 0: #leftward movement 
            player.x -= speed
        if keys[pygame.K_RIGHT] and player.x + player.width() < width: # rightward movement
            player.x += speed
        if keys[pygame.K_UP] and player.y > 0: # upward movement 
            player.y -= speed
        if keys[pygame.K_DOWN] and player.y + player.height()< height: # downward movement
            player.y += speed

        if keys[pygame.K_SPACE]:
            player.shoot()
            
        
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(enemy_laser_speed, player)
            
            if random.randrange(0, x*60)==1:
                enemy.shoot()
            if (enemy.y + enemy.height() > height) :       #if the enemy goes off screen or if the player collides with the enemy, lives will be                  
                lives-=1                                   #decremented by 1
                enemies.remove(enemy)        
            if collide(enemy, player):
                player.health-=10                              #if enemy and player collide, the health is decremented by 10
                player.score+=10
                enemies.remove(enemy)
            
        player.move_lasers(-speed, enemies)  
main()    

