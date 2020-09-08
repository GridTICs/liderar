import smbus
import socket
import time
import threading
import sys
from timeit import default_timer as timer
#from requests.exceptions import ConnectionError

i2c = smbus.SMBus(1) #canal 1 de raspy


#nro_educiaa = 2
slave0_addr = 0x40
slave1_addr = 0x41
#LED_ON, LED_OFF control registers (address 06h to 45h)
#LEDn_ON_L
#LEDn_ON_H
#LEDn_OFF_L
#LEDn_OFF_H
base = 0x07 #+ (nro_educiaa-1)*16 # LED0_ON_H = 07h
#host = "192.168.50.22"
#port = 8000
#NUM_EDU_CIAA = 1
stop_threads = False
config = "/home/pi/entornos.txt"


def lee_estados(nibble):
    #leido = "\r\nentradas digitales actuales ["
    global base
    byte = 0x00

    if (nibble >= 0 and nibble <= 3):
        slave_addr = slave0_addr
    elif (nibble >= 4 and nibble <= 7):
        slave_addr = slave1_addr
        nibble -= 4
    else:
        return -1

    for pin in range(4):
        #print(str(nibble)+" "+str(pin))
        byte = byte | i2c.read_byte_data(slave_addr, base + 16*nibble + 4*pin)
        byte = byte >> 1
    byte >> 1

    return byte

def a_uno (nibble, pin):

    if (nibble >= 0 and nibble <= 3):
        slave_addr = slave0_addr
    elif (nibble >= 4 and nibble <= 7):
        slave_addr = slave1_addr
        nibble -= 4
    else:
        return -1

    i2c.write_byte_data(slave_addr, base + 16*nibble + 4*pin, 0x10) #LEDn_ON_H[4] (LEDn full ON)
    i2c.write_byte_data(slave_addr, base+2+16*nibble + 4*pin, 0x00) #LEDn_OFF_H[4] (LEDn full OFF)


def a_cero (nibble, pin):

    if (nibble >= 0 and nibble <= 3):
        slave_addr = slave0_addr
    elif (nibble >= 4 and nibble <= 7):
        slave_addr = slave1_addr
        nibble -= 4
    else:
        return -1

    i2c.write_byte_data(slave_addr, base + 16*nibble + 4*pin, 0x00)
    i2c.write_byte_data(slave_addr, base+2+16*nibble + 4*pin, 0x10)

def cadena_estados (nibble):

    cadena = ""
    byte = lee_estados(nibble)

    for i in range(4):
        cadena += "GPIO_" + str(i) + ": " + str(byte & 0x01) + "   "
        byte = byte >> 1

    return cadena

def conecta_server(ip, port, nibble):
    global stop_threads

    print("Hilo: "+ ip +":"+ str(port) +" Nibble: "+str(nibble))

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.setblocking(False)
    except socket.error as e:
        print("No se pudo conectar a " + ip + ":" +str(port) )
        sys.exit()

    if (nibble >= 0 and nibble <= 3):
        slave_addr = slave0_addr
    elif (nibble >= 4 and nibble <= 7):
        slave_addr = slave1_addr
        #nibble -= 4
    else:
        print("Nibble fuera de rango" + str(nibble))
        sys.exit()

    anterior = timer()

    while True:
        try:
            comando = s.recv(1024).decode()
            #print (comando.decode())
            #print (len(comando))
            if len(comando) == 1:
                if comando == "s":
                    #estado = format(lee_estados(nibble),'04b')+ "\r\n"
                    estado = cadena_estados(nibble)
                    #s.send(estado.encode())
                elif comando == "1" or comando == "2" or comando == "3" or comando == "4":
                    pin = int(comando)-1
                    estado = 0x10 and i2c.read_byte_data(slave_addr, base + 16*nibble + 4*pin)
                    # print(estado)
                    if estado == 0:
                        a_uno(nibble, pin)
                    else:
                        a_cero(nibble, pin)
                    #estado = format(lee_estados(nibble),'04b')+ "\r"
                    #estado = cadena_estados(nibble)
                    #s.send(estado.encode())
            else:
                info = "\r\n Comando invalido\r\n"
                s.send(info.encode())

        except socket.error as e:
            #print(str(port))
            #print(timer())
            if stop_threads == True:
                break

        actual = timer()
        if (actual - anterior)> 0.2:
            info = "\33[2J\033[2;2H             Estímulos EDU-CIAA\n\n\r  "
            s.send(info.encode())
            estado = cadena_estados(nibble)
            s.send(estado.encode())
            info = "\r\n\n     ^^^         ^^^         ^^^         ^^^   "
            info += "\r\n  [Tecla 1]   [Tecla 2]   [Tecla 3]   [Tecla 4]"
            info += "\r\n\n           Dirección: 0x" + format(slave_addr, '02x') + "  Nibble: " + str(nibble)
            s.send(info.encode())
            anterior = actual

def main():
    global stop_threads, config

    #Bit SLEEP saca de modo Low power mode. Oscillator off ver referencia[2] en Mode Register 1 ( Pagina 14 )
    #MODE1[4] - Mode register 1 (address 00h) - Bit 4 SLEEP
    try:
        i2c.write_byte_data (slave0_addr, 0x00, 0x01)
    except IOError as e:
        print("0x" + format(slave0_addr, '02x') + ": PCA9685 no accesible por I2C")
    try:
        i2c.write_byte_data (slave1_addr, 0x00, 0x01)
    except IOError as e:
        print("0x" + format(slave1_addr, '02x') + ": PCA9685 no accesible por I2C")

    f = open(config, "r")
    #for num_hilo in range(NUM_EDU_CIAA):
    for linea in f:
        server=linea.splitlines()
        campo=server[0].split(":")
        ip=campo[0]
        port=int(campo[1])
        nibble=int(campo[2])
        #print(ip + ":"+ str(port))
        hilo = threading.Thread(target=conecta_server,
                                args=(ip,port,nibble,))
        hilo.start()
    f.close()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print ("Ctrl+C")
            stop_threads = True
            main_thread = threading.current_thread()
            for t in threading.enumerate():
               if t is main_thread:
                   continue
               t.join()
            #print ("Fin")
            sys.exit()

if __name__ == "__main__":
    #conecta_server(host,port)
    main()
