from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient 
from bson.objectid import ObjectId
# sw import
import jwt, hashlib, datetime
import threading
# sw import


app = Flask(__name__)
SECRET_KEY = 'jungle_kids'


client = MongoClient('localhost', 27017)
db = client.dbkids

### 회원 가입 기능 구현 ###
@app.route('/sign_up', methods=['GET'])
def sing_up():
    return render_template('signup.html', title ='회원가입')

### 회원가입 페이지에서 입력시###
@app.route('/sign_up', methods=['POST'])
def sign_up_save():
    # 회원 가입 시 받을 정보 3가지 id=사용자실명
    id_receive = request.form['id_give']
    password_receive = request.form['password_give']
    phonenmb_receive = request.form['phonenmb_give']

    # password의 경우 보안을 위해 hash 처리
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    phonenmb_hash = hashlib.sha256(phonenmb_receive.encode('utf-8')).hexdigest()

    user_data = {
        'username': id_receive,
        'password': password_hash,
        'phonenmb': phonenmb_receive
    }

    db.users.insert_one(user_data)
    return jsonify({'result': 'success'})


@app.route('/check_up', methods=['POST'])
def check_up():
    email_receive = request.form['email_give']
    duplicate = bool(db.users.find_one({'email': email_receive}))
    return jsonify({'result': 'success', 'duplicate':duplicate})

@app.route('/')
def home():
    
    db.boyuk_requests.delete_one

    return render_template('main.html')

@app.route('/memo', methods=['POST'])
def post_article():
    writter_receive = request.form['writter_give']
    title_receive = request.form['title_give']
    startMonth_receive = request.form['startMonth_give']
    startDay_receive = request.form['startDay_give']
    startHour_receive = request.form['startHour_give']
    endHour_receive = request.form['endHour_give']
    comment_receive = request.form['comment_give']
    boyuk_requests = {
        'writter': writter_receive,
        'title': title_receive, 
        'startMonth': startMonth_receive, 
        'startDay': startDay_receive, 
        'startHour': startHour_receive, 
        'endHour': endHour_receive, 
        'comment': comment_receive
    }

    db.boyuk_requests.insert_one(boyuk_requests)
    return jsonify({'result': 'success'})

@app.route('/update', methods=['POST'])
def update_article():
    writter_receive = request.form['writter_give']
    documentId_receive = request.form['documentId_give']
    title_receive = request.form['update_title_give']
    startMonth_receive = request.form['update_startMonth_give']
    startDay_receive = request.form['update_startDay_give']
    startHour_receive = request.form['update_startHour_give']
    endHour_receive = request.form['update_endHour_give']
    comment_receive = request.form['update_comment_give']

    db.boyuk_requests.update_one(
        {'_id':ObjectId(documentId_receive)},
        {'$set':{'title':title_receive, 'startMonth':startMonth_receive, 'startDay':startDay_receive, 'startHour':startHour_receive, 'endHour':endHour_receive, 'comment':comment_receive}}
    )

    return jsonify({'result': 'success'})

@app.route('/memo', methods=['GET'])
def read_articles():
    result = list(db.boyuk_requests.find({}))

    for document in result:
        document['_id']=str(document['_id'])

    return jsonify({'result': 'success', 'articles': result})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)