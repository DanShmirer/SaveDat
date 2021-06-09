from constants import *


class MyCB(cb.Callback):
    def on_batch_end(self,batch, logs=None):
        self.model.reset_states()

def scheduler(epoch, lr):
    return lr*0.8

LRS = tf.keras.callbacks.LearningRateScheduler(scheduler, verbose=0)

def split_XY(data):
    x, y = list(), list()
    for window_start in range(len(data)):
        past_end = window_start + TIMESTEPS_PAST
        future_end = past_end + TIMESTEPS_FUTURE
        if future_end > len(data):
            break
        # slicing the past and future parts of the window
        past, future = data[window_start:past_end, :], data[past_end:future_end, :]
        x.append(past)
        y.append(future)
    return np.array(x), np.array(y)

def split_XY_data(labels_list):
    #BEFORE
    #train_xy=[]
    #for df in l:
    #    x,y=split_XY(df[[fitted_lng,fitted_lat]].to_numpy())
    #    train_xy.append((x,y))
    #return train_xy
    train_xy=[]
    for label_i_dfs in labels_list:
        X, Y = [], []
        for df in label_i_dfs:
            x, y = split_XY(df[[fitted_lng,fitted_lat]].to_numpy())
            X.extend(x)
            Y.extend(y)
        train_xy.append((X,Y))
    return train_xy
        

def build_rnn_model(name):
    model = Sequential(name=name)
    model.add(InputLayer(input_shape=(TIMESTEPS_PAST,NUM_OF_FEATURES)))
    model.add(LSTM(LSTM_NUM ,return_sequences=True))
    model.add(LSTM(LSTM_NUM ,return_sequences=True))
    model.add(LSTM(LSTM_NUM))
    model.add(RepeatVector(TIMESTEPS_FUTURE)) # repeat the input n times
    model.add(TimeDistributed(Dense(NUM_OF_FEATURES)))# adding layer for each lstm cell output
    model.compile(optimizer=ADAM, loss=MSE)
    return model

def train_models(data):
    '''
    This function build and train a rnn model for each cluster
    @ param : data list of tupples (X,y)
    @return : lable,models,history tupple of lable and rnn model
    '''
    if not os.path.exists(MODELS_PATH):
        os.mkdir(MODELS_PATH)
    else:
        shutil.rmtree(MODELS_PATH)
        os.mkdir(MODELS_PATH)
    
        
    trained_models =[]
    x=[]
    y=[]
    for index, tup in list(enumerate(data)):
        model = build_rnn_model('cluser_' + str(index))
        history_model = model.fit(np.array(tup[0]), np.array(tup[1]),
                        epochs=EPOCHS,
                        batch_size=BATCH_SIZE,
                        verbose=1,
                        callbacks=[MyCB(), LRS],
                        shuffle=False,
                        validation_split=0.1 )
        
        trained_models.append((index,model,history_model))
        x.extend(tup[0])
        y.extend(tup[1])

    default_model = build_rnn_model('default_model')
    default_history = default_model.fit(np.array(x), np.array(y),
                    epochs=EPOCHS,
                    batch_size=BATCH_SIZE,
                    verbose=1,
                    callbacks=[MyCB(), LRS], 
                    shuffle=False,
                    validation_split=0.1)
                    
    trained_models.append((9, default_model , default_history))

    models_ds = []
    
    for label, model, history in trained_models:
        if float(np.min(history.history['loss'])) <= 10**(-3):
            models_ds.append((label, model, history))
            model.save(os.path.join(MODELS_PATH, model.name), save_format='tf')

    return models_ds


def fit_transform(frames):
    scaler = MinMaxScaler()
    frame = pd.concat(frames, ignore_index=True)
    scaler.fit(frame[[global_lng,global_lat]])
    for f in frames:
        f[[fitted_lng,fitted_lat]] = scaler.transform(f[[global_lng,global_lat]])
    RELEVANT_FEATURES.extend([fitted_lng,fitted_lat])
    return scaler, frames
    
    

def load_models():
    models_paths = os.listdir(MODELS_PATH)
    with open(os.path.join(MODELS_PATH, 'kmeans.pkl'), 'rb') as f:
        kmeans_model = pickle.load(f)
    
    models = []
    for file_name in models_paths:
        if file_name == 'kmeans.pkl':
            continue
        elif file_name == 'default_model':
            label = 9
            model = load_model(os.path.join(MODELS_PATH, file_name))
            models.append([label, model])
        else: # one of the clusters
            model = load_model(os.path.join(MODELS_PATH, file_name))
            label = re.search('(?<=_)\d+',model.name)[0]
            models.append([label, model])

    return kmeans_model, models
