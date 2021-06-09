from constants import *

def extract_traj_samples():
    '''
    extract the first BEHAVIOR_SAMPLES from Train data
    @ return : samples list of dataframes
    '''
    samples = [] # list of dataframes
    for file in os.listdir(TRAIN_DATA_PATH):
        samples.append(pd.read_csv(os.path.join(TRAIN_DATA_PATH,file)).head(BEHAVIOR_SAMPLES)[[v_velocity, v_acceleration, v_ID]])
    
    return samples


def quantile(samples):
    '''
    extract behavior features from each trajectory
    @ param : samples list of Dataframes
    @ return : quantile_df Dataframe
    '''
    qs = [0.25, 0.5, 0.75]
    quantiles_df = pd.DataFrame(columns=[s25, s50, s75, a25, a50, a75])
    for df in samples:
        values = list(df[v_velocity].quantile(qs).append(df[v_acceleration].quantile(qs)))
        quantiles_df.loc[df[v_ID].unique()[0]] = values
    return quantiles_df.copy(deep=True)
   
def get_kmeans_model(quantiles_df, k):
    '''
    fit kmeans model to the data
    @ param : quantile_df Dataframe
    @ return : sklearn KMeans model
    '''
    kmeans_model = KMeans(k)
    kmeans_model.fit(quantiles_df)
    quantiles_df[LABEL] = kmeans_model.predict(quantiles_df)
    return (kmeans_model, quantiles_df.copy(deep=True))

def split_train_by_label(labels_df):
    '''
    seperate trajectories by kmeans lables
    @ param : labels_df searies kmeans lables
    @ return : clusters_dfs list of lists, each list represents the dataframe of the cluster
    '''
    clusters_dfs = []
    for i in range(K_CLUSTERS):
        clusters_dfs.append(list())
        
    for file in os.listdir(TRAIN_DATA_PATH):
        df = pd.read_csv(os.path.join(TRAIN_DATA_PATH, file))
        _id = df[v_ID].unique()[0]
        label = labels_df.loc[_id]
        clusters_dfs[label].append(df)
        
    return clusters_dfs


        

    
