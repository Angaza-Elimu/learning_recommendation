#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 07:52:20 2022

@author: faithtoo
"""

#Import main library
import numpy as np

#Import Flask modules
from flask import Flask, request, render_template

#Import pickle to save our regression model
import pickle 

#Initialize Flask and set the template folder to "template"
app = Flask(__name__, template_folder = 'template')

#Open our model 
model = pickle.load(open('quiz_recommendation.pkl','rb'))

#create our "home" route using the "index.html" page
@app.route('/')
def home():
    return render_template('index.html')

#Set a post method to yield predictions on page
@app.route('/', methods = ['POST'])
def predict():
    
    #obtain all form values and place them in an array, convert into integers
    int_features = [int(x) for x in request.form.values()]
    #Combine them all into a final numpy array
    final_features = [np.array(int_features)]
    #predict the price given the values inputted by user
    prediction = model.predict(final_features)
    
    
    output = prediction[0]
    
   
#Run app
if __name__ == "__main__":
    app.run(debug=True)