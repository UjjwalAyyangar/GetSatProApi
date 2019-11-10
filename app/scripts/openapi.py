from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin
from app.routes import *
from config import basedir
import os

import json


def make_doc():
    spec = APISpec(
        title="Get Sat Pro API",
        version="0.0.1",
        info=dict(
            description='For devs, by a devs',
        ),
        plugins=[FlaskPlugin()],
        openapi_version="3.0.2"
    )

    with app.test_request_context():
        spec.path(view=register)
        spec.path(view=login)
        spec.path(view=logout)
        spec.path(view=add_module)
        spec.path(view=create_exam)
        spec.path(view=submit_exam)
        spec.path(view=view_grade)

    path = os.path.join(basedir, 'app', 'static', 'swagger.json')
    with open(path, 'r+') as f:
        f.seek(0)
        a = json.dumps(spec.to_dict(), indent=2)
        print(spec.to_yaml())
        json.dump(spec.to_dict(), f)
