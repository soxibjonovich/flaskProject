import asyncio

from hashes import CsvController
from utils import extractFollowers, inviteFollowers

from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

csv_controller = CsvController(".")
from models import *

db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
@login_required
def hello_world():
    user = User.query.filter_by(id=current_user.id).first()
    user_hashes = {}
    if user.id:
        user_hashes = csv_controller.prepare_user_data(user.id)
    return render_template('dashboard/dashboard.html', user_hashes=user_hashes, all_hashes=len(user_hashes))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('hello_world'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        current_user.id = user.id
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('hello_world'))
        else:
            flash('Ma\'lumotlarni to\'g\'ri kiriting!', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('hello_world'))


@app.route('/addnumber/solded', methods=['GET', 'POST'])
@login_required
def add_number_handler():
    if request.method == 'POST':
        number = request.form['phone_number']
        if len(number) < 5:
            flash('Raqamni to\'g\'ri kiriting', 'danger')
            return render_template('dashboard/addnumbersold/addnumbersold.html')
        session['number'] = number

        return redirect(url_for('add_number_code_handler'))
    elif request.method == 'GET':
        session['number'] = None

    return render_template('dashboard/addnumbersold/addnumbersold.html')


@app.route('/addnumber/solded/verify', methods=['GET', 'POST'])
@login_required
def add_number_code_handler():
    if request.method == 'POST':
        ...
    elif request.method == 'GET':
        return render_template('dashboard/addnumbersold/verify.html')


@app.route('/group2group', methods=['GET', 'POST'])
@login_required
def group2group_handler():
    if request.method == 'POST':
        from_g = request.form['from_group']
        to_g = request.form['to_group']
        date = request.form['date']
        user_hashes = {}
        for filename in csv_controller.prepare_user_data(current_user.id).keys():
            user_hashes += csv_controller.get_info_from_file(filename)
        return
        async def run_tasks():
            result = await extractFollowers(user_hashes, from_g, to_g, date)
            if result[0] == "error":
                flash(result[1], 'danger')
            elif result[0] == "success":
                await inviteFollowers(users=result[1], client=result[-1], to_group=to_g)
                flash('So\'rov muvoffaqiyatli yakunlandi!', 'success')

        asyncio.run(run_tasks())
        return render_template('dashboard/group2group.html')
    return render_template('dashboard/group2group.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
