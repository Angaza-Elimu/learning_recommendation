from django.urls import path
from learning_recommendation.api import views

urlpatterns = [
    path('',views.index_page),
    path('predict', views.classify_student),
]