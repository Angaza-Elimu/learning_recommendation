from django.shortcuts import render
import pickle
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render

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
    #Open our model 
    model = pickle.load(open('diagnostic_test_recommendation.pkl','rb'))
    #obtain all form values and place them in an array, convert into integers
    int_features = [int(x) for x in request.form.values()]
    #Combine them all into a final numpy array
    final_features = [np.array(int_features)]
    #predict the price given the values inputted by user
    prediction = model.predict(final_features)
    
    
    output = prediction[0]


    predictions = {
                    'error' : '0',
                    'message' : 'Successful',
                    'prediction' : output,
                    'scaled': scaled_value
                  }

    return predictions
    
            

def testPredictionCorrect(self):
    resp = self.api_client.get('/predict', format='json')
    self.assertValidJSONResponse(resp)


#Set a post method to yield predictions on page