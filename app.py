from flask import Flask
from models import db
from routes.dashboard import dashboard_bp
from routes.basic_info import basic_bp
from routes.inventory_mgmt import inventory_bp
from routes.sales_mgmt import sales_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medicine.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
db.init_app(app)

# 注册蓝图
app.register_blueprint(dashboard_bp)
app.register_blueprint(basic_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(sales_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
