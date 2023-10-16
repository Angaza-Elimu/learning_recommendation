from django.urls import path
from api import views

urlpatterns = [
    path('',views.index_page),
    path('predict_v1', views.classify_student_v1),
    path('predict_v2', views.diagnostic_recommendation),
    path('retrieve_diagnostic_questions', views.retrieve_diagnostic_questions),
    path('retrieve_diagnostic_recommendation', views.retrieve_diagnostic_recommendation),
    path('assignUserSchools', views.assign_user_schools),
]
