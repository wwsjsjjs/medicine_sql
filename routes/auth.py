from flask import Blueprint, session, redirect, url_for, render_template, request
from models import EmployeeInfo

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    employees = EmployeeInfo.query.all()
    if request.method == 'POST':
        employee_id = int(request.form['employee_id'])
        session['employee_id'] = employee_id
        return redirect(request.args.get('next') or url_for('dashboard.index'))
    return render_template('login.html', employees=employees, current_id=session.get('employee_id'))

@auth_bp.route('/logout')
def logout():
    session.pop('employee_id', None)
    return redirect(url_for('auth.login'))
