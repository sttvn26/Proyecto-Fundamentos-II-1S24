# Importamos la biblioteca de Pygame, que nos permite crear juegos y aplicaciones gráficas
import pygame
import random
import socket
import struct

# Definimos el ancho y alto de la ventana del juego
ANCHO = 1000
ALTO = 700

# Establecemos cuántas veces por segundo se actualizará el juego
FPS = 60

# Inicializamos Pygame, lo que nos permite usar sus funciones
pygame.init()

# Inicializamos el sistema de sonido de Pygame
pygame.mixer.init()

# Creamos la ventana del juego con el ancho y alto definidos
pantalla = pygame.display.set_mode((ANCHO, ALTO))

# Ponemos un título a la ventana del juego
pygame.display.set_caption("Juego")

# Creamos un reloj que nos ayudará a controlar la velocidad del juego
reloj = pygame.time.Clock()

# Creamos una superficie (como una hoja de papel) donde dibujaremos todo
buffer = pygame.Surface((ANCHO, ALTO))

# Cargamos una imagen para usar como fondo y la redimensionamos al tamaño de la ventana
fondo = pygame.transform.scale(pygame.image.load("cancha.png").convert(), (ANCHO, ALTO))

# Creamos un grupo donde almacenaremos todos los objetos del juego (como personajes y balas)
todos_los_sprites = pygame.sprite.Group()

# Definimos una clase para nuestro personaje principal, el Jugador
class Jugador(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.prefix = f"jugador"
        ancho = 80
        alto = 80
        self.sprites = []
        self.cargar_sprites(0, ancho, alto)
        self.sprite_actual = 0
        self.image = self.sprites[self.sprite_actual]
        self.rect = self.image.get_rect()
        self.rect.centerx = ANCHO / 2 - 480
        self.rect.right = ANCHO - 100
        self.rect.bottom = ALTO / 2
        self.velocidad_animacion = 0.05
        self.ultimo_update = pygame.time.get_ticks()
        self.animacion_en_curso = False
        self.tiempo_inicio_animacion = 0
        self.animando = False

    def reiniciar_posicion(self):
        self.rect.centerx = ANCHO / 2 - 480
        self.rect.right = ANCHO - 100
        self.rect.bottom = ALTO / 2

    def cargar_sprites(self, indice, ancho, alto):
        if indice < 4:
            imagen = pygame.image.load(f"{self.prefix}{indice}.png")
            imagen = pygame.transform.scale(imagen, (ancho, alto))
            imagen.set_colorkey((24, 144, 168))
            self.sprites.append(imagen)
            self.cargar_sprites(indice + 1, ancho, alto)

    def update(self, bola_moviendo):
        if self.animacion_en_curso:
            ahora = pygame.time.get_ticks()
            tiempo_transcurrido = ahora - self.tiempo_inicio_animacion
            if tiempo_transcurrido >= len(self.sprites) * self.velocidad_animacion * 1000:
                self.animacion_en_curso = False
                self.animando = False
                self.sprite_actual = len(self.sprites) - 1
                self.image = self.sprites[0]
            else:
                self.sprite_actual = int(tiempo_transcurrido / (self.velocidad_animacion * 1000))
                self.image = self.sprites[self.sprite_actual]

        if not bola_moviendo:
            teclas_pulsadas = pygame.key.get_pressed()
            if teclas_pulsadas[pygame.K_UP]:
                self.rect.y -= 5
            if teclas_pulsadas[pygame.K_DOWN]:
                self.rect.y += 5

            if teclas_pulsadas[pygame.K_SPACE] and not self.animando:
                self.animacion_en_curso = True
                self.animando = True
                self.tiempo_inicio_animacion = pygame.time.get_ticks()

# Definimos una clase para una bola en el juego
class Bola(pygame.sprite.Sprite):
    def __init__(self, jugador):
        pygame.sprite.Sprite.__init__(self)
        ancho = 30
        alto = 30
        self.jugador = jugador
        imagen = pygame.image.load("bola.png")
        imagen = pygame.transform.scale(imagen, (ancho, alto))
        imagen.set_colorkey((24, 144, 168))
        self.image = imagen
        self.rect = self.image.get_rect()
        self.posicion_inicial = self.rect.copy()
        self.rect.right = ANCHO - 150
        self.rect.bottom = ALTO / 2
        self.movimiento_izquierda = False

    def update(self):
        teclas_pulsadas = pygame.key.get_pressed()
        if teclas_pulsadas[pygame.K_SPACE]:
            self.velocidad_x = -5
        else:
            self.velocidad_x = 0

        if teclas_pulsadas[pygame.K_UP]:
            self.rect.y -= 5
        if teclas_pulsadas[pygame.K_DOWN]:
            self.rect.y += 5

        if teclas_pulsadas[pygame.K_SPACE]:
            self.movimiento_izquierda = True

        if self.movimiento_izquierda:
            self.rect.x -= 5
            if self.rect.left <= 0:
                self.movimiento_izquierda = False
                self.rect.right = ANCHO - 150
                self.rect.bottom = ALTO / 2

# Definimos una clase para un arco en el juego
class Arco(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        ancho = 50
        alto = 150
        imagen = pygame.image.load("arco.png")
        imagen = pygame.transform.scale(imagen, (ancho, alto))
        imagen.set_colorkey((41, 123, 16))
        self.image = imagen
        self.rect = self.image.get_rect()
        self.rect.centerx = ANCHO / 2 - 300
        self.rect.bottom = ALTO - 50
        self.velocidad = 2

    def update(self):
        self.rect.y += self.velocidad
        if self.rect.top <= 0 or self.rect.bottom >= ALTO:
            self.velocidad *= -1

# Crear dos instancias de Jugador y inicializarlas
jugador1 = Jugador()
jugador2 = Jugador()

# Crear una instancia de Bola y de Arco, y agregarlas al grupo de sprites
bola = Bola(jugador1)
arco = Arco()

# Agregar los jugadores, la bola y el arco al grupo de sprites
todos_los_sprites.add(jugador1, jugador2, bola, arco)

# Inicializamos las variables para los puntajes y para el control de turnos
puntaje_jugador1 = 0
puntaje_jugador2 = 0
turno_jugador1 = True  # Indica si es el turno del jugador 1
tiros_jugador1 = 0
tiros_jugador2 = 0
max_tiros = 7

def aplicar_var():
    # Generar un número aleatorio entre 1 y 100
    probabilidad = random.randint(1, 100)
    # Decidir si se aplica VAR con una probabilidad del 20%
    return probabilidad <= 50

def resta_circular(valor, resta, modulo):
    resultado = (valor - resta) % modulo
    return resultado if resultado >= 0 else resultado + modulo

def enviar_puntaje(puntaje):
    try:
        # Conectar al servidor de la Raspberry Pi Pico W
        server_address = ('192.168.219.226', 8080)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(server_address)
            mensaje = struct.pack('i', puntaje)
            sock.sendall(mensaje)
    except Exception as e:
        print(f"Error al enviar los puntajes: {e}")

corriendo = True
while corriendo:
    reloj.tick(FPS)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

    buffer.blit(fondo, (0, 0))
    
    # Verificar colisiones y actualizar puntajes y tiros
    if bola.rect.colliderect(arco.rect):
        if turno_jugador1:
            if bola.rect.colliderect(arco.rect):
                if aplicar_var():
                    enviar_puntaje(puntaje_jugador1)
                    puntaje_jugador1 = resta_circular(puntaje_jugador1, 3, 8)
                else:
                    if puntaje_jugador1 != 7:
                        puntaje_jugador1 += 1
            tiros_jugador1 += 1
        else:
            if bola.rect.colliderect(arco.rect):
                if aplicar_var():
                    enviar_puntaje(puntaje_jugador2)
                    puntaje_jugador2 = resta_circular(puntaje_jugador2, 3, 8)
                else:
                    if puntaje_jugador2 != 7:
                        puntaje_jugador2 += 1
            tiros_jugador2 += 1


        bola.rect = bola.posicion_inicial.copy()
        turno_jugador1 = not turno_jugador1  # Alternar turnos
        
    elif bola.rect.left <= 0:
        if turno_jugador1:
            tiros_jugador1 += 1
        else:
            tiros_jugador2 += 1
        bola.rect = bola.posicion_inicial.copy()
        turno_jugador1 = not turno_jugador1  # Alternar turnos

    # Verificar si ambos jugadores han terminado sus tiros
    if tiros_jugador1 >= max_tiros and tiros_jugador2 >= max_tiros:
        corriendo = False

    fuente = pygame.font.Font(None, 36)
    texto_puntaje1 = fuente.render("Jugador 1: " + str(puntaje_jugador1), True, (255, 255, 255))
    buffer.blit(texto_puntaje1, (10, 10))
    texto_puntaje2 = fuente.render("Jugador 2: " + str(puntaje_jugador2), True, (255, 255, 255))
    buffer.blit(texto_puntaje2, (10, 50))

    for sprite in todos_los_sprites:
        if isinstance(sprite, Jugador):
            if (turno_jugador1 and sprite == jugador1) or (not turno_jugador1 and sprite == jugador2):
                sprite.update(bola.movimiento_izquierda)
                if bola.movimiento_izquierda:
                    sprite.reiniciar_posicion()
        elif isinstance(sprite, Arco):
            sprite.update()
        else:
            sprite.update()
    
    todos_los_sprites.draw(buffer)
    pantalla.blit(buffer, (0, 0))
    pygame.display.flip()

pygame.quit()

# Mostrar el ganador
if puntaje_jugador1 > puntaje_jugador2:
    print("El ganador es el Jugador 1")
elif puntaje_jugador2 > puntaje_jugador1:
    print("El ganador es el Jugador 2")
else:
    print("Es un empate")
