from constants import *
from ClientHandler import *

class Server:
    def __init__(self, ip, port, rms, scaler):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # ipV4, TCP
        self.stop_server_ = False
        self.executor = ThreadPoolExecutor(max_workers=None)
        self.client_handlers = []
        self.roads_manager = rms
        self.scaler = scaler
        self.clients_counter = 0

    def start(self):
        '''
        main server loop
        '''
        if os.path.exists(CONCLUDED_DATA_PATH):
            shutil.rmtree(CONCLUDED_DATA_PATH)
        os.mkdir(CONCLUDED_DATA_PATH)

        if os.path.exists(CLIENTS_FINAL_DATA_PATH):
            shutil.rmtree(CLIENTS_FINAL_DATA_PATH)
        os.mkdir(CLIENTS_FINAL_DATA_PATH)

        
        
        self.sock.bind((self.ip, self.port))
        self.sock.listen(BACKLOG)
        self.sock.settimeout(SERVER_TIME_OUT_IN_SECONDS)
        print('SERVER IS UP... \nWAITING FOR CONNECTIONS')
        #network_log.info("Server is up.")
        try:
            while not self.stop_server_:
                client_socket, client_info = self.sock.accept()
                print("New client was submited: " + str(client_info[1]))
                ch = ClientHandler(client_socket, self.roads_manager, client_info ,self.scaler, self.clients_counter)
                self.executor.submit(ch.handle)
                self.clients_counter += 1
        except socket.timeout:
            print(f"Server is Closing after {self.clients_counter} clients done --->",socket.timeout)
        except Exception as e:
            print("Server raise exception:")
            raise e
        finally:
            self.stop_server()


    def stop_server(self):
        self.stop_server_ = True
        self.executor.shutdown(wait=False)
        self.sock.close()
