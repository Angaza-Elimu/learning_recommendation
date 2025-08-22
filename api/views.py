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
from datetime import datetime

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
    user_id = request.data.get('user_id')
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

@api_view(['GET'])
def fln_angaza_quizzes(request):
    """
    Get FLN Angaza quizzes
    Optional query parameters:
    - quiz_id: Get a specific quiz by ID
    - grade_id: Filter by grade
    - lesson_id: Filter by lesson
    - quiz_type: Filter by quiz type
    """
    try:
        # Check if requesting a specific quiz
        quiz_id = request.GET.get('quiz_id')
        if quiz_id:
            try:
                quiz = models.FLNAngazaQuizzes.objects.get(id=quiz_id)
                quiz_dict = format_quiz_for_response(quiz)
                return Response({
                    'error': '0',
                    'message': 'Successful',
                    'data': [quiz_dict]  # Return as array to match existing format
                })
            except models.FLNAngazaQuizzes.DoesNotExist:
                print(f'Quiz with ID {quiz_id} not found')
                return Response({
                    'error': '1',
                    'message': f'Quiz with ID {quiz_id} not found',
                    'data': []
                }, status=404)
        
        # Get query parameters for filtering multiple quizzes
        grade_id = request.GET.get('grade_id')
        lesson_id = request.GET.get('lesson_id')
        quiz_type = request.GET.get('quiz_type')
        
        # Start with all quizzes
        quizzes = models.FLNAngazaQuizzes.objects.all()
        
        # Apply filters if provided
        if grade_id:
            quizzes = quizzes.filter(grade_id=grade_id)
        if lesson_id:
            quizzes = quizzes.filter(lesson_id=lesson_id)
        if quiz_type:
            quizzes = quizzes.filter(quiz_type=quiz_type)
            
        # Convert to list of dictionaries
        quiz_list = []
        for quiz in quizzes:
            quiz_dict = format_quiz_for_response(quiz)
            quiz_list.append(quiz_dict)
            
        return Response({
            'error': '0',
            'message': 'Successful',
            'data': quiz_list
        })
        
    except Exception as e:
        print("Error details:", str(e))
        import traceback
        print("Full traceback:", traceback.format_exc())
        return Response({
            'error': '1',
            'message': str(e)
        }, status=500)

def format_quiz_for_response(quiz):
    """Helper function to format a quiz for API response"""
    # Parse options
    options = json.loads(quiz.options) if isinstance(quiz.options, str) else quiz.options
    formatted_options = []
    
    # Transform options to match expected format
    for opt in options:
        formatted_option = {
            'id': opt.get('label', ''),
            'src': opt.get('src', ''),
            'label': opt.get('label', ''),
            'text': opt.get('text', ''),
            'is_correct': opt.get('is_correct', False),
            'content': opt.get('text', ''),
            'option_sound': opt.get('option_sound'),
        }
        formatted_options.append(formatted_option)

    return {
        'id': str(quiz.id),
        'question_type': quiz.question_type,
        'question': quiz.question,
        'question_sound': quiz.question_sound,
        'answer_sound': quiz.answer_sound,
        'hint': quiz.hint,
        'options': formatted_options,
        'taxonomy_tag': quiz.taxonomy_tag,
        'strand_id': quiz.strand_id,
        'substrand_id': quiz.substrand_id
    }

@api_view(['POST'])
def fln_diagnostic_quizzes(request):
    """
    Get diagnostic quizzes from FLN Angaza table
    Required parameters:
    - grade_id: Grade ID
    Optional parameters:
    - strand_id: Filter by strand
    - substrand_id: Filter by substrand
    - lesson_id: Filter by lesson
    - limit: Number of questions to return (default: 5)
    """
    try:
        # Get required parameters
        grade_id = request.data.get('grade_id')
        print('Received request for grade_id:', grade_id)
        print('Request data:', request.data)
        print('Request headers:', request.headers)
        
        if not grade_id:
            return Response({
                'error': '1',
                'message': 'grade_id is required'
            }, status=400)

        # Start with diagnostic quizzes for the specified grade
        quizzes = models.FLNAngazaQuizzes.objects.filter(
            grade_id=grade_id,
            quiz_type='starter_quiz'
        )
        print('Found quizzes count:', quizzes.count())
        
        if quizzes.count() == 0:
            print(f'No quizzes found for grade_id: {grade_id}')
            # Check what grades have quizzes
            available_grades = models.FLNAngazaQuizzes.objects.values_list('grade_id', flat=True).distinct()
            print('Available grades with quizzes:', list(available_grades))
            return Response({
                'error': '0',
                'message': f'No quizzes found for grade {grade_id}. Available grades: {list(available_grades)}',
                'data': []
            })

        # Get optional parameters
        strand_id = request.data.get('strand_id')
        substrand_id = request.data.get('substrand_id')
        lesson_id = request.data.get('lesson_id')
        limit = int(request.data.get('limit', 5))  # Default to 5 questions

        # Apply additional filters if provided
        if strand_id:
            quizzes = quizzes.filter(strand_id=strand_id)
        if substrand_id:
            quizzes = quizzes.filter(substrand_id=substrand_id)
        if lesson_id:
            quizzes = quizzes.filter(lesson_id=lesson_id)

        # Randomly select 'limit' number of questions
        quizzes = list(quizzes)
        selected_quizzes = random.sample(quizzes, min(limit, len(quizzes)))

        # Convert to list of dictionaries
        quiz_list = []
        for quiz in selected_quizzes:
            quiz_dict = format_quiz_for_response(quiz)
            quiz_list.append(quiz_dict)

        return Response({
            'error': '0',
            'message': 'Successful',
            'total_available': len(quizzes),
            'questions_returned': len(quiz_list),
            'data': quiz_list
        })

    except Exception as e:
        print("Error details:", str(e))
        import traceback
        print("Full traceback:", traceback.format_exc())
        return Response({
            'error': '1',
            'message': str(e)
        }, status=500)

@api_view(['POST'])
def fln_diagnostic_recommendation(request):
    """
    Get recommendations based on FLN diagnostic quiz answers
    Required parameters:
    - grade_id: Grade ID
    - answers: Array of objects containing:
        - question_id: ID of the question
        - marked: 1 if correct, 0 if incorrect
        - taxonomy_tag: Level of the question (remember, understand, etc.)
    """
    try:
        # Get required parameters
        grade_id = request.data.get('grade_id')
        answers = request.data.get('answers')
        
        if not grade_id or not answers:
            return Response({
                'error': '1',
                'message': 'grade_id and answers are required'
            }, status=400)

        # Calculate weighted score like in the original endpoint
        total_score = len(answers)
        total_weighted_mark = 0
        
        for answer in answers:
            marked = answer.get('marked', 0)
            taxonomy_tag = answer.get('taxonomy_tag', 'remember')
            weighted_mark = marked * getQuestionLevelCode(taxonomy_tag)
            total_weighted_mark += weighted_mark
            answer['weighted_mark'] = weighted_mark

        if total_score > 0:
            score = total_weighted_mark / float(total_score)
        else:
            score = 0

        # Determine recommendation based on score
        if score < 0.6:  # If score is less than 60%
            # Get remedial content
            return Response(fln_low_level_material(answers, grade_id))
        else:
            # Get advanced content
            return Response(fln_high_level(answers, grade_id))

    except Exception as e:
        print("Error details:", str(e))
        import traceback
        print("Full traceback:", traceback.format_exc())
        return Response({
            'error': '1',
            'message': str(e)
        }, status=500)

def fln_low_level_material(answers, grade_id):
    """Get remedial content for failed questions"""
    # Get questions for concepts that need reinforcement
    remedial_questions = []
    
    # Get unique substrand_ids from answers
    substrand_ids = set()
    for answer in answers:
        if answer.get('marked', 0) == 0:  # If question was answered incorrectly
            substrand_id = answer.get('substrand_id')
            if substrand_id:
                substrand_ids.add(substrand_id)
    
    print(f"Found {len(substrand_ids)} substrands with incorrect answers")
    
    # If no substrand_ids found, get general remedial questions
    if not substrand_ids:
        questions = models.FLNAngazaQuizzes.objects.filter(
            grade_id=grade_id,
            quiz_type='starter_quiz',
            taxonomy_tag__in=['remember', 'understand']
        ).order_by('?')[:5]  # Get 5 random basic questions
        
        print(f"No specific substrands found, getting {questions.count()} general remedial questions")
    else:
        # Get remedial questions for each failed substrand
        for substrand_id in substrand_ids:
            questions = models.FLNAngazaQuizzes.objects.filter(
                grade_id=grade_id,
                quiz_type='starter_quiz',
                taxonomy_tag__in=['remember', 'understand'],
                substrand_id=substrand_id
            ).order_by('?')[:2]  # Get 2 random questions per substrand
            
            print(f"Found {questions.count()} questions for substrand {substrand_id}")
            
            for question in questions:
                question_dict = {
                    'id': question.id,
                    'question': question.question,
                    'question_type': question.question_type,
                    'options': json.loads(question.options) if isinstance(question.options, str) else question.options,
                    'question_sound': question.question_sound,
                    'answer_sound': question.answer_sound,
                    'hint': question.hint,
                    'taxonomy_tag': question.taxonomy_tag,
                    'strand_id': question.strand_id,
                    'substrand_id': question.substrand_id
                }
                remedial_questions.append(question_dict)

    # If still no questions found, get basic questions without substrand filter
    if not remedial_questions:
        print("No specific remedial questions found, getting basic questions")
        questions = models.FLNAngazaQuizzes.objects.filter(
            grade_id=grade_id,
            quiz_type='starter_quiz',
            taxonomy_tag='remember'
        ).order_by('?')[:5]
        
        for question in questions:
            question_dict = {
                'id': question.id,
                'question': question.question,
                'question_type': question.question_type,
                'options': json.loads(question.options) if isinstance(question.options, str) else question.options,
                'question_sound': question.question_sound,
                'answer_sound': question.answer_sound,
                'hint': question.hint,
                'taxonomy_tag': question.taxonomy_tag,
                'strand_id': question.strand_id,
                'substrand_id': question.substrand_id
            }
            remedial_questions.append(question_dict)

    print(f"Returning {len(remedial_questions)} remedial questions")
    
    return {
        'error': '0',
        'recommendation_type': 'remedial',
        'message': 'Practice these concepts to improve understanding',
        'questions': remedial_questions
    }

def fln_high_level(answers, grade_id):
    """Get advanced content for successful students"""
    print(f"Getting advanced questions for grade {grade_id}")
    print(f"Received {len(answers)} answers")
    
    MIN_QUESTIONS = 3  # Minimum number of questions to return
    advanced_questions = []
    
    # First try to get advanced questions (analyze, evaluate, create)
    available_questions = models.FLNAngazaQuizzes.objects.filter(
        grade_id=grade_id,
        quiz_type='starter_quiz',
        taxonomy_tag__in=['analyze', 'evaluate', 'create']
    )
    print(f"Found {available_questions.count()} total advanced questions for grade {grade_id}")
    
    # Get unique substrand_ids from correct answers
    substrand_ids = set()
    for answer in answers:
        if answer.get('marked', 1) == 1:  # If question was answered correctly
            substrand_id = answer.get('substrand_id')
            if substrand_id:
                substrand_ids.add(substrand_id)
    
    print(f"Found {len(substrand_ids)} substrands with correct answers: {substrand_ids}")
    
    # Get questions for each substrand
    for substrand_id in substrand_ids:
        questions = models.FLNAngazaQuizzes.objects.filter(
            grade_id=grade_id,
            quiz_type='starter_quiz',
            taxonomy_tag__in=['analyze', 'evaluate', 'create'],
            substrand_id=substrand_id
        ).order_by('?')[:2]  # Get 2 random questions
        
        print(f"Found {questions.count()} questions for substrand {substrand_id}")
        
        for question in questions:
            question_dict = format_quiz_for_response(question)
            advanced_questions.append(question_dict)
    
    # If we don't have enough questions, try getting any advanced questions without substrand filter
    if len(advanced_questions) < MIN_QUESTIONS:
        remaining = MIN_QUESTIONS - len(advanced_questions)
        print(f"Need {remaining} more questions, getting general advanced questions")
        
        # Exclude questions we already have
        existing_ids = [q['id'] for q in advanced_questions]
        questions = models.FLNAngazaQuizzes.objects.filter(
            grade_id=grade_id,
            quiz_type='starter_quiz',
            taxonomy_tag__in=['analyze', 'evaluate', 'create']
        ).exclude(
            id__in=existing_ids
        ).order_by('?')[:remaining]
        
        print(f"Found {questions.count()} additional advanced questions")
        
        for question in questions:
            question_dict = format_quiz_for_response(question)
            advanced_questions.append(question_dict)
    
    # If we still don't have enough questions, get 'apply' level questions
    if len(advanced_questions) < MIN_QUESTIONS:
        remaining = MIN_QUESTIONS - len(advanced_questions)
        print(f"Still need {remaining} more questions, getting 'apply' level questions")
        
        existing_ids = [q['id'] for q in advanced_questions]
        questions = models.FLNAngazaQuizzes.objects.filter(
            grade_id=grade_id,
            quiz_type='starter_quiz',
            taxonomy_tag='apply'
        ).exclude(
            id__in=existing_ids
        ).order_by('?')[:remaining]
        
        print(f"Found {questions.count()} 'apply' level questions")
        
        for question in questions:
            question_dict = format_quiz_for_response(question)
            advanced_questions.append(question_dict)
    
    # If we still don't have enough questions, get the highest level questions available
    if len(advanced_questions) < MIN_QUESTIONS:
        remaining = MIN_QUESTIONS - len(advanced_questions)
        print(f"Still need {remaining} more questions, getting highest level available")
        
        # Get all available taxonomy levels for this grade
        available_tags = list(models.FLNAngazaQuizzes.objects.filter(
            grade_id=grade_id,
            quiz_type='starter_quiz'
        ).values_list('taxonomy_tag', flat=True).distinct())
        
        print(f"Available taxonomy tags: {available_tags}")
        
        if available_tags:
            # Sort tags by difficulty level
            available_tags.sort(key=lambda x: getQuestionLevelCode(x), reverse=True)
            
            # Try each level in descending order until we have enough questions
            existing_ids = [q['id'] for q in advanced_questions]
            
            for tag in available_tags:
                if len(advanced_questions) >= MIN_QUESTIONS:
                    break
                    
                print(f"Trying to get questions with tag: {tag}")
                questions = models.FLNAngazaQuizzes.objects.filter(
                    grade_id=grade_id,
                    quiz_type='starter_quiz',
                    taxonomy_tag=tag
                ).exclude(
                    id__in=existing_ids
                ).order_by('?')[:remaining]
                
                print(f"Found {questions.count()} questions at {tag} level")
                
                for question in questions:
                    question_dict = format_quiz_for_response(question)
                    advanced_questions.append(question_dict)
                    existing_ids.append(question_dict['id'])
                
                remaining = MIN_QUESTIONS - len(advanced_questions)
    
    print(f"Returning {len(advanced_questions)} total questions with taxonomy levels: {[q['taxonomy_tag'] for q in advanced_questions]}")
    
    return {
        'error': '0',
        'recommendation_type': 'advanced',
        'message': 'Try these challenging questions to further develop your skills',
        'questions': advanced_questions
    }

@api_view(['POST'])
def save_user_response(request):
    """
    Save user's quiz response
    Required parameters:
    - user_id: User ID
    - quiz_id: Quiz ID
    - selected_option: Selected option label
    - is_correct: Whether the answer was correct
    - grade_id: Grade ID
    - quiz_type: Type of quiz (e.g., 'starter_quiz')
    Optional parameters:
    - strand_id: Strand ID
    - substrand_id: Substrand ID
    - lesson_id: Lesson ID
    - taxonomy_tag: Taxonomy level
    - response_time: Time taken to answer in seconds
    - device_info: Device information as JSON
    """
    try:
        # Get required parameters
        user_id = request.data.get('user_id')
        quiz_id = request.data.get('quiz_id')
        selected_option = request.data.get('selected_option')
        is_correct = request.data.get('is_correct')
        grade_id = request.data.get('grade_id')
        quiz_type = request.data.get('quiz_type')

        if not all([user_id, quiz_id, selected_option, is_correct is not None, grade_id, quiz_type]):
            return Response({
                'error': '1',
                'message': 'Missing required parameters'
            }, status=400)

        # Create user response
        response = models.FLNUserResponses.objects.create(
            user_id=user_id,
            quiz_id=quiz_id,
            selected_option=selected_option,
            is_correct=is_correct,
            grade_id=grade_id,
            quiz_type=quiz_type,
            # Optional fields
            strand_id=request.data.get('strand_id'),
            substrand_id=request.data.get('substrand_id'),
            lesson_id=request.data.get('lesson_id'),
            taxonomy_tag=request.data.get('taxonomy_tag'),
            response_time=request.data.get('response_time'),
            device_info=request.data.get('device_info')
        )

        return Response({
            'error': '0',
            'message': 'Response saved successfully',
            'response_id': response.id
        })

    except Exception as e:
        print("Error details:", str(e))
        import traceback
        print("Full traceback:", traceback.format_exc())
        return Response({
            'error': '1',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
def get_user_threshold(request):
    """
    Get a user's recommendation threshold
    Required query parameters:
    - user_id: User ID
    - quiz_type: Type of quiz (e.g., 'starter_quiz')
    """
    try:
        user_id = request.GET.get('user_id')
        quiz_type = request.GET.get('quiz_type')

        if not user_id or not quiz_type:
            return Response({
                'error': '1',
                'message': 'user_id and quiz_type are required'
            }, status=400)

        # Get or create threshold
        threshold, created = models.FLNUserThresholds.objects.get_or_create(
            user_id=user_id,
            quiz_type=quiz_type,
            defaults={'recommendation_threshold': 0.6}  # Default threshold
        )

        return Response({
            'error': '0',
            'message': 'Threshold retrieved successfully',
            'data': {
                'user_id': threshold.user_id,
                'quiz_type': threshold.quiz_type,
                'threshold': threshold.recommendation_threshold,
                'created_at': threshold.created_at,
                'updated_at': threshold.updated_at
            }
        })

    except Exception as e:
        print("Error details:", str(e))
        import traceback
        print("Full traceback:", traceback.format_exc())
        return Response({
            'error': '1',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
def get_threshold_history(request):
    """
    Get threshold change history for a user
    Required query parameters:
    - user_id: User ID
    - quiz_type: Type of quiz (e.g., 'starter_quiz')
    Optional parameters:
    - limit: Number of history entries to return (default: 10)
    - from_date: Filter changes from this date (YYYY-MM-DD)
    - to_date: Filter changes to this date (YYYY-MM-DD)
    """
    try:
        user_id = request.GET.get('user_id')
        quiz_type = request.GET.get('quiz_type')
        limit = int(request.GET.get('limit', 10))
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')

        if not user_id or not quiz_type:
            return Response({
                'error': '1',
                'message': 'user_id and quiz_type are required'
            }, status=400)

        # Build query
        history_query = models.FLNUserThresholdHistory.objects.filter(
            user_id=user_id,
            quiz_type=quiz_type
        ).order_by('-created_at')

        if from_date:
            try:
                from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                history_query = history_query.filter(created_at__date__gte=from_date)
            except ValueError:
                return Response({
                    'error': '1',
                    'message': 'from_date must be in YYYY-MM-DD format'
                }, status=400)

        if to_date:
            try:
                to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
                history_query = history_query.filter(created_at__date__lte=to_date)
            except ValueError:
                return Response({
                    'error': '1',
                    'message': 'to_date must be in YYYY-MM-DD format'
                }, status=400)

        # Get current threshold
        current_threshold = get_user_recommendation_threshold(user_id, quiz_type)

        # Get history entries
        history = history_query[:limit]
        history_list = [{
            'old_threshold': entry.old_threshold,
            'new_threshold': entry.new_threshold,
            'reason': entry.reason,
            'created_by': entry.created_by,
            'created_at': entry.created_at
        } for entry in history]

        return Response({
            'error': '0',
            'message': 'History retrieved successfully',
            'data': {
                'current_threshold': current_threshold,
                'history': history_list,
                'total_changes': history_query.count(),
                'changes_shown': len(history_list)
            }
        })

    except Exception as e:
        print("Error details:", str(e))
        import traceback
        print("Full traceback:", traceback.format_exc())
        return Response({
            'error': '1',
            'message': str(e)
        }, status=500)

@api_view(['POST'])
def update_user_threshold(request):
    """
    Update a user's recommendation threshold
    Required parameters:
    - user_id: User ID
    - quiz_type: Type of quiz (e.g., 'starter_quiz')
    - threshold: New threshold value (between 0 and 1)
    Optional parameters:
    - reason: Reason for the change
    - created_by: Who made the change
    """
    try:
        user_id = request.data.get('user_id')
        quiz_type = request.data.get('quiz_type')
        threshold = request.data.get('threshold')
        reason = request.data.get('reason')
        created_by = request.data.get('created_by')

        if not all([user_id, quiz_type, threshold is not None]):
            return Response({
                'error': '1',
                'message': 'user_id, quiz_type, and threshold are required'
            }, status=400)

        try:
            threshold = float(threshold)
        except (TypeError, ValueError):
            return Response({
                'error': '1',
                'message': 'threshold must be a number between 0 and 1'
            }, status=400)

        if not 0 <= threshold <= 1:
            return Response({
                'error': '1',
                'message': 'threshold must be between 0 and 1'
            }, status=400)

        # Get or create threshold object
        threshold_obj, created = models.FLNUserThresholds.objects.get_or_create(
            user_id=user_id,
            quiz_type=quiz_type,
            defaults={'recommendation_threshold': threshold}
        )

        if not created:
            # Record change in history before updating
            old_threshold = threshold_obj.recommendation_threshold
            threshold_obj.recommendation_threshold = threshold
            threshold_obj.save()
            threshold_obj.record_change(old_threshold, reason, created_by)
        else:
            # Record initial threshold setting
            threshold_obj.record_change(0.6, "Initial threshold setting" if not reason else reason, created_by)

        return Response({
            'error': '0',
            'message': 'Threshold updated successfully',
            'data': {
                'user_id': threshold_obj.user_id,
                'quiz_type': threshold_obj.quiz_type,
                'threshold': threshold_obj.recommendation_threshold,
                'created_at': threshold_obj.created_at,
                'updated_at': threshold_obj.updated_at
            }
        })

    except Exception as e:
        print("Error details:", str(e))
        import traceback
        print("Full traceback:", traceback.format_exc())
        return Response({
            'error': '1',
            'message': str(e)
        }, status=500)

def get_user_recommendation_threshold(user_id, quiz_type):
    """Helper function to get a user's recommendation threshold"""
    try:
        threshold = models.FLNUserThresholds.objects.get(
            user_id=user_id,
            quiz_type=quiz_type
        )
        return threshold.recommendation_threshold
    except models.FLNUserThresholds.DoesNotExist:
        return 0.6  # Default threshold

@api_view(['POST'])
def get_user_recommendations(request):
    """
    Get personalized recommendations based on user's quiz responses
    Required parameters:
    - user_id: User ID
    - quiz_type: Type of quiz (e.g., 'starter_quiz', 'diagnostic_quiz')
    - grade_id: Grade ID
    Optional parameters:
    - limit: Number of responses to consider (default: 10)
    - strand_id: Filter by strand
    - substrand_id: Filter by substrand
    """
    try:
        # Get required parameters
        user_id = request.data.get('user_id')
        quiz_type = request.data.get('quiz_type')
        grade_id = request.data.get('grade_id')

        if not all([user_id, quiz_type, grade_id]):
            return Response({
                'error': '1',
                'message': 'user_id, quiz_type, and grade_id are required'
            }, status=400)

        # Get optional parameters
        limit = int(request.data.get('limit', 10))
        strand_id = request.data.get('strand_id')
        substrand_id = request.data.get('substrand_id')

        # Build the query
        responses_query = models.FLNUserResponses.objects.filter(
            user_id=user_id,
            quiz_type=quiz_type,
            grade_id=grade_id
        )

        if strand_id:
            responses_query = responses_query.filter(strand_id=strand_id)
        if substrand_id:
            responses_query = responses_query.filter(substrand_id=substrand_id)

        # Get the most recent responses
        responses = list(responses_query.order_by('-created_at')[:limit])
        print(f"Found {len(responses)} responses for user {user_id}")

        if not responses:
            # If no responses found, get starter questions
            questions_query = models.FLNAngazaQuizzes.objects.filter(
                grade_id=grade_id,
                quiz_type='starter_quiz',
                taxonomy_tag='remember'
            )
            
            if substrand_id:
                questions_query = questions_query.filter(substrand_id=substrand_id)
            if strand_id:
                questions_query = questions_query.filter(strand_id=strand_id)
            
            questions = list(questions_query.order_by('?')[:5])  # Get 5 random starter questions
            print(f"No responses found, returning {len(questions)} starter questions")
            
            question_list = [{
                'id': q.id,
                'question': q.question,
                'question_type': q.question_type,
                'options': json.loads(q.options) if isinstance(q.options, str) else q.options,
                'question_sound': q.question_sound,
                'answer_sound': q.answer_sound,
                'hint': q.hint,
                'taxonomy_tag': q.taxonomy_tag,
                'strand_id': q.strand_id,
                'substrand_id': q.substrand_id
            } for q in questions]

            return Response({
                'error': '0',
                'message': 'No previous responses found. Starting with basic questions.',
                'recommendation_type': 'starter',
                'questions': question_list
            })

        # Calculate performance metrics
        total_questions = len(responses)
        correct_answers = sum(1 for r in responses if r.is_correct)
        performance_rate = correct_answers / total_questions if total_questions > 0 else 0
        print(f"Performance rate: {performance_rate}")

        # Calculate weighted score
        total_weighted_mark = 0
        answers = []  # Prepare answers array for recommendation functions
        
        for response in responses:
            taxonomy_tag = response.taxonomy_tag or 'remember'
            marked = 1 if response.is_correct else 0
            weighted_mark = marked * getQuestionLevelCode(taxonomy_tag)
            total_weighted_mark += weighted_mark
            
            # Add to answers array
            answers.append({
                'marked': marked,
                'taxonomy_tag': taxonomy_tag,
                'substrand_id': response.substrand_id
            })

        score = total_weighted_mark / float(total_questions) if total_questions > 0 else 0
        print(f"Weighted score: {score}")

        # Get user's threshold
        threshold = get_user_recommendation_threshold(user_id, quiz_type)
        print(f"Using threshold {threshold} for user {user_id}")

        # Get recommended questions based on the score
        if score < threshold:  # Use user's threshold instead of hardcoded 0.6
            print(f"Score {score} < threshold {threshold}, getting remedial questions")
            response_data = fln_low_level_material(answers, grade_id)
        else:
            print(f"Score {score} >= threshold {threshold}, getting advanced questions")
            response_data = fln_high_level(answers, grade_id)

        # Add performance analytics to the response
        response_data.update({
            'performance_analytics': {
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'performance_rate': performance_rate,
                'weighted_score': score,
                'threshold': threshold  # Include threshold in response
            }
        })

        print(f"Returning {len(response_data.get('questions', []))} recommended questions")
        return Response(response_data)

    except Exception as e:
        print("Error details:", str(e))
        import traceback
        print("Full traceback:", traceback.format_exc())
        return Response({
            'error': '1',
            'message': str(e)
        }, status=500)

def getAverageQuestionLevel(taxonomy_performance):
    """Calculate average question level from taxonomy performance"""
    if not taxonomy_performance:
        return 1  # Default to lowest level if no data
    
    total_weight = 0
    total_questions = 0
    
    for tag, stats in taxonomy_performance.items():
        level = getQuestionLevelCode(tag)
        total_weight += level * stats['total']
        total_questions += stats['total']
    
    return total_weight / total_questions if total_questions > 0 else 1

def threshold_manager(request):
    """Serve the threshold manager HTML page"""
    return render(request, 'api/threshold_manager.html')

@api_view(['GET'])
def get_quiz_by_id(request, quiz_id):
    """
    Get a specific quiz question by ID
    URL parameter:
    - quiz_id: ID of the quiz question to fetch
    """
    try:
        quiz = models.FLNAngazaQuizzes.objects.get(id=quiz_id)
        
        quiz_data = {
            'id': quiz.id,
            'question': quiz.question,
            'question_type': quiz.question_type,
            'options': json.loads(quiz.options) if isinstance(quiz.options, str) else quiz.options,
            'question_sound': quiz.question_sound,
            'answer_sound': quiz.answer_sound,
            'hint': quiz.hint,
            'taxonomy_tag': quiz.taxonomy_tag,
            'strand_id': quiz.strand_id,
            'substrand_id': quiz.substrand_id,
            'grade_id': quiz.grade_id,
            'quiz_type': quiz.quiz_type,
            'lesson_id': quiz.lesson_id
        }

        return Response({
            'error': '0',
            'message': 'Quiz retrieved successfully',
            'data': quiz_data
        })

    except models.FLNAngazaQuizzes.DoesNotExist:
        return Response({
            'error': '1',
            'message': f'Quiz with ID {quiz_id} not found'
        }, status=404)
    except Exception as e:
        print("Error details:", str(e))
        import traceback
        print("Full traceback:", traceback.format_exc())
        return Response({
            'error': '1',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
def get_user_responses(request):
    """
    Get user responses with filtering options
    Required parameters:
    - user_id: User ID
    Optional parameters:
    - quiz_type: Filter by quiz type (e.g., 'starter_quiz')
    - from_date: Filter responses from this date (YYYY-MM-DD)
    - to_date: Filter responses to this date (YYYY-MM-DD)
    - grade_id: Filter by grade
    - strand_id: Filter by strand
    - substrand_id: Filter by substrand
    - is_correct: Filter by correctness (true/false)
    - limit: Number of responses to return (default: 50)
    """
    try:
        # Get required parameters
        user_id = request.GET.get('user_id')
        if not user_id:
            return Response({
                'error': '1',
                'message': 'user_id is required'
            }, status=400)

        # Build query
        responses_query = models.FLNUserResponses.objects.filter(
            user_id=user_id
        ).order_by('-created_at')

        # Apply optional filters
        quiz_type = request.GET.get('quiz_type')
        if quiz_type:
            responses_query = responses_query.filter(quiz_type=quiz_type)

        from_date = request.GET.get('from_date')
        if from_date:
            try:
                from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                responses_query = responses_query.filter(created_at__date__gte=from_date)
            except ValueError:
                return Response({
                    'error': '1',
                    'message': 'from_date must be in YYYY-MM-DD format'
                }, status=400)

        to_date = request.GET.get('to_date')
        if to_date:
            try:
                to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
                responses_query = responses_query.filter(created_at__date__lte=to_date)
            except ValueError:
                return Response({
                    'error': '1',
                    'message': 'to_date must be in YYYY-MM-DD format'
                }, status=400)

        grade_id = request.GET.get('grade_id')
        if grade_id:
            responses_query = responses_query.filter(grade_id=grade_id)

        strand_id = request.GET.get('strand_id')
        if strand_id:
            responses_query = responses_query.filter(strand_id=strand_id)

        substrand_id = request.GET.get('substrand_id')
        if substrand_id:
            responses_query = responses_query.filter(substrand_id=substrand_id)

        is_correct = request.GET.get('is_correct')
        if is_correct is not None:
            is_correct = is_correct.lower() == 'true'
            responses_query = responses_query.filter(is_correct=is_correct)

        # Apply limit
        limit = int(request.GET.get('limit', 50))
        responses = responses_query[:limit]

        # Prepare response data
        response_list = []
        for response in responses:
            # Get the associated quiz question
            try:
                quiz = models.FLNAngazaQuizzes.objects.get(id=response.quiz_id)
                quiz_data = {
                    'id': quiz.id,
                    'question': quiz.question,
                    'question_type': quiz.question_type,
                    'options': json.loads(quiz.options) if isinstance(quiz.options, str) else quiz.options,
                    'taxonomy_tag': quiz.taxonomy_tag
                }
            except models.FLNAngazaQuizzes.DoesNotExist:
                quiz_data = None

            response_data = {
                'id': response.id,
                'quiz_id': response.quiz_id,
                'selected_option': response.selected_option,
                'is_correct': response.is_correct,
                'attempt_number': response.attempt_number,
                'response_time': response.response_time,
                'created_at': response.created_at,
                'quiz_type': response.quiz_type,
                'grade_id': response.grade_id,
                'strand_id': response.strand_id,
                'substrand_id': response.substrand_id,
                'lesson_id': response.lesson_id,
                'taxonomy_tag': response.taxonomy_tag,
                'quiz_details': quiz_data
            }
            response_list.append(response_data)

        # Calculate summary statistics
        total_responses = len(response_list)
        correct_responses = sum(1 for r in response_list if r['is_correct'])
        accuracy_rate = correct_responses / total_responses if total_responses > 0 else 0

        # Group by taxonomy tag
        taxonomy_performance = {}
        for response in response_list:
            tag = response.get('taxonomy_tag')
            if tag:
                if tag not in taxonomy_performance:
                    taxonomy_performance[tag] = {
                        'total': 0,
                        'correct': 0
                    }
                taxonomy_performance[tag]['total'] += 1
                if response['is_correct']:
                    taxonomy_performance[tag]['correct'] += 1

        return Response({
            'error': '0',
            'message': 'Responses retrieved successfully',
            'data': {
                'responses': response_list,
                'summary': {
                    'total_responses': total_responses,
                    'correct_responses': correct_responses,
                    'accuracy_rate': accuracy_rate,
                    'taxonomy_performance': {
                        tag: {
                            'total': stats['total'],
                            'correct': stats['correct'],
                            'accuracy_rate': stats['correct'] / stats['total'] if stats['total'] > 0 else 0
                        }
                        for tag, stats in taxonomy_performance.items()
                    }
                }
            }
        })

    except Exception as e:
        print("Error details:", str(e))
        import traceback
        print("Full traceback:", traceback.format_exc())
        return Response({
            'error': '1',
            'message': str(e)
        }, status=500)

@api_view(['POST'])
def fln_quiz_by_id(request):
    """
    Get a single FLN Angaza quiz by ID
    Required parameters:
    - quiz_id: Quiz ID
    """
    try:
        quiz_id = request.data.get('quiz_id')
        print('Fetching quiz with ID:', quiz_id)
        
        if not quiz_id:
            return Response({
                'error': '1',
                'message': 'quiz_id is required'
            }, status=400)

        try:
            quiz = models.FLNAngazaQuizzes.objects.get(id=quiz_id)
        except models.FLNAngazaQuizzes.DoesNotExist:
            print(f'Quiz with ID {quiz_id} not found')
            return Response({
                'error': '1',
                'message': f'Quiz with ID {quiz_id} not found',
                'data': []
            }, status=404)

        # Parse options
        options = json.loads(quiz.options) if isinstance(quiz.options, str) else quiz.options
        formatted_options = []
        
        # Transform options to match expected format
        for opt in options:
            formatted_option = {
                'id': opt.get('label', ''),
                'src': opt.get('src', ''),
                'label': opt.get('label', ''),
                'text': opt.get('text', ''),
                'is_correct': opt.get('is_correct', False),
                'content': opt.get('text', ''),
                'option_sound': opt.get('option_sound'),
            }
            formatted_options.append(formatted_option)

        quiz_dict = {
            'id': str(quiz.id),
            'question_type': quiz.question_type,
            'question': quiz.question,
            'question_sound': quiz.question_sound,
            'answer_sound': quiz.answer_sound,
            'hint': quiz.hint,
            'options': formatted_options,
            'taxonomy_tag': quiz.taxonomy_tag,
            'strand_id': quiz.strand_id,
            'substrand_id': quiz.substrand_id
        }

        print('Returning quiz:', quiz_dict)
        return Response({
            'error': '0',
            'message': 'Successful',
            'data': [quiz_dict]  # Return as array to match existing format
        })

    except Exception as e:
        print("Error details:", str(e))
        import traceback
        print("Full traceback:", traceback.format_exc())
        return Response({
            'error': '1',
            'message': str(e)
        }, status=500)
