from app import app
from flask import abort, request, jsonify, g, url_for
from flask_httpauth import HTTPBasicAuth
from flask_login import current_user, login_user
from app import session,  flask_bcrypt, jwt
from app.models import UserInfo
from flask_jwt_extended import(
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity
)

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
    password = flask_bcrypt.generate_password_hash(request.json.get('password'))
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
@jwt_required
def get_user(id):
    user = session.query(UserInfo).filter_by(User_ID=id).one()
    print (user)
    if not user:
        abort(400)
    return jsonify({'username': user.Username})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    #return data

    if data is None:
        abort(404)

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # whatever username is entered
    username = data['username']
    password = data['password']
    user = session.query(UserInfo).filter_by(Username=username).first()
    #print (user.Login_password)
    #return data
    if user and flask_bcrypt.check_password_hash(user.Login_password, password):
        access_token = create_access_token(identity=data)
        refresh_token = create_refresh_token(identity=data)
        del data['password']
        data['token'] = access_token
        data['refresh'] = refresh_token
        return data
        #return jsonify(data)

    else:
        return jsonify({'Status':'Invalid'})


@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    ret = {
        'token': create_access_token(identity=current_user)
    }
    return jsonify({'data':ret})


@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({
        'message':'Missing Authorization header'
    }
    ),401
# TODO
"""
Implement Login from this - https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
Combine it with this - https://blog.miguelgrinberg.com/post/restful-authentication-with-flask
JWT - https://medium.com/@riken.mehta/full-stack-tutorial-3-flask-jwt-e759d2ee5727

"""
