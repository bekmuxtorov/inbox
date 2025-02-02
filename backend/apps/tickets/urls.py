from .views import TicketCreateView
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from . import views


app_name = 'tickets'

urlpatterns = [
    # api based path
    path('tickets/create/', TicketCreateView.as_view(), name='ticket_create'),

    # template based views
    path('', views.TicketListView.as_view(), name='ticket_list'),
    path('<int:pk>/',
         views.TicketDetailView.as_view(), name='ticket_detail'),
    path("<str:room_name>/", views.room, name="room"),
]
