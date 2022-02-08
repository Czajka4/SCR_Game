#
#   main file
#
# ________ Imaports ________
import os
import csv
import random
import pygame
import pygame.locals
from datetime import datetime
from models import Player, Alien, Bullet, StatusBar, Text, Powerup

# ___ BUGI
# TODO : Interfejs gry, pytanie o login
# TODO : Zminne hudu w jednym miejscu
# TODO : Różne dźwieki broni
# TODO: Pociski nie znikaja po zabiciu potwora

# ________ Variables ________
# --- Game
NICK = "Unknown_Player"
display_width = 1200
display_height = 800
screen_size = (display_width, display_height)
FPS = 60

music_volume = 0.05
gun_volume = 0.1

# ________ Media ________
background_img = r'files/sprites/backgrounds/bc_3.jpg'
soldier_path = r'files/sprites/soldier/soldier1a.png'
aliens_path = r'files/sprites/aliens'
bullet_path = r'files/sprites/weapons/'
powers_path = r'files/sprites/powerups/'
gun_sound = r'./files/sounds/gun-gunshot-02.mp3'
music_theme = r'./files/sounds/Music1.mp3'
score_file = 'game_score.csv'

# ________ Init ________
pygame.init()

screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Alien Shooter 420')

pygame.mixer.init()
pygame.mixer.music.load(music_theme)
pygame.mixer.music.set_volume(music_volume)
pygame.mixer.music.play(-1)
gunshot = pygame.mixer.Sound(gun_sound)
gunshot.set_volume(gun_volume)


def generate_background():
    background = pygame.image.load(background_img)
    background = background.convert()
    return background


def generate_player():
    player = Player(screen)

    # Player Stats
    default_hp = 400
    max_hp = 400
    default_armor = 100
    max_armor = 200
    default_speed = 4
    player_status = [[default_hp, max_hp], [default_armor, max_armor], default_speed]
    
    return player, player_status


def generate_enemies(player):
    enemy_count = [5, 10, 15]
    enemy_img = []
    for file in os.listdir(aliens_path):
        enemy_img.append(pygame.image.load('./' + aliens_path + '/' + file))

    # [speed, damage, hp, attack speed, score value]
    # TODO : Alien balance, now game is about 50-80 sec
    alien_stats = [[3, 2, 4, 100, 3],
                   [3, 3, 4, 100, 4],
                   [5, 1, 1, 120, 6],
                   [5, 1, 2, 130, 7],
                   [2, 4, 5, 80, 9],
                   [2, 5, 6, 80, 10]]

    aliens = []

    # generate aliens 10 timesa
    for _ in range(10):
        while True:
            a = random.randint(0, len(enemy_count)-1)
            if enemy_count[a]:
                aliens.append(Alien(screen, alien_stats[a][0], alien_stats[a][1],
                                    alien_stats[a][2], alien_stats[a][3], alien_stats[a][4],
                                    enemy_img[a], a, player.rect.center))
                enemy_count[a] = enemy_count[a] - 1
                break

    return aliens, alien_stats, enemy_img


def generate_ammo():
    ammo = [[20, 10], [15, 5], [50, 5]]
    ammo_capacity = [20, 15, 50]

    text = ''
    text_xy = (display_width - display_width*0.8, display_height - display_height*0.05)

    for index in range(len(ammo)):
        text += str(ammo[index][0]) + ',' + str(ammo[index][1]) + ','

    ammo_text = Text(27, (255, 255, 255), text_xy, text,
                     '1:  %s  [%s]         2:  %s  [%s]         3: %s  [%s]', 255)

    # Bullet images
    bullet_images = []
    for file in os.listdir(bullet_path):
        bullet_images.append(pygame.image.load('./' + bullet_path + '/' + file))

    return ammo, ammo_capacity, ammo_text, bullet_images


def generate_powers():
    powerup_images = []
    for file in os.listdir(powers_path):
        powerup_images.append(pygame.image.load('./' + powers_path + '/' + file))
    return powerup_images


def generate_hud():
    # Game HUD
    bar_h = (display_width - 260,  display_height - 75)
    bar_a = (display_width - 260,  display_height - 40)
    text_h = (display_width - 135,  display_height - 60)
    text_a = (display_width - 135,  display_height - 25)
    score_xy = (display_width - display_width*0.85, display_height - display_height*0.96)

    health = StatusBar(bar_h, (255, 0, 0), (0, 0, 0), (250, 30), 200, 400, 0, None)
    armour = StatusBar(bar_a, (238, 233, 233), (139, 137, 137), (250, 30), 100, 200, 0, None)

    health_text = Text(25, (255, 255, 255), text_h, '400,400', '%s/%s', 255)
    armour_text = Text(25, (0, 0, 0), text_a, '200,200', '%s/%s', 255)
    score_text = Text(30, (255, 255, 255), score_xy, '0,0', 'Score:%s     Time:%s  ', 255)

    return health, armour, health_text, armour_text, score_text


def key_action(keystate, player, reload_status, reload):
    if keystate[pygame.locals.K_w]:
        player.go_up(screen)
        if reload_status:
            # sets the reload bar above the player
            reload.set_position((player.rect.center[0] - 40, player.rect.center[1] + -60))

    if keystate[pygame.locals.K_a]:
        player.go_left(screen)
        if reload_status:
            # sets the reload bar above the player
            reload.set_position((player.rect.center[0] - 40, player.rect.center[1] + -60))

    if keystate[pygame.locals.K_s]:
        player.go_down(screen)
        if reload_status:
            # sets the reload bar above the player
            reload.set_position((player.rect.center[0] - 40, player.rect.center[1] + -60))

    if keystate[pygame.locals.K_d]:
        player.go_right(screen)
        if reload_status:
            # sets the reload bar above the player
            reload.set_position((player.rect.center[0] - 40, player.rect.center[1] + -60))


def random_powerup(bullet, bullet_col, powerup_images):
    powerup_chance = random.randint(0, 100)
    power, powerup_status = False, False

    # 1/100 chance to spawn invincible
    if powerup_chance == 0:
        powerup_status = True
        power = Powerup(bullet_col[bullet][0].rect.center, 5, powerup_images[5])

    # 2/100 chance to spawn 2x speed
    elif powerup_chance == 1 or powerup_chance == 2:
        powerup_status = True
        power = Powerup(bullet_col[bullet][0].rect.center, 0, powerup_images[0])

    # 2/100 chance to spawn 2x damage
    elif powerup_chance == 3 or powerup_chance == 4:
        powerup_status = True
        power = Powerup(bullet_col[bullet][0].rect.center, 1, powerup_images[1])

    # 2/100 chance to spawn hp+100
    elif powerup_chance == 5 or powerup_chance == 6:
        powerup_status = True
        power = Powerup(bullet_col[bullet][0].rect.center, 2, powerup_images[2])

    # 2/100 chance to spawn armour+100
    elif powerup_chance == 7 or powerup_chance == 8:
        powerup_status = True
        power = Powerup(bullet_col[bullet][0].rect.center, 3, powerup_images[3])

    # 4/100 chance to spawn ammo
    elif powerup_chance == 9 or powerup_chance == 10 or powerup_chance == 11 or powerup_chance == 12:
        powerup_status = True
        power = Powerup(bullet_col[bullet][0].rect.center, 4, powerup_images[4])

    return power, powerup_status


def save_game_score(score, game_time):
    game_date = datetime.now()
    game_date = game_date.strftime("%H:%M:%S  %d.%m.%Y")

    row = (str(NICK), str(score), str(game_time), game_date)

    with open(score_file, 'a') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(row)


# ___ MAIN GAME
def main():
    # ___GAMEPLAY
    clock = pygame.time.Clock()
    keep_playing = True

    # ___ Background
    background = generate_background()
    screen.blit(background, (0, 0))

    #  ___ Player
    player, player_status = generate_player()

    # ___ Enemies
    aliens, alien_stats, enemy_img = generate_enemies(player)
    alien_swarm = pygame.sprite.Group(aliens)

    # ___ Amunition
    ammo, ammo_capacity, ammo_text, bullet_images = generate_ammo()

    # ___ Level settings
    # Score
    score = 0
    t_sec = 0   # Relative time, more time=  more aliens
    t_last = 0   # Relative time, more time=  more aliens

    # ___ Weapons settings
    weapon = [True, True, True]
    current_weapon = 0
    rifle_ticks = 0  # for Rifle weapon fire time
    machine_gun_fire = False
    machine_gun_delay = 0

    reload_time = [1, 1.5, 2]
    reload_status = False
    reload = StatusBar((player.rect.center[0] - 40, player.rect.center[1] + -60),
                       (0, 255, 0), (0, 0, 0), (70, 7), 0, 100, 1, reload_time[current_weapon])

    # ___ Game HUD
    health, armour, health_text, armour_text, score_text = generate_hud()

    powers_sprites = pygame.sprite.Group()
    aliens_sprites = pygame.sprite.Group(alien_swarm)
    bullets_sprites = pygame.sprite.Group()
    bullet_hitbox = pygame.sprite.Group()
    reloading = pygame.sprite.Group()

    sprites_tuple = (bullets_sprites, bullet_hitbox, player, aliens_sprites, powers_sprites, reloading,
                     health, armour, health_text, armour_text, score_text, ammo_text)
    all_sprites = pygame.sprite.OrderedUpdates(sprites_tuple)

    # ___ Special Powers
    powerup_images = generate_powers()
    speed_timer = 0
    damage_timer = 0
    invincible_timer = 0
    speed_status = False
    double_status = False
    invincible_status = False

    #__________________
    # ___ GAME LOOP
    while keep_playing:
        # Time variables
        clock.tick(FPS)
        t = pygame.time.get_ticks()
        if t % FPS == 0:
            t_sec += 1

        # Player rotation to the mouse cursor
        player.rotate(pygame.mouse.get_pos())
        # Key Pressed
        keystate = pygame.key.get_pressed()
        key_action(keystate, player, reload_status, reload)

        # EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keep_playing = False
                save_game_score(score, t_sec)

            # Mouse button
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # TODO : Statystyki broni w zmiennych
                # Pistol bullets [speed: 15, damage: 3]
                if current_weapon == 0 and ammo[0][0]:
                    # play sound
                    gunshot.play()
                    # subtract ammo
                    ammo[0][0] = ammo[0][0] - 1
                    # passes img, player angle, player rect, mouse pos, speed and damage
                    bullet1 = Bullet(bullet_images[0], player.get_angle(),
                                     player.rect.center, pygame.mouse.get_pos(), 15, 3, double_status)
                    bullet2 = Bullet(None, None, player.rect.center,
                                     pygame.mouse.get_pos(), 15, 3, double_status)
                    bullets_sprites.add(bullet1)
                    bullet_hitbox.add(bullet2)
                    sprites_tuple = (bullets_sprites, bullet_hitbox, player, aliens_sprites, powers_sprites, reloading,
                                     health, armour, health_text, armour_text, score_text, ammo_text)

                    all_sprites = pygame.sprite.OrderedUpdates(sprites_tuple)

                # Rfile bullets [speed: 10, damage: 8]
                elif current_weapon == 1 and ammo[1][0]:
                    delta = (t - rifle_ticks) / 1000.0

                    if delta > FPS/(FPS*2):
                        rifle_ticks = t
                        gunshot.play()
                        ammo[1][0] = ammo[1][0] - 1
                        bullet1 = Bullet(bullet_images[1], player.get_angle(),
                                         player.rect.center, pygame.mouse.get_pos(), 10, 8, double_status)
                        bullet2 = Bullet(None, None, player.rect.center, pygame.mouse.get_pos(), 10, 8, double_status)
                        bullets_sprites.add(bullet1)
                        bullet_hitbox.add(bullet2)
                        sprites_tuple = (bullets_sprites, bullet_hitbox, player, aliens_sprites, powers_sprites, reloading,
                                         health, armour, health_text, armour_text, score_text, ammo_text)

                        all_sprites = pygame.sprite.OrderedUpdates(sprites_tuple)

                # Machine gun bullets hold to keep shooting[speed: 14, damage:6]
                elif current_weapon == 2 and ammo[2][0]:
                    machine_gun_fire = True

                # If no ammo reaload
                else:
                    if not reload_status and ammo[current_weapon][1]:
                        reload_status = True
                        reload = StatusBar((player.rect.center[0] - 40, player.rect.center[1] + -60),
                                           (0, 255, 0), (0, 0, 0), (70, 7), 0, 100, 1, reload_time[current_weapon])
                        reloading.add(reload)
                        sprites_tuple = (bullets_sprites, bullet_hitbox, player, aliens_sprites, powers_sprites, reloading,
                                         health, armour, health_text, armour_text, score_text, ammo_text)
                        all_sprites = pygame.sprite.OrderedUpdates(sprites_tuple)

            elif event.type == pygame.MOUSEBUTTONUP:
                if current_weapon == 2:
                    machine_gun_fire = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and weapon[0] and not reload_status:
                    current_weapon = 0
                    player.change_image(0)
                    machine_gun_fire = False

                elif event.key == pygame.K_2 and weapon[1] and not reload_status:
                    current_weapon = 1
                    player.change_image(1)
                    machine_gun_fire = False

                elif event.key == pygame.K_3 and weapon[2] and not reload_status:
                    current_weapon = 2
                    player.change_image(2)

        # Machinegun fire
        if machine_gun_fire:
            machine_gun_delay += 1
            # Fire rate:
            if machine_gun_delay % 3 == 0:
                gunshot.play()

                bullet1 = Bullet(bullet_images[0], player.get_angle(), player.rect.center,
                                 pygame.mouse.get_pos(), 16, 5, double_status)
                bullet2 = Bullet(None, None, player.rect.center, pygame.mouse.get_pos(), 16, 5, double_status)

                bullets_sprites.add(bullet1)
                bullet_hitbox.add(bullet2)

                sprites_tuple = (bullets_sprites, bullet_hitbox, player, aliens_sprites, powers_sprites, reloading,
                                 health, armour, health_text, armour_text, score_text, ammo_text)
                all_sprites = pygame.sprite.OrderedUpdates(sprites_tuple)

                ammo[2][0] = ammo[2][0] - 1

        if ammo[2][0] == 0:
            machine_gun_fire = False

        if reload_status and reload.get_reload():
            ammo[current_weapon][0] = ammo_capacity[current_weapon]
            ammo[current_weapon][1] = ammo[current_weapon][1] - 1
            reload_status = False

        #Collisions
        # Player <> Alien
        player_alien_col = pygame.sprite.spritecollide(player, aliens_sprites, False)
        if player_alien_col:
            for alien in player_alien_col:
                alien.move(False)

                # If the player is not invincible
                if not invincible_status and alien.get_attack():
                    if player_status[1][0] > 0:
                        player_status[1][0] = player_status[1][0] - alien.get_damage()
                        # If armour is a negative value add the negative armour value to health
                        if player_status[1][0] < 0:
                            player_status[0][0] = player_status[0][0] + player_status[1][0]
                            player_status[1][0] = 0
                    else:
                        # Take health
                        player_status[0][0] = player_status[0][0] - alien.get_damage()

                        # Death
                        if player_status[0][0] <= 0:
                            keep_playing = False
        else:
            for alien in aliens_sprites:
                alien.move(True)
                alien.reset_attack()

        # Bullet <> Alien
        bullet_col = pygame.sprite.groupcollide(bullet_hitbox, aliens_sprites, True, False) # c
        if bullet_col:
            for bullet in bullet_col.keys():
                if not (bullet_col[bullet][0].damage_hp(bullet.get_damage())):  # Return false if alien hp<=0
                    score += bullet_col[bullet][0].get_value()  # Add the value of the alien killed to score
                    bullet_col[bullet][0].kill()    # Kill the alien

                    # Power up chance to drop after alien kill
                    power, powerup_status = random_powerup(bullet, bullet_col, powerup_images)
                    if powerup_status:
                        powers_sprites.add(power)
                        sprites_tuple = (bullets_sprites, bullet_hitbox, player, aliens_sprites, powers_sprites, reloading,
                                         health, armour, health_text, armour_text, score_text, ammo_text)
                        all_sprites = pygame.sprite.OrderedUpdates(sprites_tuple)

        # Player <> Powerups
        player_power_col = pygame.sprite.spritecollide(player, powers_sprites, False)
        if player_power_col:
            for buff in player_power_col:
                powerup_type = buff.get_type()

                # 2x speed
                if powerup_type == 0:
                    speed_timer = 0
                    speed_status = True
                    player.increase_speed()

                # 2x damage
                elif powerup_type == 1:
                    double_status = True
                    damage_timer = 0

                # +100 HP
                elif powerup_type == 2:
                    player_status[0][0] = player_status[0][0] + 100
                    if player_status[0][0] > player_status[0][1]:
                        player_status[0][0] = player_status[0][1]

                # + 100 Armour
                elif powerup_type == 3:
                    player_status[1][0] = player_status[1][0] + 100
                    if player_status[1][0] > player_status[1][1]:
                        player_status[1][0] = player_status[1][1]

                # Ammo
                elif powerup_type == 4:
                    # TODO: Dodac poziom max ammo
                    for count, ammo_type in enumerate(ammo):
                        ammo[count][0] = ammo_capacity[count]
                        ammo[count][1] = ammo[count][1] + 1

                # Invincible
                elif powerup_type == 5:
                    invincible_status = True
                    invincible_timer = 0

                # kill the buff sprite
                buff.kill()

        # Powerups Timers
        if speed_status:
            speed_timer += 1
        if double_status:
            damage_timer += 1
        if invincible_status:
            invincible_timer += 1

        if speed_timer == FPS * 4:
            player.reset_speed()
        if damage_timer == FPS * 4:
            double_status = False
        if invincible_timer == FPS * 4:
            invincible_status = False

        # Refresh text
        score_text.set_variable(0, str(score))
        score_text.set_variable(1, str(t_sec))

        health.set_status(player_status[0][0])
        armour.set_status(player_status[1][0])
        health_text.set_variable(0, str(player_status[0][0]))
        armour_text.set_variable(0, str(player_status[1][0]))

        # Set ammo variables
        for n, i in enumerate(range(len(ammo))):
            for j in range(2):
                ammo_text.set_variable(n, str(ammo[i][j]))

        # Adjusts aliens
        for alien in aliens_sprites:
            alien.rotate(player.rect.center)
            alien.set_step_amount(player.rect.center)

        # Generate more aliens with time
        if t_sec % 2 == 0 and t_sec > 3 and t_sec != t_last:
            t_last = t_sec
            t_base = t_sec / 5  # time base for spawning aliens
            more_aliens = int(2 * t_base) + random.randint(-1, 2)

            if more_aliens > 10:
                more_aliens = 10 + random.randint(1, 10)

            for _ in range(more_aliens):
                a = random.randint(0, 5)
                alien = (Alien(screen, alien_stats[a][0], alien_stats[a][1], alien_stats[a][2], alien_stats[a][3],
                               alien_stats[a][4], enemy_img[a], a, player.rect.center))
                aliens_sprites.add(alien)
                sprites_tuple = (bullets_sprites, bullet_hitbox, player, aliens_sprites, powers_sprites, reloading,
                                 health, armour, health_text, armour_text, score_text, ammo_text)

                all_sprites = pygame.sprite.OrderedUpdates(sprites_tuple)

        # Refresh screen
        screen.blit(background, (0, 0))
        all_sprites.update()
        all_sprites.draw(screen)

        pygame.display.flip()

    # Close the game window
    pygame.quit()


if __name__ == "__main__":
    print("Game starts")
    main()
    print("Game stops")