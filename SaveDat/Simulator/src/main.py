from constants import *
from preprocessing_module import *
from deep_learnning_module import *
from Managers import *
from Client import *
from server import *

##########################################################################
def preprocessing_init():
    frames = load_data()
    print("------>  load_data accomplished !!  ")
    scaler, frames = fit_transform(frames)
    split_by_vehcile_id(frames)
    print("------>  split_by_vehcile_id accomplished !!  ")
    train_test_split()
    print("------>  train_test_split accomplished !!  \n")

    # behaviors analysis:
    samples = extract_traj_samples()
    print("------>  extract_traj_samples accomplished !!  ")
    quantiles_df = quantile(samples)
    print("------>  quantile accomplished !!  ")
    kmeans_model, quantiles_df = get_kmeans_model(quantiles_df, K_CLUSTERS)
    print("------>  get_kmeans_model accomplished !!  ")
    clusters = split_train_by_label(quantiles_df[LABEL]) 
    print("------>  split_train_by_label accomplished !!  \n")

    # rnn construction
    split_xy = split_XY_data(clusters) 
    print("------>  split_XY_data accomplished !!  ")


    del frames
    del quantiles_df 
    del clusters
    del samples

    trained_models = train_models(split_xy)
    print("------>  train_models accomplished !!  ")
    with open(os.path.join(MODELS_PATH,'kmeans.pkl'), 'wb') as f:
        pickle.dump(kmeans_model,f)

    del split_xy
       # MVC model construction
    rnns_map = {}
    for l,m,_ in trained_models:
        rnns_map[l] = m
    return scaler, kmeans_model, rnns_map

def load_preprocessing_models():
    kmeans_model, trained_models = load_models()
    frames = load_data()
    #print("------>  load_data accomplished !!  ")
    scaler, _ = fit_transform(frames)
    del frames
    rnns_map = {}
    for l,m in trained_models:
        rnns_map[l] = m
    return scaler, kmeans_model, rnns_map
##########################################################################3







print("------  running main  ------ ")
mode_of_operation = input("For training models Enter 1\nFor loading models enter 2\n")
if int(mode_of_operation) == 1:
    ## preprocessing:
    scaler, kmeans_model, rnns_map = preprocessing_init()
else:
    scaler, kmeans_model, rnns_map = load_preprocessing_models()
    


rm = RoadManager(POLY_101,kmeans_model,rnns_map)
rms = RoadsManager([rm])
server = Server(IP, PORT, rms, scaler)

try:
    server_thread = threading.Thread(target = server.start)
    server_thread.start()
    clients_threads = list()
    train_files = list(os.listdir(TEST_DATA_PATH))
    random.shuffle(train_files)
    for train_file in train_files:
        client = Client(os.path.join(TEST_DATA_PATH, train_file))
        client_thread = threading.Thread(target = client.run_client)
        clients_threads.append(client_thread)

    while(len(clients_threads) > 1):
        th1 = clients_threads.pop()
        th1.start()
        th2 = clients_threads.pop()
        th2.start()
        th1.join()
        th2.join()
    
    server_thread.join()
    print("Main.py is Finished")
except Exception as e:
    print("Main.py Except block")
    print(e)
    traceback.print_exc()
