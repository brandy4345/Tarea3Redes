import socket
from t3 import SocketTCP

IP_VM ="localhost"
PORT= 8000
BUFFER_SIZE= 150
#cantidad de bytes maximos que se enviaran
BYTES_Q = 16

def main ():
    #ruta= input("Ingrese ruta de archivo: ")
    ruta = "test.txt"
    with open(ruta,"rb") as f:
        file = f.read().decode()
    address = (IP_VM,PORT)
    client_socketTCP = SocketTCP()
    client_socketTCP.connect(address)
    client_socketTCP.send(file)
    '''
    sock= socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    address = (IP_VM,PORT)
    for i in range(0,len(file),BYTES_Q):
        seg = {
            "ACK": "0",
            "SYN": "0",
            "FIN": "0",
            "SEQ": "0000000000001",
            "DATA": file[i:i+BYTES_Q]
        }
        sock.sendto(socketTCP.create_segment(seg),address)
        data,server_address = sock.recvfrom(BUFFER_SIZE)
        print("servidor: ", data.decode())
    sock.close()
    '''
if __name__ == "__main__":
    main()