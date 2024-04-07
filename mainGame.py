# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 11:05:00 2013

@author: Leo
"""

import pygame
from sys import exit
from pygame.locals import *
from gameRole import *
import random


# 初始化游戏
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('飞机大战')

# 载入游戏音乐
bullet_sound = pygame.mixer.Sound('resources/sound/bullet.wav')
enemy1_down_sound = pygame.mixer.Sound('resources/sound/enemy1_down.wav')
game_over_sound = pygame.mixer.Sound('resources/sound/game_over.wav')
bullet_sound.set_volume(0.3)
enemy1_down_sound.set_volume(0.3)
game_over_sound.set_volume(0.3)
pygame.mixer.music.load('resources/sound/game_music.wav')
pygame.mixer.music.play(-1, 0.0)
pygame.mixer.music.set_volume(0.25)

# 载入背景图
background = pygame.image.load('resources/image/background.png').convert()
game_over = pygame.image.load('resources/image/gameover.png')

filename = 'resources/image/shoot.png'
plane_img = pygame.image.load(filename)

# 设置玩家相关参数
player_rect = []
player_rect.append(pygame.Rect(2, 99, 99, 136))        # 玩家精灵图片区域
player_rect.append(pygame.Rect(167, 360, 99, 126))
player_rect.append(pygame.Rect(167, 234, 99, 126))     # 玩家爆炸精灵图片区域
player_rect.append(pygame.Rect(333, 627, 99, 126))
player_rect.append(pygame.Rect(333, 501, 99, 126))
player_rect.append(pygame.Rect(432, 624, 99, 106))
player_pos = [200, 600]
player = Player(plane_img, player_rect, player_pos)

# 定义子弹对象使用的surface相关参数
bullet_rect = pygame.Rect(1004, 987, 9, 21)
bullet_img = plane_img.subsurface(bullet_rect)

# 定义敌机对象使用的surface相关参数  ///Corte perfecto: 539, 614, 49, 35
enemy1_rect = pygame.Rect(537, 614, 53, 35)
enemy1_img = plane_img.subsurface(enemy1_rect)
enemy1_down_imgs = []
enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(267, 347, 57, 43)))
enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(873, 697, 57, 43)))
enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(267, 296, 57, 43)))
enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(930, 697, 57, 43)))

enemies1 = pygame.sprite.Group()

# 存储被击毁的飞机，用来渲染击毁精灵动画
enemies_down = pygame.sprite.Group()

# PowerUps
powerup1_rect = pygame.Rect(268, 399, 56, 85)
powerup1_img = plane_img.subsurface(powerup1_rect)
powerups = pygame.sprite.Group()

shoot_frequency = 0
enemy_frequency = 0
powerup_frequency = 0

is_double_fire = False
double_fire_time = 0

player_down_index = 16

score = 0

clock = pygame.time.Clock()

running = True

def shoot_frequency_setter(frequency = 15):
    if not player.is_hit:
        global shoot_frequency
        if shoot_frequency % frequency == 0:
            bullet_sound.play()
            player.shoot(bullet_img)
        shoot_frequency += 1
        if shoot_frequency >= frequency:
            shoot_frequency = 0

def enemy_frequency_setter(frequency = 50):
    global enemy_frequency
    if enemy_frequency % frequency == 0:
        enemy1_pos = [random.randint(0, SCREEN_WIDTH - enemy1_rect.width), 0]
        enemy1 = Enemy(enemy1_img, enemy1_down_imgs, enemy1_pos)
        enemies1.add(enemy1)
    enemy_frequency += 1
    if enemy_frequency >= 100:
        enemy_frequency = 0

def powerup_frequency_setter(frequency = 400):
    global powerup_frequency
    if powerup_frequency % frequency == 0:
        powerup1_pos = [random.randint(0, SCREEN_WIDTH - powerup1_rect.width), 0]
        powerup1 = PowerUp(powerup1_img, powerup1_pos)
        powerups.add(powerup1)
    powerup_frequency += 1
    if powerup_frequency >= 1000:
        powerup_frequency = 0

    # if player.is_hit:
    #     if key_pressed[K_SPACE]:
    #         player.is_hit = False
    #         running = True

while running:
    # 控制游戏最大帧率为60
    clock.tick(45)
    
    # 控制发射子弹频率,并发射子弹  //Frecuencia de disparo, valor predeterminado: 15
    if is_double_fire:
        shoot_frequency_setter(6)
        double_fire_time += 1
        if double_fire_time >= 330:
            double_fire_time = 0
            is_double_fire = False
    else: 
        shoot_frequency_setter()

    # 生成敌机 //Velocidad de aparición de enemigos: 50, 33, 25
    if (score >= 9000):
        if (score >= 28000):
            if (score >= 52000):
                enemy_frequency_setter(20)
            else:
                enemy_frequency_setter(25)
        else:
            enemy_frequency_setter(33)
    else:
        enemy_frequency_setter()

    # Frecuencia de aparición de power ups, solo si no se tiene en uso uno igual. 400 predeterminado
    if not is_double_fire:
        powerup_frequency_setter(600)

    # Mover power ups, colisión y eliminar al salir de la pantalla. Activa double fire
    for pup in powerups:
        pup.move()
        if pygame.sprite.collide_circle(pup, player):
            powerups.remove(pup)
            is_double_fire = True
        if pup.rect.top > SCREEN_HEIGHT:
            powerups.remove(pup)


    # 移动子弹，若超出窗口范围则删除
    for bullet in player.bullets:
        bullet.move()
        if bullet.rect.bottom < 0:
            player.bullets.remove(bullet)

    # 移动敌机，若超出窗口范围则删除
    for enemy in enemies1:
        if (score >= 75000):
            enemy.increase_Speed()
        enemy.move()
        # 判断玩家是否被击中
        if pygame.sprite.collide_circle(enemy, player):
            enemies_down.add(enemy)
            enemies1.remove(enemy)
            player.is_hit = True
            game_over_sound.play()
            break
        if enemy.rect.top > SCREEN_HEIGHT:
            enemies1.remove(enemy)

    # 将被击中的敌机对象添加到击毁敌机Group中，用来渲染击毁动画
    enemies1_down = pygame.sprite.groupcollide(enemies1, player.bullets, 1, 1)
    for enemy_down in enemies1_down:
        enemies_down.add(enemy_down)

    # 绘制背景
    screen.fill(0)
    screen.blit(background, (0, 0))

    # 绘制玩家飞机
    if not player.is_hit:
        screen.blit(player.image[player.img_index], player.rect)
        # 更换图片索引使飞机有动画效果
        player.img_index = shoot_frequency // 8
    else:
        player.img_index = player_down_index // 8
        screen.blit(player.image[player.img_index], player.rect)
        player_down_index += 1
        if player_down_index > 47:
            running = False

    # 绘制击毁动画
    for enemy_down in enemies_down:
        if enemy_down.down_index == 0:
            enemy1_down_sound.play()
        if enemy_down.down_index > 7:
            enemies_down.remove(enemy_down)
            score += 1000
            continue
        screen.blit(enemy_down.down_imgs[enemy_down.down_index // 2], enemy_down.rect)
        enemy_down.down_index += 1

    # 绘制子弹和敌机 //Dibujar las 3 cosas
    player.bullets.draw(screen)
    enemies1.draw(screen)
    powerups.draw(screen)

    # 绘制得分
    score_font = pygame.font.Font(None, 36)
    score_text = score_font.render(str(score), True, (128, 128, 128))
    text_rect = score_text.get_rect()
    text_rect.topleft = [10, 10]
    screen.blit(score_text, text_rect)

    # 更新屏幕
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
            
    # 监听键盘事件
    key_pressed = pygame.key.get_pressed()
    # 若玩家被击中，则无效
    if not player.is_hit:
        if key_pressed[K_w] or key_pressed[K_UP]:
            player.moveUp()
        if key_pressed[K_s] or key_pressed[K_DOWN]:
            player.moveDown()
        if key_pressed[K_a] or key_pressed[K_LEFT]:
            player.moveLeft()
        if key_pressed[K_d] or key_pressed[K_RIGHT]:
            player.moveRight()


font = pygame.font.Font(None, 48)
text = font.render('Score: '+ str(score), True, (255, 0, 0))
text_rect = text.get_rect()
text_rect.centerx = screen.get_rect().centerx
text_rect.centery = screen.get_rect().centery + 24
screen.blit(game_over, (0, 0))
screen.blit(text, text_rect)

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    pygame.display.update()
