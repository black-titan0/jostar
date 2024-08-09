from django.urls import path

from jostars.views import JostarCreateView, JostarListView, RateJostarView

urlpatterns = [
    path('', JostarCreateView.as_view()),
    path('list', JostarListView.as_view()),
    path('rate', RateJostarView.as_view()),
]
