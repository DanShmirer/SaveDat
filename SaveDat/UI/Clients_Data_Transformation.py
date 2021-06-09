# consts and imports
import pandas as pd
import os
import sys

from pyproj import Transformer
transformer = Transformer.from_crs(2229,4326)

colors = ['blue', 'rgb(250,237,84)','red','white']
msg = 'ID : {0}<br>LABEL : {1}<br>SPEED : {2}'

GLOBAL_X = 'Global_X'
GLOBAL_Y = 'Global_Y'
V_VEL = 'v_Vel'
V_ACC = 'v_Acc'
CPS_ERR = 'cannot provide service'
CSV_EXT = '.csv'

V_ID = "Vehicle_ID"
LATS = "Latitudes"
LNGS = "Longitudes"
LABEL = "Label"
SPEED = "Speed"
ACCL = "Acceleration"
G_TIME = 'Global_Time'
UNNAMED = 'Unnamed: 0'

COLOR = 'Color'
TEXT = 'Text'

OUTPUT_FILE = 'Concluded_Data.csv'
CURR_WD = os.getcwd()
OUTPUT_PATH = os.path.join(CURR_WD,OUTPUT_FILE)

cols = [LATS, LNGS, LABEL, G_TIME]
cols_dict = {GLOBAL_X : LNGS,GLOBAL_Y : LATS,V_VEL : SPEED,V_ACC : ACCL}

# add csv extentions
def add_extentions(path): 
    filenames = os.listdir(path)
    for filename in filenames:
        if len(filename)>4 and filename[-4:]==CSV_EXT:
            continue
        new_filename = filename + CSV_EXT
        filepath = os.path.join(path,filename)
        new_filepath = os.path.join(path, new_filename)
        os.rename(filepath, new_filepath)
        
def del_extentions(path): 
    filenames = os.listdir(path)
    for filename in filenames:
        if filename[-4:]==CSV_EXT:
            new_filename = filename[:-4]
            filepath = os.path.join(path,filename)
            new_filepath = os.path.join(path, new_filename)
            os.rename(filepath, new_filepath)
            
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------

# join all dataframes to one
def unite_dfs(src_path):
    dfs = []
    for filename in os.listdir(src_path):
        fullpath = os.path.join(src_path, filename)
        df = pd.read_csv(fullpath)
        if UNNAMED in list(df.columns):
            df = df.drop(UNNAMED, axis=1)
        dfs.append(df)
    mother_df = dfs[0]
    for i in range(1,len(dfs)):
        mother_df = mother_df.append(dfs[i])
    return mother_df
    
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------

# rename columns
def rename_columns(df):
    if UNNAMED in df.columns:
        df.drop([UNNAMED], axis=1, inplace=True)
    df.rename(columns=cols_dict, inplace=True)
    return df
    
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------

# transform NAD38 to WGS84
def t_coord(row_df):
    return transformer.transform(xx=row_df[LNGS], yy=row_df[LATS])
def t_coords(df):
    return df.apply(t_coord, axis=1)
def fix_coords(df):
    if UNNAMED in df.columns:
        df.drop([UNNAMED], inplace=True)
    lats_lngs = t_coords(df)
    lats = []
    lngs = []
    for lat_lng in lats_lngs:
        lats.append(lat_lng[0])
        lngs.append(lat_lng[1])
    df[LATS] = lats
    df[LNGS] = lngs
    return df
    
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------

# Fix labels: 0- label 0, 1- label 1, 2- defaultive label, 3- mismatch label
def t_label(row_df):
    if row_df[LABEL]==CPS_ERR:
        return 3
    curr = int(row_df[LABEL])
    if curr==-1: return 3
    elif curr==9: return 2
    return int(row_df[LABEL])
def t_labels(df):
    return df.apply(t_label, axis=1)
def fix_labels(df):
    if UNNAMED in df.columns: 
        df.drop([UNNAMED],axis=1)
    df[LABEL] = t_labels(df)
    return df
    
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------

# build text on mapbox hover
def format_msg(row_df):
    return msg.format(int(row_df[V_ID]), int(row_df[LABEL]), int(row_df[SPEED]))
def build_text(df):
    return df.apply(format_msg, axis=1)
    
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------

# match color to mapbox markers
def match_color(row_df):
    index = int(row_df[LABEL])
    return colors[index]
def match_colors(df):
    return df.apply(match_color, axis=1)
    
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------

# add UI data
def add_UI_data(df,dst):
    if UNNAMED in df.columns:
        df.drop([UNNAMED], axis=1)  
    df[COLOR] = match_colors(df)
    df[TEXT] = build_text(df)
    df.to_csv(dst, index=False)
    
def fix_UI(src,dst):
    df = add_extentions(src)
    df = unite_dfs(src)
    df = rename_columns(df)
    df = fix_coords(df)
    df = fix_labels(df)
    add_UI_data(df, dst)
    
if len(sys.argv) < 2:
    print('Source path must be provided: "Client Data" directory, generated by the simulator')
else: 
    print('GIVEN: ' + sys.argv[1])
    print('Running...')
    fix_UI(sys.argv[1], OUTPUT_PATH)
    print('Done.')