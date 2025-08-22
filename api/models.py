from django.db import models
import json

# Create your models here.
class QuizQuestions(models.Model):
    class Meta:
        db_table = "quizq_questions"
        managed = False  # Set to False since table already exists
    subtopic_id = models.CharField(max_length=255)
    subject_id = models.IntegerField(null=True)
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
    created_at = models.DateField(auto_now_add=True)
    question_level = models.CharField(max_length=255)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)

class StrandActivities(models.Model):
    class Meta:
        db_table = "strand_activities_assessments"
        managed = False  # Set to False since table already exists
    id  = models.IntegerField(primary_key=True)
    subtopic_id = models.CharField(max_length=255)
    subject_id = models.IntegerField(null=True)
    score = models.IntegerField(null=True)
    topic_id = models.IntegerField(null=True)
    class_id = models.IntegerField(name="class")
    taxonomy_tag = models.CharField(max_length=255)
    explanation = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    key_word = models.CharField(max_length=255)
    question = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)

class Subtopics(models.Model):
    class Meta:
        db_table = "subtopics"
        managed = False  # Set to False since table already exists
    id = models.IntegerField(primary_key=True)
    topic_id = models.IntegerField(null=True)
    subtopic_name = models.CharField(max_length=255)
    subject_id = models.IntegerField(null=True)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)

class QuestionAnswers(models.Model):
    class Meta:
        db_table = 'question_answers'
        managed = False  # Set to False since table already exists

    question_id = models.IntegerField(null=True)
    subtopic_id = models.IntegerField(null=True)
    subject_id = models.IntegerField(null=True)
    quiz_id = models.IntegerField(null=True)
    student_id = models.IntegerField(null=True)

class Schools(models.Model):
    class Meta:
        db_table = 'schools'
        managed = False  # Set to False since table already exists
    school_name = models.CharField(max_length=255)
    school_code = models.CharField(max_length=255)
    county_id = models.IntegerField(null=True)

class Users(models.Model):
    class Meta:
        db_table = 'users'
        managed = False  # Set to False since table already exists
    
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    school_code = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

class FLNAngazaQuizzes(models.Model):
    class Meta:
        db_table = 'fln_angaza_quizzes'
        managed = False  # Since this is an existing table

    id = models.AutoField(primary_key=True)
    grade_id = models.IntegerField(null=True)
    strand_id = models.IntegerField(null=True)
    substrand_id = models.IntegerField(null=True)
    lesson_id = models.IntegerField(null=True)
    quiz_type = models.CharField(max_length=255)
    question = models.TextField()
    question_type = models.CharField(max_length=255)
    question_sound = models.TextField(null=True)
    options = models.JSONField()
    answer_sound = models.TextField(null=True)
    hint = models.CharField(max_length=255, null=True)
    taxonomy_tag = models.CharField(max_length=255, null=True)
    day = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question

class FLNUserResponses(models.Model):
    class Meta:
        db_table = 'fln_user_responses'
        managed = False  # Changed to False since table already exists
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['quiz_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['grade_id']),
            models.Index(fields=['strand_id']),
            models.Index(fields=['substrand_id']),
            models.Index(fields=['quiz_type']),
            models.Index(fields=['taxonomy_tag']),
        ]

    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    quiz_id = models.IntegerField()  # Changed from ForeignKey to match the existing table
    selected_option = models.CharField(max_length=1)  # Store the selected option label (A, B, C, D)
    is_correct = models.BooleanField()
    attempt_number = models.IntegerField(default=1)
    response_time = models.IntegerField(null=True)  # Time taken to answer in seconds
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    session_id = models.CharField(max_length=255, null=True)  # To group responses from the same session
    device_info = models.JSONField(null=True)  # Store device information as JSON
    grade_id = models.IntegerField()
    strand_id = models.IntegerField(null=True)
    substrand_id = models.IntegerField(null=True)
    lesson_id = models.IntegerField(null=True)
    quiz_type = models.CharField(max_length=50)  # Store the type of quiz (diagnostic, practice, etc.)
    taxonomy_tag = models.CharField(max_length=50, null=True)  # Store the taxonomy level

    def __str__(self):
        return f"Response {self.id} by User {self.user_id} for Quiz {self.quiz_id}"

class FLNUserThresholdHistory(models.Model):
    class Meta:
        db_table = 'fln_user_threshold_history'
        managed = True
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['quiz_type']),
            models.Index(fields=['created_at']),
        ]

    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    quiz_type = models.CharField(max_length=50)
    old_threshold = models.FloatField()
    new_threshold = models.FloatField()
    reason = models.CharField(max_length=255, null=True)  # Optional reason for the change
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=255, null=True)  # Who made the change

    def __str__(self):
        return f"Threshold change for user {self.user_id} ({self.quiz_type}): {self.old_threshold} → {self.new_threshold}"

class FLNUserThresholds(models.Model):
    class Meta:
        db_table = 'fln_user_thresholds'
        managed = True
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['quiz_type']),
        ]
        unique_together = [['user_id', 'quiz_type']]  # One threshold per user per quiz type

    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    quiz_type = models.CharField(max_length=50)  # e.g., 'starter_quiz', 'diagnostic_quiz'
    recommendation_threshold = models.FloatField(default=0.6)  # Default threshold of 60%
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Threshold for user {self.user_id} ({self.quiz_type}): {self.recommendation_threshold}"

    def record_change(self, old_threshold, reason=None, created_by=None):
        """Record a threshold change in the history"""
        FLNUserThresholdHistory.objects.create(
            user_id=self.user_id,
            quiz_type=self.quiz_type,
            old_threshold=old_threshold,
            new_threshold=self.recommendation_threshold,
            reason=reason,
            created_by=created_by
        )


