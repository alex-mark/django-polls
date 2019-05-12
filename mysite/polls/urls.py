from django.urls import path

from . import views


app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('mypolls/', views.MyPollsView.as_view(), name='mypolls'),
    path('create/', views.CreatePollView.as_view(), name='create'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.UpdatePollView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.DeletePollView.as_view(), name='delete'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
]
