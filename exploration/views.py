from rest_framework.response import Response
from rest_framework.decorators import api_view
from exploration.constants import FILENAME, DIR_NAME
from exploration.importer import ImporterFolder



@api_view(['GET'])
def data_viewer(request):
    df = ImporterFolder(DIR_NAME).load_data(FILENAME)

    response_dict = {'hello', len(df)}
    

    return Response(response_dict)        
