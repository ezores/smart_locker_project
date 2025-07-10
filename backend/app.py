from models import init_models
from demo_data import create_demo_data

def init_db(minimal=False):
    """Initialize the database with default data"""
    with app.app_context():
        db.create_all()
        models = init_models(db)
        User = models[0]
        Locker = models[1]
        Item = models[2]
        Log = models[3]
        Borrow = models[4]
        Return = models[5]
        Payment = models[6] if len(models) > 6 else None
        Notification = models[7] if len(models) > 7 else None
        SystemSetting = models[8] if len(models) > 8 else None
        if not minimal:
            create_demo_data(db, User, Locker, Item, Log, Borrow, Return, Payment, Notification, SystemSetting)
            logger.info("Database initialized with comprehensive demo data (from demo_data.py)")
        else:
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    email='admin@smartlocker.com',
                    first_name='Admin',
                    last_name='User',
                    role='admin',
                    department='IT'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                logger.info("Database initialized with minimal admin user") 