from rest_framework.response import Response
from rest_framework.decorators import api_view
from exploration.constants import FILENAME, DIR_NAME
from exploration.utils import data_preprocessor



@api_view(['GET'])
def data_viewer(request):
    df = data_preprocessor(DIR_NAME, FILENAME)

    response_dict = {'hello', len(df)}
    

    return Response(response_dict)        
