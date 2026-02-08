import os
import pygame
import texturas

class Rocas:
    _IMAGE = None 

    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        if Rocas._IMAGE is None:
            path = os.path.join('imagenes', 'objetos', 'roca.xcf')
            try:
                # LA CLAVE: .convert_alpha() para quitar el fondo
                img = pygame.image.load(path).convert_alpha() 
                Rocas._IMAGE = pygame.transform.scale(img, (texturas.roca, texturas.roca))
            except:
                Rocas._IMAGE = pygame.Surface((texturas.roca, texturas.roca))
                Rocas._IMAGE.fill((100, 100, 100))
        
        self.size = texturas.roca
    
    def draw(self, screen, cam_x, cam_y):
        # Al usar blit con una imagen convert_alpha, el fondo desaparece
        screen.blit(self._IMAGE, (self.x - cam_x, self.y - cam_y))
        
class Mineral_calcita:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20

    def draw(self, screen, cam_x, cam_y):
        # Simplificado: El dibujo se hace en relación a la cámara
        pygame.draw.rect(screen, texturas.rojo, (self.x - cam_x, self.y - cam_y, self.size, self.size))

class Nave:
    def __init__(self, world_x, world_y, width=120, height=80):
        self.world_x = world_x
        self.world_y = world_y
        self.width = width
        self.height = height

        # La puerta será una zona rectangular en la nave donde se puede interactuar
        self.puerta_rect = pygame.Rect(
            self.world_x + self.width//2 - 20, 
            self.world_y + self.height - 10, 
            40, 10
        )

    def draw(self, screen, camera_x, camera_y):
        # Dibujar nave en el mundo, ajustando por cámara
        rect = pygame.Rect(self.world_x - camera_x, self.world_y - camera_y, self.width, self.height)
        pygame.draw.rect(screen, (200, 200, 50), rect)  # color amarillo para nave
        # Dibujar puerta visible (opcional para debugging)
        puerta_draw = pygame.Rect(
            self.puerta_rect.x - camera_x, 
            self.puerta_rect.y - camera_y, 
            self.puerta_rect.width, 
            self.puerta_rect.height
        )
        pygame.draw.rect(screen, (0, 255, 0), puerta_draw)  # verde para puerta
