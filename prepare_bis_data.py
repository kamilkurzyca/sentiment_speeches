import pandas as pd
import os

class PrepareBisData():
    
    def __init__(self,path_to_files,index_start=None,index_end=None):
        self.path_to_files=path_to_files
        self.index_start=index_start
        self.index_end=index_end

    def create_bis_data(self):
        """
        Function processing data scrapped from internet for one consisten data frame

        Returns:
            bis_data (DataFrame): frame with speeches data.

        """
        list_of_files=os.listdir(self.path_to_files)
        bis_data=pd.concat([pd.read_csv(f'{self.path_to_files}/{file}') for file in list_of_files])
        bis_data['Date']=pd.to_datetime(bis_data['Date'],format='%Y-%m-%d')
        bis_data.set_index('Date',inplace=True)
        bis_data.drop_duplicates(subset=['Title'],inplace=True)
        bis_data.sort_index(inplace=True)
        if self.index_start==None or self.index_end==None:
            return bis_data
        else:
            return bis_data[self.index_start:self.index_end]