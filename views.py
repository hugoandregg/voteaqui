from flask import Blueprint, request, redirect, render_template, url_for
from flask.ext.mongoengine.wtf import model_form
from flask.ext.login import (current_user, login_required, login_user, logout_user, confirm_login, fresh_login_required)
from flask.views import MethodView

from voteaqui.models import *
from datetime import datetime

polls = Blueprint('polls', __name__, template_folder='templates')

class ListView(MethodView):
	@login_required
	def get(self):
		polls = []
		closed_polls = []
		user = User.objects.get(id=current_user.id)
		can_vote = True
		date = datetime.now()
		for poll in Poll.objects:
			if poll.expiration_date > date and poll.enabled:
				polls.append(poll)
			else:
				if poll.enabled:
					poll.enabled = False
					poll.save()
				closed_polls.append(poll)
		return render_template('polls/list.html', polls=polls, closed_polls=closed_polls)


class DetailView(MethodView):
	form = model_form(Comment, exclude=['author'])

	def get_context(self, poll_id):
		poll = Poll.objects.get_or_404(id=poll_id)
		form = self.form(request.form)
		user = User.objects.get(id=current_user.id)
		chosen_choice = None
		can_vote = True
		for choice in poll.choices:
			if choice.users != None:
				for choice_user in choice.users:
					if choice_user == user:
						can_vote = False
						chosen_choice = choice
						break

		context = {
			"poll": poll,
			"form": form,
			"user": user,
			"can_vote": can_vote,
			"chosen_choice": chosen_choice
		}

		return context

	@login_required
	def get(self, poll_id):
		context = self.get_context(poll_id)
		return render_template('polls/detail.html', **context)

	@login_required
	def post(self, poll_id):
		context = self.get_context(poll_id)
		form = context.get('form')
		
		if form.validate():
			comment = Comment()
			form.populate_obj(comment)
			comment.author = context.get('user')
			comment.save()

			poll = context.get('poll')
			poll.comments.append(comment)
			poll.save()

			user = context.get('user')
			user.comments.append(comment)
			user.save()
			return redirect(url_for('polls.detail', poll_id=poll_id))
		return render_template('polls/detail.html', **context)


class ClosedPollView(MethodView):
	@login_required
	def get(self, poll_id):
		poll = Poll.objects.get_or_404(id=poll_id)
		return render_template('polls/closed_poll.html', poll=poll)


class VoteView(MethodView):
	@login_required
	def get(self, poll_id, choice_id):
		poll = Poll.objects.get_or_404(id=poll_id)
		if poll.enabled:
			choice = Choice.objects.get(id=choice_id)
			choice.plus_one_vote()
			user = User.objects.get(id=current_user.id)
			choice.users.append(user)
			choice.save()
			
			poll.plus_one_vote()
			poll.save()
		return redirect(url_for('polls.detail', poll_id=poll_id))


class RemoveVoteView(MethodView):
	@login_required
	def get(self, poll_id, choice_id):
		poll = Poll.objects.get_or_404(id=poll_id)
		if poll.enabled:
			choice = Choice.objects.get(id=choice_id)
			choice.minus_one_vote()
			user = User.objects.get(id=current_user.id)
			choice.users.remove(user)
			choice.save()
			
			poll.minus_one_vote()
			poll.save()
		return redirect(url_for('polls.detail', poll_id=poll_id))


class PollCreateView(MethodView):
	form = model_form(Poll, exclude=['created_at', 'comments', 'choices', 'author', 'expiration_date', 'enabled', 'number_votes', 'tags'])

	def get_context(self):
		poll = Poll()
		form = self.form(request.form)

		context = {
			"poll": poll,
			"form": form 
		}

		return context

	@login_required
	def get(self):
		context = self.get_context()
		return render_template('polls/poll_form.html', **context)

	@login_required
	def post(self):
		context = self.get_context()
		form = context.get('form')
		date = datetime(int(request.form['expiration_date'][:4]), int(request.form['expiration_date'][5:7]), int(request.form['expiration_date'][8:10]), 0, 0, 0)
		print request.form['tags'].split(" ")
		if form.validate():
			poll = context.get('poll')
			form.populate_obj(poll)
			poll.expiration_date = date
			poll.tags = request.form['tags'].split(" ")
			user = User.objects.get(id=current_user.id)
			poll.author = user
			poll.save()

			user.polls.append(poll)
			user.save()

			return redirect(url_for('polls.list'))
		return render_template('polls/poll_form.html', **context)


class SearchPollView(MethodView):
	@login_required
	def get(self):
		return render_template('polls/search.html')

	@login_required
	def post(self):
		tag = request.form['tag']
		polls = []
		for poll in Poll.objects:
			for poll_tag in poll.tags:
				if tag in poll_tag:
					polls.append(poll)
					break

		return render_template('polls/search.html', polls=polls) 


class PollEditView(MethodView):
	form = model_form(Poll, exclude=['created_at', 'comments', 'choices', 'author', 'expiration_date', 'enabled', 'number_votes', 'tags'])

	def get_context(self, poll_id):
		poll = Poll.objects.get_or_404(id=poll_id)
		if request.method == 'POST':
			form = self.form(request.form, initial=poll._data)
		else:
			form = self.form(obj=poll)

		context = {
			"poll": poll,
			"form": form 
		}

		return context

	@login_required
	def get(self, poll_id):
		context = self.get_context(poll_id)
		return render_template('polls/edit_poll_form.html', **context)

	@login_required
	def post(self, poll_id):
		context = self.get_context(poll_id)
		form = context.get('form')
		date = datetime(int(request.form['expiration_date'][:4]), int(request.form['expiration_date'][5:7]), int(request.form['expiration_date'][8:10]), 0, 0, 0)
		if form.validate():
			poll = context.get('poll')
			form.populate_obj(poll)
			poll.expiration_date = date
			poll.save()

			return redirect(url_for('polls.list'))
		return render_template('polls/edit_poll_form.html', **context)


class ChoiceCreateView(MethodView):
	form = model_form(Choice, exclude=['votes', 'users'])

	def get_context(self, poll_id):
		poll = Poll.objects.get_or_404(id=poll_id)
		form = self.form(request.form)

		context = {
			"poll": poll,
			"form": form
		}

		return context

	@login_required
	def get(self, poll_id):
		context = self.get_context(poll_id)
		poll = Poll.objects.get_or_404(id=poll_id)
		if poll.enabled:
			return render_template('polls/choice_form.html', **context)
		return redirect(url_for('polls.detail', poll_id=poll_id))

	@login_required
	def post(self, poll_id):
		context = self.get_context(poll_id)
		form = context.get('form')
		
		if form.validate():
			choice = Choice()
			form.populate_obj(choice)
			choice.save()

			poll = context.get('poll')
			poll.choices.append(choice)
			poll.save()
			return redirect(url_for('polls.detail', poll_id=poll_id))
		return render_template('polls/choice_form.html', **context)


class PollDeleteView(MethodView):
	@login_required
	def get(self, poll_id):
		poll = Poll.objects.get_or_404(id=poll_id)
		user = User.objects.get(id=current_user.id)
		if poll.author == user:
			poll.delete()
		return redirect(url_for('polls.list'))


class DisablePollView(MethodView):
	@login_required
	def get(self, poll_id):
		poll = Poll.objects.get_or_404(id=poll_id)
		poll.enabled = False
		poll.save()

		return redirect(url_for('polls.list'))


class EnablePollView(MethodView):
	@login_required
	def get(self, poll_id):
		poll = Poll.objects.get_or_404(id=poll_id)
		date = datetime.now()
		if poll.expiration_date > date:
			poll.enabled = True
			poll.save()

			return redirect(url_for('polls.list'))
		else:
			return redirect(url_for('polls.closed', poll_id=poll_id))


class ChoiceDeleteView(MethodView):
	@login_required
	def get(self, poll_id, choice_id):
		poll = Poll.objects.get(id=poll_id)
		choice = Choice.objects.get_or_404(id=choice_id)
		user = User.objects.get(id=current_user.id)
		if poll.author == user:
			poll.choices.remove(choice)
			poll.save()
			choice.delete()
		return redirect(url_for('polls.detail', poll_id=poll_id))


class CommentDeleteView(MethodView):
	@login_required
	def get(self, poll_id, comment_id):
		comment = Comment.objects.get_or_404(id=comment_id)
		poll = Poll.objects.get(id=poll_id)
		user = User.objects.get(id=current_user.id)
		if comment.author == user:
			poll.comments.remove(comment)
			user.comments.remove(comment)
			poll.save()
			user.save()
			comment.delete()
		return redirect(url_for('polls.detail', poll_id=poll_id))


polls.add_url_rule('/', view_func=ListView.as_view('list'))
polls.add_url_rule('/<poll_id>/', view_func=DetailView.as_view('detail'))
polls.add_url_rule('/create/', view_func=PollCreateView.as_view('create'))
polls.add_url_rule('/edit/<poll_id>/', view_func=PollEditView.as_view('edit'))
polls.add_url_rule('/search/', view_func=SearchPollView.as_view('search'))
polls.add_url_rule('/create/<poll_id>/', view_func=ChoiceCreateView.as_view('create_choice'))
polls.add_url_rule('/disable/<poll_id>', view_func=DisablePollView.as_view('disable'))
polls.add_url_rule('/enable/<poll_id>', view_func=EnablePollView.as_view('enable'))
polls.add_url_rule('/closed/<poll_id>', view_func=ClosedPollView.as_view('closed'))
polls.add_url_rule('/delete/<poll_id>/', view_func=PollDeleteView.as_view('delete'))
polls.add_url_rule('/delete_choice/<poll_id>/<choice_id>/', view_func=ChoiceDeleteView.as_view('delete_choice'))
polls.add_url_rule('/delete/<poll_id>/<comment_id>/', view_func=CommentDeleteView.as_view('delete_comment'))
polls.add_url_rule('/vote/<poll_id>/<choice_id>/', view_func=VoteView.as_view('vote'))
polls.add_url_rule('/remove_vote/<poll_id>/<choice_id>/', view_func=RemoveVoteView.as_view('remove_vote'))