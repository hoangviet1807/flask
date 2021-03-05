from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.utils import  secure_filename
from datetime import timedelta



app = Flask(__name__)
app.secret_key = 'many random bytes'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'
app.config['USE_SESSION_FOR_NEXT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=20)




global COOKIE_TIME_OUT
COOKIE_TIME_OUT = 60*5 


mysql = MySQL(app)


@app.route("/", methods = ['GET','POST'])
@app.route('/login', methods = ['GET','POST'])
def login():
    msg = ''
   
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
      
        username = request.form['username']
        password = request.form['password']
        remember = request.form.getlist('inputRemember')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select * from users WHERE username = %s AND password = %s', (username, password))     
        users = cursor.fetchone()
        if users:
            session['loggedin'] = True
            session['id'] = users['id']
            session['username'] = users['username']
            session['name'] = users['name'] 
            return redirect(url_for('Index'))
        else:
            msg = 'Incorrect username/password!'

    return render_template("login.html", msg = msg)

@app.route('/Index')
def Index():
    username = ""
    if 'name' in session:
        username = session['name']
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM users")
    data = cur.fetchall()
    cur.close()

    return render_template('index2.html', account = data, username = username )



@app.route('/insert', methods = ['POST'])
def insert():
    msg = None
    if request.method == "POST":

        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select * from users WHERE username = %s', (username))  
        users = cursor.fetchone()
        if session['username'] != users['username']:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO users (username, password, name) VALUES (%s, %s, %s)", (username, password, name))
            mysql.connection.commit()
        else:
            msg = 'Username is Exist'
            return redirect(url_for('Index', msg = msg))

@app.route('/delete/<string:id_data>', methods = ['GET'])
def delete(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('Index'))





@app.route('/update',methods=['POST','GET'])
def update():

    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE users
               SET username=%s, password=%s, name=%s
               WHERE id=%s
            """, (username, password,name, id_data))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('Index'))


@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
        return redirect(url_for('login'))






if __name__ == "__main__":
    app.run(debug=True)
