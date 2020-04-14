import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_user = "mesan"
        self.database_password = "1234"
        self.database_path = "postgresql://{}:{}@{}/{}".format(self.database_user,self.database_password,'localhost:5432', self.database_name)
        #self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    #################### TEST GET QUESTIONS
    def test_get_all_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['current_category'],'all')
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_get_paginated_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)

    def test_pagination_beyond_range(self):
        res = self.client().get('/questions?page=99999999')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')

    def test_get_all_category_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['current_category'],'all')
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_get_category_paginated_questions(self):
        res = self.client().get('/categories/1/questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)

    def test_category_pagination_beyond_range(self):
        res = self.client().get('/categories/1/questions?page=99999999')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')

    def test_get_invalid_category(self):
        res = self.client().get('/categories/999/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')

    #################### TEST DELETES
    def test_succesful_delete_question(self):
        sample = Question.query.first() #delete first result for test
        question_id = sample.id
        res = self.client().delete('/questions/'+str(question_id))
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == question_id).one_or_none() #1 per id, or none
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted'],question_id)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(question,None) # object was deleted

    def test_error_delete_question(self):
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 1).one_or_none() #1 per id, or none
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'],False)        
        self.assertEqual(data['message'],'unprocessable entity')

    #################### TEST SEARCH
    # This does not seem to work as I am thinking about it
    def test_search(self):
        res = self.client().post('/questions/search',json={'searchTerm':'title'})
        data = json.loads(res.data)
        results = Question.query.filter(Question.question.ilike('%'+'title'+'%')).all()
        status = True
        for result in results:
            current = result.question.lower()
            if 'title' not in current:
                status = False # if one result does not contain title, fail
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(status,True)

    def test_error_search(self):
        res = self.client().post('/questions/search',json={'searchTerm':'oierotihgsa;dflkjgnae;srgujbgsaefuyjhb'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')

    #################### TEST CREATE
    # This does not seem to work as I am thinking about it
    def test_create(self):
        total_before = len(Question.query.all())
        res = self.client().post('/questions',json={
            'question' : 'Yes?'
            ,'answer' : 'No'
            ,'difficulty' : 5
            ,'category' : 6
            })
        data = json.loads(res.data)
        total_after = len(Question.query.all())
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['created'])
        self.assertEqual(total_before,total_after-1)

    def test_error_create(self):
        total_before = len(Question.query.all())
        res = self.client().post('/questions') # no JSON, should error out?
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'],False)        
        self.assertEqual(data['message'],'unprocessable entity')

    ##################### TEST PLAY
    def test_get_quiz_question(self):
        res = self.client().post('/quizzes',json={'quiz_category':{'type':'Science','id':1},'previous_questions':[20]})
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)        
        self.assertTrue(data['question'])

    def test_quiz_error(self):
        res = self.client().post('/quizzes',json={'quiz_category':{'type':'Fake','id':99},'previous_questions':[20]})
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()