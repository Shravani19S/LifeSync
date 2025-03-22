from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from datetime import datetime, timezone

db = SQLAlchemy()
bcrypt = Bcrypt()

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    # Relationships
    questionnaire_results = db.relationship('QuestionnaireResult', back_populates='user', cascade="all, delete-orphan")
    test_results = db.relationship('TestResult', back_populates='user', cascade="all, delete-orphan")
    questionnaire_results = db.relationship('QuestionnaireResult', back_populates='user', cascade="all, delete-orphan")
    test_results = db.relationship('TestResult', back_populates='user', cascade="all, delete-orphan")
    challenges = db.relationship('Challenge', back_populates='user', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
# TestResult Model (Stores test scores and recommendations)
class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    general_recommendation = db.Column(db.Text, nullable=False)
    date_taken = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  

    # Relationship
    user = db.relationship('User', back_populates='test_results')

# Questionnaire Result Model (Stores raw responses)
class QuestionnaireResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    responses = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float, nullable=False)
    recommendations = db.Column(db.Text, nullable=True)  
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    user = db.relationship('User', back_populates='questionnaire_results')

# Challenge Model
class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_text = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    date_assigned = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', back_populates='challenges')

# Group Challenge Model
class GroupChallenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_text = db.Column(db.String(255), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    creator = db.relationship('User')

class GroupChallengeParticipants(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_challenge_id = db.Column(db.Integer, db.ForeignKey('group_challenge.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    user = db.relationship('User')
    group_challenge = db.relationship('GroupChallenge')

# ✅ Group Model
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    creator = db.relationship('User', backref='created_groups')
    members = db.relationship('GroupMember', back_populates='group', cascade="all, delete-orphan")


# ✅ Group Members Model
class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref='group_memberships')
    group = db.relationship('Group', back_populates='members')
