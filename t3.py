import socket
import random
import time
class SocketTCP:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.IP="localhost"
        self.IP_destino = None
        self.PORT_destino = None
        self.seq_num = None
        self.buffer_size = 32 #header(16 bits) + data (16 bits)
        self.timeout = 2
        self.to_receive = 0
        self.buffered = ""

    @staticmethod
    def parse_segment(segment):
        # HEADER y Datos se ven asi:
        # Header primeros 2 bytes b"010..." Determina ACK, SYN y FIN respectivamente
        #b"...0000000000001" Numero de secuencia
        #Header total: b"0100000000000001"
        header = segment[0:16]
        data = segment[16:]
        dict = {}
        dict["ACK"] = header[0:1].decode()
        dict["SYN"] = header[1:2].decode()
        dict["FIN"] = header[2:3].decode()
        dict["SEQ"] = str(int(header[3:].decode()))
        dict["DATA"] = data.decode()
        
        return dict
    
    @staticmethod
    def create_segment(segment):
        ack = b"1" if int(segment["ACK"]) else b"0"
        syn = b"1" if int(segment["SYN"]) else b"0"
        fin = b"1" if int(segment["FIN"]) else b"0"
        seq = segment["SEQ"].zfill(13).encode()
        data = segment["DATA"].encode()
        return ack+syn+fin+seq+data
    @staticmethod
    def make_dict_seg(ack,syn,fin,seq,data):
        return {"ACK":ack,"SYN":syn,"FIN":fin,"SEQ":seq,"DATA":data}

    def bind(self,address):
        self.sock.bind(address)
    #lado cliente
    def connect(self,address):
        num = random.randint(0,100) #Secuencia inicial aleatoria entre 0 y 100
        syn = self.create_segment(self.make_dict_seg("0","1","0",str(num),""))
        self.sock.settimeout(self.timeout)
        while True:
            try:
                self.sock.sendto(syn,address) #Se envia una peticion tipo SYN
                data, new_address = self.sock.recvfrom(self.buffer_size) #Esperamos el SYN+ACK con seq=num+1
                parsed_seg = self.parse_segment(data)
                if parsed_seg["SYN"] =="1" and parsed_seg["ACK"] =="1" and parsed_seg["SEQ"] == str(num+1):
                    print("conectado al servidor")
                    break
            except socket.timeout:
                continue
        
        self.IP_destino,self.PORT_destino = new_address
        num +=2 #seq = num+2
        self.seq_num = num
        ack = self.create_segment(self.make_dict_seg("1","0","0",str(num),""))
        self.sock.sendto(ack,new_address) #Enviamos ACK con seq=num+2
    #lado servidor
    def accept(self):
        while True:
            data,client_address = self.sock.recvfrom(self.buffer_size)
            seg = self.parse_segment(data)
            if seg["SYN"] !="1":
                continue
            num = int(seg["SEQ"])
            new_sock = SocketTCP()
            new_sock.bind((self.IP,0))
            new_ip,new_port = new_sock.sock.getsockname()
            new_sock.IP_destino, new_sock.PORT_destino = client_address

            ack_syn = self.create_segment(self.make_dict_seg("1","1","0",str(num+1),""))
            while True:
                try:
                    new_sock.sock.sendto(ack_syn,client_address)
                    new_data,client_address = new_sock.sock.recvfrom(self.buffer_size)
                    new_seg = self.parse_segment(new_data)
                    if (new_seg["ACK"]=="1" or new_seg["SYN"]=="0") and new_seg["SEQ"]== str(num+2):
                        new_sock.seq_num= num+2
                        new_sock.sock.settimeout(None)
                        return new_sock, (new_ip,new_port)
                except socket.timeout:
                    continue
    def send_seg(self,seg_msg,L_msg):
        seq_exp = self.seq_num + L_msg
        while True:
            try:
                self.sock.sendto(seg_msg,(self.IP_destino,self.PORT_destino))
                data,_ = self.sock.recvfrom(self.buffer_size)
            except socket.timeout:
                continue
            pars_data = self.parse_segment(data)
            if pars_data["ACK"]== "1" and pars_data["SEQ"] == str(seq_exp):
                self.seq_num = seq_exp
                break

    #lado cliente
    def send(self,message):
        message_length = str(len(message))
        first_seg = self.create_segment(
            self.make_dict_seg("0","0","0",str(self.seq_num),message_length))
        self.sock.settimeout(self.timeout)
        self.send_seg(first_seg,len(message_length))
        for i in range(0,len(message),16):
            seg = self.create_segment(self.make_dict_seg("0","0","0",str(self.seq_num),message[i:i+16]))
            self.send_seg(seg,len(message[i:i+16]))

    def recv_seg(self):
        while True:
            data,_ = self.sock.recvfrom(self.buffer_size)
            pars_data = self.parse_segment(data)
            if str(self.seq_num) == pars_data["SEQ"]:
                self.seq_num += len(pars_data["DATA"])
                ack_response = self.create_segment(self.make_dict_seg("1","0","0",str(self.seq_num),""))
                self.sock.sendto(ack_response,(self.IP_destino,self.PORT_destino))
                return pars_data["DATA"]
            else:
                ack_response = self.create_segment(self.make_dict_seg("1","0","0",str(int(pars_data["SEQ"])+len(pars_data["DATA"])),""))
                self.sock.sendto(ack_response,(self.IP_destino,self.PORT_destino))                                


    #lado servidor
    def recv(self, buff_size):
        if self.to_receive == 0 and len(self.buffered) == 0:
            self.to_receive = int(self.recv_seg())
        t =min(self.to_receive,buff_size)
        while len(self.buffered) - t < 0:
            partial_msg = self.recv_seg()
            self.to_receive-= len(partial_msg)
            self.buffered+= partial_msg
        a = self.buffered[:buff_size]
        self.buffered = self.buffered[buff_size:]

        return a.encode()
    def close(self):
        self.sock.settimeout(self.timeout)
        fin = self.create_segment(self.make_dict_seg("0","0","1",str(self.seq_num),""))
        t = 0
        has_received= False
        #Host A envia al Host B el FIN con seq=z
        #Se envia 3 veces si no pasa nada se asume que se cerro
        while t<3:
            print("emviando fin ", t)
            try:
                self.sock.sendto(fin,(self.IP_destino,self.PORT_destino))
                data, _ = self.sock.recvfrom(self.buffer_size)
                pars_data = self.parse_segment(data)
                #Recibimos el FIN+ACK con seq =z+1
                if pars_data["ACK"]=="1" and pars_data["FIN"]=="1" and pars_data["SEQ"]==str(self.seq_num+1):
                    has_received = True
                    break
            except socket.timeout:
                t+=1
        if has_received:
            #Host A responde con un ACK y seq=z+2
            ack = self.create_segment(self.make_dict_seg("1","0","0",str(self.seq_num+2),""))  
            for i in range(3):
                print('enviando el ultimo ack', i+1)
                self.sock.sendto(ack,(self.IP_destino,self.PORT_destino))
                time.sleep(self.timeout)
        #Terminamos conexion
        self.sock.close()

    def recv_close(self):
        self.sock.settimeout(None)
        #Esperando el fin del host A
        while True:
            data,_ = self.sock.recvfrom(self.buffer_size)
            pars_data = self.parse_segment(data)
            if pars_data["FIN"] =="1" and pars_data["SEQ"] ==str(self.seq_num):
                break
        ack_fin = self.create_segment(self.make_dict_seg("1","0","1",str(self.seq_num+1),""))
        self.sock.settimeout(self.timeout)
        t = 0
        #enviamos el ACK + FIN y seq=z+1
        while t <3:
            print('enviando ack + fin ',t)
            try:
                self.sock.sendto(ack_fin,(self.IP_destino,self.PORT_destino))
                data,_ = self.sock.recvfrom(self.buffer_size)
                
            except socket.timeout:
                t+=1
                continue
            pars_data= self.parse_segment(data)
            #si recibimos el ACK y seq=z+2 terminamos conexion sino seguimos enviando el ACK
            if pars_data["ACK"]=="1" and pars_data["FIN"]=="0" and pars_data["SEQ"]==str(self.seq_num+2):
                break
        self.sock.close()
