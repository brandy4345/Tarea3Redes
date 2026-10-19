from t3 import SocketTCP

IP_VM ="localhost"
PORT= 8000
BUFFER_SIZE= 150

def main ():
    print("empezando...")
    address = (IP_VM,PORT)
    print("creando socket...")
    server_socketTCP = SocketTCP()
    server_socketTCP.bind(address)
    print("esperando clientes...")
    connection_socketTCP, new_address = server_socketTCP.accept()
    print("recibiendo mensajes...")
    msg = connection_socketTCP.recv(BUFFER_SIZE)
    print("recibido:", msg)
    print("cerrando conexion...")
    connection_socketTCP.recv_close()

if __name__ == "__main__":
    main()
