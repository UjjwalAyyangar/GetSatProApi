from app.models import File
from app.dac import general as gen_dac
from app.dac import modules as mod_dac
from app.constants import *
import sqlalchemy


def create_file(data):
    new_file = File(
        File_Name=data[FILE_NAME],
        Publisher_ID=data[TUTOR_ID],
        Module_ID=data[MODULE_ID],
        Link=data[FILE_LINK]
    )
    return gen_dac.insert(new_file)


def get_files(data):
    module = mod_dac.get_module(data[MODULE_ID])
    if module:
        return module.Files.all()
    else:
        return None


def get_file(file_id):
    try:
        return File.query.filter_by(File_ID=file_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None
