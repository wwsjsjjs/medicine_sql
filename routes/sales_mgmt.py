"""
销售管理模块路由
包括：销售登记、销售退货、财务统计
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Sales, SalesReturn, FinanceStat, DrugInfo, CustomerInfo, EmployeeInfo, Inventory
from datetime import datetime, timedelta
from sqlalchemy import func, extract

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')


def _upsert_daily_finance(stat_date, employee_id=None):
    """按日计算净销售/成本（销售-退货），写入finance_stat。"""
    from decimal import Decimal
    sales_sum = db.session.query(func.sum(Sales.quantity * DrugInfo.sale_price)).\
        join(DrugInfo, Sales.drug_id == DrugInfo.drug_id).\
        filter(Sales.sales_date == stat_date).scalar() or 0
    cost_sum = db.session.query(func.sum(Sales.quantity * DrugInfo.purchase_price)).\
        join(DrugInfo, Sales.drug_id == DrugInfo.drug_id).\
        filter(Sales.sales_date == stat_date).scalar() or 0
    return_sales = db.session.query(func.sum(SalesReturn.quantity * DrugInfo.sale_price)).\
        join(Sales, SalesReturn.sales_id == Sales.sales_id).\
        join(DrugInfo, Sales.drug_id == DrugInfo.drug_id).\
        filter(SalesReturn.return_date == stat_date).scalar() or 0
    return_cost = db.session.query(func.sum(SalesReturn.quantity * DrugInfo.purchase_price)).\
        join(Sales, SalesReturn.sales_id == Sales.sales_id).\
        join(DrugInfo, Sales.drug_id == DrugInfo.drug_id).\
        filter(SalesReturn.return_date == stat_date).scalar() or 0

    net_sales = Decimal(str(sales_sum)) - Decimal(str(return_sales))
    net_cost = Decimal(str(cost_sum)) - Decimal(str(return_cost))
    net_profit = net_sales - net_cost

    stat = FinanceStat.query.filter_by(stat_type='日', stat_date=stat_date).first()
    if stat:
        stat.total_sales = net_sales
        stat.total_cost = net_cost
        stat.total_profit = net_profit
        if employee_id:
            stat.employee_id = employee_id
    else:
        stat = FinanceStat(
            stat_type='日',
            stat_date=stat_date,
            total_sales=net_sales,
            total_cost=net_cost,
            total_profit=net_profit,
            employee_id=employee_id
        )
        db.session.add(stat)
    db.session.commit()
    return stat

# ==================== 销售登记 ====================
@sales_bp.route('/sales')
def sales_list():
    """销售列表（READ）"""
    sales_list = db.session.query(Sales, DrugInfo.name, CustomerInfo.name, EmployeeInfo.name).\
        join(DrugInfo, Sales.drug_id == DrugInfo.drug_id).\
        join(CustomerInfo, Sales.customer_id == CustomerInfo.customer_id).\
        join(EmployeeInfo, Sales.employee_id == EmployeeInfo.employee_id).\
        order_by(Sales.sales_date.desc()).all()
    return render_template('sales/sales_list.html', sales_list=sales_list)

@sales_bp.route('/sales/add', methods=['GET', 'POST'])
def sales_add():
    """添加销售（CREATE）"""
    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        warehouse_id = request.form.get('warehouse_id', 1)
        
        # 输入校验：药品、客户存在
        drug = DrugInfo.query.get(request.form['drug_id'])
        if not drug:
            flash('指定的药品不存在！', 'danger')
            return redirect(url_for('sales.sales_add'))
        
        # 验证客户是否存在
        customer = CustomerInfo.query.get(request.form['customer_id'])
        if not customer:
            flash('指定的客户不存在，请先添加客户信息！', 'danger')
            return redirect(url_for('sales.sales_add'))
        
        # 业务校验：库存存在且数量足够
        inventory = Inventory.query.filter_by(
            drug_id=request.form['drug_id'],
            warehouse_id=warehouse_id
        ).first()
        if not inventory:
            flash('该药品无库存，无法销售！', 'danger')
            return redirect(url_for('sales.sales_add'))
        if inventory.quantity < quantity:
            flash(f'库存不足！当前库存：{inventory.quantity}，销售数量：{quantity}', 'danger')
            return redirect(url_for('sales.sales_add'))
        
        # 数据库执行：插入销售记录（价格取药品售价，表中不再存价格字段）
        sale = Sales(
            drug_id=request.form['drug_id'],
            customer_id=request.form['customer_id'],
            quantity=quantity,
            sales_date=datetime.strptime(request.form['sales_date'], '%Y-%m-%d').date(),
            employee_id=request.form.get('employee_id', 1)
        )
        db.session.add(sale)
        
        # 数据库执行：扣减库存
        inventory.quantity -= quantity
        
        db.session.commit()
        flash('销售登记成功！', 'success')
        return redirect(url_for('sales.sales_list'))
    
    drugs = DrugInfo.query.filter_by(status='在售').all()
    customers = CustomerInfo.query.all()
    return render_template('sales/sales_form.html', drugs=drugs, customers=customers)

# ==================== 销售退货 ====================
@sales_bp.route('/return')
def return_list():
    """销售退货列表（READ）"""
    returns = db.session.query(SalesReturn, Sales, DrugInfo.name, EmployeeInfo.name).\
        join(Sales, SalesReturn.sales_id == Sales.sales_id).\
        join(DrugInfo, Sales.drug_id == DrugInfo.drug_id).\
        join(EmployeeInfo, SalesReturn.employee_id == EmployeeInfo.employee_id).all()
    return render_template('sales/return_list.html', returns=returns)

@sales_bp.route('/return/add', methods=['GET', 'POST'])
def return_add():
    """添加销售退货（CREATE）"""
    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        warehouse_id = request.form.get('warehouse_id', 1)
        
        # 输入校验：销售记录存在
        sale = Sales.query.get(request.form['sales_id'])
        if not sale:
            flash('指定的销售记录不存在！', 'danger')
            return redirect(url_for('sales.return_add'))
        
        # 业务校验：退货数量不能超过销售数量
        if quantity > sale.quantity:
            flash(f'退货数量不能超过销售数量！销售数量：{sale.quantity}', 'danger')
            return redirect(url_for('sales.return_add'))
        
        # 数据库执行：插入退货记录
        sales_return = SalesReturn(
            sales_id=request.form['sales_id'],
            quantity=quantity,
            reason=request.form.get('reason'),
            return_date=datetime.strptime(request.form['return_date'], '%Y-%m-%d').date(),
            employee_id=request.form.get('employee_id', 1)
        )
        db.session.add(sales_return)
        
        # 数据库执行：回补库存（存在则累加，不存在则创建）
        inventory = Inventory.query.filter_by(
            drug_id=sale.drug_id,
            warehouse_id=warehouse_id
        ).first()
        if inventory:
            inventory.quantity += quantity
        else:
            # 如果库存记录不存在，创建新记录
            inventory = Inventory(
                drug_id=sale.drug_id,
                warehouse_id=warehouse_id,
                quantity=quantity
            )
            db.session.add(inventory)
        
        db.session.commit()
        flash('销售退货处理成功！', 'success')
        return redirect(url_for('sales.return_list'))
    
    sales_records = Sales.query.order_by(Sales.sales_date.desc()).limit(100).all()
    return render_template('sales/return_form.html', sales_records=sales_records)

# ==================== 财务统计 ====================
@sales_bp.route('/finance')
def finance_list():
    """财务统计列表（READ）"""
    stats = db.session.query(FinanceStat, EmployeeInfo.name).\
        join(EmployeeInfo, FinanceStat.employee_id == EmployeeInfo.employee_id).\
        order_by(FinanceStat.stat_date.desc()).all()
    return render_template('sales/finance_list.html', stats=stats)

@sales_bp.route('/finance/generate', methods=['POST'])
def finance_generate():
    """生成财务统计（CREATE/UPDATE）"""
    stat_type = request.form['stat_type']
    stat_date = datetime.strptime(request.form['stat_date'], '%Y-%m-%d').date()
    admin = EmployeeInfo.query.filter_by(account='admin').first()
    employee_id = request.form.get('employee_id') or (admin.employee_id if admin else None)

    if stat_type == '日':
        _upsert_daily_finance(stat_date, employee_id)
    else:  # 月：聚合当月所有日报
        first_day = stat_date.replace(day=1)
        next_month = (first_day + timedelta(days=32)).replace(day=1)
        current = first_day
        while current < next_month:
            _upsert_daily_finance(current, employee_id)
            current += timedelta(days=1)
        agg = db.session.query(
            func.sum(FinanceStat.total_sales),
            func.sum(FinanceStat.total_cost),
            func.sum(FinanceStat.total_profit)
        ).filter_by(stat_type='日').\
            filter(FinanceStat.stat_date >= first_day, FinanceStat.stat_date < next_month).first()
        stat = FinanceStat.query.filter_by(stat_type='月', stat_date=first_day).first()
        if stat:
            stat.total_sales, stat.total_cost, stat.total_profit = agg
            if employee_id:
                stat.employee_id = employee_id
        else:
            stat = FinanceStat(
                stat_type='月',
                stat_date=first_day,
                total_sales=agg[0] or 0,
                total_cost=agg[1] or 0,
                total_profit=agg[2] or 0,
                employee_id=employee_id
            )
            db.session.add(stat)
        db.session.commit()

    flash('财务统计生成成功！', 'success')
    return redirect(url_for('sales.finance_list'))

# ==================== 销售报表 ====================
@sales_bp.route('/report/week')
def report_week():
    """最近一周销售情况（READ）"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    admin = EmployeeInfo.query.filter_by(account='admin').first()
    employee_id = admin.employee_id if admin else None

    current = start_date
    while current <= end_date:
        _upsert_daily_finance(current, employee_id)
        current += timedelta(days=1)

    daily_stats = FinanceStat.query.filter_by(stat_type='日').\
        filter(FinanceStat.stat_date.between(start_date, end_date)).\
        order_by(FinanceStat.stat_date).all()
    daily_sales = [(stat.stat_date, stat.total_sales) for stat in daily_stats]

    return render_template('sales/report_week.html',
                         daily_sales=daily_sales,
                         drug_sales=[],
                         start_date=start_date,
                         end_date=end_date)
