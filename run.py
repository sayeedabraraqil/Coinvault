import os
from app import create_app
from app.extensions import db, socketio
from app.services.badges import init_default_badges

app = create_app(os.environ.get('FLASK_ENV', 'development'))

with app.app_context():
    db.create_all()
    init_default_badges()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    print(f"[*] Starting COINVAULT Terminal on http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug)
