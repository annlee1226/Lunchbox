from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .data import User
from . import db
import json

pages = Blueprint('pages', __name__)


@pages.route('/', methods=['GET', 'POST'])
@login_required
def home():
    all_users = User.query.all() 
    return render_template("home.html", user=current_user, all_users=all_users)