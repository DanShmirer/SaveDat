from constants import *
from behavior_moudle import *

def load_data():
    '''
        Loading the csvs to list of dataframes
        @return : frames List[pd.DataFrame]
    '''
    frames=[]
    for file in os.listdir(DATA_PATH): 
        if not os.path.isdir(os.path.join(DATA_PATH, file)):
            frames.append(pd.read_csv(os.path.join(DATA_PATH, file))[RELEVANT_FEATURES])
    return frames

def split_by_vehcile_id(frames):
    '''
        Split each dataframe by vehcile id and store in csv format
        @param : frames list[pd.DataFrame]
    '''
    if not os.path.exists(TRAJ_DATA_PATH):
        os.mkdir(TRAJ_DATA_PATH)
    else:
        shutil.rmtree(TRAJ_DATA_PATH)
        os.mkdir(TRAJ_DATA_PATH)
    new_id = 0
    group = 'a'
    # for each 15 min data
    for frame in frames:
        # for each id
        for v_id, df in frame.groupby(v_ID):
            temp_df = df[RELEVANT_FEATURES].copy()
            temp_df[v_ID] = new_id
            temp_df.to_csv(os.path.join(TRAJ_DATA_PATH ,group + '_' + str(new_id) + '.csv'))
            new_id += 1
        # get next letter
        group  = chr(ord(group) + 1)



def train_test_split():
    '''
        Split each dataframe to train and test by TRAIN_SIZE
        @param : frames list[pd.DataFrame]
        @return : (train, test) List, List

    '''
    if not os.path.exists(TRAIN_DATA_PATH):
        os.mkdir(TRAIN_DATA_PATH)
        os.mkdir(TEST_DATA_PATH)

    else:
        shutil.rmtree(TRAIN_DATA_PATH)
        shutil.rmtree(TEST_DATA_PATH)
        os.mkdir(TRAIN_DATA_PATH)
        os.mkdir(TEST_DATA_PATH)

    files_list = os.listdir(TRAJ_DATA_PATH)

    for prefix in PREFIXES:
        files = list(filter(lambda name: prefix in name, files_list))
        len_files = len(files)
        index = 0
        np.random.shuffle(files)
        for file in files:
            if index/len_files < TRAIN_SIZE:
                shutil.move(os.path.join(TRAJ_DATA_PATH, file), os.path.join(TRAIN_DATA_PATH, file ))
            else:
                shutil.move(os.path.join(TRAJ_DATA_PATH, file), os.path.join(TEST_DATA_PATH, file ))
            index += 1
    shutil.rmtree(TRAJ_DATA_PATH)

