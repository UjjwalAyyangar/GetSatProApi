from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin
from app.services import (
    discussions,
    exams,
    flashcards,
    modules,
    grades,
    users,
    admin
)
from app import app
from config import basedir
import os

import json


def make_doc():
    spec = APISpec(
        title="Get Sat Pro API",
        version="0.0.1",
        info=dict(
            description='For squadrons, by squadrons',
        ),
        plugins=[FlaskPlugin()],
        openapi_version="3.0.2"
    )

    with app.test_request_context():
        # User service
        """
        spec.path(view=users.register)
        spec.path(view=users.login)
        spec.path(view=users.logout)
        spec.path(view=users.api_get_students)
        spec.path(view=modules.api_add_module)
        spec.path(view=modules.api_get_mods)
        spec.path(view=admin.api_del)
        spec.path(view=exams.api_create_exam)
        spec.path(view=exams.api_get_exams)
        spec.path(view=exams.api_submit_exam)
        spec.path(view=exams.api_check_sub)
        spec.path(view=grades.api_view_grade)
        spec.path(view=grades.api_view_grades)
        spec.path(view=discussions.api_create_discussion)
        spec.path(view=discussions.api_create_discus_thread)
        """

    jwt_scheme = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "We use JWT tokens for making authenticated requests"
    }

    spec.components.security_scheme("jwt", jwt_scheme)
    path = os.path.join(basedir, 'app', 'static', 'swagger.json')
    with open(path, 'r+') as f:
        f.seek(0)
        a = json.dumps(spec.to_dict(), indent=2)
        # print(spec.to_yaml())
        json.dump(spec.to_dict(), f)
