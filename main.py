from app import app


if __name__ == '__main__':
    app.debug = False
    app.run(debug=False, host='0.0.0.0', port=5000)
    #app.run(host='127.0.0.1', port=5000)