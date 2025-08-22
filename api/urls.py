from django.urls import path
from api import views

urlpatterns = [
    path('',views.index_page),
    path('predict_v1', views.classify_student_v1),
    path('predict_v2', views.diagnostic_recommendation),
    path('retrieve_diagnostic_questions', views.retrieve_diagnostic_questions),
    path('retrieve_diagnostic_recommendation', views.retrieve_diagnostic_recommendation),
    path('fln-quizzes', views.fln_angaza_quizzes),
    path('fln-diagnostic', views.fln_diagnostic_quizzes),
    path('fln-diagnostic-recommendation', views.fln_diagnostic_recommendation),
    path('fln-save-response', views.save_user_response),
    path('fln-user-recommendations', views.get_user_recommendations),
    path('fln-user-threshold', views.get_user_threshold),
    path('fln-update-threshold', views.update_user_threshold),
    path('fln-threshold-history', views.get_threshold_history),
    path('threshold-manager', views.threshold_manager),
    path('quiz/<int:quiz_id>', views.get_quiz_by_id),
    path('user-responses', views.get_user_responses),  # Get user responses with filtering
]
