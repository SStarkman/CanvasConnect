from app import db

# Something is wrong with this class, I keep getting an error

# Membership Model (Association table for many-to-many relationship between Users and Groups)
class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('memberships', lazy='dynamic'))
    group = db.relationship('Group', backref=db.backref('memberships', lazy='dynamic'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique = True)
    # Relationship to Groups (many-to-many via Membership)
    groups_as_member = db.relationship('Group', secondary='membership', back_populates='members')
    # Relationship to Group (One-to-many)
    groups_as_organizer = db.relationship('Group', backref='organizer', lazy=True)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    tag = db.Column(db.String(100))
    start_date_time = db.Column(db.DateTime)
    end_date_time = db.Column(db.DateTime)
    # Foreign Key to the User table
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationship to the People table (Organizer)
    #organizer = db.relationship('User', backref=db.backref('organizer_groups', lazy=True))
    # Relationship to Users (many-to-many via Membership)
    members = db.relationship('User', secondary='membership', back_populates='groups_as_member')





