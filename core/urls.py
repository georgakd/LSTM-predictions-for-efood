from django.contrib import admin
from django.urls import path, include  # add this
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    path('admin/', admin.site.urls),  # Django admin route
    path('api/exploration/', include('exploration.urls')),
]
