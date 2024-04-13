#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

class Login(Resource):
    def post(self):
        username = request.json.get('username')

        if not username:
            return {'message': 'The username is not available'}, 400
   
        user =User.query.filter_by(username=username).first()

        if user:
            session['user_id'] = user.id
            return user.to_dict(), 200

        return {'message': 'The user is not found'}, 404

class Logout(Resource):
    def delete(self):
        session.get('user_id')
        session.pop('user_id')
        returned_message = {'message': 'The user is logged out'}
        return returned_message, 204

class Checksession(Resource):
    def get(self):
        my_user_id = session.get('user_id')

        if my_user_id:
            user = User.query.get(my_user_id)
            return user.to_dict(), 200
        else:   
            return {}, 401

api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(Checksession, '/check_session')
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
