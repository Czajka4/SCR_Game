#
# models.py
#
import pygame
import os
import math
import random
from utils import scale_image

# ___ MODEL VARIABLES
player_scale = 0.75
enemies_scale = 0.6
item_scale = 0.7

# ___ Images
soldier_path = r'files/sprites/soldier/'


#  player class
class Player(pygame.sprite.Sprite):
    def __init__(self, screen):
        pygame.sprite.Sprite.__init__(self)

        # Create list of images
        self.__list = []
        for file in os.listdir(soldier_path):
            img = pygame.image.load('./' + soldier_path + '/' + file)
            self.__list.append(scale_image(img, player_scale))

        self.image = self.__list[0]
        self.rect = self.image.get_rect()
        self.__saved_image = self.image

        self.rect.left = 0
        self.rect.top = 200
        self.__speed = 4

        # set the angle value
        self.__angle = 0

    def reset_speed(self):
        self.__speed = 4

    def increase_speed(self):
        self.__speed = 8

    def go_left(self, screen):
        if self.rect.left >= 0:
            self.rect.left -= self.__speed

    def go_right(self, screen):
        if self.rect.right <=  screen.get_width():
            self.rect.right += self.__speed

    def go_up(self, screen):
        if self.rect.top >= 0:
            self.rect.top -= self.__speed

    def go_down(self, screen):
        if self.rect.bottom <= screen.get_height():
            self.rect.bottom += self.__speed

    def get_angle(self):
        return self.__angle

    def change_image(self, weapon):
        self.image = self.__list[weapon]
        self.__saved_image = self.image

    def rotate(self, mouse_pos):
        self.__angle = math.degrees(math.atan2(self.rect.centerx - mouse_pos[0], self.rect.centery - mouse_pos[1]))
        self.image = pygame.transform.rotate(self.__saved_image, self.__angle)
        self.rect = self.image.get_rect(center=self.rect.center)


class Alien(pygame.sprite.Sprite):
    def __init__(self, screen, speed, damage, hp, attack_speed, value, image, alien_type, player_pos):
        pygame.sprite.Sprite.__init__(self)
        self.__screen = screen
        self.__speed = speed
        self.__default_speed = speed

        self.__damage = damage
        self.__hp = hp
        self.__attack_speed = attack_speed
        self.__value = value
        self.__alien_type = alien_type

        self.__move = True
        self.__count = (attack_speed - 1)

        self.__slow = False
        self.__slow_counter = 0

        self.image = image
        self.image = scale_image(self.image, enemies_scale)
        self.__saved_image = self.image
        self.rect = self.image.get_rect()

        self.spawn()
        self.rotate(player_pos)
        self.set_step_amount(player_pos)

    def reset_attack(self):
        self.__count = self.__attack_speed - 1

    def get_attack(self):
        self.__count += 1
        if self.__count == self.__attack_speed:
            self.__count = 0
            return True
        else:
            return False

    def get_alien_type(self):
        return self.__alien_type

    def get_damage(self):
        return self.__damage

    def get_value(self):
        return self.__value

    def damage_hp(self, damage):
        self.__hp -= damage
        if self.__hp > 0:
            return True
        else:
            return False

    def set_step_amount(self, player_pos):
        try:
            self.__distance = math.sqrt \
                (pow(player_pos[0] - self.rect.centerx, 2) + pow(player_pos[1] - self.rect.centery, 2))
            self.__animation_steps = self.__distance / self.__speed
            self.__dx = (player_pos[0] - self.rect.centerx) / self.__animation_steps
            self.__dy = (player_pos[1] - self.rect.centery) / self.__animation_steps
        except:
            self.__dx = 0
            self.__dy = 0

    def move(self, boolval):
        self.__move = boolval

    def spawn(self):
        self.__spawn = random.randint(1, 3)
        if self.__spawn == 1:
            self.__x = random.randrange(0, -300, -30)
            self.__y = random.randint(0, self.__screen.get_height() - 100)
        elif self.__spawn == 2:
            self.__x = random.randint(self.__screen.get_width(), self.__screen.get_width() + 300)
            self.__y = random.randint(0, self.__screen.get_height() - 100)
        else:
            self.__x = random.randint(0, self.__screen.get_width())
            self.__y = random.randint(self.__screen.get_height(), self.__screen.get_height() + 300)

        self.rect.center = (self.__x, self.__y)

    def rotate(self, player_pos):
        self.__angle = math.degrees(math.atan2(self.rect.centerx - player_pos[0], self.rect.centery - player_pos[1]))
        self.image = pygame.transform.rotate(self.__saved_image, self.__angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        if self.__move:
            self.rect.centerx += self.__dx
            self.rect.centery += self.__dy
        if self.__slow:
            self.__slow_counter += 1
            if self.__slow_counter >= 400:
                self.__speed = self.__default_speed
                self.__slow_counter = 0
                self.__slow = False


class Bullet(pygame.sprite.Sprite):
    def __init__(self, image, angle, player_pos, mouse_pos, speed, damage, double_damage):
        pygame.sprite.Sprite.__init__(self)

        if double_damage:
            self.__damage = damage * 2
        else:
            self.__damage = damage

        self.__damage = damage

        self.__x = player_pos[0]
        self.__y = player_pos[1]

        self.__target_x = mouse_pos[0]
        self.__target_y = mouse_pos[1]

        if image:
            self.image = image
            self.image.convert()
            self.rect = self.image.get_rect()
            self.rect.center = (self.__x, self.__y)
            self.image = pygame.transform.rotate(self.image, angle)
            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            self.image = pygame.Surface((5, 5))
            self.image.fill((255, 0, 0))
            self.image.set_alpha(0)
            self.rect = self.image.get_rect()
            self.rect.center = (self.__x, self.__y)

        self.__distance = math.sqrt(pow(self.__target_x - self.__x, 2) + pow(self.__target_y - self.__y, 2))
        self.__animation_steps = self.__distance / speed
        self.__dx = (self.__target_x - self.__x) / self.__animation_steps
        self.__dy = (self.__target_y - self.__y) / self.__animation_steps

    def get_damage(self):
        return self.__damage

    def update(self):
        self.rect.centerx += self.__dx
        self.rect.centery += self.__dy
        if self.rect.top < 0 or self.rect.bottom > 620 or self.rect.left < 0 or self.rect.right > 1280:
            self.kill()


class StatusBar(pygame.sprite.Sprite):
    def __init__(self, position, color1, color2, size, status1, status2, typeof, increase):
        pygame.sprite.Sprite.__init__(self)

        self.__colors = [color1, color2]
        self.__size = size
        self.__s1 = status1
        self.__s2 = float(status2)
        self.__m = size[0] * 100
        self.__type = typeof
        self.__increase = increase

        self.image = pygame.Surface(size)
        self.image.fill(color2)
        pygame.draw.rect(self.image, color1, ((0, 0), (self.__s1 / self.__s2 * 100 * self.__m, self.__size[1])), 0)

        self.rect = self.image.get_rect()
        self.rect.left = position[0]
        self.rect.top = position[1]

    def set_position(self, position):
        self.rect.left = position[0]
        self.rect.top = position[1]

    def set_status(self, current_status):
        self.image.fill(self.__colors[1])
        pygame.draw.rect(self.image, self.__colors[0], ((0, 0),
                        (current_status / self.__s2 * 100 * self.__m, self.__size[1])), 0)

    def get_reload(self):
        if self.__s2 - self.__s1 < 0:
            return True

    def update(self):
        if self.__type:
            self.image.fill(self.__colors[1])
            self.__s1 += self.__increase
            pygame.draw.rect(self.image, self.__colors[0],
                             ((0, 0), (self.__s1 / self.__s2 * 100 * self.__m, self.__size[1])), 0)

            if self.__s2 - self.__s1 < -1:
                self.kill()


class Text(pygame.sprite.Sprite):
    def __init__(self, size, color, position, variables, message, alpha):
        pygame.sprite.Sprite.__init__(self)
        self.__font = pygame.font.Font(r"files/fonts/space_font.ttf", int(size/1.5))
        self.__color = color
        self.__position = position

        if variables:
            self.__variables = variables.split(',')
            if len(self.__variables) > 3:
                self.__variables.pop()

        self.__message = message
        self.__m = ''
        self.__alpha = alpha

    def set_variable(self, index, value):
        self.__variables[index] = value

    def set_alpha(self, alpha):
        self.__alpha = alpha

    def update(self):
        if self.__variables:
            self.__m = self.__message % tuple(self.__variables)
        else:
            self.__m = self.__message

        self.image = self.__font.render(self.__m, True, self.__color)
        self.image.set_alpha(self.__alpha)
        self.rect = self.image.get_rect()
        self.rect.center = (self.__position)


class Powerup(pygame.sprite.Sprite):
    def __init__(self, location, num, image):
        pygame.sprite.Sprite.__init__(self)

        self.image = scale_image(image, item_scale)
        self.rect = self.image.get_rect()
        self.rect.center = location

        self.__type = num

        self.__count = 0
        self.__alpha = 255

    def get_type(self):
        return self.__type

    def update(self):
        self.__count += 1
        if self.__alpha == 0:
            self.kill()
        elif self.__count >= 300:
            self.image.set_alpha(self.__alpha)
            self.__alpha -= 3
