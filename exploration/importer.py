import os
import pandas as pd
from core.generic_importer import Importer

class ImporterFolder(Importer):
    """ Helper class to load datasets from local disk. """

    def __init__(self, dir_name):
        self.path = self.form_dir_path(dir_name)
        super().__init__()
    
    def form_dir_path(self, dir_name):
        """ Load dataset with measurements from a specified file.

         :param `str` dir_name: the name of the directory for the dataset provided
         """

        return super().form_dir_path(dir_name)
        
    def load_data(self, file_name):
        """ Load dataset with measurements from a specified file.

         :param `str` file_name: the filename for the dataset provided
         """
        
        return super().load_data(self.path, file_name)
        


    

        
