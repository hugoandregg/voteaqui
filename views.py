from flask import Blueprint, request, redirect, render_template, url_for
from flask.ext.mongoengine.wtf import model_form
from flask.views import MethodView

from voteaqui.models import *

polls = Blueprint('polls', __name__, template_folder='templates')

class ListView(MethodView):
	def get(self):
		polls = Poll.objects.all()
		return render_template('polls/list.html', polls=polls)


class DetailView(MethodView):
	form = model_form(Comment)

	def get_context(self, poll_id):
		poll = Poll.objects.get_or_404(id=poll_id)
		form = self.form(request.form)

		context = {
			"poll": poll,
			"form": form
		}

		return context

	def get(self, poll_id):
		context = self.get_context(poll_id)
		return render_template('polls/detail.html', **context)

	def post(self, poll_id):
		context = self.get_context(poll_id)
		form = context.get('form')
		
		if form.validate():
			comment = Comment()
			form.populate_obj(comment)

			poll = context.get('poll')
			poll.comments.append(comment)
			poll.save()
			return redirect(url_for('polls.detail', poll_id=poll_id))
		return render_template('polls/detail.html', **context)


class PollCreateView(MethodView):
	form = model_form(Poll, exclude=['created_at', 'comments', 'choices'])

	def get_context(self):
		poll = Poll()
		form = self.form(request.form)

		context = {
			"poll": poll,
			"form": form 
		}

		return context

	def get(self):
		context = self.get_context()
		return render_template('polls/poll_form.html', **context)

	def post(self):
		context = self.get_context()
		form = context.get('form')
		print request.form['expiration_date']
		if form.validate():
			poll = context.get('poll')
			form.populate_obj(poll)
			poll.save()

			return redirect(url_for('polls.list'))
		return render_template('polls/poll_form.html', **context)


class ChoiceCreateView(MethodView):
	form = model_form(Choice, exclude=['votes'])

	def get_context(self, poll_id):
		poll = Poll.objects.get_or_404(id=poll_id)
		form = self.form(request.form)

		context = {
			"poll": poll,
			"form": form
		}

		return context

	def get(self, poll_id):
		context = self.get_context(poll_id)
		return render_template('polls/choice_form.html', **context)

	def post(self, poll_id):
		context = self.get_context(poll_id)
		form = context.get('form')
		
		if form.validate():
			choice = Choice()
			form.populate_obj(choice)

			poll = context.get('poll')
			poll.choices.append(choice)
			poll.save()
			return redirect(url_for('polls.detail', poll_id=poll_id))
		return render_template('polls/choice_form.html', **context)


class PollDeleteView(MethodView):
	def get(self, poll_id):
		poll = Poll.objects.get_or_404(id=poll_id)
		poll.delete()
		return redirect(url_for('polls.list'))


class ChoiceDeleteView(MethodView):
	def get(self, poll_id, choice_id):
		choice = Choice.objects.get_or_404(id=choice_id)
		choice.delete()
		return redirect(url_for('polls.detail'), poll_id=poll_id)


class CommentDeleteView(MethodView):
	def get(self, poll_id, comment_id):
		comment = Comment.objects.get_or_404(id=comment_id)
		comment.delete()
		return redirect(url_for('polls.detail'), poll_id=poll_id)


polls.add_url_rule('/', view_func=ListView.as_view('list'))
polls.add_url_rule('/<poll_id>/', view_func=DetailView.as_view('detail'))
polls.add_url_rule('/create/', view_func=PollCreateView.as_view('create'))
polls.add_url_rule('/create/<poll_id>/', view_func=ChoiceCreateView.as_view('create_choice'))
polls.add_url_rule('/delete/<poll_id>/', view_func=PollDeleteView.as_view('delete'))
polls.add_url_rule('/delete_choice/<poll_id>/<choice_id>/', view_func=PollDeleteView.as_view('delete_choice'))
polls.add_url_rule('/delete/<poll_id>/<comment_id>/', view_func=PollDeleteView.as_view('delete_comment'))