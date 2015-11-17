import os, datetime
from flask import current_app, Blueprint, render_template, abort, request, flash, redirect, url_for
from jinja2 import TemplateNotFound
from voteaqui import login_manager, flask_bcrypt
from flask.ext.login import (current_user, login_required, login_user, logout_user, confirm_login, fresh_login_required)

import forms
from models import User

auth_flask_login = Blueprint('auth_flask_login', __name__, template_folder='templates')

@auth_flask_login.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and "email" in request.form:
        email = request.form["email"]
        user = User.objects.get(email=email)
     	if user and flask_bcrypt.check_password_hash(user.password,request.form["password"]) and user.is_active():
			remember = False

			if login_user(user, remember=remember):
				flash("Logged in!")
				return redirect('/')
			else:
				flash("unable to log you in")

    return render_template("/auth/login.html")

#
# Route disabled - enable route to allow user registration.
#
@auth_flask_login.route("/register", methods=["GET","POST"])
def register():
	
	registerForm = forms.SignupForm(request.form)
	current_app.logger.info(request.form)

	if request.method == 'POST' and registerForm.validate() == False:
		current_app.logger.info(registerForm.errors)
		return "uhoh registration error"

	elif request.method == 'POST' and registerForm.validate():
		email = request.form['email']
		
		# generate password hash
		password_hash = flask_bcrypt.generate_password_hash(request.form['password'])

		# prepare User
		user = User(request.form['name'],email,password_hash)
		print user.email

		user.save()
		return redirect('/')

	# prepare registration form			
	# registerForm = RegisterForm(csrf_enabled=True)
	templateData = {

		'form' : registerForm
	}

	return render_template("/auth/register.html", **templateData)

@auth_flask_login.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect('/login')

@login_manager.unauthorized_handler
def unauthorized_callback():
	return redirect('/login')

@login_manager.user_loader
def load_user(id):
	return User.objects.get(id=id)