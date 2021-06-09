from constants import *


class Client():
    def __init__(self, path):
        self.path = path
        self.id = re.search('(?<=_)\d+', path)[0]
        self.data = pd.read_csv(path)
        self.lat_ = self.data[global_lat]
        self.lon_ = self.data[global_lng]
        self.driving = True
        self.speed =  self.data[v_velocity]
        self.acc =  self.data[v_acceleration]
        self.labels = []
        self.success = True

    def connect_server(self):
        '''
        connect to socket via server
        @ return : client_sock - socket
        '''
        client_sock=None
        try:
            client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as e:
            print("CLient connection was failed")
            print (e)

        client_sock.connect((IP, PORT))
        return client_sock

    def send_data_to_server(self, client_sock, data):
        '''
        This function sends data to the server over the socket
        @ param : client_sock - socket
        @ param : data - string
        '''
        client_sock.sendall(data.encode(UTF8))

    def run_client(self):
        '''
        Clients main function
        '''
        try:
            client_sock = self.connect_server()
            speed_acc, coords = self.extract_speed_acc(0, 10), self.extract_coords(0, 10)
            #Send globaltime to the ui server
            self.send_data_to_server(client_sock, str(self.data[global_time].iloc[0]))
            # Wait for ok
            if client_sock.recv(1024).decode(UTF8) != 'ok':
                print("Communication failed: ", self.path)
                self.success = False
                return

            # Sending coordiantes to the server
            self.send_data_to_server(client_sock, coords)
            # Wait for ok
            if client_sock.recv(1024).decode(UTF8) != 'ok':
                print("Communication failed: ", self.path)
                self.success = False
                return

            # Sending speed & acceleration to the server
            self.send_data_to_server(client_sock, speed_acc)
            
            # Wait for ok
            if client_sock.recv(1024).decode(UTF8) != 'ok':
                print("Communication failed: ", self.path)
                self.success = False
                return
            indices_len = len(self.data.index)

            while True:
                label = client_sock.recv(1024).decode(UTF8)
                self.labels.append(label)
                # wait for server data request (X means : "Send me all the data from timesteps [X,X+10)
                index = client_sock.recv(1024).decode(UTF8)
                if str.isnumeric(index):
                    index = int(index)
                else:
                    self.success = False
                    break
                
                if index + 10 >= indices_len:
                    print("Client is Done!")
                    client_sock.sendall("done".encode(UTF8))
                    _ = client_sock.recv(1024)
                    break

                lat_lng = self.extract_coords(index, 10)
                self.send_data_to_server(client_sock, lat_lng)
                
        except Exception as e:
            print("exception from client")
            traceback.print_exc()
            print("Client exception at client: ", self.path)
        finally:
            self.save_data(self.success)
            print("client side socket has been closed.")
            client_sock.close()



    def save_data(self, success = True):
        main_l = []
        for l in self.labels:
            main_l.extend([l]*10)
        
        if success:
            if len(self.data) > len(main_l):
                diff = len(self.data) - len(main_l)
                main_l.extend([main_l[len(main_l)-1]]*diff)
            elif len(self.data) < len(main_l):
                while(len(self.data) != len(main_l)):
                    main_l.pop()
            
        else:
            if len(self.data) > len(main_l):
                diff = len(self.data) - len(main_l)
                main_l.extend([-1]*diff)
            elif len(self.data) < len(main_l):
                while(len(self.data) != len(main_l)):
                    main_l.pop()
                    
        self.data[LABEL] = main_l
        self.data[[v_ID,v_velocity,v_acceleration,global_time,global_lng,global_lat,LABEL]].to_csv(os.path.join(CLIENTS_FINAL_DATA_PATH,self.id))

    def extract_coords(self, start, chunk_size):
        lats = ""
        lons = ""
        for i in range(start, start + chunk_size):
            if i != (start + chunk_size-1):
                lats += str(self.lat_[i]) + ","
                lons += str(self.lon_[i]) + ","
            else:
                lats += str(self.lat_[i]) + ','
                lons += str(self.lon_[i])
        return lats + lons


    def extract_speed_acc(self, start, chunk_size):
        speed = ""
        acc = ""

        for i in range(start, start + chunk_size):
            if i != (start + chunk_size-1):
                speed += str(self.speed[i]) + ","
                acc += str(self.acc[i]) + ","
            else:
                speed += str(self.speed[i]) + ','
                acc += str(self.acc[i])
                
        return speed + acc


