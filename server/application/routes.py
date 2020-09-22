from application import app, db, bcrypt
from flask import render_template, redirect, url_for, request, Flask, jsonify, redirect
from application.forms import RegistrationForm, LoginForm, UpdateAccountForm
from application.models import Users
from flask_login import login_user, current_user, logout_user, login_required, current_user
from itertools import cycle
from PIL import Image
import pymysql
import sqlalchemy
import requests
import subprocess
import json

@app.route('/planner', methods=['GET', 'POST'])
def planner():
    form = dayCheck()
    return render_template("planner.html", title = "Planner", form=form)#, plan=plan)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        db.session.commit()
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name        
        form.email.data = current_user.email        
    return render_template('account.html', title='Account', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_pw = bcrypt.generate_password_hash(form.password.data)

        user = Users(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=hash_pw
            )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user=Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
    return render_template('login.html', title='Login', form=form)

@app.route("/account/delete")
@login_required
def account_delete():
    user = current_user.id
    account = Users.query.filter_by(id=user).first()
    logout_user()
    db.session.delete(account)
    db.session.commit()
    return redirect(url_for('register'))


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    report={}
    f = open('/application/surfScrape/quotes.json')
    data = json.load(f)
    days_string = data[0]["day"]
    size_string = data[0]["size"]
    size, days = stringminipulation(size_string, days_string)
    report = makeDictionary(size, days)
    f.close()
    return render_template('home.html', title='Home', report=report)


def picSize(size):
    pic_sizes = []
    for i in range(len(size)):
        if "-" in size[i]:
            pic_sizes.append(int(size[i][2]))
        else:
            pic_sizes.append(int(size[i].replace("ft", "")))
    return pic_sizes

def makeDictionary(size, days):
    report={}
    i = 0
    x = 0
    size_temp=[]
    while x != len(days):
        while i != (len(size)):
            if i % 8 !=0 or i == 0:
                size_temp.append(size[i])
                report[days[x]] = size_temp
                i+=1
            else:
                report[days[x]] = size_temp
                size_temp=[]
                size_temp.append(size[i])
                i+=1
                break
        x +=1
    return report

def stringminipulation(size,day):
    times = ["12am", "3am", "6am", "9am", "Noon", "3pm", "6pm", "9pm"]
    character_replaced_size = size.replace('[', '').replace("'",'').replace(',','').replace(']','')
    character_replaced_day = day.replace('[', '').replace("'",'').replace(']','')
    size_list = list(character_replaced_size.split(" "))
    day_list = list(character_replaced_day.split(","))
    picture_size = picSize(size_list)
    for i in range(len(day_list)):
        day_list[i] = day_list[i].strip()
    size_list = list(map(list, (zip(size_list, cycle(times), picture_size)) if len(size_list) > len(times) else (zip(cycle(size_list), times, picture_size))))
    return size_list, day_list
