from django.db import models
import json

# Create your models here.
class QuizQuestions(models.Model):
    class Meta:
        db_table = "quizq_questions"
    subtopic_id = models.CharField(max_length=255)
    subject_id = models.IntegerField(...)
    question = models.CharField(max_length=255)
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    option_a_explanation = models.CharField(max_length=255)
    option_b_explanation = models.CharField(max_length=255)
    option_c_explanation = models.CharField(max_length=255)
    option_d_explanation = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    additional_notes = models.CharField(max_length=255)
    created_at = models.DateField(...)
    question_level = models.CharField(max_length=255)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)

class StrandActivities(models.Model):
    class Meta:
        db_table = "strand_activities_assessments"
    subtopic_id = models.CharField(max_length=255)
    subject_id = models.IntegerField(...)
    score = models.IntegerField(...)
    topic_id =  models.IntegerField(...)
    class_id = models.IntegerField(name="class")
    taxonomy_tag = models.CharField(max_length=255)
    explanation = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    key_word = models.CharField(max_length=255)
    question = models.CharField(max_length=255)
    created_at = models.DateField(...)
    updated_at = models.DateField(...)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)

class SubStrands(models.Model):
    class Meta:
        db_table = "sub_strands"
    id = models.IntegerField(primary_key=True)
    topic_id = models.IntegerField(name="strand_id")
    subtopic_name = models.CharField(max_length=255, name="sub_strand_name")
    subject_id = models.IntegerField(name="course_id")

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)


# class Subtopics(models.Model):
#     class Meta:
#         db_table = "subtopics"
#     id = models.IntegerField(primary_key=True)
#     topic_id = models.IntegerField(...)
#     subtopic_name = models.CharField(max_length=255)
#     subject_id = models.IntegerField(...)

#     def toJSON(self):
#         return json.dumps(self, default=lambda o: o.__dict__,
#             sort_keys=True, indent=4)

class QuestionAnswers(models.Model):
    class Meta:
        db_table = 'question_answers'

    question_id = models.IntegerField(...)
    subtopic_id = models.IntegerField(...)
    subject_id = models.IntegerField(...)
    quiz_id = models.IntegerField(...)
    student_id = models.IntegerField(...)

class Schools(models.Model):
    class Meta:
        db_table = 'schools'
    school_name = models.CharField(max_length=255)
    school_code = models.CharField(max_length=255)
    county_id = models.IntegerField(...)

class Users(models.Model):
    class Meta:
        db_table = 'users'
    
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    school_code = models.CharField(max_length=255)
    password = models.CharField(max_length=255)


