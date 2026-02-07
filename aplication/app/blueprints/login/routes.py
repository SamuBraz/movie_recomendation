from flask import request, render_template, redirect, url_for, Blueprint


from ...extensions import db
from app.blueprints.login.models import User


login = Blueprint('login',__name__,template_folder= 'templates')


@login.route('/')
def index():
    return "deu certo"