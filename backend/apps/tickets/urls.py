from django.urls import path, include

from . import views

app_name = 'main'

urlpatterns = [
    # api based path
    path('api/', include('apps.main.api.urls', namespace='api')),

    # template based views
    path('', views.index, name="index"),
    path("<str:room_name>/", views.room, name="room"),
]
