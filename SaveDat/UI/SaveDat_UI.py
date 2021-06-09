
        #####################################################################################
        #                                                                                   #
        #      DASH Application - SaveDat- ML Based GPS Data Comoression Dashboard          #
        #           Submitted by: Shir Boxer, Dan Shmirer, Guy Cohen,                       #
        #                     Itai Blumenkrantz & Mike Lasry                                #
        #                      Supervisor: Dr.Shay Horovitz                                 #   
        #                                                                       Group #203  #
        #####################################################################################

# ----------------------- Imports -------------------------------------------------------------------------------------
import dash 
import os
import plotly.graph_objs as go
import pandas as pd
import dash_daq as daq
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
from collections import deque

import Util

# ---------------------- Constants ------------------------------------------------------------------------------------
DAEFAULT_GRAPH = go.Figure(data=[],layout=go.Layout(template='plotly_dark'))
mapbox_access_token = 'pk.eyJ1IjoibWlrZWxhc3J5MTIzIiwiYSI6ImNrb2g4eGVvNzA4cWgyd3JtczVub2QycnEifQ.haZyneucrLcDEMwrdmYjEQ'

CURR_WD = os.getcwd()
DATA = 'data'
DB_NAME = 'Concluded_Database.csv'
DATA_PATH =os.path.join(CURR_WD, DATA, DB_NAME)

COLMAN_LOGO = 'colman_logo.png'
ASSETS = 'assets'
LOGO_PATH = os.path.join(CURR_WD, ASSETS, COLMAN_LOGO)

CA_FWY_TITLE = "101 FWY, California Projection"
TEAL_COLOR = 'rgb(17,157,255)'
SWAMP_COLOR = 'rgb(64,128,128)'
PURPLE_COLOR = 'rgb(163,73,164)'

CR = 5
MIN_PARALLEL_PTS = 1
main_graph_interval = 1
comparison_interval = 1

y_min = 500
y_max = -500

SECOND = 1000
QUEUE_LEN = 100
GARPH_HEIGHT = 500
COORD_SIZE_BYTES = 2*4 # Representing COORD. takes -two- floats -32bit- each (4Bytes)
LON_CENTER = -118.362516833
LAT_CENTER = 34.1373230852

CARD_STYLE = dict(textAlign='center', color='white', fontSize=14)
CARD_HEADER_STYLE_S = dict(fontSize='11px',textDecoration='underline',textAlign='center')
CARD_HEADER_STYLE_L = dict(fontSize='16px',textDecoration='underline',textAlign='center')
ALIGN_CENTER = dict(textAlign='center')
GRAPH_TITLE_FONT_L = dict(size=36, color='rgb(115,115,115)')
GRAPH_TITLE_FONT_S = dict(size=26, color='rgb(115,115,115)')
GRAPH_TITLE_FONT_XS = dict(size=20, color='rgb(115,115,115)')

CARD_CLASS = 'card container text-white border-white'
main_graph_style = {'padding-bottom':'2px','padding-left':'2px','height':'60vh',}

LABELS_VOLUME = 'LBLV'
BY_LABEL_STATUS = 'BLBL'

V_ID = 'Vehicle_ID'
G_TIME = 'Global_Time'
LON = 'Longitudes'
LAT = 'Latitudes'
LABEL = 'Label'
SPEED = 'Speed'
ACCL = 'Acceleration'
GEN = 'Generated'
TRNSF = 'Transfered'
UNNAMED = 'Unnamed: 0'

TEXT = 'Text'
SPEED = 'Speed'
COLOR = 'Color'

TOTAL_SO_FAR = 'Total_SF'
TRNSF_SO_FAR = 'Transfered_SF'
SAVED = 'Saved'

LABEL_0 = '0'
LABEL_1 = '1'
LABEL_2 = '2'
LABEL_3 = '3'
#LABEL_4 = '4'

# ----------------------- Database Class --------------------------------
class SaveDatDataBase:
    def __init__(self, path):
        self.data, self.labels_count = self.build_data(path)
        self.time_steps = sorted(list(self.data.keys()))
        
        self.ptr = -1
        print('[DATABASE] Init')
    
    def get_next(self):
        self.ptr+=1
        return self.data[self.time_steps[self.ptr%len(self.time_steps)]] 
        
    def build_data(self, path):
        print('[DATABASE] Building data...' )
        df = pd.read_csv(path)
        if UNNAMED in df.columns:
            df.drop(UNNAMED, axis=1)
        
        data = {}
        idl_map = {}
        labels_counts = []
        
        
        for timestep, sub_df in sorted(df.groupby(by=G_TIME)):
            counts = [0,0,0,0]
            if len(sub_df)>= MIN_PARALLEL_PTS:
                data[timestep] = sub_df
                
                # create labels count tracking
                for lbl in sorted(pd.unique(sub_df[LABEL])): 
                    dff = sub_df[sub_df[LABEL]==lbl]
                
                    for id_ in pd.unique(dff[V_ID]):
                        idl_map[id_] = lbl
                        
                for vid in idl_map:
                    l = idl_map[vid]
                    if   l==0: counts[0] += 1
                    elif l==1: counts[1] += 1
                    elif l==2: counts[2] += 1
                    elif l==3: counts[3] += 1
                    
                labels_counts.append(counts)
                
        return data, labels_counts
    
    def get_lcounts(self):
        return self.labels_count[self.ptr%len(self.labels_count)]
    
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
db = SaveDatDataBase(DATA_PATH)

total_generated = 0
total_transmitted = 0
total_saved = 0

mismatch_ids = []
piechart_info = [8,17,3,1]

all_saved_dq = deque(maxlen=QUEUE_LEN)
saved_mb_dq = deque(maxlen=QUEUE_LEN)

generated_dq = deque(maxlen=QUEUE_LEN)
transfered_dq = deque(maxlen=QUEUE_LEN)

l0_dq = deque(maxlen=QUEUE_LEN)
l1_dq = deque(maxlen=QUEUE_LEN)
l2_dq = deque(maxlen=QUEUE_LEN)
l3_dq = deque(maxlen=QUEUE_LEN)

print('[APPLICATION] Init')
print('-'*50)
# Initialize DASH application
app = dash.Dash(name=__name__,external_stylesheets=[dbc.themes.DARKLY])

# Set application layout
app.layout = html.Div(children=[
       
        # Mapbox interval
        dcc.Interval(
            id='main_graph_interval',
            interval = SECOND*1, #main_graph_interval
            n_intervals=0
            ),
        
        # Comparison Interval
        dcc.Interval(
            id='secondary_interval',
            interval=SECOND,
            n_intervals=0
            ),
    
        # Indicator interval
        dcc.Interval(
            id='indicator_interval',
            interval=SECOND*1,
            n_intervals=0
            ),
    
        dbc.Row(style=dict(height=10)), # Break row
        
        # Header
        dbc.Row(children=[
            
            # Colman logo
            dbc.Col(
                dbc.Card(dbc.CardImg(src=LOGO_PATH)),
                align='center',
                width=dict(size=1, offset=0, order=1),
                style=dict(display='inline-block', align='center')                
                ),
            
            # SaveDat logo
            dbc.Col(
                    html.H1('SaveDat'),
                    width=dict(size=5,offset=0, order=2),
                    style= dict(textAlign='center',
                                color='info',
                                fontSize=22
                                ),
                    align='center',
                ),
            
            # streaming indicator
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        daq.Indicator(
                            value=True,
                            color='red',
                            id='stream_indicator',
                            label='Live Data Dashboard',
                            )]
                        )
                    ),
                align='center',
                width=dict(size=2, offset=0,order=3),
                style=dict(textAlign='center', align='middle')
                )
            ], style={'height':'80 px'}, justify='around'
            ),
        
        dbc.Row(style=dict(height=20)), # Break row
        
        # Info Cards Row
        dbc.Row(id='cards_row', children=[
            
            dbc.Col(
                dbc.Card([html.P('Connected', style=CARD_HEADER_STYLE_L), 
                          html.P(children=[],
                                 style=ALIGN_CENTER,
                                 id='c1')],
                         className='border-warning'),
                width=dict(size=2,offset=0,order=1)
                ),
            
            dbc.Col(
                dbc.Card(
                      children=[
                              html.P('Generated',
                                     style=CARD_HEADER_STYLE_L),
                              html.P(children=[],
                                     style=ALIGN_CENTER,
                                     id='c2')
                          ], className='border-danger'
                    ),
                width=dict(size=2, offset=0, order=2)
                ),
            
            dbc.Col(
                dbc.Card(
                      children=[
                              html.P('Transmitted',
                                     style=CARD_HEADER_STYLE_L),
                              html.P(children=[], 
                                     style=ALIGN_CENTER,
                                     id='c3')]
                          , className='border-info'
                    ),
                width=dict(size=2, offset=0, order=3)
                ),            
            
            dbc.Col(
                dbc.Card(
                        [html.P('Saved', style=CARD_HEADER_STYLE_L),
                        html.P(children=[],
                               style=ALIGN_CENTER,
                               id='c4'
                        )],
                        className='border-success'
                ),
                width=dict(size=2, offset=0, order=3)
                ),  
            
            dbc.Col(
                dbc.Card(
                        [html.P('Failed Clients', style=CARD_HEADER_STYLE_S),
                        html.P(children=[],
                               style=ALIGN_CENTER,
                               id='c5'
                        )],
                        className='border-danger'
                ),
                width=dict(size=1, offset=0, order=3)
                ),            
            
            dbc.Col(
                dbc.Card( children=[
                    dbc.Row(style=dict(height=3 )),
                    dcc.Dropdown(
                        id='sddm',
                        style=dict(color='black'),
                        options=[
                            {'label':' Labels Volume','value':LABELS_VOLUME},
                            {'label':' Transmission By Label','value':BY_LABEL_STATUS}
                            ],
                        value=LABELS_VOLUME,
                        placeholder='Data Status'
                        ),
                    
                    dbc.Row(style=dict(height=1)),
                    
                     dcc.Dropdown(
                         id='lddm',
                         placeholder='Labels Filter',
                         options=[
                                {'label':'L0','value':LABEL_0},
                                {'label':'L1','value':LABEL_1},
                                {'label':'Default','value':LABEL_2},
                                #{'label':'Mismatch','value':LABEL_3}
                            ],
                         multi=True,
                         value=[LABEL_0, LABEL_1],
                         style=dict(color='black',bs_size="lg"),
                         )
                     ],
                    
                    className='container border-light',
                    style={'height':'85px','margin':'auto'},
                    ),
                width=dict(size=3, offset=0, order=4)
                )
            
            ], justify='around', align='center'
            ),
        
        # Break row
        dbc.Row(style=dict(height=30)), 
        
        # Graphs row        
        dbc.Row(children=[
            
            # Mapbox Graph
            dbc.Col(
                dbc.Card(dbc.CardBody(
                dcc.Graph(
                    id = 'main_graph', 
                    config = {'displayModeBar':False, 'scrollZoom':True}, 
                    )
                )), 
                width={'size':8,'offset':0,'order':1}
                ),
            
            # Comparison graph
            dbc.Col(
                dbc.Card(dbc.CardBody(
                dcc.Graph(
                    id='comparison_graph',
                    config= {'displayModeBar':False, 'scrollZoom':True},
                    animate=False,
                    style=dict(theme='dark')
                    ))),
                width={'size':4,'offset':0,'order':2}
                )], align='center', style={'height':'10vhs'}
            )
        ], style=dict(marginLeft='50px', marginRight='50px')
  )

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@                       Application Callbacks                     @@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@app.callback(Output(component_id='main_graph',component_property='figure'),
              Output(component_id='c1', component_property='children'),
              Output(component_id='c2', component_property='children'),
              Output(component_id='c3', component_property='children'),
              Output(component_id='c4', component_property='children'),
              Output(component_id='c5', component_property='children'),
              Output(component_id='stream_indicator', component_property='color'),
    
              [Input(component_id='main_graph_interval', component_property='n_intervals')],
               
              State(component_id='lddm',component_property='value')) 
def live_update_mapbox_graph(n, labels):
    """ Docstring:
    ------------------------------------------------------------------------------
    Decorator annotations:
        Output(component id to change as result, property of component to change)
        Input(component id recieved as input, the property of component as input TRIGGER when changed)
    ------------------------------------------------------------------------------
    @ param n: Int, intervals count of graph update which triggers this callback
    @ param labels: List, all labels selected at labels dropdown when interval event occures
    @ return : The 'figure' property of graph component for re-rendering, along with the 
                information-cards contents, and the streaming indicator color (blinking 'red')
    ------------------------------------------------------------------------------
   """
    
    global total_generated, total_transmitted, total_saved, mismatch_ids
    title = CA_FWY_TITLE
   # Variables init
    rel_labels = []    
    gen_to_show =''
    trnsm_to_show =''
    saved_to_show=''
    
    # Obtain current state
    for label in labels:
        rel_labels.append(label)
    
    # Get next data
    df = db.get_next()
    
    # --------------------
    # Update relevant data 
    # --------------------
    
    # calculate failed clients count
    curr_mismatch_ids = list(pd.unique(df[df[LABEL]==3][V_ID]))
    mismatch_ids = list(set(mismatch_ids+curr_mismatch_ids))
    mismatch_count = len(mismatch_ids)
    
    # calculate current dataframe saved data
    curr_mismatch_pts_count = len(df[df[LABEL]==3])
    generated = len(df)*COORD_SIZE_BYTES
    transmitted = (len(df[df[LABEL]!=3])/CR+curr_mismatch_pts_count)* COORD_SIZE_BYTES
    saved = generated-transmitted
    
    total_generated += generated
    total_transmitted += transmitted
    total_saved += saved
    saves_perc = (1-total_transmitted/total_generated)*100
    
    l0_generated = len(df[df[LABEL]==0])*COORD_SIZE_BYTES
    l0_transmitted = round(l0_generated/CR)
    l0_saved = l0_generated-l0_transmitted
    
    l1_generated = len(df[df[LABEL]==1])*COORD_SIZE_BYTES
    l1_transmitted = round(l1_generated/CR)
    l1_saved = l1_generated-l1_transmitted
    
    l2_generated = len(df[df[LABEL]==2])*COORD_SIZE_BYTES
    l2_transmitted = round(l2_generated/CR)
    l2_saved = l2_generated-l2_transmitted
    
    l3_generated = len(df[df[LABEL]==3])*COORD_SIZE_BYTES
    l3_transmitted = round(l3_generated)
    l3_saved = l3_generated-l3_transmitted
    
    # Traces data
    all_saved_dq.append(saved)
    l0_dq.append(l0_saved)
    l1_dq.append(l1_saved)
    l2_dq.append(l2_saved)
    l3_dq.append(l3_saved)
    
    # Filter data
    dff = df[df[LABEL].isin(labels)]
    
    # ----------
    # Set figure
    # ----------
    fig = go.Figure()
    fig.add_trace(
        go.Scattermapbox(
            name='California 101 Free Way',
            ids = dff[V_ID],
            lat = dff[LAT],
            lon = dff[LON],
            mode='markers',
            text = '',
            hoverinfo='text',
            hovertext = dff[TEXT],
            textposition = 'top left',
            texttemplate = 'dark',
            marker = dict(
                symbol="circle",
                allowoverlap=True,
                size=7,
                color=dff[COLOR],
            ),
            subplot = 'mapbox'
        )
    )
    
    # -----------------
    # Set figure layout
    # -----------------    
    fig.layout = go.Layout( 
            height=400,           
            uirevision= 'foo', #preserves state of figure/map after callback activated
            clickmode= 'event+select',
            hovermode='closest',
            hoverdistance=2,
            paper_bgcolor='#000',
            title=dict(text=title,font=GRAPH_TITLE_FONT_S),
            mapbox_style='dark',
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=25,
                center=dict(lon=LON_CENTER, lat=LAT_CENTER),
                pitch=60,
                zoom=15
            )
        )
    fig.update_layout(title_x=0.5, 
                      template='plotly_dark', 
                      paper_bgcolor='rgb(17,17,17)'
                      )
    fig.layout.height = GARPH_HEIGHT
    
    # -------------------------
    # Define components content
    # -------------------------
    
    color = 'rgb(48,48,48)' if n%2==0 else 'red'
    
    if total_generated>=1000: gen_to_show = f"{round(total_generated/1000,1)} KB"
    elif total_generated>=1000000: gen_to_show = f"{round(total_generated/1000000,1)} MB"
    else: gen_to_show = f"{round(total_generated)} Bytes"
    
    if total_transmitted>=1000: trnsm_to_show = f"{round(total_transmitted/1000,1)} KB"
    elif total_transmitted>=1000000: trnsm_to_show = f"{round(total_transmitted/1000000,1)} MB"
    else: trnsm_to_show = f"{round(total_transmitted)} Bytes"

    saved_to_show = f"{round(saves_perc,3)}%"
    return (fig, len(dff), gen_to_show, trnsm_to_show, saved_to_show, mismatch_count,color)


@app.callback(Output(component_id='comparison_graph', component_property='figure'),
              [Input(component_id='secondary_interval', component_property='n_intervals'),
               Input(component_id='sddm', component_property='value'),
               Input(component_id='lddm', component_property='value')])

def live_update_secondary_graph(n, status, labels):

    global y_min, y_max
    
    # ------------
    # Extract Data
    # ------------
    
    #title = str(len(l0_dq))
    l0_saved = list(l0_dq)
    l1_saved = list(l1_dq)
    l2_saved = list(l2_dq)
    
    all_saved = list(all_saved_dq)

    # --------------
    # Set Axes scale
    # --------------

    all_rel_lists = []
    if status==LABELS_VOLUME:
        all_rel_lists = [l0_saved, l2_saved, l2_saved, all_saved]
    elif status==BY_LABEL_STATUS:
        all_rel_lists = [l0_saved, l1_saved, l2_saved, all_saved]
        
    for l in all_rel_lists:
      y_min = min(y_min, min(l))
      y_max = max(y_max, max(l))
      
    x_min = max(0, n-len(l0_saved))
    x_max = x_min+QUEUE_LEN
    if n<QUEUE_LEN: 
        x_max = len(all_rel_lists[0])
    
    X = [(i+1) for i in range(x_min, x_max)]
    
    # --------------------------------
    # Construct and return right graph
    # --------------------------------
    
    if status == BY_LABEL_STATUS:
        title = 'Transmission Comparison'
        #title = str(x_min) + ', '+str(x_max)+': ' +str(n)+'- '+str(len(l0_saved))
        #title = str(len(l0_saved))
        saved_trace = go.Scatter(
                x=X,
                y=all_saved,
                name='All',
                mode='lines',
                marker=dict(color=PURPLE_COLOR)
            )
        l0_trace = go.Scatter(
            x=X,
            y=l0_saved,
            name='Label 0',
            mode='lines',
            marker=dict(color=Util.colors[0])
        )
        
        l1_trace = go.Scatter(
            x=X,
            y=l1_saved,
            name='Label 1',
            mode='lines',
            marker=dict(color=Util.colors[1])
        )
        
        l2_trace = go.Scatter(
            x=X,
            y=l2_saved,
            name='Default label',
            mode='lines',
            marker=dict(color=Util.colors[2])
        )
        
        traces = [l0_trace, l1_trace, l2_trace]
        data = [saved_trace]
        
        for lbl in labels:
            data.append(traces[int(lbl)])
        
        layout = go.Layout(
                title=dict(text=title, font=GRAPH_TITLE_FONT_S),
                xaxis=dict(range=[x_min,x_max]),
                yaxis=dict(range=[y_min*0.5, y_max*2.5]),
                legend=dict(x=0, y=1),
                uirevision='moo',
                height=GARPH_HEIGHT
            )
        
        fig = go.Figure(data=data,layout=layout)
        fig.update_layout(
            template = 'plotly_dark', 
            title_x=0.5,
            xaxis={'title':'Time steps (10Hz)'}, 
            yaxis={'title':'Data Volume (Bytes)'}
        )
    
        return fig
    
    elif status==LABELS_VOLUME:
        info = db.get_lcounts()
        
        
        trace = go.Pie(
            labels=['Label 0','Label 1','Default', 'Mismatch'], 
            values=info,
            hole=.3
        )
        
        layout = go.Layout(
            template='plotly_dark',
            title=dict(text='Data Volume', font=GRAPH_TITLE_FONT_S),
        )
        
        fig = go.Figure(data=[trace],layout=layout) 
        fig.update_layout( title_x=.5)
        fig.update_traces(hoverinfo='label+value', textinfo='percent', textfont_size=15,
                      marker=dict(colors=Util.colors, line=dict(color='#000', width=3)))
        
        fig.layout.height = GARPH_HEIGHT
        return fig
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@                     End Callbacks                       @@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    
# run application
if __name__ == '__main__':
    app.run_server(debug=False)
    print('[SERVER] Runing....')
    