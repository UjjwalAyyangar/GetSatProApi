from app import app
from flask import abort, request, jsonify, g, url_for
from flask_httpauth import HTTPBasicAuth
from flask_login import current_user, login_user
from app import session
from app.models import UserInfo


@app.route('/')
@app.route('/index')
def index():
    return 'Hello, World!'


# User Registration
@app.route('/register', methods=['POST'])
def register():
    #print (type(request.get_json()))
    #return jsonify(request.get_json())

    data = request.get_json()

    for key in request.get_json():
        if data[key] == None:
            abort(400)

    username = request.json.get('username')
    password = request.json.get('password')
    fname = request.json.get('fname')
    lname = request.json.get('lname')
    email = request.json.get('email')
    phone = request.json.get('phone')
    role_id = request.json.get('role_id')
    group_id = request.json.get('group_id')

    new_user = UserInfo(
        Username=username,
        Login_password=password,
        First_Name=fname,
        Last_Name=lname,
        Email=email,
        Phone=phone,
        Role_ID=int(role_id),
        Group_ID=int(group_id)
    )

    session.add(new_user)
    session.commit()

    return (jsonify(
        {'username': new_user.Username}
    ), 201)


# Get users
@app.route('/users/<int:id>')
def get_user(id):
    user = session.query(UserInfo).filter_by(User_ID=id).one()
    print (user)
    if not user:
        abort(400)
    return jsonify({'username': user.Username})


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # whatever username is entered
    user = session.query(UserInfo).filter_by(Username=username).first()
    if user is None or not user.check_password(password):
        flash("invalid")
        return redirect(url_for('login'))

    login_user(user, [form_data])

    form = LoginForm()
    return


# TODO
"""
Implement Login from this - https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
Combine it with this - https://blog.miguelgrinberg.com/post/restful-authentication-with-flask
JWT - https://medium.com/@riken.mehta/full-stack-tutorial-3-flask-jwt-e759d2ee5727

"""
