from y2k_editor import app, db_init

if __name__ == '__main__':
    db_init()
    app.run(debug=True)
