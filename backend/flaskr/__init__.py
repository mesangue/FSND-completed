import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request,questions): #This method, as seen in example, is defined here so it can be called later. It only paginates results
    page = request.args.get('page', 1, type=int) #default = 1
    start =  (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    formatted_questions = [question.format() for question in questions] # uses format property of object Question to get JSON of each question
    current_questions = formatted_questions[start:end]
    if len(current_questions) <= 0 :
      abort(404)
    return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  # WORK IN PROGESS
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  #CORS(app)
  CORS(app, resources={r'/*': {'origins': '*'}})
  '''
  @DONE: Use the after_request decorator to set Access-Control-Allow
  '''
  #DOUBLE CHECK BEFORE SUBMITTING THAT WE ALLOW ONLY THE METHODS WE NEED
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Methods','GET, POST, DELETE') #Not using: , PATCH, OPTIONS
    return response
  '''
  @DONE: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET']) #Get is default, but lets be explicit
  # curl http://127.0.0.1:5000/categories
  def get_categories():
    categories = Category.query.all()
    if len(categories) == 0:
      abort(404)
    aux_dict = {}
    for item in categories:
      aux_dict[item.id] = item.type
    return jsonify({
      'success' : True
      ,'categories':aux_dict
      })

  '''
  @DONE: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET']) #Get is default, but lets be explicit
  def get_questions():
    # curl http://127.0.0.1:5000/questions
    questions = Question.query.all() #all questions
    total_questions = len(questions)
    current_questions = paginate_questions(request,questions)
    current_category = 'all'
    if total_questions == 0:
      abort(404)
    return jsonify({
      'success':True
      ,'total_questions': total_questions
      ,'questions': current_questions
      ,'categories' :  [category.type for category in Category.query.all()]
      ,'current_category' : current_category #should not be necessary, but instructions above are unclear (request current_category)
      })

  '''
  @DONE: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE']) #note to self: this only happens with delete method on this route
  # curl -X DELETE http://127.0.0.1:5000/questions/1
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none() #1 per id, or none
      if question is None:
        abort(404) #abort if book does not exist
      question.delete()
      questions = Question.query.all()
      total_questions = len(questions)
      current_questions = paginate_questions(request,questions) #note, request has not changed when we press delete
      return jsonify({
        'success':True
        ,'deleted':question_id
        ,'questions':current_questions
        ,'total_questions':total_questions
        })
    except:
      abort(422)
  '''
  @DONE: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST']) 
  def add_question():
    # curl -X POST http://127.0.0.1:5000/add
    data = request.get_json()
    try:
      new_question = Question(
        question = data['question']
        ,answer = data['answer']
        ,difficulty = data['difficulty']
        ,category = data['category']
      )
      new_question.insert()
      questions = Question.query.all()
      total_questions = len(questions)
      current_questions = paginate_questions(request,questions) #note, request has not changed when we press delete
      return jsonify({
        'success':True
        ,'total_questions': total_questions
        ,'questions': current_questions
        ,'created': new_question.id
        })
    except:
      abort(422)  
  '''
  @DONE: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST']) 
  def search_questions():
    # curl -X POST http://127.0.0.1:5000/questions/search
    try:
      term = request.get_json()['searchTerm'] #This is a mess. Took me hours to see that I had to use get_json. Get form, or get would not work
      results = Question.query.filter(Question.question.ilike('%'+term+'%')).all()
      total_questions = len(results)
      current_category = 'all'
      current_questions = paginate_questions(request,results)
      if total_questions == 0:
        abort(404)
      return jsonify({
        'success':True
        ,'total_questions': total_questions
        ,'questions': current_questions
        ,'current_category' : current_category
        ,'term': term
        })
    except:
      abort(404)
  '''
  @DONE: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET']) #Get is default, but lets be explicit
  def get_category_questions(category_id):
    # curl http://127.0.0.1:5000/categories/1/questions
    category_id = category_id+1 # noted things where shifted
    categories = [category.id for category in Category.query.all()]
    if category_id not in categories:
      abort(404)
    questions = Question.query.filter(Question.category == category_id).all() #all questions
    total_questions = len(questions)
    current_questions = paginate_questions(request,questions)
    current_category = 'all'
    if total_questions == 0:
      abort(404)
    return jsonify({
      'success':True
      ,'total_questions': total_questions
      ,'questions': current_questions
      ,'categories' :  [category.type for category in Category.query.all()]
      ,'current_category' : current_category
      })

  '''
  @DONE: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one questionat a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  ''' 
  @app.route('/quizzes', methods=['POST']) 
  def get_random_question():
    # curl -X POST -H "Content-Type: application/json" -d '{"previous_questions":[1,2,3],"quiz_category":1}' http://127.0.0.1:5000/quizzes
    data = request.get_json()
    if data['quiz_category'] is None or data['previous_questions'] is None:
      abort(404)
    if data['quiz_category']['id'] == 0:
      all_questions = Question.query.distinct().all()
    else:
      all_questions = Question.query.filter(Question.category==data['quiz_category']['id']).distinct().all()
    if len(all_questions) == 0:
      abort(404)
    ids = [row.id for row in all_questions]
    previous_questions = data['previous_questions']
    quiz_category = 'all'
    repeated = True
    while repeated:
      position = random.randint(0,len(all_questions)+1)
      try:
        selected = ids[position]
        if selected not in previous_questions:
          repeated = False
      except:
        repeated = True
    question = Question.query.filter(Question.id == selected).one_or_none().format()
    return jsonify({
      'success':True
      ,'question': question
      })
  '''
  @DONE: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def no_found(error):
    return jsonify({
      'success':False
      ,'error':404
      ,'message': 'resource not found'
      }), 404 #note to self: this comma was relevant. It was returning 200 without it

  @app.errorhandler(422)
  def no_found(error):
    return jsonify({
      'success':False
      ,'error':422
      ,'message': 'unprocessable entity'
      }), 422

  @app.errorhandler(400)
  def no_found(error):
    return jsonify({
      'success':False
      ,'error':400
      ,'message': 'bad request'
      }), 400

  @app.errorhandler(500)
  def no_found(error):
    return jsonify({
      'success':False
      ,'error':500
      ,'message': 'internal server error'
      }), 500

  return app

