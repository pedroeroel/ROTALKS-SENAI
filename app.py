from flask import Flask, render_template, request, redirect, session
import mysql.connector
from config import *

def connectDB():
    
    connect = mysql.connector.connect(
        host = DB_HOST,
        user = DB_USER,
        password = DB_PASSWORD,
        database = DB_NAME
    )
    return connect

def stopDB(cursor, connect):
    cursor.close()
    connect.close()

app = Flask(__name__)
app.secret_key = SECRET_KEY

@app.route('/')
def index():
    SQLcommand = '''
    SELECT post.*, userro.userName
    FROM post
    JOIN userro ON post.userId = userro.userId
    ORDER BY post.postDate DESC
'''

    connectionDB = connectDB()
    cursorDB = connectionDB.cursor()
    cursorDB.execute(SQLcommand)
    posts = cursorDB.fetchall()
    stopDB(cursorDB, connectionDB)

    # Format the data before sending to the pattern

    fposts = []

    for post in posts:
        fposts.append({
            'postId': post[0],
            'userId': post[1],
            'content': post[2],
            'date': post[3].strftime("%d/%m/%y %H:%M"),
            'author': post[4]
        })

    if 'userId' in session:
        login = True
        userId = session['userId']
    else:
        login = False
        userId = ''

    if 'adm' in session:
        adm = True
        login = True
    else:
        adm = False

    return render_template('index.html', adm=adm, posts=fposts, login=login, userId=userId)


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/access', methods=['GET', 'POST'])
def access():

    if request.method == 'GET':
        return redirect('/login')
    
    session.clear()

    inputEmail = request.form['email']
    inputPassword = request.form['password']

    if inputEmail == ADM_EMAIL and inputPassword == MASTER_PASSWORD:
        session['adm'] = True
        return redirect('/adm')

    SQLcommand = 'SELECT * FROM userro WHERE userEmail = %s AND userPassword = %s'
    connectionDB = connectDB()
    cursorDB = connectionDB.cursor()
    cursorDB.execute(SQLcommand, (inputEmail, inputPassword))
    userFound = cursorDB.fetchone()
    stopDB(cursorDB, connectionDB)

    if userFound:
        session["userId"] = userFound[0]
        return redirect('/')
    else:
        return render_template("login.html", errormsg="User/password is incorrect!")
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/newpost')
def newpost():
    if 'adm' in session:
            adm = True
            login = True
    else:
        adm = False

    if 'userId' in session:
        userId = session['userId']
        SQLcommand = 'SELECT * FROM userro WHERE userId = %s'
        connectionDB = connectDB()
        cursorDB = connectionDB.cursor()
        cursorDB.execute(SQLcommand, (userId,))
        userFound = cursorDB.fetchone()
        stopDB(cursorDB, connectionDB)

        login = True
        
        return render_template('newpost.html', login=login, adm=adm, user=userFound)
    else:
        return redirect('/login')

@app.route('/createpost', methods=['GET', 'POST'])    
def createpost():
    
    if request.method == 'GET':
        return redirect('/newpost')
    
    userId = request.form['userId']
    content = request.form['content']
    
    if content:
        connectionDB = connectDB()
        cursorDB = connectionDB.cursor()
        cursorDB.execute("SET time_zone = '-3:00';")
        SQLcommand = 'INSERT INTO post (userId, postContent) VALUES (%s, %s)'
        cursorDB.execute(SQLcommand, (userId, content))
        connectionDB.commit()
        stopDB(cursorDB, connectionDB)
    return redirect('/')

@app.errorhandler(404)
def page_not_found(error):

    if 'adm' in session:
        adm = True
        login = True
    elif 'userId' in session:
        login = True
        adm = False

    return render_template('error404.html', adm=adm, login=login), 404

@app.route('/adm')
def adm():

    if 'adm' not in session:
        return redirect('/login')
    
    connectionDB = connectDB()
    cursorDB = connectionDB.cursor()
    SQLcommand = 'SELECT * FROM userro'
    cursorDB.execute(SQLcommand)
    users = cursorDB.fetchall()

    SQLcommand = '''
        SELECT post.*, userro.userName
        FROM post
        JOIN userro ON post.userId = userro.userId
        ORDER BY post.postDate DESC ;
'''

    adm = True
    login = True

    cursorDB.execute(SQLcommand)
    posts = cursorDB.fetchall()

    stopDB(cursorDB, connectionDB)
    
    return render_template('adm.html', adm=adm, login=login, userlist=users, posts=posts)

@app.route('/newuser')
def newuser():
    if 'adm' not in session:
        return redirect('/login')
    
    adm=True
    login=True
    
    return render_template('newuser.html', adm=adm, login=login)

@app.route('/create-user', methods=['POST'])
def create_user():

    if 'adm' not in session:
        return redirect('/login')
    
    adm=True
    login=True
    
    if request.method == 'POST':
        userName = request.form['name']
        userEmail = request.form['email']
        userPassword = request.form['password']

        if userName and userEmail and userPassword:
            try:
                connectionDB = connectDB()
                cursorDB = connectionDB.cursor()
                SQLcommand = 'INSERT INTO userro (userName, userEmail, userPassword) VALUES (%s, %s, %s);'
                cursorDB.execute(SQLcommand, (userName, userEmail, userPassword))
                connectionDB.commit()
            except mysql.connector.IntegrityError:
                return render_template('newuser.html', login=login, adm=adm,  errormsg=f'The email {userEmail} is already registered!')
            finally:
                stopDB(cursorDB, connectionDB)
    
    return redirect('/adm')

@app.route('/edit-user/<int:id>')
def edit_user(id):

    if 'adm' not in session:
        return redirect('/login')
    
    session['userId'] = id

    connectionDB = connectDB()
    cursorDB = connectionDB.cursor()
    SQLcommand = 'SELECT * FROM userro WHERE userId = %s'
    cursorDB.execute(SQLcommand, (id, ))
    found_user = cursorDB.fetchone()
    stopDB(cursorDB, connectionDB)

    adm=True
    login=True

    return render_template('edituser.html', login=login, adm=adm, user=found_user)

@app.route('/update-user', methods=['POST'])
def update_user():

    if 'adm' not in session:
        return redirect('/login')
    
    if request.method == "POST":
        user_id = session.get('userId')
        userName = request.form['name']
        userEmail = request.form['email']
        userPassword = request.form['password']

        if userName and userEmail and userPassword:
            connectionDB = connectDB()
            cursorDB = connectionDB.cursor()
            SQLcommand = "UPDATE userro SET userName = %s, userEmail = %s, userPassword = %s WHERE userId = %s"
            cursorDB.execute(SQLcommand, (userName, userEmail, userPassword, user_id))
            connectionDB.commit()
            stopDB(cursorDB, connectionDB)
    
    return redirect('/adm')


@app.route('/delete-user/<int:id>')
def delete_user(id):

    if 'adm' not in session:
        return redirect('/login')

    connectionDB = connectDB()
    cursorDB = connectionDB.cursor()
    SQLcommand = 'DELETE FROM post WHERE userId = %s'
    cursorDB.execute(SQLcommand, (id, ))
    connectionDB.commit()

    SQLcommand = 'DELETE FROM userro WHERE userId = %s'
    cursorDB.execute(SQLcommand, (id, ))
    connectionDB.commit()

    return redirect('/adm')

@app.route('/delete-post/<int:id>')
def delete_post(id):

    connectionDB = connectDB()
    cursorDB = connectionDB.cursor()
    
    if not session:
        return redirect('/login')
    
    if session['adm']:
        adm = True
        SQLcommand = 'SELECT * FROM post WHERE postId = %s'
        cursorDB.execute(SQLcommand, (id, ))
        post = cursorDB.fetchone()
    
    elif session['userId']:
        userId = session['userId']
        SQLcommand = 'SELECT * FROM post WHERE postId = %s AND userId = %s'
        cursorDB.execute(SQLcommand, (id, userId,))
        post = cursorDB.fetchone()

    
    if post: 
        SQLcommand = 'DELETE FROM post WHERE postId = %s'
        cursorDB.execute(SQLcommand, (id, ))
        connectionDB.commit()
        stopDB(cursorDB, connectionDB)
    else:
        return redirect('/')

    if 'adm' in session:
        return redirect('/adm')
    else:
        return redirect('/')

if status == 'local':
    if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0', port='3000')