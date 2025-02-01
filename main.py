# импортирование и подключение необходимых модулей
import pygame
import time
import random
import os

pygame.init()
pygame.font.init()
pygame.mixer.init()

#general objects
#основные объекты
screen = pygame.display.set_mode((550, 550))
clock = pygame.time.Clock()
running = True

menu = True
level = False
levels_list = False
end_game = False

#class window
#Классы окон приложения

#окно окончания игры
class EndGameWindow:
    def __init__(self):
        self.end_game_title = Text(pygame.font.SysFont('Arial', 48), 'Game Over', (255, 0, 0), 150, 0)
        self.restart = Text(pygame.font.SysFont('Arial', 48), 'Menu', (255, 0, 0), 200, 100)
    
    # переход в меню
    def go_to_menu(self):
        global menu, end_game
        menu = True
        end_game = False
    
    # обновление
    def update(self):
        screen.fill((0, 0, 0))
        self.end_game_title.update()
        self.restart.update()


#окно списка уровней
class LevelListWindow:
    def __init__(self):
        self.list_menu_title = Text(pygame.font.SysFont('Arial', 24), 'List Level', (255, 255, 255), 200, 0)
        self.list_number_levels_title = []
        self.list_path_map = []
    
    # загрузка карты
    def load_map(self):
        self.list_path_map = os.listdir('data\\maps')
        self.list_number_levels_title = [Text(pygame.font.SysFont('Arial', 24), f'{i  + 1}', (255, 255, 255), i * 50 % 550, (i * 50 // 550) * 50 + 50) for i in range(len(self.list_path_map))]

    # вернуть список
    def get_list_number_levels_title(self):
        return self.list_number_levels_title

    # вернуть список путей карт
    def get_list_path_map(self):
        return self.list_path_map

    # перейти к окну
    def go_to_level(self, path):
        global levels_list, level
        levels_list = False
        level = True
        level_game_window.set_map(path)
        level_game_window.set_gun()
    
    # загрузить выбранную карту
    def load_choosed_map(self, mouse_pos):
        levels_coord = [sprite.get_coord() for sprite in self.list_number_levels_title]
        ind = 0
        flag = False
        for i in range(len(levels_coord)):
            if levels_coord[i][0] <= mouse_pos[0] <= levels_coord[i][0] + 50 and levels_coord[i][1] <= mouse_pos[1] <= levels_coord[i][1] + 50:
                ind = i
                flag = True
        if flag:
            level_list_window.go_to_level('data\\maps\\' + self.list_path_map[ind])

    # обновление
    def update(self):
        screen.fill((0, 0, 0))
        self.list_menu_title.update()
        for sprite in self.list_number_levels_title:
            sprite.update()
        self.load_map()


#окно меню
class MenuWindow:
    def __init__(self):
        self.menu_title = Text(pygame.font.SysFont('Arial', 24), 'MENU:', (255, 255, 255), 150, 150)
        self.play_title = Text(pygame.font.SysFont('Arial', 24), 'PLAY', (255, 255, 255), 150, 200)
    
    # переход к списку уровней
    def go_to_level_list(self):
        global menu, levels_list
        menu = False
        levels_list = True
    
    # обновление
    def update(self):
        screen.fill((0, 0, 0))
        self.menu_title.update()
        self.play_title.update()


#окно самого уровня
class LevelWindow:
    def __init__(self):
        self.flashlight = Flashlight(False, 100.0, (0.05, 0.01), 'data\\sound\\flashlight.mp3', 'data\\sound\\add_battery.mp3')
        self.walls_group = GroupWalls()
        self.batteries_group = GroupBatteries()
        self.floors_group = GroupFloors()
        self.enemies_group = GroupEnemies()
        self.bullets_group = GroupBullets()
        self.ammouns_group = GroupAmmouns()
        self.player = Player('data\\picture\\player_up.png', 250, 250, 'data\\sound\\step_player.mp3', 'data\\sound\\kill_sound.mp3')
        self.gun = Gun('data\\picture\\gun.png', -50, -50,'data\\sound\\take_gun.mp3','data\\sound\\fire_gun.mp3', 2)
        self.count_kill_title  = Text(pygame.font.SysFont('Arial', 24), 'Count kill: 0', (255, 0, 0), 0, 50)
        self.count_kill = 0
        self.gun_find = False
    
    # при смерти игрока
    def death_player(self):
        spritecollide = pygame.sprite.spritecollide(self.player, self.enemies_group, False)
        if len(spritecollide) > 0:
            self.player.play_sound_kill()
            self.go_to_end_game()
    
    # при находке патронов
    def find_ammoun(self):
        spritecollide = pygame.sprite.spritecollide(self.player, self.ammouns_group, True)
        if len(spritecollide) > 0:
            for sprite in spritecollide:
                sprite.play_sound_ammoun()
                self.gun.add_count_bullet(sprite.get_count_bullet())
                self.gun.get_count_bullet_title().change_text(f'Bullets: {self.gun.get_count_bullet()}')
    
    # при находке батарейки
    def find_battery(self):
        spritecollide = pygame.sprite.spritecollide(self.player, self.batteries_group, True)
        self.flashlight.add_energy(spritecollide)
    
    # найдено ли оружие
    def get_find_gun(self):
        return self.gun_find
    
    # при находке оружия
    def find_gun(self):
        if self.gun.get_coord() == self.player.get_coord():
            self.gun.take_gun()
            self.gun_find = True
    
    # установить положение оружия в начале уровня
    def set_gun(self):
        choosed_coord = random.choice(self.floors_group.get_list_coord_floor())
        self.gun.set_coord(choosed_coord[0], choosed_coord[1])

    # при огне из оружия
    def fire_gun(self):
        if time.time() - self.gun.get_last_time_fire() >= self.gun.get_time_recharge() and self.gun.get_count_bullet() > 0:
            self.bullets_group.add_bullet(level_game_window.player.get_side())
            self.gun.play_fire_gun()
            self.gun.set_last_time_fire(time.time())
            self.gun.add_count_bullet(-1)
            self.gun.get_count_bullet_title().change_text(f'Bullets: {self.gun.get_count_bullet()}')
    
    # при попадании пули куда-либо
    def shot_gun(self):
        spritecollide1 = pygame.sprite.groupcollide(self.enemies_group, self.bullets_group, False, True)
        spritecollide2 = pygame.sprite.groupcollide(self.walls_group, self.bullets_group, False, True)
        if len(spritecollide1) > 0:
            for sprite in spritecollide1:
                sprite.add_health(-1)
                if sprite.get_health() < 1:
                    sprite.kill()
                    self.count_kill += 1
            self.count_kill_title.change_text(f'Count kill: {self.count_kill}')
    
    # при включении или выключении
    def light_or_dark(self):
        if self.flashlight.get_on_off() and self.flashlight.get_energy() > 0:
            self.walls_group.set_light()
            self.batteries_group.set_light()
            self.enemies_group.set_light()
            self.floors_group.set_light()
            self.gun.set_light()
            self.bullets_group.set_light()
            self.ammouns_group.set_light()
        else:
            self.walls_group.set_dark()
            self.batteries_group.set_dark()
            self.enemies_group.set_dark()
            self.floors_group.set_dark()
            self.gun.set_dark()
            self.bullets_group.set_dark()
            self.ammouns_group.set_dark()
    
    # установить карту
    def set_map(self, path):
        with open(path, 'r') as file:
            data = file.read().split()
        for i in range(len(data)):
            line = [el for el in data[i]]
            for j in range(len(line)):
                if line[j] == '#':
                    self.walls_group.add_wall(Wall('data\\picture\\wall.png', i * 50, j * 50))
                if line[j] == '.':
                    self.floors_group.add_floor(Floor('data\\picture\\floor.png', i * 50, j * 50))
    
    # перейти в конец игры
    def go_to_end_game(self):
        global level, end_game
        self.enemies_group.empty()
        self.enemies_group.get_list_enemy().clear()
        self.batteries_group.empty()
        self.batteries_group.get_list_battery().clear()
        self.walls_group.empty()
        self.walls_group.get_list_walls().clear()
        self.floors_group.empty()
        self.floors_group.get_list_coord_floor().clear()
        self.ammouns_group.empty()
        self.flashlight.set_energy(1000)
        self.enemies_group.set_last_time_spawn(time.time())
        self.batteries_group.set_last_time_spawn(time.time())
        self.ammouns_group.set_last_time_spawn(time.time())
        self.flashlight.set_on_off(False)
        self.count_kill_title.change_text(f'Count kill: 0')
        self.gun_find = False
        self.gun.set_on_floor(True)
        self.gun.set_count_bullet(5)
        self.gun.get_count_bullet_title().change_text(f'Bullets: {self.gun.get_count_bullet()}')

        level = False
        end_game = True
    
    # обновление
    def update(self):
        self.flashlight.lower_energy()
        self.batteries_group.set_random_battery()
        self.enemies_group.set_random_enemy()
        self.ammouns_group.set_new_random_ammouns()
        self.enemies_group.enemies_go_to_player()
        self.enemies_group.change_animations()
        self.bullets_group.move()

        self.light_or_dark()
        self.find_battery()
        self.death_player()
        self.find_gun()
        self.shot_gun()
        self.find_ammoun()

        screen.fill((0, 0, 0))
        self.floors_group.update()
        self.batteries_group.update()
        self.enemies_group.update()
        self.walls_group.update()
        self.bullets_group.update()
        self.gun.update()
        self.ammouns_group.update()
        self.player.update()
        self.flashlight.get_energy_title().update()
        self.gun.get_count_bullet_title().update()
        self.count_kill_title.update()


#class obj
#классы объектов
#класс группы патронов
class GroupAmmouns(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.last_time_spawn = time.time()
        self.time_respawn_ammouns = random.randint(5, 10)
    
    def set_new_random_ammouns(self):
        if time.time() - self.last_time_spawn >= self.time_respawn_ammouns:
            choosed_coord = random.choice(level_game_window.floors_group.get_list_coord_floor())
            self.add(Ammoun('data\\picture\\ammoun.png', choosed_coord[0], choosed_coord[1], random.randint(1, 3), 'data\\sound\\take_ammouns.mp3'))
            self.last_time_spawn = time.time()
            self.time_respawn_ammouns = random.randint(25, 40)
    
    def set_light(self):
        for sprite in self.sprites():
            sprite.set_light()
    
    def set_dark(self):
        for sprite in self.sprites():
            sprite.set_dark()
    
    def set_last_time_spawn(self, time):
        self.last_time_spawn= time
    
    def move_up(self):
        for sprite in self.sprites():
            sprite.move_up()

    def move_down(self):
        for sprite in self.sprites():
            sprite.move_down()

    def move_left(self):
        for sprite in self.sprites():
            sprite.move_left()

    def move_right(self):
        for sprite in self.sprites():
            sprite.move_right()


#класс патроны
class Ammoun(pygame.sprite.Sprite):
    def __init__(self, image, x, y, ammount_bullet, sound_ammoun):
        super().__init__()
        self.surface = pygame.transform.scale(pygame.image.load(image), (50, 50))
        self.surface.set_colorkey((255, 255, 255))
        self.light = self.surface.copy()
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.ammount_bullet = ammount_bullet
        self.sound_ammoun = pygame.mixer.Sound(sound_ammoun)
    
    def get_count_bullet(self):
        return self.ammount_bullet

    def play_sound_ammoun(self):
        self.sound_ammoun.play()

    def set_light(self):
        self.surface = self.light.copy()
    
    def set_dark(self):
        self.surface.fill((0, 0, 0))

    def move_up(self):
        self.rect.y += 50
    
    def move_down(self):
        self.rect.y -= 50
    
    def move_left(self):
        self.rect.x += 50
    
    def move_right(self):
        self.rect.x -= 50
    
    def update(self):
        screen.blit(self.surface, self.rect)


#класс группы пуль
class GroupBullets(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
    
    def add_bullet(self, side):
        if side == 'U':
            self.add(Bullet('data\\picture\\bullet_up.png', level_game_window.player.get_coord()[0] + 15, level_game_window.player.get_coord()[1], side, 10))
        if side == 'D':
            self.add(Bullet('data\\picture\\bullet_down.png', level_game_window.player.get_coord()[0] + 15, level_game_window.player.get_coord()[1], side, 10))
        if side == 'L':
            self.add(Bullet('data\\picture\\bullet_left.png', level_game_window.player.get_coord()[0] + 15, level_game_window.player.get_coord()[1], side, 10))
        if side == 'R':
            self.add(Bullet('data\\picture\\bullet_right.png', level_game_window.player.get_coord()[0] + 15, level_game_window.player.get_coord()[1], side, 10))
    
    def set_dark(self):
        for sprite in self.sprites():
            sprite.set_dark()

    def set_light(self):
        for sprite in self.sprites():
            sprite.set_light()

    def move(self):
        for sprite in self.sprites():
            sprite.move()
    
    def move_up(self):
        for sprite in self.sprites():
            sprite.move_up()

    def move_down(self):
        for sprite in self.sprites():
            sprite.move_down()

    def move_left(self):
        for sprite in self.sprites():
            sprite.move_left()

    def move_right(self):
        for sprite in self.sprites():
            sprite.move_right()


#класс пуль
class Bullet(pygame.sprite.Sprite):
    def __init__(self, image, x, y, side, speed):
        super().__init__()
        self.surface = pygame.transform.scale(pygame.image.load(image), (10, 10))
        self.surface.set_colorkey((255, 255, 255))
        self.light = self.surface.copy()
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.side = side
        self.speed = speed
    
    def move(self):
        if self.side == 'U':
            self.rect.y -= self.speed
        elif self.side == 'D':
            self.rect.y += self.speed
        elif self.side == 'L':
            self.rect.x -= self.speed
        elif self.side == 'R':
            self.rect.x += self.speed
    
    def move_up(self):
        self.rect.y += 50
    
    def move_down(self):
        self.rect.y -= 50
    
    def move_left(self):
        self.rect.x += 50
    
    def move_right(self):
        self.rect.x -= 50

    def set_dark(self):
        self.surface.fill((0, 0, 0))
    
    def set_light(self):
        self.surface = self.light.copy()
    
    def update(self):
        screen.blit(self.surface, self.rect)


#класс оружия
class Gun(pygame.sprite.Sprite):
    def __init__(self, image,  x, y,path_sound_take_gun, path_fire_gun, time_recharge):
        super().__init__()
        self.surface = pygame.transform.scale(pygame.image.load(image), (50, 50))
        self.surface.set_colorkey((255, 255, 255))
        self.light = self.surface.copy()
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.on_floor = True
        self.sound_take_gun = pygame.mixer.Sound(path_sound_take_gun)
        self.sound_fire_gun = pygame.mixer.Sound(path_fire_gun)
        self.last_time_fire = time.time()
        self.time_recharge = time_recharge
        self.count_bullet = 5
        self.count_bullet_title = Text(pygame.font.SysFont('Arial', 24), 'Bullets: 0', (255, 0, 0), 0, 100)
        self.count_bullet_title.change_text(f'Bullets: {self.count_bullet}')
    
    def set_coord(self, x, y):
        self.rect.x = x
        self.rect.y = y
    
    def get_coord(self):
        return (self.rect.x, self.rect.y)

    def get_count_bullet(self):
        return self.count_bullet
    
    def set_count_bullet(self, count):
        self.count_bullet = count
    
    def add_count_bullet(self, count):
        self.count_bullet += count
    
    def get_time_recharge(self):
        return self.time_recharge

    def get_last_time_fire(self):
        return self.last_time_fire

    def set_last_time_fire(self, time):
        self.last_time_fire = time
    
    def get_count_bullet_title(self):
        return self.count_bullet_title
    
    def move_up(self):
        self.rect.y += 50
    
    def move_down(self):
        self.rect.y -= 50
    
    def move_left(self):
        self.rect.x += 50
    
    def move_right(self):
        self.rect.x -= 50
    
    def set_light(self):
        self.surface = self.light.copy()
    
    def set_dark(self):
        self.surface.fill((0, 0, 0))
    
    def take_gun(self):
        self.sound_take_gun.play()
        self.rect.x = -1000
        self.rect.y = -1000
        self.on_floor = False
    
    def play_fire_gun(self):
        self.sound_fire_gun.play()
    
    def set_on_floor(self, on_floor):
        self.on_floor = on_floor
    
    def update(self):
        if self.on_floor:
            screen.blit(self.surface, self.rect)
            self.count_bullet_title.update()


#класс группы призраков
class GroupEnemies(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.time_respawn_enemy = random.randint(5, 35)
        self.last_time_spawn = time.time()
        self.list_enemy = []
    
    def pos_in_list(self, coord):
        return coord in self.list_enemy

    def add_enemy(self, enemy):
        self.add(enemy)
        self.list_enemy.append(enemy.get_coord())
    
    def get_list_enemy(self):
        return self.list_enemy
    
    def move_up(self):
        self.list_enemy.clear()
        for sprite in self.sprites():
            sprite.move(0, 50)
            self.list_enemy.append(sprite.get_coord())

    def move_down(self):
        self.list_enemy.clear()
        for sprite in self.sprites():
            sprite.move(0, -50)
            self.list_enemy.append(sprite.get_coord())

    def move_left(self):
        self.list_enemy.clear()
        for sprite in self.sprites():
            sprite.move(50, 0)
            self.list_enemy.append(sprite.get_coord())

    def move_right(self):
        self.list_enemy.clear()
        for sprite in self.sprites():
            sprite.move(-50, 0)
            self.list_enemy.append(sprite.get_coord())

    def set_random_enemy(self):
        if time.time() - self.last_time_spawn >= self.time_respawn_enemy:
            choosed_coord = random.choice(level_game_window.floors_group.get_list_coord_floor())
            while self.pos_in_list(choosed_coord) or level_game_window.batteries_group.pos_in_list(choosed_coord):
                choosed_coord = random.choice(level_game_window.floors_group.get_list_coord_floor())
            self.add(Enemy(choosed_coord[0], choosed_coord[1], random.randint(1, 3), 0.1, 'data\\sound\\step.mp3', random.randint(1, 3), 'data\\picture\\ghost1.png', 'data\\picture\\ghost2.png', 'data\\picture\\ghost3.png'))
            self.last_time_spawn = time.time()
            self.time_respawn_enemy = random.randint(5, 35)
    
    def change_color_enemies(self, color):
        for sprite in self.sprites():
            sprite.set_color(color)
    
    def enemies_go_to_player(self):
        for sprite in self.sprites():
            sprite.go_to_player()
    
    def set_last_time_spawn(self, time):
        self.last_time_spawn = time
    
    def set_light(self):
        for sprite in self.sprites():
            sprite.set_light()
    
    def set_dark(self):
        for sprite in self.sprites():
            sprite.set_dark()
    
    def change_animations(self):
        for sprite in self.sprites():
            sprite.change_animation()


#класс призрака
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, time_anim, sound_path, health, *args):
        super().__init__()
        self.health = health
        self.surface = pygame.Surface((50, 50))
        self.surface.set_colorkey((255, 255, 255))
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed
        self.last_move = time.time()
        self.sound_step = pygame.mixer.Sound(sound_path)
        self.list_animation = [pygame.transform.scale(pygame.image.load(el), (50, 50)) for el in args]
        self.last_time_anim = time.time()
        self.time_anim = time_anim
        for el in self.list_animation:
            el.set_colorkey((255, 255, 255))
        self.current_anim = 0
    
    def get_coord(self):
        return (self.rect.x, self.rect.y)

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y
    
    def set_color(self, color):
        self.surface.fill(color)
    
    def set_light(self):
        self.surface = self.list_animation[self.current_anim].copy()
    
    def set_dark(self):
        self.surface.fill((0, 0, 0))
    
    def add_health(self, health):
        self.health += health
    
    def get_health(self):
        return self.health
    
    def change_animation(self):
        if time.time() - self.last_time_anim >= self.time_anim:
            self.surface = self.list_animation[self.current_anim].copy()
            self.current_anim = (self.current_anim + 1) % len(self.list_animation)
            self.last_time_anim = time.time()
    
    def play_sound_step(self):
        if not (0 <= self.rect.x <= 550 and 0 <= self.rect.y <= 550):
            self.sound_step.set_volume(0.0)
        elif not (50 <= self.rect.x <= 450 and 50 <= self.rect.y <= 450):
            self.sound_step.set_volume(0.2)
        elif not (100 <= self.rect.x <= 400 and 100 <= self.rect.y <= 400):
            self.sound_step.set_volume(0.5)
        elif not (200 <= self.rect.x <= 300 and 200 <= self.rect.y <= 300):
            self.sound_step.set_volume(0.8)
        else:
            self.sound_step.set_volume(1.0)
        
        self.sound_step.play()


    def go_to_player(self):
        if time.time() - self.last_move >= self.speed:
            player_coord = level_game_window.player.get_coord()
            move_x = 0
            move_y = 0

            if player_coord[0] > self.rect.x:
                move_x = 50
            elif player_coord[0] < self.rect.x:
                move_x = -50
            
            if player_coord[1] > self.rect.y:
                move_y = 50
            elif player_coord[1] < self.rect.y:
                move_y = -50

            self.move(move_x, move_y)

            self.play_sound_step()
            self.last_move = time.time()

    def update(self):
        screen.blit(self.surface, self.rect)


#класс группы полов
class GroupFloors(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.list_floor = []

    def pos_in_list(self, coord):
        return coord in self.list_floor

    def get_list_coord_floor(self):
        return self.list_floor

    def move_up(self):
        self.list_floor.clear()
        for sprite in self.sprites():
            sprite.move(0, 50)
            self.list_floor.append(sprite.get_coord())

    def move_down(self):
        self.list_floor.clear()
        for sprite in self.sprites():
            sprite.move(0, -50)
            self.list_floor.append(sprite.get_coord())

    def move_left(self):
        self.list_floor.clear()
        for sprite in self.sprites():
            sprite.move(50, 0)
            self.list_floor.append(sprite.get_coord())

    def move_right(self):
        self.list_floor.clear()
        for sprite in self.sprites():
            sprite.move(-50, 0)
            self.list_floor.append(sprite.get_coord())
    
    def add_floor(self, floor):
        self.add(floor)
        self.list_floor.append(floor.get_coord())
    
    def set_dark(self):
        for sprite in self.sprites():
            sprite.set_dark()
    
    def set_light(self):
        for sprite in self.sprites():
            sprite.set_light()

#класс полов
class Floor(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.surface = pygame.transform.scale(pygame.image.load(image), (50, 50))
        self.light = self.surface.copy()
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def get_coord(self):
        return (self.rect.x, self.rect.y)

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y
    
    def set_dark(self):
        self.surface.fill((0, 0, 0))
    
    def set_light(self):
        self.surface = self.light.copy()
    
    def update(self):
        screen.blit(self.surface, self.rect)


#класс группы батареек
class GroupBatteries(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.time_respawn_battery = random.randint(2, 15)
        self.last_time_spawn = time.time()
        self.list_battery = []

    def pos_in_list(self, coord):
        return coord in self.list_battery

    def get_list_battery(self):
        return self.list_battery

    def set_random_battery(self):
        if time.time() - self.last_time_spawn >= self.time_respawn_battery:
            choosed_coord = random.choice(level_game_window.floors_group.get_list_coord_floor())
            while self.pos_in_list(choosed_coord):
                choosed_coord = random.choice(level_game_window.floors_group.get_list_coord_floor())
            self.add(Battery('data\\picture\\battery.png', choosed_coord[0], choosed_coord[1]))
            self.last_time_spawn = time.time()
            self.time_respawn_battery = random.randint(5, 15)
    
    def change_color_batteries(self, color):
        for sprite in self.sprites():
            sprite.set_color(color)

    def move_up(self):
        self.list_battery.clear()
        for sprite in self.sprites():
            sprite.move(0, 50)
            self.list_battery.append(sprite.get_coord())

    def move_down(self):
        self.list_battery.clear()
        for sprite in self.sprites():
            sprite.move(0, -50)
            self.list_battery.append(sprite.get_coord())

    def move_left(self):
        self.list_battery.clear()
        for sprite in self.sprites():
            sprite.move(50, 0)
            self.list_battery.append(sprite.get_coord())

    def move_right(self):
        self.list_battery.clear()
        for sprite in self.sprites():
            sprite.move(-50, 0)
            self.list_battery.append(sprite.get_coord())
    
    def add_battery(self, battery):
        self.add(battery)
        self.list_battery.append(battery.get_coord())
    
    def set_last_time_spawn(self, time):
        self.last_time_spawn = time
    
    def set_dark(self):
        for sprite in self.sprites():
            sprite.set_dark()
    
    def set_light(self):
        for sprite in self.sprites():
            sprite.set_light()


#класс батареек
class Battery(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.surface = pygame.transform.scale(pygame.image.load(image),(50, 50))
        self.surface.set_colorkey((255, 255, 255))
        self.light = self.surface.copy()
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.energy = 10
    
    def get_coord(self):
        return (self.rect.x, self.rect.y)

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y
    
    def set_color(self, color):
        self.surface.fill(color)
    
    def set_light(self):
        self.surface = self.light.copy()
    
    def set_dark(self):
        self.surface.fill((0, 0, 0))
    
    def get_energy_battery(self):
        return self.energy
    
    def update(self):
        screen.blit(self.surface, self.rect)


#класс фонариков
class Flashlight:
    def __init__(self, on_off, energy_max, energy_speed, sound_path_flashlight, sound_path_battery):
        self.on_off = on_off
        self.energy_max = energy_max
        self.energy = self.energy_max
        self.energy_speed = energy_speed[0]
        self.energy_time = energy_speed[1]
        self.last_flash_on = time.time()
        self.energy_title = Text(pygame.font.SysFont('Arial', 28), f'{int(self.energy)}%', (255, 0, 0), 0, 0)
        self.sound_flashlight = pygame.mixer.Sound(sound_path_flashlight)
        self.sound_battery = pygame.mixer.Sound(sound_path_battery)

    def turn_on_off(self):
        self.on_off = not self.on_off
        self.sound_flashlight.play()
        if self.on_off:
            self.last_flash_on = time.time()
    
    def lower_energy(self):
        if time.time() - self.last_flash_on >= self.energy_time and self.on_off and self.energy > 0:
            self.energy -= self.energy_speed
            self.last_flash_on = time.time()
            self.energy_title.change_text(f'{int(self.energy)}%')

    def add_energy(self, sprites):
        energy = sum([sprite.get_energy_battery() for sprite in sprites])
        if self.energy + float(energy) > self.energy_max:
            self.energy = self.energy_max
        else:
            self.energy += float(energy)
        if energy > 0:
            self.sound_battery.play()
        self.energy_title.change_text(f'{int(self.energy)}%')
    
    def set_energy(self, energy):
        self.energy = energy
    
    def set_on_off(self, on_off):
        self.on_off = on_off

    def get_energy_title(self):
        return self.energy_title

    def get_on_off(self):
        return self.on_off

    def get_energy(self):
        return self.energy


#класс группы стен
class GroupWalls(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.list_wall = []
    
    def move_up(self):
        self.list_wall.clear()
        for sprite in self.sprites():
            sprite.move(0, 50)
            self.list_wall.append(sprite.get_coord())
    
    def move_down(self):
        self.list_wall.clear()
        for sprite in self.sprites():
            sprite.move(0, -50)
            self.list_wall.append(sprite.get_coord())
    
    def move_left(self):
        self.list_wall.clear()
        for sprite in self.sprites():
            sprite.move(50, 0)
            self.list_wall.append(sprite.get_coord())
    
    def move_right(self):
        self.list_wall.clear()
        for sprite in self.sprites():
            sprite.move(-50, 0)
            self.list_wall.append(sprite.get_coord())

    def change_color_walls(self, color):
        for sprite in self.sprites():
            sprite.set_color(color)
    
    def set_light(self):
        for sprite in self.sprites():
            sprite.set_light()
    
    def set_dark(self):
        for sprite in self.sprites():
            sprite.set_dark()
    
    def pos_in_list(self, coord):
        return coord in self.list_wall

    def add_wall(self, wall):
        self.add(wall)
        self.list_wall.append(wall.get_coord())
    
    def get_list_walls(self):
        return self.list_wall


#класс текста
class Text:
    def __init__(self, font, text, color, x, y):
        self.color = color
        self.font = font
        self.surface = self.font.render(text, True, self.color)
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def change_text(self, new_text):
        self.surface = self.font.render(new_text, True, self.color)
    
    def get_coord(self):
        return (self.rect.x, self.rect.y)

    def update(self):
        screen.blit(self.surface, self.rect)


#класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, image, x, y, sound_path_step, sound_path_kill):
        super().__init__()
        self.surface = pygame.transform.scale(pygame.image.load(image), (50, 50))
        self.surface_up = pygame.transform.scale(pygame.image.load('data\\picture\\player_up.png'), (50, 50))
        self.surface_down = pygame.transform.scale(pygame.image.load('data\\picture\\player_down.png'), (50, 50))
        self.surface_left = pygame.transform.scale(pygame.image.load('data\\picture\\player_left.png'), (50, 50))
        self.surface_right = pygame.transform.scale(pygame.image.load('data\\picture\\player_right.png'), (50, 50))
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.sound_step = pygame.mixer.Sound(sound_path_step)
        self.sound_death = pygame.mixer.Sound(sound_path_kill)
        self.sound_step.set_volume(0.1)
        self.side = 'U'

    def get_coord(self):
        return (self.rect.x, self.rect.y)

    def play_sound_step(self):
        self.sound_step.play()
    
    def play_sound_kill(self):
        self.sound_death.play()
    
    def set_up_side(self):
        self.surface = self.surface_up.copy()
        self.side = 'U'
    
    def set_down_side(self):
        self.surface = self.surface_down.copy()
        self.side = 'D'
    
    def set_left_side(self):
        self.surface = self.surface_left.copy()
        self.side = 'L'
    
    def set_right_side(self):
        self.surface = self.surface_right.copy()
        self.side = 'R'
    
    def get_side(self):
        return self.side
    
    def update(self):
        screen.blit(self.surface, self.rect)


#класс стены
class Wall(pygame.sprite.Sprite):
    def __init__(self, image,  x, y):
        super().__init__()
        self.surface = pygame.transform.scale(pygame.image.load(image), (50, 50))
        self.light = self.surface.copy()
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y
    
    def set_color(self, color):
        self.surface.fill(color)
    
    def get_coord(self):
        return (self.rect.x, self.rect.y)

    def set_light(self):
        self.surface = self.light.copy()
    
    def set_dark(self):
        self.surface.fill((0, 0, 0))
    
    def update(self):
        screen.blit(self.surface, self.rect)


#window obj
#объекты окон
level_game_window = LevelWindow()
menu_window = MenuWindow()
level_list_window = LevelListWindow()
end_game_window = EndGameWindow()


#цикл игры
while running:
    #циклы действий
    for event in pygame.event.get():
        #для закрытия
        if event.type == pygame.QUIT:
            running = False
        #при нажатии клавиш
        elif event.type == pygame.KEYDOWN:
            #при окне уровень
            if level:
                # для передвижения вперёд
                player_coord = level_game_window.player.get_coord()
                if event.key == pygame.K_w and not level_game_window.walls_group.pos_in_list((player_coord[0], player_coord[1] - 50)):
                    level_game_window.walls_group.move_up()
                    level_game_window.batteries_group.move_up()
                    level_game_window.floors_group.move_up()
                    level_game_window.enemies_group.move_up()
                    level_game_window.gun.move_up()
                    level_game_window.bullets_group.move_up()
                    level_game_window.ammouns_group.move_up()
                    level_game_window.player.play_sound_step()
                    level_game_window.player.set_up_side()
                # для передвижения назад
                if event.key == pygame.K_s and not level_game_window.walls_group.pos_in_list((player_coord[0], player_coord[1] + 50)):
                    level_game_window.walls_group.move_down()
                    level_game_window.batteries_group.move_down()
                    level_game_window.floors_group.move_down()
                    level_game_window.enemies_group.move_down()
                    level_game_window.gun.move_down()
                    level_game_window.bullets_group.move_down()
                    level_game_window.ammouns_group.move_down()
                    level_game_window.player.play_sound_step()
                    level_game_window.player.set_down_side()
                # для передвижения влево
                if event.key == pygame.K_a and not level_game_window.walls_group.pos_in_list((player_coord[0] - 50, player_coord[1])):
                    level_game_window.walls_group.move_left()
                    level_game_window.batteries_group.move_left()
                    level_game_window.floors_group.move_left()
                    level_game_window.enemies_group.move_left()
                    level_game_window.gun.move_left()
                    level_game_window.bullets_group.move_left()
                    level_game_window.ammouns_group.move_left()
                    level_game_window.player.play_sound_step()
                    level_game_window.player.set_left_side()
                # для передвижения вправо
                if event.key == pygame.K_d and not level_game_window.walls_group.pos_in_list((player_coord[0] + 50, player_coord[1])):
                    level_game_window.walls_group.move_right()
                    level_game_window.batteries_group.move_right()
                    level_game_window.floors_group.move_right()
                    level_game_window.enemies_group.move_right()
                    level_game_window.gun.move_right()
                    level_game_window.bullets_group.move_right()
                    level_game_window.ammouns_group.move_right()
                    level_game_window.player.play_sound_step()
                    level_game_window.player.set_right_side()
                # для включения/выключения фонарика
                if event.key == pygame.K_f:
                    level_game_window.flashlight.turn_on_off()
                # для стрельбы
                if event.key == pygame.K_SPACE and level_game_window.get_find_gun():
                    level_game_window.fire_gun()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # при нажатии мыши
            mouse_pressed = pygame.mouse.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            # при окне уровень
            if menu:
                # переход к окну списко уровней
                if mouse_pressed[0] and 150 <= mouse_pos[0] <= 200 and 200 <= mouse_pos[1] <= 230:
                    menu_window.go_to_level_list()
            if levels_list:
                # при переходе к уровню
                level_list_window.load_choosed_map(mouse_pos)
            if end_game:
                # при переходе в меню при проигрыше
                if mouse_pressed[0] and 200 <= mouse_pos[0] <= 300 and 100 <= mouse_pos[1] <= 150:
                    end_game_window.go_to_menu()

    if menu:
        menu_window.update()
    if level:
        level_game_window.update()
    if levels_list:
        level_list_window.update()
    if end_game:
        end_game_window.update()

    pygame.display.flip()
    clock.tick(60)

pygame.mixer.quit()
pygame.font.quit()
pygame.quit()