from django.urls import path

from jostars.views import JostarCreateView

urlpatterns = [
    path('', JostarCreateView.as_view()),
]
