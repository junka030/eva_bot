from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
import random

# create app and config SQLite database (local)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
db = SQLAlchemy(app) #initialize

# define database model (structure/scheme)
class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('choice.id'))

class Choice(db.Model):
    __tablename__ = 'choice'
    id = db.Column(db.Integer, primary_key = True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    choice_text = db.Column(db.String(200), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)


# routes
# get JSON data of all questions and corresponding choices
@app.route('/questions',methods=['GET'])
def get_questions():
    questions = Question.query.all() # get all questions from db
    data = []
    for q in questions:
        choices = Choice.query.filter_by(question_id=q.id).all() # get choices for the question
        data.append({
            'id' : q.id,
            'question' : q.question,
            'choices' : [{'id': choice.id, 'text': choice.choice_text} for choice in choices]
        })
    
    return jsonify(data)


# get random question
@app.route('/questions/random', methods=['GET'])
def get_random_question():
    random_question = Question.query.order_by(func.random()).first() 
    choices = Choice.query.filter_by(question_id=random_question.id).all()
    return jsonify({
        'id': random_question.id,
        'question': random_question.question,
        'choices': [{'id': choice.id, 'text': choice.choice_text} for choice in choices]
    })


# answer response
@app.route('/questions/<int:question_id>/choices/<int:choice_id>', methods=['GET'])
def get_choice(question_id, choice_id):
    try:
        choice = Choice.query.filter_by(question_id=question_id, id=choice_id).first()
        if choice is None:
            return jsonify({'error': 'Choice not found'}), 404
        
        return jsonify({
            'id': choice.id,
            'text': choice.choice_text,
            'is_correct': choice.is_correct
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# add question
@app.route('/questions', methods=['POST'])
def add_question():
    data = request.json
    new_question = Question(question=data['question'])
    db.session.add(new_question)
    db.session.commit()
    for choice in data['choices']:
        new_choice = Choice(
            question_id=new_question.id, 
            choice_text=choice['text'], 
            is_correct=choice['is_correct']
        )
        db.session.add(new_choice)
        if choice['is_correct']:
            new_question.answer_id = new_choice.id
    db.session.commit()
    return jsonify({'id': new_question.id}), 201


# view database
@app.route('/view_db', methods=['GET'])
def view_db():
    questions = Question.query.all()
    data = []
    for question in questions:
        choices = Choice.query.filter_by(question_id=question.id).all()
        data.append({
            'id': question.id,
            'question': question.question,
            'answer_id': question.answer_id,
            'choices': [{'id': choice.id, 'text': choice.choice_text, 'is_correct': choice.is_correct} for choice in choices]
        })
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)

"""
# run this to create database

from app import app, db

# Ensure we're working within the application context
with app.app_context():
    # Now we can perform SQLAlchemy operations
    db.create_all()
"""