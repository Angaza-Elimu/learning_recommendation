from django.urls import path
from api import views

urlpatterns = [
    path('',views.index_page),
    path('predict_v1', views.classify_student_v1),
    path('predict_v2', views.diagnostic_recommendation)
]
