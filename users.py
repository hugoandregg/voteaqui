from flask import request, redirect, render_template, url_for
from voteaqui.models import User
from voteaqui import app

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)