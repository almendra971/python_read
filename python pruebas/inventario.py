import pygame
import json

class Item:
    # Clase para representar un item
    def __init__(self, nombre, tipo, max_stack=999, icono=None, descripcion=""):
        self.nombre = nombre
        self.tipo = tipo  # "material", "herramienta", "consumible", etc.
        self.max_stack = max_stack
        self.icono = icono
        self.descripcion = descripcion
        self.cantidad = 1
         
    
    def copy(self):
        # Crea una copia del item
        nuevo = Item(self.nombre, self.tipo, self.max_stack, self.icono, self.descripcion)
        nuevo.cantidad = self.cantidad
        return nuevo


class Inventory:
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Inventario principal (40 slots tipo Terraria)
        self.slots_inventario = [None] * 40
        
        # Hotbar (10 slots de acceso rápido)
        self.hotbar = [None] * 10
        self.hotbar_seleccionado = 0
        
        # UI
        self.visible = False
        self.slot_size = 25
        self.padding = 4
        self.slots_por_fila = 10
        
        # Drag & Drop
        self.dragging = False
        self.dragged_item = None
        self.dragged_from = None  # (tipo, index) - tipo: "inv", "hot"
        self.drag_offset = (0, 0)
        
        # Tooltip
        self.tooltip_item = None
        self.tooltip_pos = (0, 0)
        
        # Colores inventario
        self.color_fondo = (40, 40, 60)
        self.color_slot = (26, 26, 46)
        self.color_slot_hover = (52, 52, 76)
        self.color_borde = (88, 88, 116)
        self.color_texto = (255, 255, 255)
        self.color_cantidad = (220, 220, 220)
        self.color_hotbar_selected = (255, 215, 0)
        
        # Categorías de colores para rareza
        self.colores_rareza = {
            "comun": (200, 200, 200),
            "poco_comun": (100, 255, 100),
            "raro": (100, 150, 255),
            "epico": (200, 100, 255),
            "legendario": (255, 165, 0)
        }
        
        # Base de datos de items
        self.items_database = self._crear_items_database()
    
    def _crear_items_database(self):
        """Crea la base de datos de items disponibles"""
        db = {}
        
        # Materiales
        db["Roca"] = Item("Roca", "material", 999, None, "Roca común del planeta")
        db["Calcita"] = Item("Calcita", "material", 999, None, "Mineral cristalino")
        db["Hierro"] = Item("Hierro", "material", 999, None, "Metal resistente")
        db["Cristal"] = Item("Cristal", "material", 999, None, "Cristal energético")
        
        # Consumibles
        db["Combustible"] = Item("Combustible", "consumible", 99, None, "Restaura 25% energía")
        db["Kit Reparación"] = Item("Kit Reparación", "consumible", 20, None, "Repara sistemas")
        
        # Herramientas
        db["Pico"] = Item("Pico", "herramienta", 1, None, "Para minar rocas")
        db["Scanner"] = Item("Scanner", "herramienta", 1, None, "Analiza el entorno")
        
        return db
    
    def toggle(self):
        """Mostrar/ocultar inventario"""
        self.visible = not self.visible
        if not self.visible:
            self.cancelar_drag()

    def get_item_seleccionado(self):
        
        # Verificamos que el índice esté dentro del rango de la hotbar
        if 0 <= self.hotbar_seleccionado < len(self.hotbar):
            return self.hotbar[self.hotbar_seleccionado]
        return None
    
    def agregar_item(self, nombre_item, cantidad=1):
        """Agrega items al inventario (con stacking automático)"""
        if nombre_item not in self.items_database:
            print(f"⚠ Item desconocido: {nombre_item}")
            return False
        
        item_template = self.items_database[nombre_item]
        cantidad_restante = cantidad
        
        # Primero buscar slots con el mismo item (para stackear)
        for slot in self.hotbar + self.slots_inventario:
            if slot and slot.nombre == nombre_item:
                espacio_disponible = item_template.max_stack - slot.cantidad
                if espacio_disponible > 0:
                    agregar = min(espacio_disponible, cantidad_restante)
                    slot.cantidad += agregar
                    cantidad_restante -= agregar
                    if cantidad_restante <= 0: return True
        while cantidad_restante > 0:
            slot_vacio = self._encontrar_slot_vacio()
            if slot_vacio is None: return False
        
            nuevo_item = item_template.copy()
            agregar = min(item_template.max_stack, cantidad_restante)
            nuevo_item.cantidad = agregar
            cantidad_restante -= agregar
        
        tipo_slot, index = slot_vacio
        if tipo_slot == "hot":
            self.hotbar[index] = nuevo_item
        else:
            self.slots_inventario[index] = nuevo_item #solo se llenan los slots que no tengan el pico y el combustible
            return True
        
        # Luego buscar slots vacíos
        while cantidad_restante > 0:
            slot_vacio = self._encontrar_slot_vacio()
            if slot_vacio is None:
                print(f"⚠ Inventario lleno! {cantidad_restante} items no agregados")
                return False
            
            nuevo_item = item_template.copy()
            agregar = min(item_template.max_stack, cantidad_restante)
            nuevo_item.cantidad = agregar
            cantidad_restante -= agregar
            
            tipo_slot, index = slot_vacio
            if tipo_slot == "hot":
                self.hotbar[index] = nuevo_item
            else:
                self.slots_inventario[index] = nuevo_item
        
        return True
    
    def _encontrar_slot_vacio(self):
        """Encuentra el primer slot vacío"""
        # Primero en hotbar
        for i, slot in enumerate(self.hotbar):
            if slot is None:
                return ("hot", i)
        
        # Luego en inventario
        for i, slot in enumerate(self.slots_inventario):
            if slot is None:
                return ("inv", i)
        
        return None
    
    def remover_item(self, nombre_item, cantidad=1):
        """Remueve items del inventario"""
        cantidad_a_remover = cantidad
        
        for slot in self.hotbar + self.slots_inventario:
            if slot and slot.nombre == nombre_item:
                if slot.cantidad >= cantidad_a_remover:
                    slot.cantidad -= cantidad_a_remover
                    if slot.cantidad <= 0:
                        # Buscar y limpiar el slot
                        for i, s in enumerate(self.hotbar):
                            if s is slot:
                                self.hotbar[i] = None
                        for i, s in enumerate(self.slots_inventario):
                            if s is slot:
                                self.slots_inventario[i] = None
                    return True
                else:
                    cantidad_a_remover -= slot.cantidad
                    slot.cantidad = 0
                    # Limpiar slot
                    for i, s in enumerate(self.hotbar):
                        if s is slot:
                            self.hotbar[i] = None
                    for i, s in enumerate(self.slots_inventario):
                        if s is slot:
                            self.slots_inventario[i] = None
        
        return cantidad_a_remover == 0
    
    def get_item_hotbar(self, index):
        """Obtiene el item del hotbar en el índice dado"""
        if 0 <= index < len(self.hotbar):
            return self.hotbar[index]
        return None
    
    def draw(self, screen):
        """Dibuja el inventario completo"""
        # Dibujar hotbar siempre
        self._draw_hotbar(screen)
        
        # Dibujar inventario completo si está visible
        if self.visible:
            self._draw_inventario_completo(screen)
        
        # Dibujar item arrastrado
        if self.dragging and self.dragged_item:
            self._draw_dragged_item(screen)
        
        # Dibujar tooltip
        if self.tooltip_item and not self.dragging:
            self._draw_tooltip(screen)
    
    def _draw_hotbar(self, screen):
        """Dibuja la barra de acceso rápido"""
        hotbar_width = self.slots_por_fila * (self.slot_size + self.padding) + self.padding
        x = (self.screen_width - hotbar_width) // 1
        y = self.screen_height - self.slot_size - 550
        
        # Fondo semi-transparente
        s = pygame.Surface((hotbar_width, self.slot_size + 10))
        s.set_alpha(180)
        s.fill(self.color_fondo)
        screen.blit(s, (x - 5, y - 5))
        
        # Dibujar slots del hotbar
        for i in range(10):
            slot_x = x + i * (self.slot_size + self.padding)
            slot_y = y
            
            # Resaltar slot seleccionado
            if i == self.hotbar_seleccionado:
                pygame.draw.rect(screen, self.color_hotbar_selected, 
                               (slot_x - 2, slot_y - 2, self.slot_size + 4, self.slot_size + 4), 3)
            
            self._draw_slot(screen, slot_x, slot_y, self.hotbar[i], ("hot", i))
            
            # Número del slot
            font = pygame.font.SysFont("Arial", 14)
            num_text = font.render(str((i + 1) % 10), True, (150, 150, 150))
            screen.blit(num_text, (slot_x + 2, slot_y + 2))
    
    def _draw_inventario_completo(self, screen):
        """Dibuja el inventario completo (40 slots)"""
        filas = 4
        
        inv_width = self.slots_por_fila * (self.slot_size + self.padding) + 40
        inv_height = (filas + 1) * (self.slot_size + self.padding) + 100
        
        x = (self.screen_width - inv_width) // 2
        y = (self.screen_height - inv_height) // 2
        
        # Fondo
        s = pygame.Surface((inv_width, inv_height))
        s.set_alpha(240)
        s.fill(self.color_fondo)
        screen.blit(s, (x, y))
        
        # Borde
        pygame.draw.rect(screen, self.color_borde, (x, y, inv_width, inv_height), 3)
        
        # Título
        font_titulo = pygame.font.SysFont("Arial", 28, bold=True)
        titulo = font_titulo.render("INVENTARIO", True, self.color_texto)
        screen.blit(titulo, (x + 20, y + 15))
        
        # Botón cerrar
        font_cerrar = pygame.font.SysFont("Arial", 24, bold=True)
        cerrar = font_cerrar.render("X", True, (255, 100, 100))
        screen.blit(cerrar, (x + inv_width - 40, y + 15))

        # Dibujar slots del inventario principal
        for i in range(40):
            fila = i // self.slots_por_fila
            columna = i % self.slots_por_fila
            
            slot_x = x + 20 + columna * (self.slot_size + self.padding)
            slot_y = y + 80 + fila * (self.slot_size + self.padding) # Ajustar el eje y para dejar espacio al título
            
            # ¡
            self._draw_slot(screen, slot_x, slot_y, self.slots_inventario[i], ("inv", i))

        
    def _draw_slot(self, screen, x, y, item, slot_id):
        """Dibuja un slot individual con contenido centrado"""
        mouse_pos = pygame.mouse.get_pos()
        rect = pygame.Rect(x, y, self.slot_size, self.slot_size)

        # Determinar color del fondo 
        if rect.collidepoint(mouse_pos) and not self.dragging:
            color = self.color_slot_hover
            self.tooltip_item = item  # Guardamos el item para el tooltip
            self.tooltip_pos = mouse_pos
        else:
            color = self.color_slot
        
        # Dibujar el cuadro del slot
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, self.color_borde, rect, 2)

        # si existe un item, dibujarlo
        if item is not None:
            # Dibujar la letra inicial (P, C, R...)
            font_icono = pygame.font.SysFont("Arial", 18, bold=True)
            # Aquí usamos 'item.nombre', por eso 'item' debe existir
            icono_text = font_icono.render(item.nombre[0], True, self.colores_rareza.get("comun"))
            
            # Centrado matemático perfecto
            icono_rect = icono_text.get_rect(center=rect.center)
            screen.blit(icono_text, icono_rect)
            
            # Dibujar la cantidad si es mayor a 1
            if item.cantidad > 1:
                font_cant = pygame.font.SysFont("Arial", 11, bold=True)
                cant_str = str(item.cantidad)
                cant_text = font_cant.render(cant_str, True, self.color_cantidad)
                
                # Posición en la esquina inferior derecha
                cant_pos = (x + self.slot_size - cant_text.get_width() - 2, 
                            y + self.slot_size - cant_text.get_height() - 2)
                
                # Sombra negra para que se vea bien sobre cualquier fondo
                sombra = font_cant.render(cant_str, True, (0, 0, 0))
                screen.blit(sombra, (cant_pos[0] + 1, cant_pos[1] + 1))
                screen.blit(cant_text, cant_pos)
    
    def _draw_dragged_item(self, screen):
        """Dibuja el item siendo arrastrado"""
        if not self.dragged_item:
            return
        
        mouse_pos = pygame.mouse.get_pos()
        x = mouse_pos[0] - self.slot_size // 2
        y = mouse_pos[1] - self.slot_size // 2
        
        # Dibujar con transparencia
        s = pygame.Surface((self.slot_size, self.slot_size))
        s.set_alpha(200)
        s.fill(self.color_slot)
        screen.blit(s, (x, y))
        
        pygame.draw.rect(screen, self.color_borde, (x, y, self.slot_size, self.slot_size), 2)
        
        # Icono
        font_icono = pygame.font.SysFont("Arial", 24, bold=True)
        icono_text = font_icono.render(self.dragged_item.nombre[0], True, self.colores_rareza.get("comun"))
        screen.blit(icono_text, (x + 15, y + 8))
        
        # Cantidad
        if self.dragged_item.cantidad > 1:
            font_cant = pygame.font.SysFont("Arial", 14, bold=True)
            cant_text = font_cant.render(str(self.dragged_item.cantidad), True, self.color_cantidad)
            screen.blit(cant_text, (x + self.slot_size - 21, y + self.slot_size - 19))
    
    def _draw_tooltip(self, screen):
        if not self.tooltip_item:
            return
        
        font_nombre = pygame.font.SysFont("Arial", 16, bold=True)
        font_desc = pygame.font.SysFont("Arial", 13)
        
        # Textos
        nombre_text = font_nombre.render(self.tooltip_item.nombre, True, self.color_texto)
        desc_text = font_desc.render(self.tooltip_item.descripcion, True, (200, 200, 200))
        tipo_text = font_desc.render(f"Tipo: {self.tooltip_item.tipo}", True, (150, 150, 150))
        
        # Tamaño del tooltip
        width = max(nombre_text.get_width(), desc_text.get_width(), tipo_text.get_width()) + 20
        height = 80
        
        x = self.tooltip_pos[0] + 15
        y = self.tooltip_pos[1] - 10
        
        # Ajustar si se sale de la pantalla
        if x + width > self.screen_width:
            x = self.tooltip_pos[0] - width - 15
        if y + height > self.screen_height:
            y = self.screen_height - height - 10
        
        # Fondo
        s = pygame.Surface((width, height))
        s.set_alpha(240)
        s.fill((20, 20, 30))
        screen.blit(s, (x, y))
        
        pygame.draw.rect(screen, self.color_borde, (x, y, width, height), 2)
        
        # Textos
        screen.blit(nombre_text, (x + 10, y + 10))
        screen.blit(desc_text, (x + 10, y + 35))
        screen.blit(tipo_text, (x + 10, y + 55))
        
        # Resetear tooltip
        self.tooltip_item = None
    
    def handle_event(self, event):
        # Maneja eventos del mouse y teclado
        # Hotbar con teclas 1-0
        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_9:
                self.hotbar_seleccionado = event.key - pygame.K_1
            elif event.key == pygame.K_0:
                self.hotbar_seleccionado = 9
            elif event.key == pygame.K_i:
                self.toggle()
        
        # Mouse wheel para cambiar hotbar
        if event.type == pygame.MOUSEWHEEL:
            self.hotbar_seleccionado = (self.hotbar_seleccionado - event.y) % 10
        
        # Click del mouse
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)
        
        # Soltar mouse
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._handle_release(event.pos)

    
    def _handle_click(self, pos):
        # Maneja clicks del mouse
        # Verificar si clickeó el botón cerrar
        if self.visible:
            inv_width = self.slots_por_fila * (self.slot_size + self.padding) + 40
            inv_height = 5 * (self.slot_size + self.padding) + 100
            x = (self.screen_width - inv_width) // 2
            y = (self.screen_height - inv_height) // 2
            
            close_rect = pygame.Rect(x + inv_width - 50, y + 10, 40, 40)
            if close_rect.collidepoint(pos):
                self.toggle()
                return
        
        # Buscar qué slot clickeó
        slot_clickeado = self._get_slot_at_pos(pos)
        if slot_clickeado:
            tipo, index = slot_clickeado
            item = self.hotbar[index] if tipo == "hot" else self.slots_inventario[index]
            
            if item:
                # Iniciar drag
                self.dragging = True
                self.dragged_item = item
                self.dragged_from = slot_clickeado
                
                # Limpiar slot original
                if tipo == "hot":
                    self.hotbar[index] = None
                else:
                    self.slots_inventario[index] = None
    
    def _handle_release(self, pos):
        """Maneja soltar el mouse"""
        if not self.dragging:
            return
        
        # Buscar dónde soltó
        slot_destino = self._get_slot_at_pos(pos)
        
        if slot_destino:
            tipo_dest, index_dest = slot_destino
            item_destino = self.hotbar[index_dest] if tipo_dest == "hot" else self.slots_inventario[index_dest]
            
            # Si hay un item en el destino
            if item_destino:
                # Si son del mismo tipo, intentar stackear
                if item_destino.nombre == self.dragged_item.nombre:
                    espacio = item_destino.max_stack - item_destino.cantidad
                    agregar = min(espacio, self.dragged_item.cantidad)
                    item_destino.cantidad += agregar
                    self.dragged_item.cantidad -= agregar
                    
                    # Si quedó algo, devolverlo al slot original
                    if self.dragged_item.cantidad > 0:
                        tipo_orig, index_orig = self.dragged_from
                        if tipo_orig == "hot":
                            self.hotbar[index_orig] = self.dragged_item
                        else:
                            self.slots_inventario[index_orig] = self.dragged_item
                else:
                    # Intercambiar items
                    if tipo_dest == "hot":
                        self.hotbar[index_dest] = self.dragged_item
                    else:
                        self.slots_inventario[index_dest] = self.dragged_item
                    
                    tipo_orig, index_orig = self.dragged_from
                    if tipo_orig == "hot":
                        self.hotbar[index_orig] = item_destino
                    else:
                        self.slots_inventario[index_orig] = item_destino
            else:
                # Slot vacío, mover directamente
                if tipo_dest == "hot":
                    self.hotbar[index_dest] = self.dragged_item
                else:
                    self.slots_inventario[index_dest] = self.dragged_item
        else:
            # Soltó fuera, devolver al slot original
            tipo_orig, index_orig = self.dragged_from
            if tipo_orig == "hot":
                self.hotbar[index_orig] = self.dragged_item
            else:
                self.slots_inventario[index_orig] = self.dragged_item
        
        # Cancelar drag
        self.cancelar_drag()
    
    def _get_slot_at_pos(self, pos):
        """Obtiene qué slot está en la posición dada"""
        # Verificar hotbar
        hotbar_width = self.slots_por_fila * (self.slot_size + self.padding) + self.padding
        x_hotbar = (self.screen_width - hotbar_width) // 2
        y_hotbar = self.screen_height - self.slot_size - 20
        
        for i in range(10):
            slot_x = x_hotbar + i * (self.slot_size + self.padding)
            rect = pygame.Rect(slot_x, y_hotbar, self.slot_size, self.slot_size)
            if rect.collidepoint(pos):
                return ("hot", i)
        
        # Verificar inventario completo si está visible
        if self.visible:
            inv_width = self.slots_por_fila * (self.slot_size + self.padding) + 40
            inv_height = 5 * (self.slot_size + self.padding) + 100
            x = (self.screen_width - inv_width) // 2
            y = (self.screen_height - inv_height) // 2
            
            for i in range(40):
                fila = i // self.slots_por_fila
                columna = i % self.slots_por_fila
                
                slot_x = x + 20 + columna * (self.slot_size + self.padding)
                slot_y = y + 60 + fila * (self.slot_size + self.padding)
                
                rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
                if rect.collidepoint(pos):
                    return ("inv", i)
        
        return None
    
    def cancelar_drag(self):
        """Cancela el drag actual"""
        self.dragging = False
        self.dragged_item = None
        self.dragged_from = None
    
    def guardar_inventario(self, archivo="inventario.json"):
        """Guarda el inventario en un archivo"""
        data = {
            "hotbar": [],
            "inventario": []
        }
        
        for item in self.hotbar:
            if item:
                data["hotbar"].append({"nombre": item.nombre, "cantidad": item.cantidad})
            else:
                data["hotbar"].append(None)
        
        for item in self.slots_inventario:
            if item:
                data["inventario"].append({"nombre": item.nombre, "cantidad": item.cantidad})
            else:
                data["inventario"].append(None)
        
        with open(archivo, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Inventario guardado en {archivo}")
    
    def cargar_inventario(self, archivo="inventario.json"):
        try:
            with open(archivo, 'r') as f:
                data = json.load(f)
            
            # Cargar hotbar
            for i, item_data in enumerate(data.get("hotbar", [])):
                if item_data and item_data["nombre"] in self.items_database:
                    item = self.items_database[item_data["nombre"]].copy()
                    item.cantidad = item_data["cantidad"]
                    self.hotbar[i] = item
            
            # Cargar inventario
            for i, item_data in enumerate(data.get("inventario", [])):
                if item_data and item_data["nombre"] in self.items_database:
                    item = self.items_database[item_data["nombre"]].copy()
                    item.cantidad = item_data["cantidad"]
                    self.slots_inventario[i] = item
            
            print(f"✓ Inventario cargado desde {archivo}")
            return True
        except FileNotFoundError:
            print(f"⚠ Archivo {archivo} no encontrado")
            return False
    
    def usar_consumible(self):
        #Resta 1 a la cantidad del item seleccionado si es un consumible
        item = self.get_item_seleccionado()
        
        if item and item.tipo == "consumible":
            item.cantidad -= 1
            nombre_usado = item.nombre
            
            # Si se acaba el stack, limpiamos el slot de la hotbar
            if item.cantidad <= 0:
                self.hotbar[self.hotbar_seleccionado] = None
                
            return nombre_usado # Retornamos el nombre para saber qué efecto aplicar
        return None
    
 