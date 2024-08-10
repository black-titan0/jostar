from django.urls import path

from jostars.views import JostarCreateView, JostarListView, RateJostarView, ShareJostarView, GetJostarByLinkView

urlpatterns = [
    path('', JostarCreateView.as_view()),
    path('list', JostarListView.as_view()),
    path('rate', RateJostarView.as_view()),
    path('share/<int:jostar_id>', ShareJostarView.as_view()),
    path('shared/<str:token>', GetJostarByLinkView.as_view()),
]
