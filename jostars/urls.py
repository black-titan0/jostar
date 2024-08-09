from django.urls import path

from jostars.views import JostarCreateView, JostarListView

urlpatterns = [
    path('', JostarCreateView.as_view()),
    path('list', JostarListView.as_view()),
]
