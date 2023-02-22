import unittest
from unittest.mock import patch
from django.test import TestCase, Client
from api import models
from fetch_data import FetchData
from rest_framework.test import APITestCase
from .models import QuizQuestions, Subtopics, QuestionAnswers, Schools, Users
from rest_framework.test import APIClient


from django.urls import reverse
# Create your tests here.


class predictTestCase(APITestCase):
    def test_prediction_correct(self):
        data = {
            "resource_access": 77,
            "announcements_view": 14,
            "abscence": 0,
            "discussion": 28,
            "raised_hands": 50
        }
        resp = self.client.post('/predict', data, format='json')
        self.assertEqual(resp.status_code, 200)



class UrlsTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_about_page(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_contact_page(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)

    def test_invalid_page(self):
        response = self.client.get('/invalid-page/')
        self.assertEqual(response.status_code, 404)


class ApiConfigTest(TestCase):
    
    def test_app_config_name(self):
        """
        Test that the name attribute of ApiConfig is set to 'api'.
        """
        self.assertEqual(ApiConfig.name, 'api')

class TestFetchData(unittest.TestCase):

    @patch('api.models.QuizQuestions.objects')
    def test_high_level_questions(self, mock_query):
        fetch_data = FetchData(1)
        passed_subtopics = [1, 2, 3]

        # Mocking the results of database query
        mock_query.raw.return_value = [{'question_level': 'create', 'subtopic_id': 1}, {'question_level': 'evaluate', 'subtopic_id': 1}, {'question_level': 'analyze', 'subtopic_id': 1}]
        
        result = fetch_data.high_level_questions(passed_subtopics, 1)

        self.assertEqual(result, [{'question_level': 'create', 'subtopic_id': 1}, {'question_level': 'evaluate', 'subtopic_id': 1}, {'question_level': 'analyze', 'subtopic_id': 1}, {'question_level': 'create', 'subtopic_id': 1}, {'question_level': 'evaluate', 'subtopic_id': 1}, {'question_level': 'analyze', 'subtopic_id': 1}, {'question_level': 'create', 'subtopic_id': 1}, {'question_level': 'evaluate', 'subtopic_id': 1}, {'question_level': 'analyze', 'subtopic_id': 1}])

    @patch('api.models.QuizQuestions.objects')
    def test_failed_subtopic_materials(self, mock_query):
        fetch_data = FetchData(1)
        failed_subtopics = [4, 5, 6]

        # Mocking the results of database query
        mock_query.raw.return_value = [{'subtopic_id': 1}]

        result = fetch_data.failed_subtopic_materials(failed_subtopics)

        self.assertEqual(result, [{'subtopic_id': 1}])

    @patch('api.models.QuizQuestions.objects')
    def test_create_questions(self, mock_query):
        fetch_data = FetchData(1)
        mark = 1

        # Mocking the results of database query
        mock_query.filter.return_value.values.return_value = [{'question_level': 'create', 'subtopic_id': 1}]

        result = fetch_data.create_questions(mark)

        self.assertEqual(result, {'question_level': 'create', 'subtopic_id': 1})

    @patch('api.models.QuizQuestions.objects')
    def test_evaluate_questions(self, mock_query):
        fetch_data = FetchData(1)
        mark = 1

        # Mocking the results of database query
        mock_query.filter.return_value.values.return_value = [{'question_level': 'evaluate', 'subtopic_id': 1}]
        
        result = fetch_data.evaluate_questions(mark)

        self.assertEqual(result, {'question_level': 'evaluate', 'subtopic_id': 1})

    @patch('api.models.QuizQuestions.objects')
    def test_analyze_questions(self, mock_query):
        fetch_data = FetchData(1)
        mark = 1

        # Mocking the results of database query
        mock_query.filter.return_value.values.return_value = [{'question_level': 'analyze', 'subtopic_id': 1}]
        
        result = fetch_data.analyze_questions(mark)
        self.assertEqual(result, {'question_level': 'analyze', 'subtopic_id': 1})

    def setUp(self):
        self.fetch_data = FetchData()

    def test_apply_questions(self):
        data = [
            {"question": "What is the capital of France?", "answer": "Paris"},
            {"question": "What is the largest country in the world?", "answer": "Russia"},
            {"question": "What is the currency of Japan?", "answer": "Yen"},
            {"question": "What is the highest mountain in Africa?", "answer": "Kilimanjaro"}
        ]

        questions = self.fetch_data.apply_questions(data)

        self.assertEqual(len(questions), 4)
        self.assertIsInstance(questions, list)
        for question in questions:
            self.assertIn("question", question)
            self.assertIn("answer", question)


class ModelsTestCase(TestCase):
    def setUp(self):
        # create some sample objects to use in the tests
        self.quiz_question = QuizQuestions.objects.create(
            subtopic_id='1', subject_id=1, question='What is the capital of France?',
            option_a='London', option_b='Paris', option_c='New York', option_d='Madrid',
            option_a_explanation='London is the capital of England',
            option_b_explanation='Correct! Paris is the capital of France',
            option_c_explanation='New York is a city in the United States',
            option_d_explanation='Madrid is the capital of Spain',
            answer='b', additional_notes='None', created_at='2022-02-22', question_level='Easy'
        )
        self.subtopic = Subtopics.objects.create(
            id=1, topic_id=1, subtopic_name='French culture', subject_id=1
        )
        self.question_answer = QuestionAnswers.objects.create(
            question_id=1, subtopic_id=1, subject_id=1, quiz_id=1, student_id=1
        )
        self.school = Schools.objects.create(
            school_name='Test School', school_code='123', county_id=1
        )
        self.user = Users.objects.create(
            first_name='Test', last_name='User', email='testuser@test.com',
            phone_number='1234567890', school_code='123', password='password'
        )

    def test_quiz_questions_model(self):
        # test the QuizQuestions model
        self.assertEqual(str(self.quiz_question), 'What is the capital of France?')
        self.assertEqual(self.quiz_question.subtopic_id, '1')
        self.assertEqual(self.quiz_question.subject_id, 1)
        self.assertEqual(self.quiz_question.question, 'What is the capital of France?')
        self.assertEqual(self.quiz_question.option_a, 'London')
        self.assertEqual(self.quiz_question.option_b, 'Paris')
        self.assertEqual(self.quiz_question.option_c, 'New York')
        self.assertEqual(self.quiz_question.option_d, 'Madrid')
        self.assertEqual(self.quiz_question.option_a_explanation, 'London is the capital of England')
        self.assertEqual(self.quiz_question.option_b_explanation, 'Correct! Paris is the capital of France')
        self.assertEqual(self.quiz_question.option_c_explanation, 'New York is a city in the United States')
        self.assertEqual(self.quiz_question.option_d_explanation, 'Madrid is the capital of Spain')
        self.assertEqual(self.quiz_question.answer, 'b')
        self.assertEqual(self.quiz_question.additional_notes, 'None')
        self.assertEqual(str(self.quiz_question.created_at), '2022-02-22')
        self.assertEqual(self.quiz_question.question_level, 'Easy')
    
    def test_subtopics_model(self):
        # test the Subtopics model
        self.assertEqual(str(self.subtopic), 'French culture')
        self.assertEqual(self.subtopic.id, 1)
        self.assertEqual(self.subtopic.topic_id, 1)
        self.assertEqual(self.subtopic.subtopic_name, 'French culture')
        self.assertEqual(self.subtopic.subject_id, 1)

    def test_question_answers_model(self):
        # Create a QuestionAnswers object
        qa = QuestionAnswers.objects.create(
            question_id=1,
            subtopic_id=1,
            subject_id=1,
            quiz_id=1,
            student_id=1
        )

        # Check that the object was created successfully
        self.assertIsNotNone(qa)
        self.assertEqual(qa.question_id, 1)
        self.assertEqual(qa.subtopic_id, 1)
        self.assertEqual(qa.subject_id, 1)
        self.assertEqual(qa.quiz_id, 1)
        self.assertEqual(qa.student_id, 1)

        # Check that the object's string representation is correct
        self.assertEqual(str(qa), f"QuestionAnswers {qa.id}")

    def test_users_model(self):
        user = Users.objects.get(email='john.doe@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.phone_number, '555-1234')
        self.assertEqual(user.school_code, 'SCH001')
        self.assertEqual(user.password, 'password')  
        
    def test_schools_model(self):
        school = Schools.objects.get(school_name='School 1')
        self.assertEqual(school.school_code, 'SCH001')
        self.assertEqual(school.county_id, 1)

class TestViews(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_index_page(self):
        response = self.client.get('/index_page/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['error'], "0")
        self.assertEqual(response.data['message'], "Successful")

    def test_classify_student_v1_success(self):
        payload = {
            "raised_hands": 30,
            "resource_access": 4,
            "announcements_view": 1,
            "discussion": 70,
            "abscence": 3
        }
        response = self.client.post('/classify_student_v1/', payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['error'], "0")
        self.assertEqual(response.data['message'], "Successful")
        self.assertIn('prediction', response.data)

    def test_classify_student_v1_invalid_params(self):
        payload = {
            "raised_hands": 30,
            "resource_access": 4,
            "announcements_view": None,
            "discussion": 70,
            "abscence": 3
        }
        response = self.client.post('/classify_student_v1/', payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['error'], "1")
        self.assertEqual(response.data['message'], "Invalid Parameters")

    def test_classify_student_v1_exception(self):
        payload = {
            "raised_hands": 30,
            "resource_access": 4,
            "announcements_view": 1,
            "discussion": 70,
            "abscence": 3
        }
        # corrupt the model file
        open('svm.sav', 'w').write('invalid data')
        response = self.client.post('/classify_student_v1/', payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['error'], "2")
        self.assertIn('No module named', response.data['message'])

    def test_diagnostic_recommendation(self):
        payload = {
            "question_level_code": "understand",
            "marked": 3,
            "subtopic_id": 1,
            "question_id": 1
        }
        response = self.client.post('/diagnostic_recommendation/', payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['error'], "0")
        self.assertEqual(response.data['message'], "Successful")
        self.assertIn('prediction', response.data)
        self.assertIn('quiz_question', response.data)

    def test_retrieve_diagnostic_questions(self):
        payload = {
            "topic_id": 1
        }
        response = self.client.post('/retrieve_diagnostic_questions/', payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('questions', response.data)

    def test_retrieve_diagnostic_recommendation(self):
        payload = {
            "topic_id": 1,
            "answers": [{"marked": 1, "question_level": "remember"}]
        }
        response = self.client.post('/retrieve_diagnostic_recommendation/', payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('recommend', response.data['prediction'])

class TestViews(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_index_page(self):
        response = self.client.get('/index_page/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['error'], "0")
        self.assertEqual(response.data['message'], "Successful")

    def test_classify_student_v1_success(self):
        payload = {
            "raised_hands": 30,
            "resource_access": 4,
            "announcements_view": 1,
            "discussion": 70,
            "abscence": 3
        }
        response = self.client.post('/classify_student_v1/', payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['error'], "0")
        self.assertEqual(response.data['message'], "Successful")
        self.assertIn('prediction', response.data)

    def test_classify_student_v1_invalid_params(self):
        payload = {
            "raised_hands": 30,
            "resource_access": 4,
            "announcements_view": None,
            "discussion": 70,
            "abscence": 3
        }
        response = self.client.post('/classify_student_v1/', payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['error'], "1")
        self.assertEqual(response.data['message'], "Invalid Parameters")

    def test_classify_student_v1_exception(self):
        payload = {
            "raised_hands": 30,
            "resource_access": 4,
            "announcements_view": 1,
            "discussion": 70,
            "abscence": 3
        }
        # corrupt the model file
        open('svm.sav', 'w').write('invalid data')
        response = self.client.post('/classify_student_v1/', payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['error'], "2")
        self.assertIn('No module named', response.data['message'])

    def test_diagnostic_recommendation(self):
        payload = {
            "question_level_code": "understand",
            "marked": 3,
            "subtopic_id": 1,
            "question_id": 1
        }
        response = self.client.post('/diagnostic_recommendation/', payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['error'], "0")
        self.assertEqual(response.data['message'], "Successful")
        self.assertIn('prediction', response.data)
        self.assertIn('quiz_question', response.data)

    def test_retrieve_diagnostic_questions(self):
        payload = {
            "topic_id": 1
        }
        response = self.client.post('/retrieve_diagnostic_questions/', payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('questions', response.data)

    def test_retrieve_diagnostic_recommendation(self):
        payload = {
            "topic_id": 1,
            "answers": [{"marked": 1, "question_level": "remember"}]
        }
        response = self.client.post('/retrieve_diagnostic_recommendation/', payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('recommend', response.data['prediction'])