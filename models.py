import datetime
from flask import url_for
from voteaqui import db

class Comment(db.Document):
	body = db.StringField(required=True)
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	author = db.ReferenceField('User')


class User(db.Document):
	name = db.StringField(required=True)
	email = db.EmailField(required=True)
	password = db.StringField(required=True)
	active = db.BooleanField(default=True)
	polls = db.ListField(db.ReferenceField('Poll'))
	comments = db.ListField(db.ReferenceField('Comment'))

	def is_active(self):
		return self.active

	def get_id(self):
		return self.id

	def is_authenticated(self):
		"""Return True if the user is authenticated."""
		return self.authenticated

	def is_anonymous(self):
		"""False, as anonymous users aren't supported."""
		return False

	def __unicode__(self):
		return self.name

class Choice(db.Document):
	name = db.StringField(required=True, max_length=50)
	description = db.StringField()
	votes = db.IntField(default=0)
	users = db.ListField(db.ReferenceField(User))

	def plus_one_vote(self):
		self.votes += 1

	def __unicode__(self):
		self.name


class Poll(db.Document):
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	expiration_date = db.DateTimeField()
	title = db.StringField(required=True, max_length=30)
	description = db.StringField()
	enabled = db.BooleanField(default=True)
	author = db.ReferenceField(User)
	choices = db.ListField(db.ReferenceField(Choice))
	comments = db.ListField(db.ReferenceField(Comment))
	number_votes = db.IntField(default=0)

	def plus_one_vote(self):
		self.number_votes += 1

	def __unicode__(self):
		return self.title

	meta = {
		'indexes': ['-created_at', '-id'],
		'ordering': ['-number_votes']
	} 