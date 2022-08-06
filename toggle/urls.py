from django.urls import path

from . import views

urlpatterns = [
    path('', views.indexview , name='index'),
    path('lock_api/lock-states/', views.listall_states, name='states'),
    path('api/lock/records', views.listall_states, name='states'),
    path('lock_api/last-state/', views.last_state, name='last-state'),
    path('api/lock/last-record', views.last_state, name='last-state'),
    path('lock_api/create-state/', views.create_state, name='create-state'),
    path('opendoor/', views.open_the_lock)
]
