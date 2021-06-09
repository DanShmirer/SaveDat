from constants import *


LATS = 'Latitudes'
LNGS = 'Longitudes'


class CH_Data_Transmittor:
    def __init__(self, v_id):
        self.id = v_id
        self.data = {
                        LABEL: [],
                        LATS : [],
                        LNGS : [],
                        global_time:[]
                    } 

    def set_time(self,time=0):
        self.data[global_time].append(time)
        
    def set_behavior(self,label=9):
            self.data[LABEL].append(label)
        
    def set_data(self, lats=None, lngs=None):
        """
        ----------------------------------------
        lats : list-like, optional
            The latitudes list of size 20. 
            If not specified, latter values maintained
        lngs : list-like, optional
            The longitudes list of size 20.
            If not specified, latter values maintained
        Returns None.
        ----------------------------------------
        """
        if lats!=None: self.data[LATS].extend(lats)
        if lngs!=None: self.data[LNGS].extend(lngs)
            
    def send_data(self):
        max_len = len(self.data[LATS])
        for key in self.data:
            if  len(self.data[key]) != max_len:
                self.data[key] = [self.data[key][0]]*max_len

        df = pd.DataFrame(data=self.data)
        df.to_csv(os.path.join(CONCLUDED_DATA_PATH, str(self.id)+ '.csv'))
        
    def stop(self):
        self.conn.close()