import network
import socket
import machine
import struct
import time

# Conéctate a la red Wi-Fi
ssid = 'Steven'
password = 'ocpv4938'
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Espera a que la conexión se establezca
while not wlan.isconnected():
    machine.idle()

print('Conexión establecida con la red:', wlan.ifconfig())

# Configura el socket del servidor
addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
server = socket.socket()
server.bind(addr)
server.listen(1)

print('Servidor escuchando en', addr)

# Configurar pines GPIO
pin15 = machine.Pin(15, machine.Pin.OUT)
pin14 = machine.Pin(14, machine.Pin.OUT)
pin13 = machine.Pin(13, machine.Pin.OUT)
pin12 = machine.Pin(12, machine.Pin.OUT)

def convertir_a_binario(valor):
    binario = [0, 0, 0]
    for i in range(3):
        binario[2 - i] = (valor >> i) & 1
    return binario

def establecer_pines(valor):
    binario = convertir_a_binario(valor)
    pin15.value(binario[2])
    pin14.value(binario[1])
    pin13.value(binario[0])

while True:
    cl, addr = server.accept()
    print('Conexión desde', addr)
    cl_file = cl.makefile('rwb', 0)
    while True:
        data = cl_file.read(4)  # Leer 4 bytes para el entero
        if not data:
            break
        # Desempaquetar los datos
        puntaje = struct.unpack('i', data)[0]
        print('Puntaje recibido:', puntaje)
        establecer_pines(puntaje)
        if puntaje:
            pin12.value(1)
            time.sleep(2)
            pin12.value(0)
    cl.close()
