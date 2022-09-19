from django.shortcuts import render
from django.http import JsonResponse
import pickle
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import serializers
from django.shortcuts import render
from api import models
from django.forms.models import model_to_dict
from api import fetch_data
from sklearn.preprocessing import StandardScaler
import numpy as np
# Create your views here.

@api_view(['GET'])
def index_page(request):
    return_data = {

        "error" : "0",
        "message" : "Successful"
    }
    return Response(return_data)

@api_view(['POST'])
def classify_student_v1(request):
    try:
        resource_access = request.data.get('resource_access',None)
        announcements_view = request.data.get('announcements_view', None)
        abscence_days_from_platform = request.data.get('abscence', None)
        discussions = request.data.get('discussion', None)
        raised_hands = request.data.get('raised_hands', None)

        fields = [raised_hands,resource_access,announcements_view,discussions,abscence_days_from_platform]
        if not None in fields:
            resource_access = float(resource_access)
            announcements_view = float(announcements_view)
            abscence_days_from_platform = float(abscence_days_from_platform)
            discussions = float(discussions)
            raised_hands = float(raised_hands)
            result = [raised_hands,resource_access,announcements_view,discussions,abscence_days_from_platform]
            model_path = 'svm.sav'
            scaler_path = 'scaler.sav'
            classifier = pickle.load(open(model_path, 'rb'))
            scaler = pickle.load(open(scaler_path, 'rb'))
            scaled_value = scaler.transform([result])
            prediction = classifier.predict(scaled_value)
            predictions = {
                'error' : '0',
                'message' : 'Successful',
                'prediction' : prediction,
                'scaled': scaled_value
            }
            model_path = 'svm.sav'
            classifier = pickle.load(open(model_path, 'rb'))
        else:
            predictions = {
                'error' : '1',
                'message': 'Invalid Parameters'
            }
    except Exception as e:
        predictions = {
            'error' : '2',
            "message": str(e)
        }

    return Response(predictions)

@api_view(['POST'])
def diagnostic_recommendation(request):
    print(request.data)
    #Open our model
    model = pickle.load(open('v2_weights/quiz_recommendation.pkl','rb'))
    #obtain all form values and place them in an array, convert into integers
    question_level_code = request.data.get('question_level_code')

    marked = request.data.get('marked')

    subtopic_id = request.data.get('subtopic_id')

    question_id = request.data.get('question_id')
    # print(int_features)
    final_features = [float(question_level_code), float(marked)]
    np_array = [np.array(final_features)]

    prediction = model.predict(np_array)

    output = prediction[0]
    print(output)

    fetch_da = fetch_data.FetchData(subtopic_id)

    if output == 'recommend analyze questions':
        fetch_da.analyze_questions(mark=1)
    elif output == 'recommend create questions':
        fetch_da.create_questions(mark=1)
    elif output == 'recommend evaluate questions':
        fetch_da.evaluate_questions(mark=1)
    elif output == 'recommend understand questions':
        fetch_da.understand_questions(mark=1)
    elif output == 'recommend remember questions':
        fetch_da.remember_questions(mark=1)
    elif output == 'recommend apply questions':
        fetch_da.apply_questions(mark=1)


    fetch_da.evaluate_questions(mark=1)

    quiz_questions = list(models.QuizQuestions.objects.filter(subtopic_id = 384).values())
    # data = serializers.serialize('json', quiz_questions)
    # data = serializers.Serialize('json',quiz_questions)
    predictions = {
                    'error' : '0',
                    'message' : 'Successful',
                    'prediction' : output,
                    'quiz_question': quiz_questions
                    # 'scaled': scaled_value
                  }

    return Response(predictions)



def testPredictionCorrect(self):
    resp = self.api_client.get('/predict', format='json')
    self.assertValidJSONResponse(resp)


#Set a post method to yield predictions on page
