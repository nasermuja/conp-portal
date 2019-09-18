# -*- coding: utf-8 -*-
"""Models Module

Module that contains the Data Models

"""
from app import db
from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from sqlalchemy.orm.collections import attribute_mapped_collection
from datetime import datetime
from pytz import timezone
import enum

eastern = timezone('US/Eastern')


class AffiliationTypesEnum(enum.Enum):
    pi = 'Principal Investigator (Professor)'
    ra = 'Research Associate'
    pd = 'Post-Doctoral Fellow'
    phd = 'Doctoral Candidate'
    ms = 'Masters Student'
    ifs = 'Informatics Specialist'
    oth = 'Other'

class User(UserMixin, db.Model):
    """
        Provides User Model
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # User Authentication Information (Required by Flask-User)
    # we will use the users email as the primary means of login
    email = db.Column(db.String(128), unique=True)
    email_confirmed_at = db.Column(db.DateTime)
    password = db.Column(db.String(256), nullable=False, server_default='')
    active = db.Column(db.Boolean, nullable=False, server_default='0')

    # Customizable Fields
    first_name = db.Column(db.String(64), nullable=False, server_default='')
    last_name = db.Column(db.String(64), nullable=False, server_default='')
    affiliation = db.Column(db.String(128))
    affiliation_type = db.Column(db.Enum(AffiliationTypesEnum),
                                 default=AffiliationTypesEnum.pi,
                                 nullable=False
                                )
    expiration = db.Column(db.DateTime, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now(tz=eastern))
    date_updated = db.Column(db.DateTime, nullable=False, default=datetime.now(tz=eastern))

    roles = db.relationship('Role', secondary='users_roles',
                            backref=db.backref('users', lazy='dynamic'))

    def has_role(self,role):
        """
            Utility function to check if user has a particular role

            Args:
                role: role to test against

            Returns:
                True if the user has the role, otherwise, False
        """
        for item in self.roles:
            if item.name == role:
                return True
        return False

    def role(self): ### To DO: is this needed
        for item in self.roles:
            return item.name

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Role(db.Model):
    """
    Provides Role Model for Role based authorization
    """
    __tablename__ = "roles"
    id = db.Column(db.Integer(), primary_key=True)
    # for @roles_accepted()
    name = db.Column(db.String(50), nullable=False, server_default='', unique=True)
    label = db.Column(db.String(255), server_default='')  # for display purposes

    def __repr__(self):
        return self.name


class UsersRoles(db.Model):
    """
    Provides a pivot table for user role association
    """
    __tablename__ = 'users_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


# OAUTH Model
class OAuth(OAuthConsumerMixin, db.Model):
    """
    provides a pivot table for oauth associations
    """
    __table_args__ = (db.UniqueConstraint("provider", "provider_user_id"),)
    provider_user_id = db.Column(db.String(256), nullable=False)
    provider_user_login = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id),nullable=False)
    user = db.relationship(User,
                           backref=db.backref("oauth",
                                    collection_class=attribute_mapped_collection('provider'),
                                    cascade="all, delete-orphan")
                           )


class Dataset(db.Model):
    """
        Provides DataSet Model
    """
    __tablename__ = 'datasets'

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.String(64), index=True, unique=True)
    annex_uuid = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.Text, index=True)
    owner_id = db.Column(db.Integer, index=True)
    download_path = db.Column(db.String(64), index=True)
    raw_data_url = db.Column(db.String(128), index=True)
    image = db.Column(db.LargeBinary, default=None)
    name = db.Column(db.String(256), index=True)
    modality = db.Column(db.String(64), index=True)
    version = db.Column(db.String(6), index=True)
    format = db.Column(db.String(64), index=True)
    category = db.Column(db.String(64), index=True)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_updated = db.Column(db.DateTime, default=datetime.now())
    is_private = db.Column(db.Boolean, index=True)

    def __repr__(self):
        return '<Dataset {}>'.format(self.name)


class DatasetStats(db.Model):
    """
        Provides DatasetStats model for keeping stats on downloads and views
    """
    __tablename__ = 'dataset_stats'

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.String(64), index=True, unique=True)
    size = db.Column(db.Integer, index=True)
    files = db.Column(db.Integer, index=True)
    sources = db.Column(db.Integer, index=True)
    num_subjects = db.Column(db.Integer, index=True)
    num_downloads = db.Column(db.Integer, index=True)
    num_likes = db.Column(db.Integer, index=True)
    num_views = db.Column(db.Integer, index=True)
    date_updated = db.Column(db.DateTime, default=datetime.now())


class Pipeline(db.Model):
    """
        Provides Pipeline Model for describing metadata for an execution pipeline
    """
    __tablename__ = 'pipelines'

    id = db.Column(db.Integer, primary_key=True)
    pipeline_id = db.Column(db.Integer, index=True, unique=True)
    owner_id = db.Column(db.Integer, index=True)
    name = db.Column(db.String(256), index=True)
    version = db.Column(db.String(128), index=True)
    is_private = db.Column(db.Boolean, index=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now(tz=eastern))
    date_updated = db.Column(db.DateTime, nullable=False, default=datetime.now(tz=eastern))

    def __repr__(self):
        return '<Pipeline {}>'.format(self.name)
