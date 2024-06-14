import asyncio
import datetime
import random
import threading
import time
from operator import attrgetter

import schedule

from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from hashes import CsvController
from forms import GetCode, Login, EditProfile

from utils import *
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = generate_password_hash("habibulloh")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

csv_controller = CsvController("./hashes/")

from models import *
from plugins import add_plugins

add_plugins(app)
db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
@login_required
def hello_world():
    page_number = request.args.get('page', 1)
    try:
        page_number = int(page_number)
    except ValueError:
        page_number = 1

    user = User.query.filter_by(id=current_user.id).first()
    user_hashes = []
    if user and user.id:
        user_hashes = Hashes.query.filter_by(user_id=user.id).all()

    content = paginate(user_hashes, page_number, 100)
    return render_template('dashboard/dashboard.html',
                           user_hashes=content[0],
                           all_hashes=len(user_hashes),
                           current_page=content[1])


@app.route('/<user_id>/<hash_id>/unarchive', methods=["POST", "GET"])
@login_required
async def unarchived_handler(user_id, hash_id):
    user = load_user(user_id)
    getcode = request.args.get("getcode", False, type=bool)
    if getcode:
        hash = Hashes.query.filter_by(user_id=user_id, id=hash_id).first()
        result = await get_code(hash.hash, hash.clone_device_name)

        if result:
            flash(f"Kod {result}, kod muvofffaqqiyatli olindi", "success")
            return render_template('dashboard/hash_unarchive.html', hash=hash, user=user, is_wait=True)
    hash = Hashes.query.filter_by(id=hash_id, user_id=user_id).first()

    if request.method == "POST":
        ...
    return render_template('dashboard/hash_unarchive.html', hash=hash, user=user)


@app.route('/login', methods=['GET', 'POST'])
async def login():
    form = Login()
    if current_user.is_authenticated:
        return redirect(url_for('hello_world'))
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Ma\'lumotlarni to\'g\'ri kiriting!', 'danger')
            return render_template('login.html', form=form)
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('hello_world'))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
async def logout():
    logout_user()
    return redirect(url_for('hello_world'))


@app.route('/addnumber/', methods=['GET', 'POST'])
@login_required
async def add_private_number():
    if request.method == "POST":
        number = request.form['phone_number']
        if Hashes.check_phone_number(number):
            flash("Bu raqam platformaga oldin qo'shilgan", "danger")
            return render_template('dashboard/addnumberprvt/addnumber.html')
        if len(number) < 5:
            flash('Raqamni to\'g\'ri kiriting! ', 'danger')
            return render_template('dashboard/addnumberprvt/addnumber.html')
        session['once_dataname'] = generate_random_password()
        result = await send_code(session['once_dataname'], number)
        if "error" in result.keys():
            flash(result['error'], 'danger')
            return render_template('dashboard/addnumberprvt/addnumber.html')
        session['phone_hash'] = result['phone_code_hash']
        session['number'] = number
        return redirect(url_for('verify_prvt_number_handler', phone=number))
    return render_template("dashboard/addnumberprvt/addnumber.html")


@app.route('/addnumber/<phone>/verify', methods=["POST", "GET"])
@login_required
async def verify_prvt_number_handler(phone: str):
    user = User.query.get(int(current_user.id))
    form = GetCode()
    if request.method == 'POST':
        if form.validate_on_submit():
            if not form.code.data.replace("-", "").isdigit():
                flash('Kod xato kiritilgan', 'danger')
                return render_template('dashboard/addnumberprvt/verify.html', number=phone, form=form)
            result = await get_hash(
                dataname=session['once_dataname'],
                phone=phone,
                phone_code_hash=session['phone_hash'],
                code=form.code.data,
                password=form.two_code.data,
                edit_password=False,
                new_password=user.twofacode
            )
            if isinstance(result, dict):
                flash(result["error"], 'danger')
                return render_template('dashboard/addnumberprvt/verify.html', number=phone, form=form)
            session.pop('phone_hash')
            session['hash'] = result
            print(result)
            hash_info = await get_info(result, random_device=True)
            db.session.add(Hashes(
                hash=result,
                user_id=current_user.id,
                work_status=Status.Inactive,
                hash_status=HashStatus.live,
                phone_number=session['number'],
                name=hash_info[0].first_name,
                telegram_id=hash_info[0].id,
                clone_device_name=hash_info[1]
            ))
            csv_controller.add_new_hash(session['hash'], current_user.id)
            db.session.commit()
            delete_file(f"./sessions/{session['once_dataname']}.session")
            session.pop('once_dataname')
            return redirect(url_for("add_private_number"))
    return render_template('dashboard/addnumberprvt/verify.html', number=phone, form=form)


@app.route('/addnumber/solded', methods=['GET', 'POST'])
@login_required
async def add_number_handler():
    if request.method == 'POST':
        number = request.form['phone_number']
        if Hashes.check_phone_number(number):
            flash("Bu raqam platformaga oldin qo'shilgan", "danger")
            return render_template('dashboard/addnumbersold/addnumber.html')
        if len(number) < 5:
            flash('Raqamni to\'g\'ri kiriting', 'danger')
            return render_template('dashboard/addnumbersold/addnumber.html')
        session['once_dataname'] = generate_random_password()
        result = await send_code(session['once_dataname'], number)
        if "error" in result:
            flash(result["error"], 'danger')
            return render_template('dashboard/addnumbersold/addnumber.html')
        session['phone_hash'] = result['phone_code_hash']
        session['number'] = number
        return redirect(url_for('add_number_code_handler', phone=number))
    session.pop('number', None)
    session.pop('phone_hash', None)
    return render_template('dashboard/addnumbersold/addnumber.html')


@app.route('/addnumber/solded/<phone>/verify', methods=['GET', 'POST'])
@login_required
async def add_number_code_handler(phone: str):
    form = GetCode()
    if request.method == 'POST':
        if form.validate_on_submit():
            if not form.code.data.replace("-", "").isdigit():
                flash('Kod xato kiritilgan', 'danger')
                return render_template('dashboard/addnumbersold/verify.html', number=phone, form=form)
            result = await get_hash(dataname=session['once_dataname'], phone=phone,
                                    phone_code_hash=session['phone_hash'], code=form.code.data,
                                    password=form.two_code.data)
            if isinstance(result, dict):
                flash(result["error"], 'danger')
                return render_template('dashboard/addnumbersold/verify.html', number=phone, form=form)
            session.pop('phone_hash')
            session['hash'] = result
            delete_file(f"{session['once_dataname']}.session")
            session.pop('once_dataname')
            result = await get_info(session['hash'], random_device=True)
            db.session.add(InProgressHashes(
                hash=session['hash'],
                user_id=current_user.id,
                hash_status=HashStatus.live,
                phone_number=session['number'],
                name=result[0].first_name,
                telegram_id=result[0].id,
                clone_device_name=result[1]
            ))
            db.session.commit()
            return redirect(url_for('check_devices_handler', phone=phone))
    return render_template('dashboard/addnumbersold/verify.html', number=phone, form=form)


@app.route('/addnumber/solded/<phone>/devices', methods=['GET', 'POST'])
@login_required
async def check_devices_handler(phone: str):
    all_devices = await get_devices(session['hash'])
    if request.method == "POST":
        if len(all_devices[0]) == 1:
            if all_devices[0][0].device_model == "PC 64bit":
                flash("Muvoffaqiyatli raqam qo'shildi", "success")
                csv_controller.add_new_hash(session['hash'], current_user.id)
                result = await get_info(session['hash'], all_devices[1].device_model, random_device=True)
                db.session.add(Hashes(
                    hash=session['hash'],
                    user_id=current_user.id,
                    work_status=Status.Inactive,
                    hash_status=HashStatus.live,
                    phone_number=session['number'],
                    name=result[0].first_name,
                    telegram_id=result[0].id,
                    clone_device_name=result[1]
                ))
                db.session.commit()
                delete_file(f"./sessions/{session['once_dataname']}.session")
                return render_template('dashboard/addnumbersold/devices.html', number=phone, devices=all_devices[0],
                                       is_active=False)
            else:
                flash("Boshqa aktiv seanslarni yoping", "danger")
                return render_template('dashboard/addnumbersold/devices.html', number=phone, devices=all_devices[0],
                                       is_active=True)
        else:
            flash("Boshqa aktiv seanslarni yoping", "danger")
            return render_template('dashboard/addnumbersold/devices.html', number=phone, devices=all_devices[0],
                                   is_active=True)
    return render_template('dashboard/addnumbersold/devices.html', phone=phone, devices=all_devices[0], is_active=True)


@app.route('/group2group', methods=['GET', 'POST'])
@login_required
async def group2group_handler():
    if request.method == 'POST':
        free_hashes = Hashes.query.filter_by(user_id=current_user.id, work_status=Status.Inactive).all()

        if not free_hashes:
            flash("Hozirda sizning hamma profillaringiz ishlayapti birozdan keyin urinib ko'ring", 'warning')
            return render_template('dashboard/group2group.html')

        from_g = request.form['from_group']
        to_g = request.form['to_group']
        date = request.form['date']
        author = request.form['author']

        for hash in free_hashes:
            hash.work_status = Status.Active
        db.session.commit()

        try:
            result = await invite_followers(
                [hash.hash for hash in free_hashes],
                from_g,
                to_g,
                date
            )
            if result[0] == "error":
                flash(result[1], 'danger')
                for hash in free_hashes:
                    hash.work_status = Status.Inactive
                db.session.commit()
            elif result[0] == "success":
                flash('So\'rov muvoffaqiyatli yakunlandi!', 'success')

                for hash in free_hashes:
                    new_task = Tasks(
                        task_type=TaskType.GroupToGroupDate,
                        hash=hash.hash,
                        user_id=current_user.id,
                        hash_added_date=hash.hash_added_date,
                        date=datetime.strptime(date, '%m/%d/%Y'),
                        link=to_g,
                        task_author=author
                    )

                    db.session.add(new_task)
                    hash.work_status = Status.Inactive
                db.session.add(
                    db.session.add(
                        TaskHistory(
                            task_type=TaskType.ChannelDate,
                            task_added_date=datetime.utcnow(),
                            task_expire_date=datetime.strptime(date, '%m/%d/%Y'),
                            link=to_g,
                            task_author=author,
                            hash_count=len(free_hashes)
                        )
                    )
                )
                db.session.commit()
        except Exception as e:
            app.logger.error(f"Error in group2group_handler: {str(e)}")
            flash("Kutilmagan xato yuz berdi. Iltimos, qayta urinib ko'ring.", 'danger')
            for hash in free_hashes:
                hash.work_status = Status.Inactive
            db.session.commit()

        return render_template('dashboard/group2group.html')
    return render_template('dashboard/group2group.html')


@app.route('/profile', methods=["POST", "GET"])
@login_required
async def profile_handler():
    try:
        user = User.query.get(current_user.id)
    except AttributeError:
        return redirect("login")
    if request.method == "POST":
        ...
    user_hashes = csv_controller.prepare_user_data(current_user.id)
    return render_template("dashboard/profile.html", user=user, user_hashes_len=sum(user_hashes.values()))


@app.route('/edit_profile/<id>', methods=["POST", "GET"])
@login_required
async def edit_profile(id: str):
    form = EditProfile()
    user = User.query.get(int(id))
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('login'))
    if request.method == "POST":
        if form.password.data:
            user.password = form.password.data
        user.twofacode = form.twofacode.data
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile_handler'))
    return render_template('dashboard/edit_profile.html', user=user, form=form)


@app.route('/addtochannel/', methods=["POST", "GET"])
@login_required
async def addtochannel_handle():
    user_inactive_hashes = Hashes.query.filter_by(user_id=current_user.id, work_status=Status.Inactive).all()

    if request.method == "POST":
        channel_username = request.form['username']
        len_hash = int(request.form['num_hashes'])
        date = request.form['date']
        author = request.form['author']

        if len_hash > len(user_inactive_hashes):
            flash("siz kiritgan raqam sizda bo'sh bo'lgan hashlar sonidan ko'p", "danger")
            return redirect(url_for('addtochannel_handle'))

        selected_hashes = user_inactive_hashes[:len_hash]

        for hash in selected_hashes:
            db.session.add(
                Tasks(
                    task_type=TaskType.ChannelDate,
                    hash=hash.hash,
                    user_id=current_user.id,
                    hash_added_date=hash.hash_added_date,
                    date=datetime.strptime(date, '%m/%d/%Y'),
                    link=channel_username,
                    task_author=author
                )
            )

        db.session.add(
            TaskHistory(
                user_id=current_user.id,
                task_type=TaskType.ChannelDate,
                task_added_date=datetime.utcnow(),
                task_expire_date=datetime.strptime(date, '%m/%d/%Y'),
                link=channel_username,
                task_author=author,
                hash_count=len_hash
            )
        )

        for hash in selected_hashes:
            hash.work_status = Status.Active

        db.session.commit()
        result = await join_channel([_.hash for _ in selected_hashes], channel_username)
        for hash in selected_hashes:
            hash.work_status = Status.Inactive

        db.session.commit()
        flash(list(result.values())[0], list(result.keys())[0])
        return render_template('dashboard/addtochannel.html', user_inactive_hashes=user_inactive_hashes)

    return render_template('dashboard/addtochannel.html', user_inactive_hashes=user_inactive_hashes)


@app.route('/history/<task_type>')
@login_required
async def activity_history(task_type):
    task_type_map = {
        'channel': TaskType.ChannelDate,
        'group': TaskType.GroupToGroupDate,
        'private': TaskType.PrivateChat
    }

    if task_type not in task_type_map:
        return "Invalid task type", 404

    activities = TaskHistory.get_tasks_from_user_id(user_id=current_user.id)
    if request.method == "POST":
        # Handle POST request
        pass

    return render_template(f'dashboard/history/{task_type}_history.html', activities=set(activities))


@app.route('/delete_chats')
@login_required
async def activity_history_private_chats():
    force = request.args.get("force")


@app.route('/force_quit')
@login_required
async def delete_task():
    author = request.args.get("author")
    link = request.args.get("link")
    task_type = request.args.get("type")

    tasks = TaskHistory.query.filter_by(task_author=author, link=link).all()
    for task in tasks:
        task.task_expire_date = datetime.utcnow()

    db.session.commit()
    await check_tasks()

    flash("Muvoffaqqiyatli o'chirildi", "success")
    return redirect(url_for('activity_history', task_type=task_type))


if __name__ == '__main__':
    async def check_tasks():
        now = datetime.utcnow()
        with app.app_context():
            print("[*] checking")
            tasks_to_delete = TaskHistory.query.filter(TaskHistory.task_expire_date <= now).all()
            for task_history in tasks_to_delete:
                tasks = Tasks.query.filter_by(task_author=task_history.task_author,
                                              task_type=task_history.task_type,
                                              user_id=task_history.user_id).all()
                for task in tasks:
                    if task.task_type == TaskType.PrivateChat:
                        ...
                    else:
                        await leave(task.hash, task.link)
                    db.session.delete(task)
                db.session.delete(task_history)
            db.session.commit()


    def run_check_tasks():
        asyncio.run(check_tasks())


    def schedule_tasks():
        schedule.every(30).seconds.do(run_check_tasks)
        while True:
            schedule.run_pending()
            time.sleep(1)


    scheduler_thread = threading.Thread(target=schedule_tasks)
    scheduler_thread.start()

    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8080)
