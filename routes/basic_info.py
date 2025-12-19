"""
基础信息管理模块路由
包括：药品、员工、客户、供应商管理
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, DrugInfo, EmployeeInfo, CustomerInfo, SupplierInfo
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
    """添加药品"""
    if request.method == 'POST':
        drug = DrugInfo(
            name=request.form['name'],
            spec=request.form.get('spec'),
            manufacturer=request.form.get('manufacturer'),
            approval_number=request.form.get('approval_number'),
            category=request.form.get('category'),
            unit=request.form.get('unit'),
            purchase_price=request.form.get('purchase_price'),
            sale_price=request.form.get('sale_price'),
            expiry_date=datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date() if request.form.get('expiry_date') else None,
            status=request.form.get('status', '在售')
        )
        db.session.add(drug)
        db.session.commit()
        flash('药品添加成功！', 'success')
        return redirect(url_for('basic.drug_list'))
    return render_template('basic/drug_form.html', drug=None)

@basic_bp.route('/drugs/edit/<int:drug_id>', methods=['GET', 'POST'])
def drug_edit(drug_id):
    """编辑药品"""
    drug = DrugInfo.query.get_or_404(drug_id)
    if request.method == 'POST':
        drug.name = request.form['name']
        drug.spec = request.form.get('spec')
        drug.manufacturer = request.form.get('manufacturer')
        drug.approval_number = request.form.get('approval_number')
        drug.category = request.form.get('category')
        drug.unit = request.form.get('unit')
        drug.purchase_price = request.form.get('purchase_price')
        drug.sale_price = request.form.get('sale_price')
        drug.expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date() if request.form.get('expiry_date') else None
        drug.status = request.form.get('status')
        drug.update_time = datetime.now()
        db.session.commit()
        flash('药品更新成功！', 'success')
        return redirect(url_for('basic.drug_list'))
    return render_template('basic/drug_form.html', drug=drug)

@basic_bp.route('/drugs/delete/<int:drug_id>')
def drug_delete(drug_id):
    """删除药品"""
    drug = DrugInfo.query.get_or_404(drug_id)
    db.session.delete(drug)
    db.session.commit()
    flash('药品删除成功！', 'success')
    return redirect(url_for('basic.drug_list'))

# ==================== 员工管理 ====================
@basic_bp.route('/employees')
def employee_list():
    """员工列表"""
    employees = EmployeeInfo.query.all()
    return render_template('basic/employee_list.html', employees=employees)

@basic_bp.route('/employees/add', methods=['GET', 'POST'])
def employee_add():
    """添加员工"""
    if request.method == 'POST':
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
        db.session.add(employee)
        db.session.commit()
        flash('员工添加成功！', 'success')
        return redirect(url_for('basic.employee_list'))
    return render_template('basic/employee_form.html', employee=None)

@basic_bp.route('/employees/edit/<int:employee_id>', methods=['GET', 'POST'])
def employee_edit(employee_id):
    """编辑员工"""
    employee = EmployeeInfo.query.get_or_404(employee_id)
    if request.method == 'POST':
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
        db.session.commit()
        flash('员工更新成功！', 'success')
        return redirect(url_for('basic.employee_list'))
    return render_template('basic/employee_form.html', employee=employee)

@basic_bp.route('/employees/delete/<int:employee_id>')
def employee_delete(employee_id):
    """删除员工"""
    employee = EmployeeInfo.query.get_or_404(employee_id)
    db.session.delete(employee)
    db.session.commit()
    flash('员工删除成功！', 'success')
    return redirect(url_for('basic.employee_list'))

# ==================== 客户管理 ====================
@basic_bp.route('/customers')
def customer_list():
    """客户列表"""
    customers = CustomerInfo.query.all()
    return render_template('basic/customer_list.html', customers=customers)

@basic_bp.route('/customers/add', methods=['GET', 'POST'])
def customer_add():
    """添加客户"""
    if request.method == 'POST':
        customer = CustomerInfo(
            name=request.form['name'],
            type=request.form.get('type'),
            contact=request.form.get('contact'),
            phone=request.form.get('phone'),
            address=request.form.get('address')
        )
        db.session.add(customer)
        db.session.commit()
        flash('客户添加成功！', 'success')
        return redirect(url_for('basic.customer_list'))
    return render_template('basic/customer_form.html', customer=None)

@basic_bp.route('/customers/edit/<int:customer_id>', methods=['GET', 'POST'])
def customer_edit(customer_id):
    """编辑客户"""
    customer = CustomerInfo.query.get_or_404(customer_id)
    if request.method == 'POST':
        customer.name = request.form['name']
        customer.type = request.form.get('type')
        customer.contact = request.form.get('contact')
        customer.phone = request.form.get('phone')
        customer.address = request.form.get('address')
        customer.update_time = datetime.now()
        db.session.commit()
        flash('客户更新成功！', 'success')
        return redirect(url_for('basic.customer_list'))
    return render_template('basic/customer_form.html', customer=customer)

@basic_bp.route('/customers/delete/<int:customer_id>')
def customer_delete(customer_id):
    """删除客户"""
    customer = CustomerInfo.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash('客户删除成功！', 'success')
    return redirect(url_for('basic.customer_list'))

# ==================== 供应商管理 ====================
@basic_bp.route('/suppliers')
def supplier_list():
    """供应商列表"""
    suppliers = SupplierInfo.query.all()
    return render_template('basic/supplier_list.html', suppliers=suppliers)

@basic_bp.route('/suppliers/add', methods=['GET', 'POST'])
def supplier_add():
    """添加供应商"""
    if request.method == 'POST':
        supplier = SupplierInfo(
            name=request.form['name'],
            contact=request.form.get('contact'),
            phone=request.form.get('phone'),
            address=request.form.get('address'),
            qualification_no=request.form.get('qualification_no')
        )
        db.session.add(supplier)
        db.session.commit()
        flash('供应商添加成功！', 'success')
        return redirect(url_for('basic.supplier_list'))
    return render_template('basic/supplier_form.html', supplier=None)

@basic_bp.route('/suppliers/edit/<int:supplier_id>', methods=['GET', 'POST'])
def supplier_edit(supplier_id):
    """编辑供应商"""
    supplier = SupplierInfo.query.get_or_404(supplier_id)
    if request.method == 'POST':
        supplier.name = request.form['name']
        supplier.contact = request.form.get('contact')
        supplier.phone = request.form.get('phone')
        supplier.address = request.form.get('address')
        supplier.qualification_no = request.form.get('qualification_no')
        supplier.update_time = datetime.now()
        db.session.commit()
        flash('供应商更新成功！', 'success')
        return redirect(url_for('basic.supplier_list'))
    return render_template('basic/supplier_form.html', supplier=supplier)

@basic_bp.route('/suppliers/delete/<int:supplier_id>')
def supplier_delete(supplier_id):
    """删除供应商"""
    supplier = SupplierInfo.query.get_or_404(supplier_id)
    db.session.delete(supplier)
    db.session.commit()
    flash('供应商删除成功！', 'success')
    return redirect(url_for('basic.supplier_list'))
