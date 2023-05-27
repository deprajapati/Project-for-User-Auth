from flask.globals import request
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from project_orm import User
from utils import *
import pandas as pd
import numpy as np
import joblib

from flask import Flask,session,flash,redirect,render_template,url_for

app = Flask(__name__)
app.secret_key = "the basics of life with python"

def load_xgb_model():
    xgb_r = joblib.load('training/xgb_r.pkl')
    return xgb_r

def make_df(team, targeted_productivity, smv, wip, over_time, 
            incentive, idle_time, idle_men, no_of_style_change, 
            no_of_workers, month, quarter_Quarter1, quarter_Quarter2, 
            quarter_Quarter3, quarter_Quarter4, quarter_Quarter5,
            day_Sunday, 
            day_Monday, 
            day_Tuesday, 
            day_Wednesday,
            day_Thursday, 
            day_Saturday, 
        ):
    dfinp = pd.DataFrame({
        'team' : [team],
        'targeted_productivity' : [targeted_productivity],
        'smv' : [smv],
        'wip' : [wip],
        'over_time' : [over_time],
        'incentive' : [incentive],
        'idle_time' : [idle_time],
        'idle_men': [idle_men],
        'no_of_style_change' : [no_of_style_change],
        'no_of_workers' : [no_of_workers],
        'month' : [month],
        'quarter_Quarter1' : [quarter_Quarter1],
        'quarter_Quarter2' : [quarter_Quarter2],
        'quarter_Quarter3' : [quarter_Quarter3],
        'quarter_Quarter4' : [quarter_Quarter4],
        'quarter_Quarter5' : [quarter_Quarter5],
        'day_Monday' : [day_Monday],
        'day_Saturday' : [day_Saturday],
        'day_Sunday' : [day_Sunday],
        'day_Thursday' : [day_Thursday],
        'day_Tuesday' : [day_Tuesday],
        'day_Wednesday' : [day_Wednesday]
    })
    return dfinp
def predict_performance(inp):
    model = load_xgb_model()
    return model.predict(inp)[0] * 100


def get_db():
    engine = create_engine('sqlite:///database.db')
    Session = scoped_session(sessionmaker(bind=engine))
    return Session()

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email and validate_email(email):
            if password and len(password)>=6:
                try:
                    sess = get_db()
                    user = sess.query(User).filter_by(email=email,password=password).first()
                    if user:
                        session['isauth'] = True
                        session['email'] = user.email
                        session['id'] = user.id
                        session['name'] = user.name
                        del sess
                        flash('login successfull','success')
                        return redirect('/home')
                    else:
                        flash('email or password is wrong','danger')
                except Exception as e:
                    flash(e,'danger')
    return render_template('index.html',title='login')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        if name and len(name) >= 3:
            if email and validate_email(email):
                if password and len(password)>=6:
                    if cpassword and cpassword == password:
                        try:
                            sess = get_db()
                            newuser = User(name=name,email=email,password=password)
                            sess.add(newuser)
                            sess.commit()
                            del sess
                            flash('registration successful','success')
                            return redirect('/')
                        except:
                            flash('email account already exists','danger')
                    else:
                        flash('confirm password does not match','danger')
                else:
                    flash('password must be of 6 or more characters','danger')
            else:
                flash('invalid email','danger')
        else:
            flash('invalid name, must be 3 or more characters','danger')
    return render_template('signup.html',title='register')

@app.route('/forgot',methods=['GET','POST'])
def forgot():
    return render_template('forgot.html',title='forgot password')

@app.route('/home',methods=['GET','POST'])
def home():
    if session.get('isauth'):
        username = session.get('name')
        if request.method == 'POST':
            print(request.form)
            team = request.form.get('team')
            trageted_productivity = request.form.get('trageted_productivity')
            smv = request.form.get('smv')
            wip = request.form.get('wip')
            over_time = request.form.get('over_time')
            inceptive = request.form.get('inceptive')
            idle_time = request.form.get('idle_time')
            idle_men = request.form.get('idle_men')
            no_of_style_change = request.form.get('no_of_style_change')
            no_of_workers = request.form.get('no_of_workers')
            month = request.form.get('month')
            quarter_Quarter1 = request.form.get('quarter_Quarter1')
            quarter_Quarter2 = request.form.get('quarter_Quarter2')
            quarter_Quarter3 = request.form.get('quarter_Quarter3')
            quarter_Quarter4 = request.form.get('quarter_Quarter4')
            quarter_Quarter5 = request.form.get('quarter_Quarter5')
            day_Sunday = request.form.get('day_Sunday')
            day_Monday = request.form.get('day_Monday')
            day_Tuesday = request.form.get('day_Tuesday')
            day_Wednesday = request.form.get('day_Wednesday')
            day_Thursday = request.form.get('day_Thursday')
            day_Saturday = request.form.get('day_Saturday')

            try:
                df = make_df(team, trageted_productivity, smv, wip, over_time,
                               inceptive, idle_time, idle_men, no_of_style_change,
                               no_of_workers, month, quarter_Quarter1, quarter_Quarter2,
                                quarter_Quarter3, quarter_Quarter4, quarter_Quarter5,
                                day_Sunday, day_Monday, day_Tuesday, day_Wednesday,
                                day_Thursday, day_Saturday)
                performance = predict_performance(df)
                flash(f'predicted performance is {performance}','success')
                return render_template('home.html',title=f'Home|{username}',performance=performance)
            except Exception as e:
                flash(e,'danger')    
        return render_template('home.html',title=f'Home|{username}')

    flash('please login to continue','warning')
    return redirect('/')

@app.route('/about')
def about():
    return render_template('about.html',title='About Us')

@app.route('/logout')
def logout():
    if session.get('isauth'):
        session.clear()
        flash('you have been logged out','warning')
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True,threaded=True)


