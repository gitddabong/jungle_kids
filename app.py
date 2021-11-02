from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient 

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbkids

@app.route('/')
def home():
    # 여기서 등록된 달을 기준으로 오름차순 정렬을 하는데, 연도가 적혀있지 않아 가장 빨리 들어온 의뢰인지 정확히 알 수 없으므로 질문태클을 받을 수 있으니 이 부분은 설명을 해야 함.
    result = list(db.boyuk_requests.find({}, {'_id': 0}))

    #return render_template('index.html')
    return render_template('index.html', results=result)


@app.route('/memo', methods=['POST'])
def post_article():
    title_receive = request.form['title_give']
    startMonth_receive = request.form['startMonth_give']
    startDay_receive = request.form['startDay_give']
    startHour_receive = request.form['startHour_give']
    endHour_receive = request.form['endHour_give']
    comment_receive = request.form['comment_give']
    boyuk_requests = {
        'title': title_receive, 
        'startMonth': startMonth_receive, 
        'startDay': startDay_receive, 
        'startHour': startHour_receive, 
        'endHour': endHour_receive, 
        'comment': comment_receive
    }

    db.boyuk_requests.insert_one(boyuk_requests)

    return jsonify({'result': 'success'})

"""
@app.route('/memo', methods=['GET'])
def read_articles():
    result = list(db.boyuk_requests.find({}, {'_id': 0}))
    #return jsonify({'result': 'success', 'articles': result})
    return render_template('index.html', results=result)
"""

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)