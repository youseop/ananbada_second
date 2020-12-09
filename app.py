from flask import Flask, render_template, jsonify, request, session, redirect
from haversine import haversine
import datetime
from bson.objectid import ObjectId
from db import db
from hash import get_hash_value
from find_coord import find_coord

app = Flask(__name__)

app.secret_key = "1"

SEOUL_COORD = (126.83809728245, 37.5591190960732)

## HTML을 주는 부분
@app.route('/')
def index():
    user = session.get("user")
    return render_template('share.html', user=user)


@app.route('/register')
def getRegister():
    user = session.get("user")
    if not user:
        return redirect("/")
    return render_template('register.html', user=user)

@app.route('/profile')
def getProfile():
    user = session.get("user")
    return render_template('profile.html', user=user)

@app.route('/need')
def getNeed():
    user = session.get("user")
    get_items = list(db.items.find({"share":"false"}))
    for i in range(len(get_items)):
        get_items[i]["_id"] = str(get_items[i]["_id"])
    return render_template('need.html', get_items=get_items, user=user)

@app.route('/login', methods=["GET"])
def getLogin():
    user = session.get("user")
    flash = request.args.get("flash")
    if user:
        return redirect("/")
    return render_template('login.html', user=user, flash=flash)

@app.route('/search', methods=['POST'])
def search():
    url_receive = request.form['search_input']
    url_name = request.form['url_name']

    result = list(db.items.find({"$or":[{"title": {"$regex":url_receive}, "share" : url_name},{"description" : {"$regex":url_receive},"share" : url_name}]},{'imgUrl':False}))

    for i in range(len(result)):
        result[i]["_id"] = str(result[i]["_id"])

    return jsonify({'result': 'success', 'items': result})


@app.route('/mypage/<user_id>')
def mypage(user_id):
<<<<<<< HEAD
    user_id = user_id
    user = db.Users.find_one({'user_id':user_id})
    share= list(db.items.find({"user_id":user_id, "share":'true'}))
    need = list(db.items.find({"user_id":user_id, "share":'false'}))
    cnt_share, cnt_need = len(share), len(need)
    return render_template('profile.html', user = user, share = share, need = need, cnt_share = cnt_share,
                           cnt_need = cnt_need)
=======
    user_item = user_id #마이페이지 조회 대상, 게시글 작성자
    user = db.Users.find_one({'user_id':user_id})	    
    user_now = session.get('user')['user_id']
    share= list(db.items.find({"user_id":user_id, "share":'true'}))	    
    check_user = False
    need = list(db.items.find({"user_id":user_id, "share":'false'}))	    
    if user_item == user_now :
        check_user = True
    print(check_user, user_item, user_now)
    print(user_now, user_id)
    user = db.Users.find_one({'user_id':user_item})
    share= list(db.items.find({"user_id":user_item, "share":'true'}))
    need = list(db.items.find({"user_id":user_item, "share":'false'}))

    cnt_share, cnt_need = len(share), len(need)

    return render_template('profile.html', user = user, share = share, need = need, cnt_share = cnt_share,
                           cnt_need = cnt_need, check_user = check_user)
>>>>>>> f7ad3cf700f25867518095d01253a56bc038a1ef


@app.route('/login', methods=["POST"])
def postLogin():
    user_id = request.form["userId"]
    user_pwd = get_hash_value(request.form["userPwd"])

    user = db.Users.find_one({"user_id": user_id}, {"_id": 0})

    if not user:
        flash = "사용자가 존재하지 않습니다."
    elif user["user_pwd"] != user_pwd:
        flash = "아이디와 비밀번호가 일치하지 않습니다."
    else:
        session["user"] = user
        return redirect("/")

    return redirect(f"/login?flash={flash}")


@app.route('/join', methods=["GET"])
def getJoin():
    user = session.get("user")
    flash = request.args.get("flash")
    if user:
        return redirect("/")
    return render_template("join.html", flash=flash)


@app.route('/join', methods=["POST"])
def postJoin():
    user_id = request.form["userId"]
    user_pwd = request.form["userPwd"]
    user_address = request.form["userAddress"]
    coord = find_coord(user_address)

    user = db.Users.find_one({"user_id": user_id})

    if user:
        flash = "이미 존재하는 아이디입니다."
    elif len(user_pwd) < 8:
        flash = "비밀번호의 길이는 8자 이상이어야합니다."
    else:
        doc = {
            "user_id": user_id,
            "user_pwd": get_hash_value(user_pwd),
            "user_address": request.form["userAddress"],
            "user_sex": user_address,
            "user_nickname": request.form["userNickname"],
            "user_coord": coord
        }
        db.Users.insert_one(doc)
        doc["_id"] = 0
        session["user"] = doc
        return redirect("/")

    return redirect("/join?flash={flash}")

@app.route('/logout', methods=["GET"])
def logout():
    session.pop("user")
    return redirect("/")


## 웹에서 사용할 APIs----------------------------------------

@app.route("/api/getItem", methods=["post"])
def get_item_info():
    user = session.get('user')
    id = request.form["itemId"]
    doc = db.items.find_one({"_id": ObjectId(id)})
    doc["_id"] = str(doc["_id"])
    doc["distance"] = doc["user_address"]
    user_coord = user["user_coord"] if user else None
    item_coord = doc["coord"]
    distance = str(int(haversine(user_coord, item_coord)*10)/10) + "km 이내" if user else "..km 이내"
    doc["distance"] = distance
    return jsonify(doc)

@app.route("/api/getCommentInfo", methods=["POST"])
def get_comment_info():
    id = request.form["id"]
    item = db.items.find_one({"_id":ObjectId(id)})
    comment_ids = item["comments"]
    comments = []
    for id in comment_ids:
        comment = db.comments.find_one({"_id": ObjectId(id)})
        doc = {
            "id": str(comment["_id"]),
            "written_by": comment["user_nickname"],
            "comment": comment["comment"],
            "createdAt": comment["createdAt"]
        }
        comments.append(doc)
    comments.reverse()
    return jsonify(comments)

@app.route("/api/getComment", methods=["POST"])
def get_comment():
    comment_id = request.form['id']
    result = db.comments.find_one({'_id': ObjectId(comment_id)})
    result["_id"] = str(result["_id"])
    result["user"]={"user_address":result["user"]["user_address"],"user_id":result["user"]["user_id"],"user_nickname":result["user"]["user_nickname"]}
    
    return jsonify(result)

#게시글 작성
@app.route('/item', methods=['POST'])
def post_item():
    user=session.get('user')
    share_recieve = request.form['share']
    title_recieve = request.form['title']
    description_recieve = request.form['description']
    now = datetime.datetime.now()
    nowDate = now.strftime('%m-%d %H:%M')
    imgUrl_recieve = request.form['imgUrl']
    item_address = request.form["itemAddress"]
    item_coord = find_coord(item_address)

    item = {
        'share': share_recieve,
        'title': title_recieve, 
        'description': description_recieve,
        'createdAt': nowDate,
        'imgUrl': imgUrl_recieve,
        'user_id': user["user_id"],
        'user_nickname': user["user_nickname"],
        'user_address': item_address,
        "comments": [],
        "coord": item_coord
        }

    db.items.insert_one(item)

    return redirect("/")

#댓글 작성
@app.route('/comment', methods=['POST'])
def post_comment():
    user = session.get('user')
    id_receive = request.form['id_received']

    comment_receive = request.form['comment']
    createdAt_receive = request.form['createdAt']

    comment = {
        'post_id':id_receive,
        'comment': comment_receive,
        'createdAt': createdAt_receive,
        'user_nickname': user["user_nickname"]
    }
    db.comments.insert_one(comment)


    db.items.update({ "_id" : ObjectId(id_receive) },{ "$push": { "comments" : str(comment["_id"])}})
    print("업데이트 됨")
    return jsonify({'result': 'success'})


#빌려주겠다는 게시글 불러오기
@app.route('/get_item', methods=['POST'])
def read_items():
    user = session.get('user')
    isShare = request.get_json(silent=True, cache=False, force = True)
    if isShare == 1:
        result = list(db.items.find({'share': 'true'}))
    else:
        result = list(db.items.find({'share': 'false'}))


    for i in range(len(result)):
        result[i]["_id"] = str(result[i]["_id"])
        if user:
            result[i]["distance_from_user"] = int(haversine(result[i]["coord"], user["user_coord"]) * 10) / 10
        else:
            result[i]["distance_from_user"] = ".."
    return jsonify({'result': 'success', 'items': result})


#게시글 삭제
@app.route('/delete', methods=['POST'])
def delete_item():
    id_receive = request.form['id_give']
    db.items.delete_one({'_id': ObjectId(id_receive)})
    return jsonify({'result': 'success'})


## 서버 연결
if __name__ == '__main__':
    print("http://localhost:5000")
    app.run('0.0.0.0', port=5000, debug=True)
