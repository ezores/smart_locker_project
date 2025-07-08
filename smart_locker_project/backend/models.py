from datetime import datetime
from werkzeug.security import generate_password_hash  # type: ignore[import]

def init_models(db):
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        password_hash = db.Column(db.String(128), nullable=False)
        rfid_tag = db.Column(db.String(64), unique=True)
        qr_code = db.Column(db.String(128), unique=True)
        role = db.Column(db.String(16), nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class Locker(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(32), unique=True, nullable=False)
        items = db.relationship('Item', backref='locker', lazy=True)

    class Item(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(64), nullable=False)
        locker_id = db.Column(db.Integer, db.ForeignKey('locker.id'))

    class Log(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
        locker_id = db.Column(db.Integer, db.ForeignKey('locker.id'))
        timestamp = db.Column(db.DateTime, default=datetime.utcnow)
        action_type = db.Column(db.String(32), nullable=False)

    def init_db():
        db.create_all()
        if not User.query.first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            student = User(
                username='student',
                password_hash=generate_password_hash('student123'),
                role='student'
            )
            db.session.add(admin)
            db.session.add(student)
            locker1 = Locker(name='Locker 1')
            locker2 = Locker(name='Locker 2')
            db.session.add(locker1)
            db.session.add(locker2)
            item1 = Item(name='Laptop', locker=locker1)
            item2 = Item(name='Tablet', locker=locker2)
            db.session.add(item1)
            db.session.add(item2)
            log1 = Log(user_id=1, item_id=1, locker_id=1, action_type='borrow')
            db.session.add(log1)
            db.session.commit()
    return User, Locker, Item, Log, init_db 