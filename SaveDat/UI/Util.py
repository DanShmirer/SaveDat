

msg = 'ID : {0}<br>LABEL : {1}<br>SPEED : {2}'
colors = ['blue', 'rgb(250,237,84)','red','white']


V_ID = 'Vehicle_ID'
G_TIME = 'Global_Time'
LON = 'Lon'
LAT = 'Lat'
LABEL = 'Label'
SPEED = 'Speed'
ACCL = 'Acceleration'
GEN = 'Generated'
TRNSF = 'Transfered'

TEXT = 'Text'
SPEED = 'Speed'
COLOR = 'Color'

TOTAL_SO_FAR = 'Total_SF'
TRNSF_SO_FAR = 'Transfered_SF'
SAVED = 'Saved'

feats = [V_ID, LAT,LON,LABEL, SPEED, ACCL,GEN, TRNSF]

# ----------------------------------------------------------------------------------------
colors = ['blue', 'rgb(250,237,84)','white','red']
def format_msg(row_df):
    return msg.format(int(row_df[V_ID]), int(row_df[LABEL]), int(row_df[SPEED]))

def match_color(row_df):
    index = int(row_df[LABEL])
    return colors[index]

# ----------------------------------------------------------------------------------------

def build_text(df):
    return df.apply(format_msg, axis=1)
        
def match_colors(df):
    return df.apply(match_color, axis=1)
# ----------------------------------------------------------------------------------------





