import smbus
import socket
import time

i2c = smbus.SMBus(1) #canal 1 de raspy

#Bit SLEEP saca de modo Low power mode. Oscillator off ver referencia[2] en Mode Register 1 ( Pagina 14 )
i2c.write_byte_data (0x40, 0x00, 0x01)

print "a ver como quedo ??"
time.sleep(1)
nro_educiaa = 2
base = 7+ (nro_educiaa-1)*16

def lee_estados(nro_educiaa):
    leido = []
    global base
    for puerto in range(4): 
        leido.append(i2c.read_byte_data(0x40, base+4*puerto))
    return leido

for puerto in range(4): 
    i2c.write_byte_data(0x40, base +4*puerto, 0x01)
    i2c.write_byte_data(0x40, base+2+4*puerto, 0x00)
    leido = i2c.read_byte_data(0x40, base+4*puerto)
    print "pone a 1 salida", puerto, leido 
    print lee_estados(nro_educiaa)
    time.sleep(1)
    i2c.write_byte_data(0x40, base+4*puerto, 0x00)
    i2c.write_byte_data(0x40, base+2+4*puerto, 0x01)
    leido = i2c.read_byte_data(0x40, base+4*puerto)
    print "pone a 0 salida" , puerto, leido
    print lee_estados(nro_educiaa)

def conecta_server(host,port)
    global nro_educiaa
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.send(lee_estados()
        data = s.recv(1024)
        print('Received', repr(data))


