from app import app
from models import db, HomePageSettings

with app.app_context():
    db.create_all()
    print('✅ Tables created')
    
    settings = HomePageSettings.query.first()
    if not settings:
        s = HomePageSettings()
        db.session.add(s)
        db.session.commit()
        print('✅ Default homepage settings created!')
    else:
        print('ℹ️ Homepage settings already exist')
