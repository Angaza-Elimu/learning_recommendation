import pickle
import unittest
from unittest.mock import patch, Mock, MagicMock
from django.http import HttpRequest
from django.test import TestCase, Client
import os

from rest_framework.response import Response
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning_recommendation.settings')
django.setup()

from api.apps import ApiConfig
from api.fetch_data import FetchData
from rest_framework.test import APITestCase
from .models import QuizQuestions, Subtopics, QuestionAnswers, Schools, Users
from rest_framework.test import APIClient
from django.urls import reverse
from api.views import index_page, classify_student_v1, diagnostic_recommendation, retrieve_diagnostic_questions, retrieve_diagnostic_recommendation, assign_user_schools, getQuestionLevelCode, high_level, low_level_material

# Create your tests here.
class predictTestCase(APITestCase): # pragma: no cover
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

class UrlsTest(unittest.TestCase): # pragma: no cover

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


class ApiConfigTest(unittest.TestCase): # pragma: no cover
    
    def test_app_config_name(self):
        """
        Test that the name attribute of ApiConfig is set to 'api'.
        """
        self.assertEqual(ApiConfig.name, 'api')
if __name__ == '__main__':
    unittest.main()


class TestFetchData(unittest.TestCase): # pragma: no cover
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
        self.fetch_data = FetchData(1)

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

if __name__ == '__main__':
    unittest.main()

class ModelsTestCase(unittest.TestCase):
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
if __name__ == '__main__':
    unittest.main()


class TestViews(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_index_page(self):
        response = self.client.post('/index_page/')
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

    def setUp(self):
        # Create mock data for the request object
        self.request = Mock()
        self.request.data = {}

    def test_valid_input_returns_prediction(self):
        # Set up the mock request data with valid values
        self.request.data['resource_access'] = '0.8'
        self.request.data['announcements_view'] = '0.9'
        self.request.data['abscence'] = '0.2'
        self.request.data['discussion'] = '0.7'
        self.request.data['raised_hands'] = '0.5'

        # Mock the pickle.load function
        pickle.load = Mock(return_value='mock_classifier')

        # Mock the scaler.transform function
        mock_scaled_value = 'mock_scaled_value'
        mock_scaler = Mock(transform=Mock(return_value=mock_scaled_value))
        pickle.load.return_value = mock_scaler

        # Call the function
        response = classify_student_v1(self.request)

        # Assertions
        self.assertEqual(response.data['error'], '0')
        self.assertEqual(response.data['message'], 'Successful')
        self.assertEqual(response.data['prediction'], 'mock_classifier')
        self.assertEqual(response.data['scaled'], mock_scaled_value)

    def test_invalid_parameters_returns_error(self):
        # Set up the mock request data with missing values
        self.request.data['resource_access'] = '0.8'
        self.request.data['announcements_view'] = None
        self.request.data['abscence'] = '0.2'
        self.request.data['discussion'] = '0.7'
        self.request.data['raised_hands'] = '0.5'

        # Call the function
        response = classify_student_v1(self.request)

        # Assertions
        self.assertEqual(response.data['error'], '1')
        self.assertEqual(response.data['message'], 'Invalid Parameters')

    def test_exception_occurred_returns_error(self):
        # Set up the mock request data with valid values
        self.request.data['resource_access'] = '0.8'
        self.request.data['announcements_view'] = '0.9'
        self.request.data['abscence'] = '0.2'
        self.request.data['discussion'] = '0.7'
        self.request.data['raised_hands'] = '0.5'

        # Mock the pickle.load function to raise an exception
        pickle.load = Mock(side_effect=Exception('Mock exception'))

        # Call the function
        response = classify_student_v1(self.request)

        # Assertions
        self.assertEqual(response.data['error'], '2')
        self.assertEqual(response.data['message'], 'Mock exception')

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
if __name__ == '__main__':
    unittest.main()
class TestViews(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()


    def test_index_page_returns_response(self):
        request = HttpRequest()
        response = index_page(request)
        self.assertIsNotNone(response)  
        self.assertIsInstance(response, Response)
        self.assertEqual(response.data['error'], "0")
        self.assertEqual(response.data['message'], "Successful")

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

    # def test_classify_student_v1_exception(self):
    #     payload = {
    #         "raised_hands": 30,
    #         "resource_access": 4,
    #         "announcements_view": 1,
    #         "discussion": 70,
    #         "abscence": 3
    #     }
        
    #     response = self.client.post('/classify_student_v1/', payload)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['error'], "2")
    #     self.assertIn('No module named', response.data['message'])

    # def test_diagnostic_recommendation(self):
    #     payload = {
    #         "question_level_code": "understand",
    #         "marked": 3,
    #         "subtopic_id": 1,
    #         "question_id": 1
    #     }
    #     response = self.client.post('/diagnostic_recommendation/', payload)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['error'], "0")
    #     self.assertEqual(response.data['message'], "Successful")
    #     self.assertIn('prediction', response.data)
    #     self.assertIn('quiz_question', response.data)

    # def test_retrieve_diagnostic_questions(self):
    #     payload = {
    #         "topic_id": 1
    #     }
    #     response = self.client.post('/retrieve_diagnostic_questions/', payload)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('questions', response.data)

    # def test_retrieve_diagnostic_recommendation(self):
    #     payload = {
    #         "topic_id": 1,
    #         "answers": [{"marked": 1, "question_level": "remember"}]
    #     }
    #     response = self.client.post('/retrieve_diagnostic_recommendation/', payload)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('recommend', response.data['prediction'])
if __name__ == '__main__':
    unittest.main()

class ApiConfigTests(unittest.TestCase):

    def test_name_is_correct(self):
        config = ApiConfig('api', 'api/apps.py')
        self.assertEqual(config.name, 'api', "Name should be 'api'")

    def test_name_is_not_empty(self):
        config = ApiConfig('api', 'api/apps.py')
        self.assertNotEqual(config.name, '', "Name should not be empty")

    def test_name_is_string(self):
        config = ApiConfig('api', 'api/apps.py')
        self.assertIsInstance(config.name, str, "Name should be a string")

    def test_name_length_is_greater_than_zero(self):
        config = ApiConfig('api', 'api/apps.py')
        self.assertGreater(len(config.name), 0, "Name length should be greater than zero")

if __name__ == '__main__':
    unittest.main()


class TestCoverage(unittest.TestCase):

    def test_index_page(self):
        request = HttpRequest()
        response = index_page(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            "error": "0",
            "message": "Successful"
        })

    def test_classify_student_v1(self):
        request = HttpRequest()
        request.data = {
            'resource_access': 1,
            'announcements_view': 1,
            'abscence': 1,
            'discussion': 1,
            'raised_hands': 1
        }
        expected_response = {
            'error': '0',
            'message': 'Successful',
            'prediction': ...,
            'scaled': ...
        }
        response = classify_student_v1(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['error'], expected_response['error'])
        self.assertEqual(response.data['message'], expected_response['message'])
        self.assertEqual(response.data['prediction'], expected_response['prediction'])
        self.assertEqual(response.data['scaled'], expected_response['scaled'])

    def test_diagnostic_recommendation(self):
        request = HttpRequest()
        request.data = {
            'question_level_code': 'remember',
            'marked': 1,
            'subtopic_id': 1,
            'question_id': 1
        }
        expected_response = {
            'error': '0',
            'message': 'Successful',
            'prediction': ...,
            'quiz_question': ...
        }
        response = diagnostic_recommendation(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['error'], expected_response['error'])
        self.assertEqual(response.data['message'], expected_response['message'])
        self.assertEqual(response.data['prediction'], expected_response['prediction'])
        self.assertEqual(response.data['quiz_question'], expected_response['quiz_question'])

    def test_retrieve_diagnostic_questions(self):
        request = HttpRequest()
        request.data = {
            'topic_id': 1
        }
        expected_response = {
            "questions": ...
        }
        response = retrieve_diagnostic_questions(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['questions'], expected_response['questions'])

    def test_retrieve_diagnostic_recommendation(self):
        request = HttpRequest()
        request.data = {
            'topic_id': 1,
            'answers': [...],
            'user_id': 1
        }
        expected_response = {...}
        response = retrieve_diagnostic_recommendation(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_response)

    def test_assign_user_schools(self):
        response = assign_user_schools(HttpRequest())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['school_code'], ...)

    def test_getQuestionLevelCode(self):
        self.assertEqual(getQuestionLevelCode('remember'), 1)
        self.assertEqual(getQuestionLevelCode('understand'), 2)
        self.assertEqual(getQuestionLevelCode('apply'), 3)
        self.assertEqual(getQuestionLevelCode('analyze'), 4)
        self.assertEqual(getQuestionLevelCode('evaluate'), 5)
        self.assertEqual(getQuestionLevelCode('create'), 6)
        self.assertEqual(getQuestionLevelCode('invalid'), 0)

    def test_low_level_material(self):
        questions = [...]
        prediction = 'recommend analyze questions'
        expected_response = {
            "questions": [],
            "subtopics_to_read": [...],
            "prediction": prediction
        }
        response = low_level_material(questions, prediction)
        self.assertEqual(response, expected_response)

    def test_high_level(self):
        questions = [...]
        prediction = 'recommend high level questions for passed_subtopics'
        expected_response = {
            'questions': [...],
            'subtopics_to_read': [...],
            'prediction': prediction
        }
        response = high_level(questions, prediction)
        self.assertEqual(response, expected_response)

if __name__ == '__main__':
    unittest.main()