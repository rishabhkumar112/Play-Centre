from flask import Flask, render_template, request, redirect, session, flash

from flaskext.mysql import MySQL
import hashlib
import random

app = Flask(__name__)
app.secret_key = "mysecret123"

mysql = MySQL()

app.config['MYSQL_DATABASE_HOST']  = 'localhost'
app.config['MYSQL_DATABASE_USER']  = 'root'
app.config['MYSQL_DATABASE_PASSWORD']  = 'letmein'
app.config['MYSQL_DATABASE_DB']  = 'dbms'

mysql.init_app(app)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/signup/', methods = ['POST', 'GET'])
def signup():
    if(request.method == "POST"):
        # Todo: fetch data and check for unique username;
        userd = request.form
        username = userd['username']
        password = userd['password']
        email = userd['email']
        salt = '1ab'
        actual = password + salt
        stored_pass = hashlib.md5(actual.encode())

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("select username, email from users")
        data = cursor.fetchall()

        flag = 0
        flag1 = 0
        #to check if user already registered
        for d in data:
            if(d[0] == username):
                flag = 1
                break
            elif(d[1] == email):
                flag1 = 1
                break
        
        if(flag == 0 and flag1 == 0):
            cursor.execute("INSERT INTO users(username, password, email) VALUES(%s, %s, %s)", (username, stored_pass.hexdigest(), email))
            conn.commit()
            cursor.execute("INSERT INTO money(username, amount) VALUES(%s, %s)", (username, '20'))
        elif(flag == 1):
            return "<script>alert('Username already taken! Try another one'); window.location = 'http://127.0.0.1:5000/signup/';</script>"
            
        elif (flag1 == 1):
            return "<script>alert('This email address has already been registered.'); window.location = 'http://127.0.0.1:5000/signup/';</script>"
            

        conn.commit()
        cursor.close()
        return redirect('/login/')
    return render_template('/signup.html')

@app.route('/login/', methods = ['POST', 'GET'])
def login():
    if(request.method == "POST"):
        userde = request.form
        username = userde['username']
        #for checking online status
        password = userde['password']
        p = password+'1ab'
        passcode = hashlib.md5(p.encode())
        
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("select username, password from users")
        data = cursor.fetchall()

        for d in data:
            if(d[1] == passcode.hexdigest() and d[0] == username):
                session['logged_in'] = True
                session['username'] = username
                conn.commit()
                cursor.execute("INSERT INTO status(username) VALUES(%s)", (username))
                conn.commit()
                print('logged in')
                return redirect('/')
        conn.commit()
        cursor.close()
    return render_template('/login.html')

@app.route('/logout/')
def logout():
    conn = mysql.connect()
    cursor = conn.cursor()
    
    print(session['username'])
    cursor.execute("DELETE FROM status where username = %s", (session['username']))
    
    conn.commit()
    cursor.close()
    
    session.clear()
    return redirect('/')

@app.route('/play/')
def play():

    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("select username from status")
    data = cursor.fetchall()

    online = []
    for d in data:
        online.append(d[0])

    conn.commit()
    cursor.close()
    
    return render_template('/play.html', online = online)

@app.route('/practice/', methods = ['POST', 'GET'])
def practice():
    conn = mysql.connect()
    cursor = conn.cursor()
    #for game
    lucky = []
    if(request.method == "POST"):
        
        random_num = random.randint(1, 3)
        lucky.append(random_num)
        user = request.form
        check = user['user_input']
        flag = 0
        if(random_num-int(check) == 0):
            print('won')
            flag =1
        else:
            print('lost')
            flag = 0

        cursor.execute("select amount from money where username = %s", (session['username']))
        data = cursor.fetchall()
        
        curr = int(0)
        for d in data:
            curr = int(d[0])

        conn.commit()
        inc = curr+10
        dec = curr-5

        print(inc)
        print(dec)

        if(flag == 1):
            cursor.execute("UPDATE money SET amount = %s WHERE username = %s", (inc, session['username']))
        else:
            cursor.execute("UPDATE money SET amount = %s WHERE username = %s", (dec, session['username']))
        
        conn.commit()
        cursor.close()
    return render_template('/practice.html', lucky = lucky)

@app.route('/profile/')
def profile():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select amount from money where username = %s", (session['username']))
    data = cursor.fetchall()
    
    for d in data:
        amount = int(d[0])

    conn.commit()
    details = {
        'username':session['username'],
        'amount' : amount,
    }
    cursor.close()
    return render_template('/profile.html', details = details)


if __name__ == '__main__':
    app.run(debug = True)