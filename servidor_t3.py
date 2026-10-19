import socket
from t3 import SocketTCP

IP_VM ="localhost"
PORT= 8000
BUFFER_SIZE= 15

def main ():
    address = (IP_VM,PORT)
    server_socketTCP = SocketTCP()
    server_socketTCP.bind(address)
    connection_socketTCP, new_address = server_socketTCP.accept()
    msg = connection_socketTCP.recv(BUFFER_SIZE)
    print("recibido:", msg)
    '''
    sock= socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    address = (IP_VM,PORT)
    sock.bind(address)    
    while True:
        data,client_address = sock.recvfrom(BUFFER_SIZE)
        parsed_data = socketTCP.parse_segment(data)
        print("cliente: ",parsed_data)
        response ="holii"
        sock.sendto(response.encode(),client_address)
    '''

if __name__ == "__main__":
    main()