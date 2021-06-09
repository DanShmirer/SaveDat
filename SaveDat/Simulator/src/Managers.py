import numpy as np
from constants import *
class RoadManager:
    def __init__(self, polygon, kmeans_model, rnn_map):

        self.road_polygon = polygon
        self.behaviors_model = kmeans_model
        self.rnns_map = rnn_map
        self.first_predict = True
        self.steps = -1

    def get_behavior_label(self, behavior_vector):
        '''
        get the behavior label
        @ param : behavior_vector 6D-vector
        @ return : int the corresponding label
        '''
        label = self.behaviors_model.predict(behavior_vector)
        if label in self.rnn_map.keys():
            return label
        return -1

    def predict_next(self, base_points, label, timestep):
        '''
        predict the coordinates from timestep to timestep + 10
        @ param : base_points, label, timestep list(tup), int, int
        @ return : (x,y) coordinates
        '''
        # get rnn model
        if str(label) in self.rnns_map.keys():
            model = self.rnns_map[str(label)]
        else:
            model = self.rnns_map[9]
        #reset model states
        model.reset_states()

        # number of times to use predict
        if self.first_predict:
            self.first_predict = False
            self.steps = timestep/10  # if timesteps = 50, predict 5 times

        steps = self.steps
        all_predicted_points = base_points
        while steps > 0:
            # predict next 10 steps
            next_points = model.predict(np.reshape(a=base_points,newshape=(1,10,2)))
            base_points = next_points[0]
            all_predicted_points = np.concatenate((all_predicted_points, base_points))

            steps -= 1

        return base_points, all_predicted_points


class RoadsManager:
    def __init__(self, managers_list):
        self.roads_managers = managers_list

    def get_manager(self,point):
        '''
        finding the right road manager
        @ param : point client location
        @ return : RoadManager
        '''
        for manager in self.roads_managers:
            if point.within(manager.road_polygon):
                return manager
        m = self.roads_managers[0]
        return RoadManager(m.road_polygon, m.behaviors_model,m.rnns_map)
