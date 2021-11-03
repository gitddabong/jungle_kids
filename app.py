from os import dup
from flask import Flask, render_template, jsonify, request, redirect, url_for
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from bson.objectid import ObjectId
# sw import
import jwt
import hashlib
import datetime
from utils import token_to_id, token_to_ph
# sw import

app = Flask(__name__)
SECRET_KEY = 'jungle_kids'


client = MongoClient('localhost', 27017)
db = client.dbkids


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    print(type(token_receive))
    print("토큰")
    if token_receive is not None:
        print("토큰있다")
        token_receive = bytes(token_receive[2:-1].encode('ascii'))

        try:
            payload = jwt.decode(token_receive, SECRET_KEY,
                                 algorithms=['HS256'])
            user_info = db.users.find_one({'username': payload['ID']})
            return render_template('main.html', user_info=user_info)
        except jwt.ExpiredSignatureError:
            return redirect(url_for('/sign_in', message="로그인 시간이 만료되었습니다."))
    else:
        print("토큰없음")
        return render_template('signin.html')


### 회원 가입 기능 구현 ###
@app.route('/sign_up', methods=['GET'])
def sing_up():
    return render_template('signup.html', title='회원가입')

### 회원가입 페이지에서 입력시###


@app.route('/sign_up', methods=['POST'])
def sign_up_save():
    # 회원 가입 시 받을 정보 3가지 id=사용자실명,비밀번호,전화번호,주소
    id_receive = request.form['id_give']
    password_receive = request.form['password_give']
    phonenmb_receive = request.form['phonenmb_give']
    address_receive = request.form['address_give']

    # password의 경우 보안을 위해 hash 처리
    password_hash = hashlib.sha256(
        password_receive.encode('utf-8')).hexdigest()

    address_hash = hashlib.sha256(address_receive.encode('utf-8')).hexdigest()

    user_data = {
        'username': id_receive,
        'password': password_hash,
        'phonenmb': phonenmb_receive,
        'address': address_hash,
    }

    db.users.insert_one(user_data)
    return jsonify({'result': 'success'})


@app.route('/check_up', methods=['POST'])
def check_up():
    phonenmb_receive = request.form['phonenmb_give']
    duplicate = bool(db.users.find_one({'phonenmb': phonenmb_receive}))
    return jsonify({'result': 'success', 'duplicate': duplicate})

### 로그인 기능 구현 ###


@app.route('/sign_in', methods=['GET'])
def sign_in():
    return render_template('signin.html', title='로그인')

### 로그인 정보 입력 ###


@app.route('/sign_in', methods=['POST'])
def sign_in_user():
    id_receive = request.form['id_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(
        password_receive.encode('utf-8')).hexdigest()

    print(password_hash)
    print(id_receive)
    result = db.users.find_one(
        {'username': id_receive, 'password': password_hash})
 ## 토큰 발행 ##
    if result is not None:
        payload = {
            'ID': id_receive,
            'PHONE': result['phonenmb'],
            'EXP': str(datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24))
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': str(token)})
    else:
        return jsonify({'result': 'fail', 'message': '성함/Password가 정확하지 않습니다.'})


@app.route('/memo', methods=['POST'])
def post_article():
    title_receive = request.form['title_give']
    startMonth_receive = request.form['startMonth_give']
    startDay_receive = request.form['startDay_give']
    startHour_receive = request.form['startHour_give']
    endHour_receive = request.form['endHour_give']
    comment_receive = request.form['comment_give']

    token_receive = request.cookies.get('mytoken')
    user_ph = token_to_ph(token_receive, SECRET_KEY)

    boyuk_requests = {
        'writter': user_ph,
        'title': title_receive,
        'startMonth': startMonth_receive,
        'startDay': startDay_receive,
        'startHour': startHour_receive,
        'endHour': endHour_receive,
        'comment': comment_receive,
        'requests': []
    }

    db.boyuk_requests.insert_one(boyuk_requests)
    return jsonify({'result': 'success'})


@app.route('/update', methods=['POST'])
def update_article():
    documentId_receive = request.form['documentId_give']
    title_receive = request.form['update_title_give']
    startMonth_receive = request.form['update_startMonth_give']
    startDay_receive = request.form['update_startDay_give']
    startHour_receive = request.form['update_startHour_give']
    endHour_receive = request.form['update_endHour_give']
    comment_receive = request.form['update_comment_give']

    # 토큰에서 사용자의 정보를 받아와 수정 가능 여부 판단
    token_receive = request.cookies.get('mytoken')
    user_ph = token_to_ph(token_receive, SECRET_KEY)

    duplicate = bool(db.boyuk_requests.find_one({'writter': user_ph, '_id': ObjectId(documentId_receive)}))

    if duplicate:
        db.boyuk_requests.update(
            {'_id': ObjectId(documentId_receive)},
            {'$set': {'title': title_receive, 'startMonth': startMonth_receive, 'startDay': startDay_receive, 'startHour': startHour_receive, 'endHour': endHour_receive, 'comment': comment_receive}}
        )

    return jsonify({'result': 'success', 'duplicate': duplicate})


@app.route('/memo', methods=['GET'])
def read_articles():
    result = list(db.boyuk_requests.find({}))

    # 클라이언트에서 문서ID를 쉽게 다루기 위해 object타입을 string타입으로 변환
    for document in result:
        document['_id'] = str(document['_id'])

    return jsonify({'result': 'success', 'articles': result})


@app.route('/accept', methods=['POST'])
def request_accept():
    # 수락을 요청한 사용자의 문서ID를 저장
    #user_documentId = str(db.users.find_one({'hpnumber':private_data_receive})['_id'])
    token_receive = request.cookies.get('mytoken')
    user_id = token_to_id(token_receive, SECRET_KEY)
    user_ph = token_to_ph(token_receive, SECRET_KEY)

    private_data = user_id + "/" + user_ph

    documentId_receive = request.form['documentId_give']

    duplicate = bool(db.boyuk_requests.find_one({'requests': private_data}))

    db.boyuk_requests.update(
        {'_id': ObjectId(documentId_receive)},
        {'$push': {'requests': {'$each': [private_data]}}}
    )
    return jsonify({'result': 'success', 'duplicate': duplicate})


@app.route('/choose', methods=['POST'])
def choose_sitter():
    # 조건은 문서ID로 해야 함
    sitter_receive = request.form["sitter_give"]
    documentId_receive = request.form["documentId_give"]

    db.boyuk_requests.update_one({'_id': ObjectId(documentId_receive)}, {
                                 '$set': {'sitter': sitter_receive}})

    return jsonify({'result': 'success'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
