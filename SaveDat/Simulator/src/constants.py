# Data source --> https://data.transportation.gov/Automobiles/Next-Generation-Simulation-NGSIM-Vehicle-Trajector/8ect-6jqj


# imports
import pandas as pd
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import random
import shutil
from datetime import datetime
import time
import json
import re
import socket
import sys
import threading
import logging
import pickle
import traceback
import copy

# communication
import socket
from concurrent.futures import ThreadPoolExecutor

# Geo modules
from haversine import haversine, Unit
from pyproj import Transformer
from shapely.geometry import Point, Polygon

# ML modules
from keras import callbacks as cb
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM, InputLayer, RepeatVector, TimeDistributed
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from sklearn.cluster import KMeans

# Visualization modules
import matplotlib.pyplot as plt




# Loggers
LOCAL = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
#LOGS = os.path.join(LOCAL, 'logs')
#NETWORK = 'network'
#NETWORK_PATH = os.path.join(LOGS, NETWORK)
#CLUSTERING = 'clustering'
#MODELS = 'models'
#BOOT = 'boot'


# Constants
DATA_PATH = os.path.join(LOCAL, 'data')
TRAJ = 'traj'
TRAIN = 'train'
TEST = 'test'
MODELS = 'models'
TRAJ_DATA_PATH = os.path.join(DATA_PATH, TRAJ)
TRAIN_DATA_PATH = os.path.join(DATA_PATH, TRAIN)
TEST_DATA_PATH = os.path.join(DATA_PATH, TEST)
MODELS_PATH = os.path.join(DATA_PATH, MODELS)
CONCLUDED_DATA_PATH = os.path.join(DATA_PATH, 'Concluded_Data')
CLIENTS_FINAL_DATA_PATH = os.path.join(DATA_PATH, 'Clients_Data')
WGS84 = 4326
NAD83 = 2229

LABEL = 'Label'
v_ID = 'Vehicle_ID'
global_time = 'Global_Time'
global_lng = 'Global_X'
global_lat = 'Global_Y'
# Attribute Definition: Vehicle type: 1 - motorcycle, 2 - auto, 3 - truck\n",
v_class = 'v_Class'
v_velocity = 'v_Vel'
v_acceleration = 'v_Acc'
fitted_lng = 'Fitted Longtitude'
fitted_lat = 'Fitted Latitude'
proj_lng = 'Proj Longtitude'
proj_lat = 'Proj Latitude'

s25 = 's25'
s50 = 's50'
s75 = 's75'

a25 = 'a25'
a50 = 'a50'
a75 = 'a75'

BEHAVIOR_SAMPLES = 10
# direction = 'Direction' # this feature isnt consistent
QS = [0.25, 0.5, 0.75]
RELEVANT_FEATURES = [v_ID, global_time, global_lng,
                     global_lat, v_class, v_velocity,
                      v_acceleration]
PREFIXES = ['a_', 'b_', 'c_']

# ML
K_CLUSTERS = 3
TRAIN_SIZE = 0.6
EPOCHS = 8
BATCH_SIZE = 1024 # GOOD ?
TIMESTEPS_PAST = 10  # in our data its 1 sec
TIMESTEPS_FUTURE = 10
NUM_OF_FEATURES = 2
LSTM_NUM = 50
ADAM = 'adam'
MSE = 'mse'

# polygons
POINT_LIST_ROAD_101 = [Point(-118.365524, 34.146374), Point(-118.373935, 34.145860),
                       Point(-118.374726, 34.155775), Point(-118.380027, 34.151443),
                       Point(-118.398048, 34.151837), Point(-118.396266, 34.156275),
                       Point(-118.407964, 34.158921), Point(-118.407986, 34.153843)]

POLY_101 = Polygon([[p.x, p.y] for p in POINT_LIST_ROAD_101])

# server
PORT = 15000
IP = '127.0.0.1'
BACKLOG = 100
SERVER_TIME_OUT_IN_SECONDS = 60
UTF8 = 'utf-8'
ERROR_SERVICE = "cannot provide service"

HEADER_SIZE = 16
