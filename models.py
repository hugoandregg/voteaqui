import datetime
from flask import url_for
from voteaqui import db

class Comment(db.EmbeddedDocument):
	body = db.StringField(required=True)


class Choice(db.EmbeddedDocument):
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
	choices = db.ListField(db.EmbeddedDocumentField(Choice))
	comments = db.ListField(db.EmbeddedDocumentField(Comment))

	def __unicode__(self):
		return self.title

	meta = {
		'indexes': ['-created_at', '-id'],
		'ordering': ['-created_at']
	} 


class User(db.Document):
	email = db.EmailField(required=True)
	password = db.StringField(required=True)
	active = db.BooleanField(default=True)
	polls = db.ListField(db.ReferenceField(Poll))
	comments = db.ListField(db.EmbeddedDocumentField(Comment))