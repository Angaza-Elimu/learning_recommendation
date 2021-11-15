
### Welcome to the Angaza adaptive learning library documentation.

This project is develoeped by Angaza Elimu and provides a modernized method of categorizing students and predicting perfomance periodically
based on their engagement with the Angaza System and any other system that implements similar features.
The main objective was to build a tool that supplements the perfomance of assessment recommendations on the Angaza Elimu E-Learning Platform.

### How it works

The model is built as a standalone django application with which specific digits based on the following features are sent.
The features used in the situation are the following: - 

- Resource Access  (How much a student interacts with platform resources such as notes and assessments)
- Announcements View (Count of Student Interaction and acting on Platform Notifications)
- Absence (The number of times a student has been absent from the platform for more than x number of days)
- Discussion (The number of times a student asks questions using a discussions feature / Class Forum feature engaging with fellow classmates)


### Installation

To use the module locally run the following commands.

        git clone https://github.com/Angaza-Elimu/learning_recommendation

from there change directory to the repository's folder.

        cd learning_recommendation

and install the application dependencies from the requirements file.

        pip install -r requirements.txt

afterwards you may run the database migrations.

        python3 manage.py migrate

then run the server with the following command.

        python3 manage.py runserver


Licensed under LGPL 3.0
