web: rm -rf migrations; rm -rf getSatPro.db; flask db init; python db_setup.py; flask migrate; flask upgrade; gunicorn main:app --log-level debug

