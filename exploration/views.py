from django.http import  HttpResponse
from rest_framework.decorators import api_view
from exploration.constants import FILENAME, DIR_NAME
from exploration.utils import data_preprocessor
import matplotlib.pyplot as plt
import io


@api_view(['GET'])
def data_viewer(request):
    df_lstm = data_preprocessor(DIR_NAME, FILENAME)
    
    fig = plt.figure()
    df_lstm.plot(x="created_at", y=["order_id", "total_order_value"])
    buf = io.BytesIO()
    plt.xticks(rotation=30)
    plt.title('Total orders and earnings per day')
    plt.savefig(buf, format='png', dpi=100)
    plt.close(fig)


    response = HttpResponse(buf.getvalue(), content_type='image/png')
    return response

@api_view(['GET'])
def data_train(request):
    df_lstm = data_preprocessor(DIR_NAME, FILENAME)

    return response           
