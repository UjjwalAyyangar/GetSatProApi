from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

"""

        requestBody:
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            username:
                                type: string
                                example: ObiWan
                                required: true
                            fname:
                                type: string
                                example: Obi
                                required: true
                            lname:
                                type: string
                                example: Wan
                                required: true
                            password:
                                type: string
                                example: Ob12W@n
                                required: true
                            email:
                                type: string
                                example: obi@wan.com
                                required: true
                            phone:
                                type: string
                                example: 999-999-9999
                                required: true
                            role_id:
                                type: string
                                example: 1
                                required: true

        responses:
            200:
                description: Create a new user
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                message: User created successfully
                                    type: string
                                Status:
                                    type: string
                                    example : 200
"""