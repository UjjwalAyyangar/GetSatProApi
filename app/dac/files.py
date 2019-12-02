# DATA ACCESS LAYER - FILES

from app.models import File
from app.dac import general as gen_dac
from app.dac import modules as mod_dac
from app.constants import *
import sqlalchemy


def create_file(data):
    """ Method used to add the details of an uploaded file into the database

    :param data: a dictionary containing the following details:
                - name of the file : string
                - tutor id : integer :  (id of the tutor who has uploaded the files)
                - module id: integer :  (id of the module where the file is uploaded)
                - link : string :  (firebase link to the file)
    :return: None if there was trouble adding file details into the database, File object otherwise
    """
    # creating a new file object
    new_file = File(
        File_Name=data[FILE_NAME],
        Publisher_ID=data[TUTOR_ID],
        Module_ID=data[MODULE_ID],
        Link=data[FILE_LINK]
    )
    # adding new file object to the database
    return gen_dac.insert(new_file)


def get_files(data):
    """ A method that is used to fetch list of all the files in the system/module

    :param data: A python dictionary containing the following details :
                - module_id : integer :  of the module whose files are requred (optional)

                if the data dictionary is empty, all the files in the system are returned, otherwise files of a specific
                module are returned.

    :return: list of File model object if query was successful, None otherwise
    """
    module = mod_dac.get_module(data[MODULE_ID])
    if module:
        # querying the database to find all the files associated with the module
        return module.Files.all()
    else:
        return None


def get_file(file_id):
    """ A method used to fetch the details of a file by

    :param file_id: integer :  id of the file whose details need to be returned
    :return: File object if the query was successful, None otherwise
    """
    try:
        # querying the db for the file
        return File.query.filter_by(File_ID=file_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return None
