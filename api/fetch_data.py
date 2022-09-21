from api import models
import random

class FetchData:

    def __init__(self, subtopic_id):
        self.subtopic_id = str(subtopic_id)

    def high_level_questions(self, passed_subtopics, subtopic_id):
        high_level_questions=[]
        for i in passed_subtopics:
            create_query = models.QuizQuestions.objects.raw('SELECT * FROM quizq_questions where question_level="create" and subtopic_id='+ self.subtopic_id)
            high_level_questions.append(create_query)
            evaluate_query= models.QuizQuestions.objects.raw('SELECT * FROM quizq_questions where question_level="evaluate" and subtopic_id='+self.subtopic_id)
            high_level_questions.append(evaluate_query)
            analyze_query= models.QuizQuestions.objects.raw('SELECT * FROM quizq_questions where question_level="analyze" and subtopic_id='+self.subtopic_id)
            high_level_questions.append(analyze_query)
        return high_level_questions

    def failed_subtopic_materials(self, failed_subtopics):
        failed_subtopic_materials=[]
        for i in failed_subtopics:
            notes_query = models.QuizQuestions.objects.raw('SELECT * FROM angaza_notes where subtopic_id='+self.subtopic_id)
            failed_subtopic_materials.append(notes_query)
            action= failed_subtopic_materials
            if len(failed_subtopic_materials) == 0:
                action= "you have mastered this topic, you can choose another topic to study"

        return action

    def create_questions(self, mark):
            create_query= models.QuizQuestions.objects.filter(question_level="create", subtopic_id=self.subtopic_id).values()
            create_questions=[]
            create_questions.append(create_query)
            if len(create_questions) != 0 :
                action = random.choice(create_questions)
            # elif len(create_questions) == 0 and mark==1:
            #     action = create_questions(self.subtopic)
            else:
                action= failed_subtopic_materials(failed_subtopics)
            return action

    def evaluate_questions(self, mark):

        evaluate_query= models.QuizQuestions.objects.filter(question_level="evaluate", subtopic_id=self.subtopic_id).values()
        evaluate_questions=[]
        evaluate_questions.append(evaluate_query)

        if  len(evaluate_questions) != 0 and mark==1 :
            action = random.choice(evaluate_questions)

        elif len(evaluate_questions) == 0 and mark==1 :
            action = self.create_questions(self)

        elif len(evaluate_questions) != 0 and mark==0 :
             action = random.choice(evaluate_questions)
        else:
            action = self.analyze_questions( mark)
        return action


    def analyze_questions(self, mark):

        analyze_query= models.QuizQuestions.objects.filter(question_level="analyze", subtopic_id=self.subtopic_id).values()
        analyze_questions=[]
        analyze_questions.append(analyze_query)
        if len(analyze_questions) != 0 and mark==1 :

            action = random.choice(analyze_questions)

        elif len(analyze_questions) == 0 and mark==1 :
            action= self.evaluate_questions( mark)

        elif len(analyze_questions) != 0 and mark==0 :
            action = random.choice(analyze_questions)
        else:
            action= self.apply_questions(mark)
        return action

    def apply_questions(self, mark):

        apply_query= models.QuizQuestions.objects.filter(question_level="apply", subtopic_id=self.subtopic_id).values()
        apply_questions=[]
        apply_questions.append(apply_query)
        if len(apply_questions) != 0 and mark==1 :

            action = random.choice(apply_questions)
        elif  len(apply_questions) == 0 and mark==1 :
            action= self.analyze_questions( mark)

        elif  len(apply_questions) != 0 and mark==0 :
            action = random.choice(apply_questions)

        else:

            action= self.understand_questions( mark)
        return action

    def understand_questions(self, mark):

        understand_query= models.QuizQuestions.objects.filter(question_level="understand", subtopic_id=self.subtopic_id).values()
        understand_questions=[]
        understand_questions.append(understand_query)
        if len(understand_questions) != 0 and mark==1 :

            action = random.choice(understand_questions)
        elif len(understand_questions) == 0 and mark==1 :
            action= self.apply_questions( mark)

        elif len(understand_questions) != 0 and mark==0 :
             action = random.choice(understand_questions)

        else:

            action = self.remember_questions( mark)
        return action

    def remember_questions(self, mark):

        remember_query= models.QuizQuestions.objects.filter(question_level="remember", subtopic_id=self.subtopic_id).values()
        remember_questions=[]
        remember_questions.append(remember_query)

        if len(remember_questions) == 0 and mark==0 :
            action = random.choice(understand_questions)
        else:
            action = random.choice(remember_questions)
        return action

    def get_subtopics(self):
        diagnostic_subtopics = []
        subtopic_query = models.Subtopics.objects.raw('SELECT * FROM subtopics where topic_id='+self.subtopic_id)
        print(subtopic_query[0].id)
        # diagnostic_subtopics.append(subtopic_query)
        return self.diagnostic_test(subtopic_query)

    def diagnostic_test(self, diagnostic_subtopics):
        diagnostic_questions = list()
        for idx, i in enumerate(diagnostic_subtopics):
            print(diagnostic_subtopics[idx].id)
            if(diagnostic_subtopics[idx].id):
                # print()
                questions_query= list(models.QuizQuestions.objects.filter(subtopic_id=str(diagnostic_subtopics[idx].id)).values())
                print(len(questions_query))
                diagnostic_questions.extend(random.choices(questions_query, k=2))
        return(diagnostic_questions)
