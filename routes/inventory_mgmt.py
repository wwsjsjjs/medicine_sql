"""
库存管理模块路由
包括：入库、库存、仓库、盘点、退货管理
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, StockIn, Inventory, Warehouse, InventoryCheck, ReturnStock, DrugInfo, SupplierInfo, EmployeeInfo
from datetime import datetime
from sqlalchemy import func

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

# ==================== 入库管理 ====================
@inventory_bp.route('/stock_in')
def stock_in_list():
    """入库列表（READ）"""
    stock_ins = db.session.query(StockIn, DrugInfo.name, SupplierInfo.name, EmployeeInfo.name, DrugInfo.purchase_price).\
        join(DrugInfo, StockIn.drug_id == DrugInfo.drug_id).\
        join(SupplierInfo, StockIn.supplier_id == SupplierInfo.supplier_id).\
        join(EmployeeInfo, StockIn.employee_id == EmployeeInfo.employee_id).all()
    return render_template('inventory/stock_in_list.html', stock_ins=stock_ins)

@inventory_bp.route('/stock_in/add', methods=['GET', 'POST'])
def stock_in_add():
    """添加入库（CREATE）"""
    if request.method == 'POST':
        location = (request.form.get('location') or '').strip() or None
        # 输入校验：药品、供应商、仓库必须存在
        drug = DrugInfo.query.get(request.form['drug_id'])
        if not drug:
            flash('指定的药品不存在，请先添加药品信息！', 'danger')
            return redirect(url_for('inventory.stock_in_add'))
        
        # 验证供应商是否存在
        supplier = SupplierInfo.query.get(request.form['supplier_id'])
        if not supplier:
            flash('指定的供应商不存在，请先添加供应商信息！', 'danger')
            return redirect(url_for('inventory.stock_in_add'))
        
        # 验证仓库是否存在
        warehouse_id = request.form.get('warehouse_id', 1)
        warehouse = Warehouse.query.get(warehouse_id)
        if not warehouse:
            flash('指定的仓库不存在，请先添加仓库信息！', 'danger')
            return redirect(url_for('inventory.stock_in_add'))
        
        # 数据库执行：插入入库记录（价格由药品表维护，此处不存）
        quantity = int(request.form['quantity'])
        stock_in = StockIn(
            drug_id=request.form['drug_id'],
            supplier_id=request.form['supplier_id'],
            quantity=quantity,
            stock_in_date=datetime.strptime(request.form['stock_in_date'], '%Y-%m-%d').date(),
            employee_id=request.form.get('employee_id', 1),  # 实际应从session获取
            remark=request.form.get('remark')
        )
        db.session.add(stock_in)
        
        # 数据库执行：更新库存（存在则累加，不存在则创建）
        inventory = Inventory.query.filter_by(
            drug_id=stock_in.drug_id,
            warehouse_id=request.form.get('warehouse_id', 1)
        ).first()
        
        if inventory:
            inventory.quantity += int(request.form['quantity'])
            if location:
                inventory.location = location
        else:
            inventory = Inventory(
                drug_id=stock_in.drug_id,
                warehouse_id=request.form.get('warehouse_id', 1),
                quantity=int(request.form['quantity']),
                location=location
            )
            db.session.add(inventory)
        
        db.session.commit()
        flash('入库登记成功！', 'success')
        return redirect(url_for('inventory.stock_in_list'))
    
    drugs = DrugInfo.query.all()
    suppliers = SupplierInfo.query.all()
    warehouses = Warehouse.query.all()
    return render_template('inventory/stock_in_form.html', drugs=drugs, suppliers=suppliers, warehouses=warehouses)

# ==================== 库存查询 ====================
@inventory_bp.route('/stock')
def stock_list():
    """库存列表（READ）"""
    stocks = db.session.query(Inventory, DrugInfo.name, DrugInfo.unit, Warehouse.name).\
        join(DrugInfo, Inventory.drug_id == DrugInfo.drug_id).\
        join(Warehouse, Inventory.warehouse_id == Warehouse.warehouse_id).all()
    return render_template('inventory/stock_list.html', stocks=stocks)

@inventory_bp.route('/stock/low')
def stock_low():
    """库存预警（READ，低于100）"""
    stocks = db.session.query(Inventory, DrugInfo.name, DrugInfo.unit, Warehouse.name).\
        join(DrugInfo, Inventory.drug_id == DrugInfo.drug_id).\
        join(Warehouse, Inventory.warehouse_id == Warehouse.warehouse_id).\
        filter(Inventory.quantity < 100).all()
    return render_template('inventory/stock_low.html', stocks=stocks)

# ==================== 仓库管理 ====================
@inventory_bp.route('/warehouses')
def warehouse_list():
    """仓库列表（READ）"""
    warehouses = db.session.query(Warehouse, EmployeeInfo.name).\
        join(EmployeeInfo, Warehouse.manager_id == EmployeeInfo.employee_id).all()
    return render_template('inventory/warehouse_list.html', warehouses=warehouses)

@inventory_bp.route('/warehouses/add', methods=['GET', 'POST'])
def warehouse_add():
    """添加仓库（CREATE）"""
    if request.method == 'POST':
        # 输入校验：管理员员工必须存在
        employee = EmployeeInfo.query.get(request.form['manager_id'])
        if not employee:
            flash('指定的管理员不存在，请先添加员工信息！', 'danger')
            return redirect(url_for('inventory.warehouse_add'))

        # 业务校验：仓库名称唯一
        exists = Warehouse.query.filter_by(name=request.form['name']).first()
        if exists:
            flash('仓库名称已存在，请更换名称。', 'danger')
            return redirect(url_for('inventory.warehouse_add'))
        
        # 数据库执行：插入仓库
        warehouse = Warehouse(
            name=request.form['name'],
            address=request.form.get('address'),
            manager_id=request.form['manager_id']
        )
        db.session.add(warehouse)
        db.session.commit()
        flash('仓库添加成功！', 'success')
        return redirect(url_for('inventory.warehouse_list'))
    
    employees = EmployeeInfo.query.all()
    return render_template('inventory/warehouse_form.html', warehouse=None, employees=employees)

@inventory_bp.route('/warehouses/edit/<int:warehouse_id>', methods=['GET', 'POST'])
def warehouse_edit(warehouse_id):
    """编辑仓库（UPDATE）"""
    warehouse = Warehouse.query.get_or_404(warehouse_id)
    if request.method == 'POST':
        # 输入处理：更新仓库基础信息
        warehouse.name = request.form['name']
        warehouse.address = request.form.get('address')
        warehouse.manager_id = request.form['manager_id']
        # 数据库执行：提交更新
        db.session.commit()
        flash('仓库更新成功！', 'success')
        return redirect(url_for('inventory.warehouse_list'))
    
    employees = EmployeeInfo.query.all()
    return render_template('inventory/warehouse_form.html', warehouse=warehouse, employees=employees)

# ==================== 库存盘点 ====================
@inventory_bp.route('/check')
def check_list():
    """盘点列表（READ）"""
    checks = db.session.query(InventoryCheck, DrugInfo.name, Warehouse.name, EmployeeInfo.name).\
        join(DrugInfo, InventoryCheck.drug_id == DrugInfo.drug_id).\
        join(Warehouse, InventoryCheck.warehouse_id == Warehouse.warehouse_id).\
        join(EmployeeInfo, InventoryCheck.employee_id == EmployeeInfo.employee_id).all()
    return render_template('inventory/check_list.html', checks=checks)

@inventory_bp.route('/check/add', methods=['GET', 'POST'])
def check_add():
    """添加盘点（CREATE）"""
    if request.method == 'POST':
        # 输入校验：库存记录必须存在
        inventory = Inventory.query.filter_by(
            drug_id=request.form['drug_id'],
            warehouse_id=request.form['warehouse_id']
        ).first()
        if not inventory:
            flash('该药品在指定仓库中没有库存记录，无法进行盘点！', 'danger')
            return redirect(url_for('inventory.check_add'))
        
        checked_qty = int(request.form['checked_quantity'])
        actual_qty = int(request.form['actual_quantity'])
        
        # 数据库执行：插入盘点记录
        check = InventoryCheck(
            drug_id=request.form['drug_id'],
            warehouse_id=request.form['warehouse_id'],
            checked_quantity=checked_qty,
            actual_quantity=actual_qty,
            diff_reason=request.form.get('diff_reason'),
            check_date=datetime.strptime(request.form['check_date'], '%Y-%m-%d').date(),
            employee_id=request.form.get('employee_id', 1)
        )
        db.session.add(check)
        
        # 数据库执行：更新库存（同步数量与盘点日期）
        inventory = Inventory.query.filter_by(
            drug_id=check.drug_id,
            warehouse_id=check.warehouse_id
        ).first()
        if inventory:
            if checked_qty != actual_qty:
                inventory.quantity = actual_qty
            inventory.last_check_date = check.check_date
        
        db.session.commit()
        flash('盘点完成！', 'success')
        return redirect(url_for('inventory.check_list'))
    
    drugs = DrugInfo.query.all()
    warehouses = Warehouse.query.all()
    return render_template('inventory/check_form.html', drugs=drugs, warehouses=warehouses)

# ==================== 退货处理 ====================
@inventory_bp.route('/return')
def return_list():
    """退货列表（READ）"""
    returns = db.session.query(ReturnStock, DrugInfo.name, SupplierInfo.name, EmployeeInfo.name).\
        join(DrugInfo, ReturnStock.drug_id == DrugInfo.drug_id).\
        join(SupplierInfo, ReturnStock.supplier_id == SupplierInfo.supplier_id).\
        join(EmployeeInfo, ReturnStock.employee_id == EmployeeInfo.employee_id).all()
    return render_template('inventory/return_list.html', returns=returns)

@inventory_bp.route('/return/add', methods=['GET', 'POST'])
def return_add():
    """添加退货（CREATE）"""
    if request.method == 'POST':
        warehouse_id = request.form.get('warehouse_id', 1)
        quantity = int(request.form['quantity'])
        drug_id = request.form['drug_id']
        supplier_id = request.form['supplier_id']
        
        # 输入校验：库存存在且数量充足
        inventory = Inventory.query.filter_by(
            drug_id=drug_id,
            warehouse_id=warehouse_id
        ).first()
        if not inventory:
            flash('该药品在指定仓库中没有库存，无法退货！', 'danger')
            return redirect(url_for('inventory.return_add'))
        if inventory.quantity < quantity:
            flash(f'库存不足！当前库存：{inventory.quantity}，退货数量：{quantity}', 'danger')
            return redirect(url_for('inventory.return_add'))

        # 业务校验：供应商采购记录与可退额度
        purchased_qty = db.session.query(func.coalesce(func.sum(StockIn.quantity), 0)).\
            filter_by(drug_id=drug_id, supplier_id=supplier_id).scalar()
        returned_qty = db.session.query(func.coalesce(func.sum(ReturnStock.quantity), 0)).\
            filter_by(drug_id=drug_id, supplier_id=supplier_id).scalar()
        if purchased_qty == 0:
            flash('该供应商没有该药品的采购记录，无法退货！', 'danger')
            return redirect(url_for('inventory.return_add'))
        if quantity + returned_qty > purchased_qty:
            flash(f'退货数量超出该供应商已采购数量！已采购 {purchased_qty}，已退 {returned_qty}，本次退货 {quantity}', 'danger')
            return redirect(url_for('inventory.return_add'))
        
        # 数据库执行：插入退货记录
        return_stock = ReturnStock(
            drug_id=drug_id,
            supplier_id=supplier_id,
            quantity=quantity,
            reason=request.form.get('reason'),
            return_date=datetime.strptime(request.form['return_date'], '%Y-%m-%d').date(),
            employee_id=request.form.get('employee_id', 1)
        )
        db.session.add(return_stock)
        
        # 数据库执行：扣减库存
        inventory.quantity -= quantity
        
        db.session.commit()
        flash('退货处理成功！', 'success')
        return redirect(url_for('inventory.return_list'))
    
    drugs = DrugInfo.query.all()
    suppliers = SupplierInfo.query.all()
    return render_template('inventory/return_form.html', drugs=drugs, suppliers=suppliers)
