from constants import *
from CH_data_transmitor import *


class ClientHandler:

    def __init__(self, client_socket, rms, local_addr, scaler, _id):
        self._id = _id
        self.client_socket = client_socket
        self.points = {}
        self.road_manager = rms
        self.behavior_vec = ()
        self.behavior = 9
        self.ip = str(local_addr[0])
        self.port = str(local_addr[1])
        self.scaler = scaler
        self.transformer = Transformer.from_crs(NAD83, WGS84)
        self.transmitor = CH_Data_Transmittor(_id)
        
        #self.ui_thread = threading.Thread(target = handle_ui)

    def handle(self):
        FIRST_STEP = 30
        STEP_SIZE = 20
        if FIRST_STEP%10 != 0 or STEP_SIZE%10 != 0:
            assert("FIRST_STEP & STEP_SIZE MUST BE MULTIPLICATION OF 10")
        try:
            
            #getting first time value
            first_time_step = self.client_socket.recv(1024).decode(UTF8)
            self.client_socket.sendall("ok".encode(UTF8))
            self.transmitor.set_time(first_time_step)
            #getting 10 lats, 10 lngs (NAD 83)
            client_coords = self.client_socket.recv(1024).decode(UTF8).split(',')
            self.client_socket.sendall("ok".encode(UTF8))
            #getting 10 speeds, 10 accelerations
            movement = self.client_socket.recv(1024).decode(UTF8).split(',')
            self.client_socket.sendall("ok".encode(UTF8))

            client_lats = list(map(float, client_coords[:10]))
            client_lngs = list(map(float, client_coords[10:]))
            #Scaling
            client_coords_map = {'lngs': client_lngs,
                                 'lats': client_lats
                          }
            # transform(scaling coordinates) from map with two array to 10x2 matrix
            # NAD83 SCALED TO range(0,1)
            client_real_points = self.scaler.transform(pd.DataFrame.from_dict(data=client_coords_map))

            #
            # CLIENT BEHAVIOR ANALYSIS
            #
            # Ask for the right manager TODO: PROJECT COORDINATES TO WGS84
            self.road_manager = self.road_manager.get_manager(Point(client_lngs[0],client_lats[0]))
            
            ## CUT START
            speeds = list(map(float, movement[:10]))
            accls = list(map(float, movement[10:]))

            speeds_q = np.quantile(speeds, QS)
            accls_q = np.quantile(accls, QS)
            values = np.concatenate((speeds_q, accls_q))

            self.behavior = self.road_manager.behaviors_model.predict(values.reshape((1,-1)))[0]
            
            ## CUT END

            while True:
                self.client_socket.sendall(str(self.behavior).encode(UTF8))
                time.sleep(0.1)
                # asking for client coordinats, starting from timestep 50
                self.client_socket.sendall(str(FIRST_STEP).encode(UTF8))
                # server_predicted_points are scaled between 0 to 1 (NAD83)
                server_predicted_points, all_server_predicted_points = self.road_manager.predict_next(client_real_points,self.behavior,FIRST_STEP)

                server_lngs = [x_y[0] for x_y in server_predicted_points]
                server_lats = [x_y[1] for x_y in server_predicted_points]
                server_predicted_coords_map = {'lngs': server_lngs,
                                                'lats': server_lats
                              }
                # back to NAD83 10x2 matrix 
                server_predicted_coords = self.scaler.inverse_transform(pd.DataFrame.from_dict(data=server_predicted_coords_map))
                FIRST_STEP = FIRST_STEP + STEP_SIZE

                # GET client's coordinats (NAD83)
                client_coords = self.client_socket.recv(1024).decode(UTF8)

                if client_coords == "done":
                    print("@@@ ClientHandler got 'done' from client @@@")
                    self.client_socket.sendall("bye".encode(UTF8))
                    self.transmitor.send_data()
                    break   

                
                client_coords = client_coords.split(',') 
                client_lats = list(map(float, client_coords[:10]))
                client_lngs = list(map(float, client_coords[10:]))

                client_real_points_mat = [[lng,lat] for lng,lat in zip(client_lngs,client_lats)]


                #Scaling
                client_coords_map = {'lngs': client_lngs,
                                 'lats': client_lats
                          }
            # transform(scaling coordinates) from map with two array to 10x2 matrix
            # NAD83 SCALED TO range(0,1)
                client_real_points = self.scaler.transform(pd.DataFrame.from_dict(data=client_coords_map))

                #TODO: CHANGE FIRST_STEP & STEP_SIZE FOT BEST VALUES
                #TODO: TEST MULTIPLE CLIENTS 

                # from NAD83 TO WGS84
                client_real_points_proj = self.project_coords(client_real_points_mat)
                server_predicted_coords = self.project_coords(server_predicted_coords)

                # checking if the client coordinats overlap the model
                if not self.are_overlap(client_real_points_proj, server_predicted_coords):
                    if self.behavior == 9: # client managed by default manager
                        self.client_socket.sendall(ERROR_SERVICE.encode(UTF8))
                        print("#### Can't provide Service to this client ####")
                        break
                    self.behavior = 9
                    
                # Sending data to UI
                self.transmitor.set_behavior(label=self.behavior)
                all_server_lngs = [x_y[0] for x_y in all_server_predicted_points]
                all_server_lats = [x_y[1] for x_y in all_server_predicted_points]
                all_server_predicted_coords_map = {'lngs': all_server_lngs,
                                                'lats': all_server_lats
                              }
                # back to NAD83 10x2 matrix 
                all_server_predicted_coords = self.scaler.inverse_transform(pd.DataFrame.from_dict(data=all_server_predicted_coords_map))
                all_server_predicted_coords = self.project_coords(all_server_predicted_coords)
                ui_lngs = [x_y[0] for x_y in all_server_predicted_coords]
                ui_lats = [x_y[1] for x_y in all_server_predicted_coords]
                self.transmitor.set_data(lats=ui_lats, lngs=ui_lngs)
            
        except Exception as e:
            print("Client Exception at client: ", self._id)
            print(e.with_traceback())
            raise e
        finally:
            self.client_socket.close()

    def are_overlap(self, points, predict_points):
        #swaping lat and lng for haversine
        pts1 = [(lat,lng) for lng,lat in points]
        pts2 = [(lat,lng) for lng,lat in predict_points]
        dis = []
        for p1,p2 in zip(pts1, pts2):
            dis.append(haversine(p1, p2,unit=Unit.METERS))
        if np.median(dis) <= 20:
            return True
        return False

    def handle_ui(self):

        pass
   
    def project_coords(self, coords):
        lngs = [x_y[0] for x_y in coords]
        lats = [x_y[1] for x_y in coords]
        coordinates_list = self.transformer.transform(lngs, lats)
        return [[lng,lat] for lng, lat in zip(coordinates_list[1],coordinates_list[0])]
        
