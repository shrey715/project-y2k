from y2k_editor import app, db_init

if __name__ == '__main__':
    db_init()
    # app.run(port=5000)
    app.run(debug=True, port=5000)
