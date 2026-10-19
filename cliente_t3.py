import socket
from t3 import SocketTCP
import sys

BUFFER_SIZE= 150
#cantidad de bytes maximos que se enviaran
BYTES_Q = 16

def main ():
    if len(sys.argv)!=3:
        print("error: No hay suficientes argumentos")
        sys.exit(1)

    IP = sys.argv[1]
    PORT = int(sys.argv[2])

    file = sys.stdin.buffer.read().decode()
    
    address = (IP,PORT)
    print("creando socket cliente...")
    client_socketTCP = SocketTCP()
    print("conectando a servidor...")
    client_socketTCP.connect(address)
    print("enviando archivo...")
    client_socketTCP.send(file)
    print("cerrando conexion...")
    client_socketTCP.close()
if __name__ == "__main__":
    main()
