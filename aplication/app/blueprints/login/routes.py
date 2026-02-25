from flask import request, render_template, redirect, url_for, Blueprint, flash
from flask_login import login_user, logout_user, current_user, login_required


from ...extensions import db, bcrypt
from app.blueprints.login.models import User


login = Blueprint('login',__name__,template_folder= 'templates')

@login.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if current_user.is_authenticated:
            #TODO: Adicionar redirecionamento
            return "já está logado."
        else:
            return render_template('login/login.html', current_user=current_user)
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter(User.email == email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return 'logado'
        else:
            flash('E-mail ou senha incorretos. Tente novamente.', 'error')
            return redirect('/login')
            
            


@login.route('/cadastro', methods=['GET', 'POST'])
def cadastro():

    if request.method == 'GET':
        if current_user.is_authenticated:
            #TODO: Adicionar redirecionamento
            return "já está logado."
        else:
            return render_template('login/cadastro.html', current_user=current_user)
    elif request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']


        hashed_password = bcrypt.generate_password_hash(password)

        user = User(name=name, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        #TODO: Adicionar redirecionamento
        return f"name: {name}, email: {email}, id: 1"

   
@login.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect('/login')
