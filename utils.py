import pygame


class Colors:
    black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)


def scale_image(image, scale):
    img_x = image.get_width() * scale
    img_y = image.get_height() * scale
    try:
        image = pygame.transform.scale(image, (img_x, img_y))
    except TypeError as e:
        if len(image) > 1:
            for c, img in enumerate(image):
                image[c] = pygame.transform.scale(img, (img_x, img_y))

    return image
