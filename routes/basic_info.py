"""
基础信息管理模块路由
包括：药品、员工、客户、供应商管理
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from models import db, DrugInfo, EmployeeInfo, CustomerInfo, SupplierInfo, Role, UserRole, log_system_action
from datetime import datetime

basic_bp = Blueprint('basic', __name__, url_prefix='/basic')

# ==================== 药品管理 ====================
@basic_bp.route('/drugs')
def drug_list():
    """药品列表"""
    drugs = DrugInfo.query.all()
    return render_template('basic/drug_list.html', drugs=drugs)

@basic_bp.route('/drugs/add', methods=['GET', 'POST'])
def drug_add():
    """添加药品（CREATE）"""
    if request.method == 'POST':
        # 输入处理：基础字段，保质期按月填写
        shelf_life_months = int(request.form['shelf_life_months']) if request.form.get('shelf_life_months') else None
        drug = DrugInfo(
            name=request.form['name'],
            spec=request.form.get('spec'),
            manufacturer=request.form.get('manufacturer'),
            approval_number=request.form.get('approval_number'),
            category=request.form.get('category'),
            unit=request.form.get('unit'),
            purchase_price=request.form.get('purchase_price'),
            sale_price=request.form.get('sale_price'),
            shelf_life_months=shelf_life_months,
            status=request.form.get('status', '在售')
        )
        # 数据库执行：写入药品表
        db.session.add(drug)
        db.session.commit()
        # 操作日志
        log_system_action(session.get('employee_id'), 'insert', 'drug_info', {
            'drug_id': drug.drug_id,
            'name': drug.name
        })
        flash('药品添加成功！', 'success')
        return redirect(url_for('basic.drug_list'))
    return render_template('basic/drug_form.html', drug=None)

@basic_bp.route('/drugs/edit/<int:drug_id>', methods=['GET', 'POST'])
def drug_edit(drug_id):
    """编辑药品（UPDATE）"""
    drug = DrugInfo.query.get_or_404(drug_id)
    if request.method == 'POST':
        # 输入处理与校验：保质期按月
        shelf_life_months = int(request.form['shelf_life_months']) if request.form.get('shelf_life_months') else None
        drug.name = request.form['name']
        drug.spec = request.form.get('spec')
        drug.manufacturer = request.form.get('manufacturer')
        drug.approval_number = request.form.get('approval_number')
        drug.category = request.form.get('category')
        drug.unit = request.form.get('unit')
        drug.purchase_price = request.form.get('purchase_price')
        drug.sale_price = request.form.get('sale_price')
        drug.shelf_life_months = shelf_life_months
        drug.status = request.form.get('status')
        drug.update_time = datetime.now()
        # 数据库执行：提交更新
        db.session.commit()
        # 操作日志
        log_system_action(session.get('employee_id'), 'update', 'drug_info', {
            'drug_id': drug.drug_id,
            'name': drug.name
        })
        flash('药品更新成功！', 'success')
        return redirect(url_for('basic.drug_list'))
    return render_template('basic/drug_form.html', drug=drug)

@basic_bp.route('/drugs/delete/<int:drug_id>')
def drug_delete(drug_id):
    """删除药品（DELETE）"""
    drug = DrugInfo.query.get_or_404(drug_id)
    # 数据库执行：删除记录
    db.session.delete(drug)
    db.session.commit()
    # 操作日志
    log_system_action(session.get('employee_id'), 'delete', 'drug_info', {
        'drug_id': drug.drug_id,
        'name': drug.name
    })
    flash('药品删除成功！', 'success')
    return redirect(url_for('basic.drug_list'))

# ==================== 员工管理 ====================
@basic_bp.route('/employees')
def employee_list():
    """员工列表（READ）"""
    employees = EmployeeInfo.query.all()
    return render_template('basic/employee_list.html', employees=employees)

@basic_bp.route('/employees/add', methods=['GET', 'POST'])
def employee_add():
    """添加员工（CREATE）"""
    if request.method == 'POST':
        # 输入处理：基础资料与账户信息（密码未加密，生产需加密）
        employee = EmployeeInfo(
            name=request.form['name'],
            department=request.form.get('department'),
            position=request.form.get('position'),
            phone=request.form.get('phone'),
            hire_date=datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date() if request.form.get('hire_date') else None,
            account=request.form.get('account'),
            password=request.form.get('password'),  # 实际应用需要加密
            status=request.form.get('status', '在职')
        )
        # 数据库执行：插入员工
        db.session.add(employee)
        db.session.commit()
        # 角色关联：根据选择的角色ID绑定用户角色（单角色）
        role_id = request.form.get('role_id')
        if role_id:
            UserRole.query.filter_by(employee_id=employee.employee_id).delete()
            db.session.add(UserRole(employee_id=employee.employee_id, role_id=role_id))
            db.session.commit()
        # 操作日志
        log_system_action(session.get('employee_id'), 'insert', 'employee_info', {
            'employee_id': employee.employee_id,
            'name': employee.name
        })
        flash('员工添加成功！', 'success')
        return redirect(url_for('basic.employee_list'))
    roles = Role.query.order_by(Role.role_id).all()
    return render_template('basic/employee_form.html', employee=None, roles=roles, current_role_id=None)

@basic_bp.route('/employees/edit/<int:employee_id>', methods=['GET', 'POST'])
def employee_edit(employee_id):
    """编辑员工（UPDATE）"""
    employee = EmployeeInfo.query.get_or_404(employee_id)
    current_role = UserRole.query.filter_by(employee_id=employee_id).first()
    if request.method == 'POST':
        # 输入处理：更新基础资料，密码仅在提交时更新
        employee.name = request.form['name']
        employee.department = request.form.get('department')
        employee.position = request.form.get('position')
        employee.phone = request.form.get('phone')
        employee.hire_date = datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date() if request.form.get('hire_date') else None
        employee.account = request.form.get('account')
        if request.form.get('password'):
            employee.password = request.form.get('password')
        employee.status = request.form.get('status')
        employee.update_time = datetime.now()
        # 数据库执行：提交更新
        db.session.commit()
        # 角色关联：更新为选择的角色（单角色）
        role_id = request.form.get('role_id')
        UserRole.query.filter_by(employee_id=employee.employee_id).delete()
        if role_id:
            db.session.add(UserRole(employee_id=employee.employee_id, role_id=role_id))
        db.session.commit()
        # 操作日志
        log_system_action(session.get('employee_id'), 'update', 'employee_info', {
            'employee_id': employee.employee_id,
            'name': employee.name
        })
        flash('员工更新成功！', 'success')
        return redirect(url_for('basic.employee_list'))
    roles = Role.query.order_by(Role.role_id).all()
    return render_template('basic/employee_form.html', employee=employee, roles=roles, current_role_id=current_role.role_id if current_role else None)

@basic_bp.route('/employees/delete/<int:employee_id>')
def employee_delete(employee_id):
    """删除员工（DELETE）"""
    employee = EmployeeInfo.query.get_or_404(employee_id)
    # 数据库执行：删除记录
    db.session.delete(employee)
    db.session.commit()
    # 操作日志
    log_system_action(session.get('employee_id'), 'delete', 'employee_info', {
        'employee_id': employee.employee_id,
        'name': employee.name
    })
    flash('员工删除成功！', 'success')
    return redirect(url_for('basic.employee_list'))

# ==================== 客户管理 ====================
@basic_bp.route('/customers')
def customer_list():
    """客户列表（READ）"""
    customers = CustomerInfo.query.all()
    return render_template('basic/customer_list.html', customers=customers)

@basic_bp.route('/customers/add', methods=['GET', 'POST'])
def customer_add():
    """添加客户（CREATE）"""
    if request.method == 'POST':
        # 输入处理：基础客户资料
        customer = CustomerInfo(
            name=request.form['name'],
            type=request.form.get('type'),
            contact=request.form.get('contact'),
            phone=request.form.get('phone'),
            address=request.form.get('address')
        )
        # 数据库执行：插入客户
        db.session.add(customer)
        db.session.commit()
        # 操作日志
        log_system_action(session.get('employee_id'), 'insert', 'customer_info', {
            'customer_id': customer.customer_id,
            'name': customer.name
        })
        flash('客户添加成功！', 'success')
        return redirect(url_for('basic.customer_list'))
    return render_template('basic/customer_form.html', customer=None)

@basic_bp.route('/customers/edit/<int:customer_id>', methods=['GET', 'POST'])
def customer_edit(customer_id):
    """编辑客户（UPDATE）"""
    customer = CustomerInfo.query.get_or_404(customer_id)
    if request.method == 'POST':
        # 输入处理：更新客户资料
        customer.name = request.form['name']
        customer.type = request.form.get('type')
        customer.contact = request.form.get('contact')
        customer.phone = request.form.get('phone')
        customer.address = request.form.get('address')
        customer.update_time = datetime.now()
        # 数据库执行：提交更新
        db.session.commit()
        # 操作日志
        log_system_action(session.get('employee_id'), 'update', 'customer_info', {
            'customer_id': customer.customer_id,
            'name': customer.name
        })
        flash('客户更新成功！', 'success')
        return redirect(url_for('basic.customer_list'))
    return render_template('basic/customer_form.html', customer=customer)

@basic_bp.route('/customers/delete/<int:customer_id>')
def customer_delete(customer_id):
    """删除客户（DELETE）"""
    customer = CustomerInfo.query.get_or_404(customer_id)
    # 数据库执行：删除记录
    db.session.delete(customer)
    db.session.commit()
    # 操作日志
    log_system_action(session.get('employee_id'), 'delete', 'customer_info', {
        'customer_id': customer.customer_id,
        'name': customer.name
    })
    flash('客户删除成功！', 'success')
    return redirect(url_for('basic.customer_list'))

# ==================== 供应商管理 ====================
@basic_bp.route('/suppliers')
def supplier_list():
    """供应商列表（READ）"""
    suppliers = SupplierInfo.query.all()
    return render_template('basic/supplier_list.html', suppliers=suppliers)

@basic_bp.route('/suppliers/add', methods=['GET', 'POST'])
def supplier_add():
    """添加供应商（CREATE）"""
    if request.method == 'POST':
        # 输入处理：基础供应商资料
        supplier = SupplierInfo(
            name=request.form['name'],
            contact=request.form.get('contact'),
            phone=request.form.get('phone'),
            address=request.form.get('address'),
            qualification_no=request.form.get('qualification_no')
        )
        # 数据库执行：插入供应商
        db.session.add(supplier)
        db.session.commit()
        # 操作日志
        log_system_action(session.get('employee_id'), 'insert', 'supplier_info', {
            'supplier_id': supplier.supplier_id,
            'name': supplier.name
        })
        flash('供应商添加成功！', 'success')
        return redirect(url_for('basic.supplier_list'))
    return render_template('basic/supplier_form.html', supplier=None)

@basic_bp.route('/suppliers/edit/<int:supplier_id>', methods=['GET', 'POST'])
def supplier_edit(supplier_id):
    """编辑供应商（UPDATE）"""
    supplier = SupplierInfo.query.get_or_404(supplier_id)
    if request.method == 'POST':
        # 输入处理：更新供应商资料
        supplier.name = request.form['name']
        supplier.contact = request.form.get('contact')
        supplier.phone = request.form.get('phone')
        supplier.address = request.form.get('address')
        supplier.qualification_no = request.form.get('qualification_no')
        supplier.update_time = datetime.now()
        # 数据库执行：提交更新
        db.session.commit()
        # 操作日志
        log_system_action(session.get('employee_id'), 'update', 'supplier_info', {
            'supplier_id': supplier.supplier_id,
            'name': supplier.name
        })
        flash('供应商更新成功！', 'success')
        return redirect(url_for('basic.supplier_list'))
    return render_template('basic/supplier_form.html', supplier=supplier)

@basic_bp.route('/suppliers/delete/<int:supplier_id>')
def supplier_delete(supplier_id):
    """删除供应商（DELETE）"""
    supplier = SupplierInfo.query.get_or_404(supplier_id)
    # 数据库执行：删除记录
    db.session.delete(supplier)
    db.session.commit()
    # 操作日志
    log_system_action(session.get('employee_id'), 'delete', 'supplier_info', {
        'supplier_id': supplier.supplier_id,
        'name': supplier.name
    })
    flash('供应商删除成功！', 'success')
    return redirect(url_for('basic.supplier_list'))
