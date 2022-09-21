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
    question_type = models.CharField(max_length=255)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)

class Subtopics(models.Model):
    class Meta:
        db_table = "subtopics"
    id = models.IntegerField(primary_key=True)
    topic_id = models.IntegerField(...)
    subtopic_name = models.CharField(max_length=255)
    subject_id = models.IntegerField(...)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)
