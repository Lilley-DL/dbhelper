from flask import Flask,render_template,url_for,request,jsonify,flash,redirect
from dotenv import load_dotenv
import csv , json, os
import psycopg2

from flask_wtf import FlaskForm
from wtforms import StringField,EmailField,SubmitField,PasswordField,HiddenField
from wtforms.validators import DataRequired,Email

import flask_login

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('CSRF_SECRET_KEY')

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

##USER MANAGEMENT

class CustomAnonymousUser(flask_login.AnonymousUserMixin):
    def __init__(self):
        self.id = None
        self.username = "Guest"
        self.email = None

login_manager.anonymous_user = CustomAnonymousUser
class User(flask_login.UserMixin):
    def __init__(self, id, userCode):
        self.id = id
        self.userCode = userCode

#load user 

#forms

class LoginForm(FlaskForm):
    userCode = StringField('User Code:',validators=[DataRequired()])
    passCode = PasswordField('Passcode: ',validators=[DataRequired()])
    submit = SubmitField("Login")



#database thingssssss
DATABASE_URL = os.environ.get('DEV_DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def insertTableData(data):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO db_tables (table_data) VALUES (%s)",(data,))
        conn.commit()
        cur.close()
        conn.close()
        app.logger.info("Data inserted succesfully")
    except (Exception, psycopg2.Error) as error:
        app.logger.error("Error while inserting data",error)


@login_manager.user_loader
def load_user(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id,user_code FROM users WHERE user_id = %s",(user_id,))
        rows = cur.fetchall()
        formatted_rows = [{"id": row[0], "userCode": row[1]} for row in rows]
        cur.close()
        conn.close()
        app.logger.info(f"USER LOADER RESULT = {rows}")

        if formatted_rows:
            userInfo = formatted_rows[0]
            current_user = User(id = userInfo['id'], userCode=userInfo['userCode'])
            #current_user = User(id=formatted_rows[0][0],userCode=formatted_rows[0][1])
            app.logger.info(f"CURRENT USER OBJECT IN loader  = id:{current_user.id}, userCode:{current_user.userCode}")
           #flask_login.login_user(current_user)
            return current_user
    except (Exception, psycopg2.Error) as error:
        app.logger.error("Error while loading user  ",error)
        return None

#request loader ? 

@login_manager.unauthorized_handler
def unauthorized_handler():
    #return "Unauthorized", 401
    return redirect(url_for('login'))

@app.route("/login",methods=['GET','POST'])
def login():
    userCode = None
    passCode = None

    form = LoginForm()

    if form.validate_on_submit():
        userCode = form.userCode.data
        passCode = form.passCode.data

        #check them against databse 
        try:
            #check the usercode exists in the databse 
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT user_id,user_code FROM users WHERE passcode = %s",(passCode,))
            rows = cur.fetchall()
            # conn.commit()
            formatted_rows = [{"id": row[0], "userCode": row[1]} for row in rows]
            cur.close()
            conn.close()
            
            if formatted_rows:
                userInfo = formatted_rows[0]
                app.logger.info(f"FORMATTED = {userInfo['id']}")

                current_user = User(id = userInfo['id'], userCode=userInfo['userCode'])
                app.logger.info(f"current user = {current_user.__dict__}")
                flask_login.login_user(current_user)
                return redirect('/')
            else:
                app.logger.info(f"NO FORMATTED ROWS TO SHOW")
                flash("user not recognised")
                return redirect('/login')
            #if code exists check the passcode matches 

            #if they match then lgo the user session in 
        except Exception as e:
            flash(e)
            app.logger.error(f"error when logging in :: {e}")
            return redirect('/login')

    if request.method == "GET":
        return render_template("login.html",form=form)

@app.route("/logout")
def logout():
    flask_login.logout_user()
    return redirect("/login")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/erd-builder")
@flask_login.login_required
def erdBuilder():
    return render_template("erdBuilder.html")

@app.route("/save",methods=['POST'])
def save():
    
    return render_template("index.html")
    # if request.method == 'POST':
    #     data = request.json
    #     processed = {'processed':data}

    #     csv_data = []
    #     for item in data:
    #         csv_data.append(item.values()) 

    #     json_data = json.dumps(processed)
    #     app.logger.info(json_data)
        
    #     #Removed for now. need to set up a new DB for it
    #     #insertTableData(json_data)

    #     app.logger.info(processed)
    #     return jsonify(processed)
    
@app.route("/tableview",methods=['GET'])
@flask_login.login_required
def tableView():
    #get the data from the csv 
    data = list()

    with open('fileSavetyest.csv','r',newline='') as file:
        reader = csv.DictReader(file)
        
        app.logger.info("\nJSON :::")
        app.logger.info(json.dumps(reader.fieldnames))
        data = list(reader)
        # for row in reader:
        #     app.logger.info("INFO ::::\n")
        #     app.logger.info(row['fields'])
            
            # data[f'table_'+row['name']] = row['name']
            # data[f''+row['name']+'_fields'] = row['fields']

    if data:                
        app.logger.info("DATA INFO\n")
        app.logger.info(data)

        return render_template('saved.html',saved_tables = data)
    else:
        return render_template('saved.html')

@app.route("/quizzes")
@flask_login.login_required
def quizzesLanding():
    return render_template("quizzes.html")

@app.route("/quiz")
@flask_login.login_required
def viewQuiz(): #add the specific route based on quiz id 
    return render_template("quiz.html")


@app.route("/builder")
@flask_login.login_required
def tabelBulder():
    return render_template('tableBuilder.html')

@app.route("/textBuilder")
@flask_login.login_required
def textBuilder():
    return render_template('textBuilder.html')

##for render to run 
if __name__ == "__main__":
    app.run()
    