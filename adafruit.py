import smbus
import socket
import time

i2c = smbus.SMBus(1) #canal 1 de raspy


nro_educiaa = 2
slave_addr = 0x40
base = 7+ (nro_educiaa-1)*16
host = "192.168.2.2"
port = 8000


#Bit SLEEP saca de modo Low power mode. Oscillator off ver referencia[2] en Mode Register 1 ( Pagina 14 )
i2c.write_byte_data (slave_addr, 0x00, 0x01)

def lee_estados(nro_educiaa):
    leido = "\r\nentradas digitales actuales ["
    global base
    for puerto in range(4): 
        leido = leido + str(i2c.read_byte_data(slave_addr, base+4*puerto)) + " "
    leido = leido[:-1] + "]\r\n?"
    return leido

def a_uno (puerto):
    i2c.write_byte_data(slave_addr, base +4*puerto, 0x01)
    i2c.write_byte_data(slave_addr, base+2+4*puerto, 0x00)

def a_cero (puerto):
    i2c.write_byte_data(slave_addr, base+4*puerto, 0x00)
    i2c.write_byte_data(slave_addr, base+2+4*puerto, 0x01)

#for puerto in range(4): 
#    i2c.write_byte_data(slave_addr, base +4*puerto, 0x01)
#    i2c.write_byte_data(slave_addr, base+2+4*puerto, 0x00)
#    leido = i2c.read_byte_data(slave_addr, base+4*puerto)
#    print "pone a 1 salida", puerto, leido 
#    print lee_estados(nro_educiaa)
#    time.sleep(1)
#    i2c.write_byte_data(slave_addr, base+4*puerto, 0x00)
#    i2c.write_byte_data(slave_addr, base+2+4*puerto, 0x01)
#    leido = i2c.read_byte_data(slave_addr, base+4*puerto)
#    print "pone a 0 salida" , puerto, leido
#    print lee_estados(nro_educiaa)

def conecta_server(host,port):
    #global nro_educiaa
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send (lee_estados(nro_educiaa))
    while True:
        comando = s.recv(1024)
        print (comando)
        print len(comando)
        if len(comando) == 1:
            if comando == "s":
                respuesta = lee_estados(nro_educiaa)
                s.send(lee_estados(nro_educiaa))
            elif comando == "0" or comando == "1" or comando == "2" or comando == "3":    
                puerto = int(comando)
                estado = i2c.read_byte_data(slave_addr, base+4*puerto)
                if estado == 0:
                    a_uno(puerto)
                    s.send(lee_estados(nro_educiaa))

                else:
                    a_cero(puerto)
                    s.send(lee_estados(nro_educiaa))
        else:
            s.send("\r\n comando invalido\r\n")
print (host, port)

if __name__ == "__main__":
    conecta_server(host,port)

