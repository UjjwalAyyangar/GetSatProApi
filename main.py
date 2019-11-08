from app import app
from db_setup import setup
setup()

if __name__ == '__main__':
    app.debug = True
    setup()
    app.run(debug=True, host='0.0.0.0', port=5000)
    #app.run(host='127.0.0.1', port=5000)