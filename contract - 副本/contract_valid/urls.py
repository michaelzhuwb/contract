
from django.urls import path
from . import views
urlpatterns = [
    path('/login', views.login),
    path('/upload_contract', views.upload),
    path('/get_info', views.get_info), 
    path('/valid_contract', views.valid_contract), 
    path('/pre_upload',views.pre_upload),
    path('/valid_contract_info', views.valid_contract_info), 

] 