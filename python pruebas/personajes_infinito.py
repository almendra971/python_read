import pygame
import texturas
import math

class Personaje:
    def __init__(self, x, y):
        # Posición absoluta en el mundo
        self.world_x = x
        self.world_y = y
        
        # Posición fija en el centro de la pantalla para el renderizado
        self.screen_x = texturas.width // 2
        self.screen_y = texturas.height // 2
        
        self.size = 20 
        self.inventory = {"Roca": 0, "Calcita": 0} 

        self.food = texturas.food_max
        self.energy = texturas.energy_max
        self.instamina = texturas.instamina
        
    def draw(self, screen): 
        # Dibujar al personaje en el centro
        pygame.draw.rect(screen, texturas.negro, (self.screen_x, self.screen_y, self.size, self.size))
        # Dibujar las barras (todas las que tenías)
        self.draw_bar(screen)
            
    def move(self, dx, dy, mundo_infinito):
        """Mueve al personaje validando colisiones en el espacio del mundo"""
        nueva_world_x = self.world_x + dx
        nueva_world_y = self.world_y + dy
        
        # IMPORTANTE: Buscamos objetos usando la posición REAL del mundo
        objetos = mundo_infinito.obtener_objetos_cercanos(self.world_x, self.world_y, radio=100)
        
        colision = False
        # Verificar colisiones con rocas
        for roca in objetos['rocas']:
            if self.check_collision_world(nueva_world_x, nueva_world_y, roca):
                colision = True
                break
        
        if not colision:
            self.world_x = nueva_world_x
            self.world_y = nueva_world_y
            # Actualizar chunks basado en la nueva posición de mundo
            mundo_infinito.actualizar(self.world_x, self.world_y)

        self.update_energy(-0.1)
            
    def check_collision_world(self, p_world_x, p_world_y, obj):
        """Detección de colisión usando coordenadas globales"""
        return (p_world_x < obj.x + obj.size and 
                p_world_x + self.size > obj.x and 
                p_world_y < obj.y + obj.size and 
                p_world_y + self.size > obj.y)
            
    def esta_cerca(self, objeto, mundo_infinito, distancia=40):
        
        p_centro_x = self.world_x + self.size / 2
        p_centro_y = self.world_y + self.size / 2
        
        o_centro_x = objeto.x + objeto.size / 2
        o_centro_y = objeto.y + objeto.size / 2
        
        dist = math.sqrt((p_centro_x - o_centro_x)**2 + (p_centro_y - o_centro_y)**2)
        return dist < distancia
    
    def recolectar(self, lista_objetos, inventario_sistema, nombre_item, mundo_infinito):
        """Lógica de recolección para mundo infinito"""
        for objeto in lista_objetos[:]:
            if self.esta_cerca(objeto, mundo_infinito):
                if inventario_sistema.agregar_item(nombre_item, 1):
                    mundo_infinito.remover_objeto(objeto)
                    print(f"Recogido: {nombre_item}")
                    return True
        return False

    def update_energy(self, amount):
        self.energy = max(0, min(self.energy + amount, texturas.energy_max))
        
    def update_food(self, amount):
        self.food = max(0, min(self.food + amount, texturas.food_max))

    def update_instamina(self, amount):
        self.instamina = max(0, min(self.instamina + amount, texturas.instamina))

    def update_state(self):
        self.update_food(-0.01) #Actualiza las barras de estadisticas con el tiempo
        self.update_instamina(-0.02)

        if self.food < texturas.food_max * 0.2 or self.instamina < texturas.instamina * 0.2:
            self.update_energy(-0.01)
        else:
            self.update_energy(0.01)

    def draw_bar(self, screen):
        # Dibuja todas las barras de estado
        bar_width = 100
        bar_height = 10
        x_offset = 10
        y_offset = 550
        
        # 1. Barra Energía
        pygame.draw.rect(screen, texturas.background, (x_offset, y_offset, bar_width, bar_height))
        ancho_e = bar_width * (self.energy / texturas.energy_max)
        pygame.draw.rect(screen, texturas.color_energy, (x_offset, y_offset, ancho_e, bar_height))
        
        # 2. Barra Comida (Recuperada)
        y_offset += 15
        pygame.draw.rect(screen, texturas.background, (x_offset, y_offset, bar_width, bar_height))
        ancho_f = bar_width * (self.food / texturas.food_max)
        pygame.draw.rect(screen, texturas.color_food, (x_offset, y_offset, ancho_f, bar_height))

        # 3. Barra Instamina (Recuperada)
        y_offset += 15
        pygame.draw.rect(screen, texturas.background, (x_offset, y_offset, bar_width, bar_height))
        ancho_i = bar_width * (self.instamina / texturas.instamina) 
        pygame.draw.rect(screen, texturas.color_instamina, (x_offset, y_offset, ancho_i, bar_height))
