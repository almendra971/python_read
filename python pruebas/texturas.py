import pygame
import sys

width = 800
height = 600
suelo = 500
roca = 40


rojo = ((255, 0, 0))
negro = ((0, 0, 0))
blanco = ((255, 255, 255))
gris = ((128, 128, 128))
azul = ((255, 255, 0))
gris_distinto = ((80, 80, 80))
amarillo = 	(255, 255, 0)
azul_claro = (0, 191, 255)
gris_oscuro = (100, 100, 100)
azul_oscuro = (0, 0, 20)
naranja = (255, 193, 137)

energy_max = 100
food_max = 100
instamina = 100


color_energy = amarillo
color_food = rojo
color_instamina = azul_claro
background = gris_oscuro

interval_update = 2000

duracion_dia = 120000
amanecer_tiempo = 30000
mañana_tiempo = 40000
tarde_tiempo = 90000
media_noche_tiempo = 120000
oscuridad_max = 180

color_noche = azul_oscuro
color_dia = blanco
color_amanecer_atardecer = naranja