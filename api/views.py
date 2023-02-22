from django.shortcuts import render
from django.http import JsonResponse
import pickle
import os
import json
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import serializers
from django.shortcuts import render
from api import models
from django.forms.models import model_to_dict
from api import fetch_data
from sklearn.preprocessing import StandardScaler
import numpy as np
import random

from django.forms.models import model_to_dict
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
    #Open our model
    model = pickle.load(open(os.path.join(settings.BASE_DIR, 'v2_weights/quiz_recommendation.pkl'),'rb'))
    #obtain all form values and place them in an array, convert into integers
    question_level_code = request.data.get('question_level_code')

    if question_level_code == 'remember':
        question_level_code = 1
    elif question_level_code == 'understand':
        question_level_code = 2
    elif question_level_code == 'apply':
        question_level_code = 3
    elif question_level_code == 'analyze':
        question_level_code = 4
    elif question_level_code == 'evaluate':
        question_level_code = 5
    elif question_level_code == 'create':
        question_level_code = 6
    else:
        question_level_code = question_level_code

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

    quiz_questions = list()

    if output == 'recommend analyze questions':
        quiz_questions = list(fetch_da.analyze_questions(marked))
    elif output == 'recommend create questions':
        quiz_questions = list(fetch_da.create_questions(marked))
    elif output == 'recommend evaluate questions':
        quiz_questions = list(fetch_da.evaluate_questions(marked))
    elif output == 'recommend understand questions':
        quiz_questions = list(fetch_da.understand_questions(marked))
    elif output == 'recommend remember questions':
        quiz_questions = list(fetch_da.remember_questions(marked))
    elif output == 'recommend apply questions':
        quiz_questions = list(fetch_da.apply_questions(marked))

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

@api_view(['POST'])
def retrieve_diagnostic_questions(request):
    topic_id =  request.data.get('topic_id')
    fetch_da = fetch_data.FetchData(topic_id)
    print(topic_id)
    subtopics = fetch_da.get_subtopics()
    print(subtopics)
    test = {
        "questions": subtopics
    }
    return Response(test)


@api_view(['POST'])
def retrieve_diagnostic_recommendation(request):
    model = pickle.load(open(os.path.join(settings.BASE_DIR, 'v2_weights/diagnostic_test_recommendation.pkl'),'rb'))
    topic_id =  request.data.get('topic_id')
    answers =  request.data.get('answers')
    total_score = len(answers)

    total_weighted_mark = 0
    for i in answers:
        print(i['marked'])
        i['weighted_mark'] = i['marked'] * getQuestionLevelCode(i['question_level'])
        total_weighted_mark += i['marked'] * getQuestionLevelCode(i['question_level'])

    score = total_weighted_mark/float(total_score)
    pred_array = [float(score)]
    prediction = model.predict([np.array(pred_array)])
    if prediction == 'recommend failed subtopic materials':
        return Response(low_level_material(answers,prediction))
    elif prediction == 'recommend high level questions for passed_subtopics':
        return Response(high_level(answers, prediction))
    else:
        return Response({})
    # score = (score - score.min()) / (score.max() - score.min())


@api_view(['POST'])
def assign_user_schools(request):
    main_school_code = 4900
    schools_without_query = models.Schools.objects.filter(school_code='').values()
    # last_school_with_query = models.Schools.objects.filter(school_code__isnull=False).order_by('-school_code').values()[0]
    # last_school_code = last_school_with_query['school_code']
    # For each schools_without_query, assign a school code
    for i in schools_without_query:
        main_school_code += 1
        print(main_school_code)
        models.Schools.objects.filter(id=i['id']).update(school_code=main_school_code)
        # replace users with school_code
        models.Users.objects.filter(school_code=i['school_name']).update(school_code=main_school_code)
    return Response({
      "school_code": main_school_code
    })



def testPredictionCorrect(self):
    resp = self.api_client.get('/predict', format='json')
    self.assertValidJSONResponse(resp)

def getQuestionLevelCode(question_code):
    if question_code == 'remember':
        return 1
    elif question_code == 'understand':
        return 2
    elif question_code == 'apply':
        return 3
    elif question_code == 'analyze':
        return 4
    elif question_code == 'evaluate':
        return 5
    elif question_code == 'create':
        return 6
    else:
        return 0


def low_level_material(questions, prediction):
    subtopic_notes = []
    for i in questions:
        subtopic = models.Subtopics.objects.filter(id=i['subtopic_id']).values()
        subtopic_notes.extend(subtopic)

    return {
        "questions": [],
        "subtopics_to_read": subtopic_notes,
        "prediction": prediction
    }
def high_level(questions,prediction):
    high_level_questions = []
    subtopic_notes = []
    for i in questions:
        print(i)
        if i['marked'] == 1:
            create_query = models.QuizQuestions.objects.filter(question_level='create', subtopic_id=i['subtopic_id']).values()
            high_level_questions.extend(create_query)
            evaluate_query= models.QuizQuestions.objects.filter(question_level='evaluate', subtopic_id=i['subtopic_id']).values()
            high_level_questions.extend(evaluate_query)
            analyze_query= models.QuizQuestions.objects.filter(question_level='analyze', subtopic_id=i['subtopic_id']).values()
            high_level_questions.extend(analyze_query)
        else:
            subtopic = models.Subtopics.objects.filter(id=i['subtopic_id']).values()
            subtopic_notes.extend(subtopic)
    return {
        'questions': high_level_questions,
        'subtopics_to_read': subtopic_notes,
        'prediction': prediction
    }
#Set a post method to yield predictions on page
