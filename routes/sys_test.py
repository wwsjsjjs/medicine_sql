"""
系统测试路由
提供测试数据生成、批量操作测试等功能
"""

from flask import Blueprint, jsonify, request, render_template, session
from models import db, DrugInfo, EmployeeInfo, CustomerInfo, SupplierInfo, log_system_action
from models import StockIn, Sales, Inventory, Warehouse, ReturnStock, SalesReturn, InventoryCheck, FinanceStat
from datetime import datetime, timedelta
from sqlalchemy import func
import random
import traceback

api_test_bp = Blueprint('api_test', __name__, url_prefix='/api/test')


# ==================== 日志辅助函数 ====================

def log_info(message):
    """统一的信息日志"""
    print(f"[INFO] {message}")


def log_success(message):
    """统一的成功日志"""
    print(f"[SUCCESS] {message}")


def log_error(message, detail=None):
    """统一的错误日志"""
    print(f"[ERROR] {message}")
    if detail:
        print(f"[ERROR] 详细信息:\n{detail}")


def handle_error(e, operation_name, rollback=True):
    """统一的错误处理"""
    if rollback:
        db.session.rollback()
    error_detail = traceback.format_exc()
    log_error(f"{operation_name}失败: {str(e)}", error_detail)
    return {
        'success': False,
        'message': f'{operation_name}失败: {str(e)}',
        'error_detail': error_detail
    }


# ==================== 核心业务逻辑测试函数 ====================

def _test_create_drug(commit=True):
    """测试：创建药品"""
    try:
        log_info("开始执行：创建药品测试")
        drug_name = f"测试药品_{random.randint(1000, 9999)}"
        approval_number = f"国药准字Z{random.randint(10000000, 99999999)}"
        
        drug = DrugInfo(
            name=drug_name,
            spec="10g*10袋",
            manufacturer="测试药厂",
            approval_number=approval_number,
            category="处方",
            unit="盒",
            purchase_price=20.0,
            sale_price=35.0,
            expiry_date=datetime.now().date() + timedelta(days=365),
            status="在售"
        )
        db.session.add(drug)
        if commit:
            db.session.commit()
            log_success(f"创建药品成功: {drug.name} (ID: {drug.drug_id})")
            log_system_action(session.get('employee_id'), 'insert', 'drug_info', {'drug_id': drug.drug_id, 'name': drug.name})
        from flask import jsonify
        return jsonify({'success': True, 'message': '创建药品测试通过', 'data': {'drug_id': drug.drug_id, 'name': drug.name}})
    except Exception as e:
        return handle_error(e, "创建药品测试")


def _test_create_supplier(commit=True):
    """测试：创建供应商"""
    try:
        log_info("开始执行：创建供应商测试")
        name = f"测试供应商_{random.randint(1000, 9999)}"
        phone = f"138{random.randint(10000000, 99999999)}"
        
        supplier = SupplierInfo(
            name=name,
            contact="张三",
            phone=phone,
            address="测试地址",
            qualification_no=f"QUAL_{random.randint(100000, 999999)}"
        )
        db.session.add(supplier)
        if commit:
            db.session.commit()
            log_success(f"创建供应商成功: {supplier.name} (ID: {supplier.supplier_id})")
            log_system_action(session.get('employee_id'), 'insert', 'supplier_info', {'supplier_id': supplier.supplier_id, 'name': supplier.name})
        from flask import jsonify
        return jsonify({'success': True, 'message': '创建供应商测试通过', 'data': {'supplier_id': supplier.supplier_id, 'name': supplier.name}})
    except Exception as e:
        return handle_error(e, "创建供应商测试")


def _test_create_customer(commit=True):
    """测试：创建客户"""
    try:
        log_info("开始执行：创建客户测试")
        name = f"测试客户_{random.randint(1000, 9999)}"
        phone = f"139{random.randint(10000000, 99999999)}"
        
        customer = CustomerInfo(
            name=name,
            type="零售",
            contact="张经理",
            phone=phone,
            address="测试地址"
        )
        db.session.add(customer)
        if commit:
            db.session.commit()
            log_success(f"创建客户成功: {customer.name} (ID: {customer.customer_id})")
            log_system_action(session.get('employee_id'), 'insert', 'customer_info', {'customer_id': customer.customer_id, 'name': customer.name})
        from flask import jsonify
        return jsonify({'success': True, 'message': '创建客户测试通过', 'data': {'customer_id': customer.customer_id, 'name': customer.name}})
    except Exception as e:
        return handle_error(e, "创建客户测试")

def _test_create_employee(commit=True):
    """测试: 创建员工"""
    try:
        name = f"测试员工_{random.randint(1000, 9999)}"
        employee = EmployeeInfo(
            name=name,
            account=f"user_{random.randint(10000, 99999)}",
            password="password",
            phone=f"136{random.randint(10000000, 99999999)}",
            department="测试部门",
            position="员工"
        )
        db.session.add(employee)
        if commit:
            db.session.commit()
            log_success(f"创建员工成功: {employee.name} (ID: {employee.employee_id})")
            log_system_action(session.get('employee_id'), 'insert', 'employee_info', {'employee_id': employee.employee_id, 'name': employee.name})
        from flask import jsonify
        return jsonify({'success': True, 'message': '创建员工测试通过', 'data': {'employee_id': employee.employee_id, 'name': employee.name}})
    except Exception as e:
        return handle_error(e, "创建员工测试")

def _test_create_warehouse(commit=True):
    """测试：创建仓库"""
    try:
        log_info("开始执行：创建仓库测试")
        name = f"测试仓库_{random.randint(1000, 9999)}"
        
        # 确保有一个员工作为管理员
        manager = EmployeeInfo.query.first()
        if not manager:
            manager = EmployeeInfo(
                name="默认管理员",
                account=f"admin_{random.randint(1000,9999)}",
                password="password",
                phone=f"137{random.randint(10000000, 99999999)}"
            )
            db.session.add(manager)
            db.session.commit()
        
        warehouse = Warehouse(
            name=name,
            address="测试仓库地址",
            manager_id=manager.employee_id
        )
        db.session.add(warehouse)
        if commit:
            db.session.commit()
            log_success(f"创建仓库成功: {warehouse.name} (ID: {warehouse.warehouse_id})")
            log_system_action(session.get('employee_id'), 'insert', 'warehouse', {'warehouse_id': warehouse.warehouse_id, 'name': warehouse.name})
        from flask import jsonify
        return jsonify({'success': True, 'message': '创建仓库测试通过', 'data': {'warehouse_id': warehouse.warehouse_id, 'name': warehouse.name}})
    except Exception as e:
        return handle_error(e, "创建仓库测试")


def _test_stock_in(drug_id=None, supplier_id=None, warehouse_id=None, commit=True):
    """测试：入库流程"""
    try:
        log_info("开始执行：入库流程测试")
        
        # 如果未提供ID，则使用最新创建的或创建新的
        if not drug_id:
            drug = DrugInfo.query.order_by(DrugInfo.drug_id.desc()).first()
            if not drug:
                res = _test_create_drug(commit=True)
                if not res['success']: return res
                drug_id = res['data']['drug_id']
            else:
                drug_id = drug.drug_id
                
        if not supplier_id:
            supplier = SupplierInfo.query.order_by(SupplierInfo.supplier_id.desc()).first()
            if not supplier:
                res = _test_create_supplier(commit=True)
                if not res['success']: return res
                supplier_id = res['data']['supplier_id']
            else:
                supplier_id = supplier.supplier_id
                
        if not warehouse_id:
            warehouse = Warehouse.query.order_by(Warehouse.warehouse_id.desc()).first()
            if not warehouse:
                res = _test_create_warehouse(commit=True)
                if not res['success']: return res
                warehouse_id = res['data']['warehouse_id']
            else:
                warehouse_id = warehouse.warehouse_id

        quantity = 100
        unit_price = 20.0
        
        # 1. 创建入库单
        stock_in = StockIn(
            drug_id=drug_id,
            supplier_id=supplier_id,
            quantity=quantity,
            unit_price=unit_price,
            total_price=quantity * unit_price,
            stock_in_date=datetime.now().date(),
            employee_id=1, # 假设ID为1的员工存在
            remark="自动化测试入库"
        )
        db.session.add(stock_in)
        # 2. 更新库存
        inventory = Inventory.query.filter_by(drug_id=drug_id, warehouse_id=warehouse_id).first()
        if inventory:
            inventory.quantity += quantity
            inventory.update_time = datetime.now()
        else:
            inventory = Inventory(
                drug_id=drug_id,
                warehouse_id=warehouse_id,
                quantity=quantity,
                update_time=datetime.now()
            )
            db.session.add(inventory)
        if commit:
            db.session.commit()
            log_success(f"入库测试成功: 药品ID {drug_id}, 数量 {quantity}")
            log_system_action(session.get('employee_id'), 'insert', 'stock_in', {'stock_in_id': stock_in.stock_in_id, 'drug_id': drug_id, 'quantity': quantity})
        from flask import jsonify
        return jsonify({'success': True, 'message': '入库流程测试通过', 'data': {'stock_in_id': stock_in.stock_in_id}})
    except Exception as e:
        return handle_error(e, "入库流程测试")


def _test_sales(drug_id=None, customer_id=None, warehouse_id=None, commit=True):
    """测试：销售流程"""
    try:
        log_info("开始执行：销售流程测试")
        
        # 准备数据
        if not drug_id:
            drug = DrugInfo.query.order_by(DrugInfo.drug_id.desc()).first()
            if not drug: return {'success': False, 'message': '无可用药品，请先执行入库测试'}
            drug_id = drug.drug_id
            
        if not customer_id:
            customer = CustomerInfo.query.order_by(CustomerInfo.customer_id.desc()).first()
            if not customer:
                res = _test_create_customer(commit=True)
                if not res['success']: return res
                customer_id = res['data']['customer_id']
            else:
                customer_id = customer.customer_id
                
        if not warehouse_id:
            warehouse = Warehouse.query.order_by(Warehouse.warehouse_id.desc()).first()
            if not warehouse: return {'success': False, 'message': '无可用仓库'}
            warehouse_id = warehouse.warehouse_id

        quantity = 10
        unit_price = 35.0
        
        # 检查库存
        inventory = Inventory.query.filter_by(drug_id=drug_id, warehouse_id=warehouse_id).first()
        if not inventory or inventory.quantity < quantity:
            # 尝试先入库
            log_info("库存不足，尝试自动入库...")
            _test_stock_in(drug_id, None, warehouse_id, commit=True)
            inventory = Inventory.query.filter_by(drug_id=drug_id, warehouse_id=warehouse_id).first()
        
        # 1. 创建销售单
        sale = Sales(
            drug_id=drug_id,
            customer_id=customer_id,
            quantity=quantity,
            unit_price=unit_price,
            total_price=quantity * unit_price,
            sales_date=datetime.now().date(),
            employee_id=1
        )
        db.session.add(sale)
        # 2. 扣减库存
        inventory.quantity -= quantity
        inventory.update_time = datetime.now()
        if commit:
            db.session.commit()
            log_success(f"销售测试成功: 药品ID {drug_id}, 数量 {quantity}")
            log_system_action(session.get('employee_id'), 'insert', 'sales', {'sales_id': sale.sales_id, 'drug_id': drug_id, 'quantity': quantity})
        from flask import jsonify
        return jsonify({'success': True, 'message': '销售流程测试通过', 'data': {'sales_id': sale.sales_id}})
    except Exception as e:
        return handle_error(e, "销售流程测试")


def _test_finance_stat(commit=True):
    """测试：财务统计"""
    try:
        log_info("开始执行：财务统计测试")
        today = datetime.now().date()
        
        # 简单的统计逻辑
        sales_total = db.session.query(db.func.sum(Sales.total_price)).filter(Sales.sales_date == today).scalar() or 0
        cost_total = db.session.query(db.func.sum(StockIn.total_price)).filter(StockIn.stock_in_date == today).scalar() or 0
        profit = sales_total - cost_total
        
        stat = FinanceStat.query.filter_by(stat_date=today, stat_type='日').first()
        if stat:
            stat.total_sales = sales_total
            stat.total_cost = cost_total
            stat.total_profit = profit
        else:
            stat = FinanceStat(
                stat_date=today,
                stat_type='日',
                total_sales=sales_total,
                total_cost=cost_total,
                total_profit=profit
            )
            db.session.add(stat)
        if commit:
            db.session.commit()
            log_success(f"财务统计测试成功: 销售额 {sales_total}, 成本 {cost_total}")
            log_system_action(session.get('employee_id'), 'insert', 'finance_stat', {'stat_id': stat.stat_id, 'date': str(today)})
        return {'success': True, 'message': '财务统计测试通过', 'data': {'stat_id': stat.stat_id}}
    except Exception as e:
        return handle_error(e, "财务统计测试")


# ==================== 路由接口 ====================

@api_test_bp.route('/')
def index():
    """测试控制台页面"""
    return render_template('testing/test_console.html')

@api_test_bp.route('/custom_data')
def custom_data():
    """自定义测试数据页面"""
    return render_template('testing/custom_data.html')

# ==================== 自定义测试数据生成API ====================

@api_test_bp.route('/custom_drug', methods=['POST'])
def custom_drug():
    """自定义药品生成"""
    try:
        data = request.json
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({'success': False, 'message': '药品名称不能为空'})
        if not data.get('purchase_price') or float(data.get('purchase_price', 0)) <= 0:
            return jsonify({'success': False, 'message': '进货价必须大于0'})
        if not data.get('sale_price') or float(data.get('sale_price', 0)) <= 0:
            return jsonify({'success': False, 'message': '销售价必须大于0'})
        
        # 验证销售价应大于进货价
        if float(data['sale_price']) < float(data['purchase_price']):
            return jsonify({'success': False, 'message': '销售价应大于或等于进货价'})
        
        # 处理有效期
        expiry_date = None
        if data.get('expiry_date'):
            from datetime import datetime
            expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        
        drug = DrugInfo(
            name=data['name'],
            spec=data.get('spec'),
            manufacturer=data.get('manufacturer'),
            approval_number=data.get('approval_number'),
            category=data.get('category', '处方'),
            unit=data.get('unit', '盒'),
            purchase_price=float(data['purchase_price']),
            sale_price=float(data['sale_price']),
            expiry_date=expiry_date,
            status=data.get('status', '在售')
        )
        
        db.session.add(drug)
        db.session.commit()
        
        log_success(f"自定义药品创建成功: {drug.name} (ID: {drug.drug_id})")
        return jsonify({
            'success': True,
            'message': f'药品 "{drug.name}" 创建成功 (ID: {drug.drug_id})',
            'data': {'drug_id': drug.drug_id, 'name': drug.name}
        })
    except Exception as e:
        return handle_error(e, "自定义药品生成")

@api_test_bp.route('/custom_customer', methods=['POST'])
def custom_customer():
    """自定义客户生成"""
    try:
        data = request.json
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({'success': False, 'message': '客户名称不能为空'})
        if not data.get('type'):
            return jsonify({'success': False, 'message': '客户类型不能为空'})
        
        # 验证电话格式（如果提供）
        if data.get('phone'):
            phone = data['phone'].strip()
            if len(phone) < 7:
                return jsonify({'success': False, 'message': '电话号码格式不正确'})
        
        customer = CustomerInfo(
            name=data['name'],
            type=data['type'],
            contact=data.get('contact'),
            phone=data.get('phone'),
            address=data.get('address')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        log_success(f"自定义客户创建成功: {customer.name} (ID: {customer.customer_id})")
        return jsonify({
            'success': True,
            'message': f'客户 "{customer.name}" 创建成功 (ID: {customer.customer_id})',
            'data': {'customer_id': customer.customer_id, 'name': customer.name}
        })
    except Exception as e:
        return handle_error(e, "自定义客户生成")

@api_test_bp.route('/custom_supplier', methods=['POST'])
def custom_supplier():
    """自定义供应商生成"""
    try:
        data = request.json
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({'success': False, 'message': '供应商名称不能为空'})
        
        # 检查名称是否已存在
        existing = SupplierInfo.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'success': False, 'message': f'供应商 "{data["name"]}" 已存在'})
        
        supplier = SupplierInfo(
            name=data['name'],
            contact=data.get('contact'),
            phone=data.get('phone'),
            address=data.get('address'),
            qualification_no=data.get('qualification_no')
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        log_success(f"自定义供应商创建成功: {supplier.name} (ID: {supplier.supplier_id})")
        return jsonify({
            'success': True,
            'message': f'供应商 "{supplier.name}" 创建成功 (ID: {supplier.supplier_id})',
            'data': {'supplier_id': supplier.supplier_id, 'name': supplier.name}
        })
    except Exception as e:
        return handle_error(e, "自定义供应商生成")

@api_test_bp.route('/custom_employee', methods=['POST'])
def custom_employee():
    """自定义员工生成"""
    try:
        data = request.json
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({'success': False, 'message': '员工姓名不能为空'})
        if not data.get('account'):
            return jsonify({'success': False, 'message': '账号不能为空'})
        if not data.get('password'):
            return jsonify({'success': False, 'message': '密码不能为空'})
        
        # 验证密码长度
        if len(data['password']) < 6:
            return jsonify({'success': False, 'message': '密码至少6位'})
        
        # 检查账号是否已存在
        existing = EmployeeInfo.query.filter_by(account=data['account']).first()
        if existing:
            return jsonify({'success': False, 'message': f'账号 "{data["account"]}" 已存在'})
        
        # 处理入职日期
        hire_date = None
        if data.get('hire_date'):
            from datetime import datetime
            hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
        
        employee = EmployeeInfo(
            name=data['name'],
            department=data.get('department'),
            position=data.get('position'),
            phone=data.get('phone'),
            hire_date=hire_date,
            account=data['account'],
            password=data['password'],  # 实际应用需要加密
            status=data.get('status', '在职')
        )
        
        db.session.add(employee)
        db.session.commit()
        
        log_success(f"自定义员工创建成功: {employee.name} (ID: {employee.employee_id})")
        return jsonify({
            'success': True,
            'message': f'员工 "{employee.name}" 创建成功 (ID: {employee.employee_id})',
            'data': {'employee_id': employee.employee_id, 'name': employee.name}
        })
    except Exception as e:
        return handle_error(e, "自定义员工生成")

@api_test_bp.route('/test_drug')
def route_test_drug():
    return jsonify(_test_create_drug())

@api_test_bp.route('/test_supplier')
def route_test_supplier():
    return jsonify(_test_create_supplier())

@api_test_bp.route('/test_customer')
def route_test_customer():
    return jsonify(_test_create_customer())

@api_test_bp.route('/test_warehouse')
def route_test_warehouse():
    return jsonify(_test_create_warehouse())

@api_test_bp.route('/test_stock_in')
def route_test_stock_in():
    return jsonify(_test_stock_in())

@api_test_bp.route('/test_sales')
def route_test_sales():
    return jsonify(_test_sales())

@api_test_bp.route('/test_finance')
def route_test_finance():
    return jsonify(_test_finance_stat())

@api_test_bp.route('/stats')
def route_stats():
    """获取系统统计信息"""
    try:
        stats = {
            'drugs': db.session.query(func.count(DrugInfo.drug_id)).scalar(),
            'customers': db.session.query(func.count(CustomerInfo.customer_id)).scalar(),
            'suppliers': db.session.query(func.count(SupplierInfo.supplier_id)).scalar(),
            'employees': db.session.query(func.count(EmployeeInfo.employee_id)).scalar(),
            'warehouses': db.session.query(func.count(Warehouse.warehouse_id)).scalar(),
            'total_inventory': db.session.query(func.sum(Inventory.quantity)).scalar() or 0,
            'stock_ins': db.session.query(func.count(StockIn.stock_in_id)).scalar(),
            'sales': db.session.query(func.count(Sales.sales_id)).scalar(),
            'returns': db.session.query(func.count(ReturnStock.return_id)).scalar(),
            'sales_returns': db.session.query(func.count(SalesReturn.sales_return_id)).scalar(),
            'inventory_checks': db.session.query(func.count(InventoryCheck.check_id)).scalar(),
            'finance_stats': db.session.query(func.count(FinanceStat.stat_id)).scalar()
        }
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return handle_error(e, "获取统计信息", rollback=False)

@api_test_bp.route('/generate_drug', methods=['POST'])
def route_generate_drug():
    res = _test_create_drug()
    data = res.get_json() if hasattr(res, 'get_json') else res
    return jsonify({'success': data['success'], 'message': data['message']})

@api_test_bp.route('/generate_customer', methods=['POST'])
def route_generate_customer():
    res = _test_create_customer()
    data = res.get_json() if hasattr(res, 'get_json') else res
    return jsonify({'success': data['success'], 'message': data['message']})

@api_test_bp.route('/generate_employee', methods=['POST'])
def route_generate_employee():
    res = _test_create_employee()
    data = res.get_json() if hasattr(res, 'get_json') else res
    return jsonify({'success': data['success'], 'message': data['message']})
    # try:
    #     name = f"测试员工_{random.randint(1000, 9999)}"
    #     employee = EmployeeInfo(
    #         name=name,
    #         account=f"user_{random.randint(10000, 99999)}",
    #         password="password",
    #         phone=f"136{random.randint(10000000, 99999999)}",
    #         department="测试部门",
    #         position="员工"
    #     )
    #     db.session.add(employee)
    #     db.session.commit()
    #     return jsonify({'success': True, 'message': f'员工 {name} 已生成'})
    # except Exception as e:
    #     return handle_error(e, "生成员工数据")

@api_test_bp.route('/generate_supplier', methods=['POST'])
def route_generate_supplier():
    res = _test_create_supplier()
    data = res.get_json() if hasattr(res, 'get_json') else res
    return jsonify({'success': data['success'], 'message': data['message']})

@api_test_bp.route('/generate_warehouse', methods=['POST'])
def route_generate_warehouse():
    # 检查是否有员工可作为管理员
    manager = EmployeeInfo.query.first()
    if not manager:
        return jsonify({'success': False, 'message': '请先生成员工数据，是否自动生成？'})
    res = _test_create_warehouse()
    return jsonify({'success': res.json['success'], 'message': res.json['message']})
    try:
        stats = {
            'drugs': db.session.query(func.count(DrugInfo.drug_id)).scalar(),
            'customers': db.session.query(func.count(CustomerInfo.customer_id)).scalar(),
            'suppliers': db.session.query(func.count(SupplierInfo.supplier_id)).scalar(),
            'employees': db.session.query(func.count(EmployeeInfo.employee_id)).scalar(),
            'warehouses': db.session.query(func.count(Warehouse.warehouse_id)).scalar(),
            'total_inventory': db.session.query(func.sum(Inventory.quantity)).scalar() or 0,
            'stock_ins': db.session.query(func.count(StockIn.stock_in_id)).scalar(),
            'sales': db.session.query(func.count(Sales.sales_id)).scalar(),
            'returns': db.session.query(func.count(ReturnStock.return_id)).scalar(),
            'sales_returns': db.session.query(func.count(SalesReturn.sales_return_id)).scalar(),
            'inventory_checks': db.session.query(func.count(InventoryCheck.check_id)).scalar(),
            'finance_stats': db.session.query(func.count(FinanceStat.stat_id)).scalar()
        }
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return handle_error(e, "获取统计信息", rollback=False)
    count = request.json.get('count', 10)
    success_count = 0
    for _ in range(count):
        if _test_sales()['success']:
            success_count += 1
    return jsonify({'success': True, 'message': f'成功执行 {success_count} 次销售操作'})

@api_test_bp.route('/batch_return_stock', methods=['POST'])
def route_batch_return_stock():
    count = request.json.get('count', 5)
    success_count = 0
    try:
        stockins = StockIn.query.limit(count).all()
        if not stockins:
            return jsonify({'success': False, 'message': '没有可退货的入库记录'})
        for stockin in stockins:
            # 随机退货数量1-5，允许重复退货
            return_quantity = random.randint(1, 5)
            return_stock = ReturnStock(
                drug_id=stockin.drug_id,
                supplier_id=stockin.supplier_id,
                quantity=return_quantity,
                reason="测试退货",
                return_date=datetime.now().date(),
                employee_id=1
            )
            db.session.add(return_stock)
            # 更新库存（StockIn没有warehouse_id，从该药品的任意仓库扣减库存）
            inventory = Inventory.query.filter_by(drug_id=stockin.drug_id).filter(Inventory.quantity >= return_quantity).first()
            if inventory:
                inventory.quantity -= return_quantity
                success_count += 1
        db.session.commit()
        return jsonify({'success': True, 'message': f'成功执行 {success_count} 次退货操作'})
    except Exception as e:
        return handle_error(e, "批量退货")

@api_test_bp.route('/batch_sales_return', methods=['POST'])
def route_batch_sales_return():
    count = request.json.get('count', 5)
    success_count = 0
    try:
        sales = Sales.query.limit(count).all()
        if not sales:
            return jsonify({'success': False, 'message': '没有可退货的销售记录'})
            
        for sale in sales:
            existing_return = SalesReturn.query.filter_by(sales_id=sale.sales_id).first()
            if existing_return: continue
            
            sales_return = SalesReturn(
                sales_id=sale.sales_id,
                quantity=1,
                reason="测试销售退货",
                return_date=datetime.now().date(),
                employee_id=1
            )
            db.session.add(sales_return)
            
            # 更新库存
            inventory = Inventory.query.filter_by(drug_id=sale.drug_id).first()
            if inventory:
                inventory.quantity += 1
                success_count += 1
                
        db.session.commit()
        return jsonify({'success': True, 'message': f'成功执行 {success_count} 次销售退货操作'})
    except Exception as e:
        return handle_error(e, "批量销售退货")

@api_test_bp.route('/batch_inventory_check', methods=['POST'])
def route_batch_inventory_check():
    count = request.json.get('count', 5)
    success_count = 0
    try:
        inventories = Inventory.query.limit(count).all()
        if not inventories:
            return jsonify({'success': False, 'message': '没有库存记录'})
            
        for inv in inventories:
            check = InventoryCheck(
                warehouse_id=inv.warehouse_id,
                drug_id=inv.drug_id,
                checked_quantity=inv.quantity,
                actual_quantity=inv.quantity, # 假设盘点无误
                diff_reason="无差异",
                check_date=datetime.now().date(),
                employee_id=1
            )
            db.session.add(check)
            success_count += 1
            
        db.session.commit()
        return jsonify({'success': True, 'message': f'成功执行 {success_count} 次库存盘点'})
    except Exception as e:
        return handle_error(e, "批量库存盘点")

@api_test_bp.route('/generate_finance_stats', methods=['POST'])
def route_generate_finance_stats():
    """生成财务统计"""
    try:
        from decimal import Decimal
        today = datetime.now().date()
        
        # 计算今日销售额
        sales_total = db.session.query(func.sum(Sales.total_price)).filter(Sales.sales_date == today).scalar() or Decimal('0')
        # 计算今日成本（这里简化处理，实际应从采购价计算）
        cost_total = sales_total * Decimal('0.6')
        profit = sales_total - cost_total
        
        # 检查是否已存在今日统计
        stat = FinanceStat.query.filter_by(stat_date=today, stat_type='日').first()
        if stat:
            stat.total_sales = sales_total
            stat.total_cost = cost_total
            stat.total_profit = profit
            message = '财务统计已更新'
        else:
            stat = FinanceStat(
                stat_date=today,
                stat_type='日',
                total_sales=sales_total,
                total_cost=cost_total,
                total_profit=profit,
                employee_id=1
            )
            db.session.add(stat)
            message = '财务统计已生成'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'data': [
                f'统计日期: {today}',
                f'销售总额: ¥{float(sales_total):.2f}',
                f'成本总额: ¥{float(cost_total):.2f}',
                f'利润总额: ¥{float(profit):.2f}'
            ]
        })
    except Exception as e:
        return handle_error(e, "生成财务统计")

@api_test_bp.route('/clear_all_data', methods=['POST'])
def route_clear_all_data():
    try:
        # 按依赖关系反向删除
        db.session.query(FinanceStat).delete()
        db.session.query(InventoryCheck).delete()
        db.session.query(SalesReturn).delete()
        db.session.query(ReturnStock).delete()
        db.session.query(Sales).delete()
        db.session.query(StockIn).delete()
        db.session.query(Inventory).delete()
        db.session.query(Warehouse).delete()
        db.session.query(CustomerInfo).delete()
        db.session.query(SupplierInfo).delete()
        db.session.query(DrugInfo).delete()
        # 可选择删除员工（保留ID为1的系统管理员）
        delete_employees = request.args.get('delete_employees', 'false') == 'true'
        if delete_employees:
            db.session.query(EmployeeInfo).filter(EmployeeInfo.employee_id != 1).delete()
        
        db.session.commit()
        return jsonify({'success': True, 'message': '所有测试数据已清空'})
    except Exception as e:
        return handle_error(e, "清空数据")

@api_test_bp.route('/system_tables_view')
def view_system_tables():
    """系统表查看页面"""
    return render_template('testing/system_tables.html')

@api_test_bp.route('/system_tables')
def system_tables():
    """查看系统表数据API"""
    try:
        from models import Role, Permission, RolePermission, UserRole, SystemLog
        
        roles = []
        permissions = []
        role_permissions = []
        user_roles = []
        logs = []
        
        # 安全地查询每个表
        try:
            roles = Role.query.all()
        except Exception as e:
            log_error(f"查询角色表失败: {str(e)}")
        
        try:
            permissions = Permission.query.all()
        except Exception as e:
            log_error(f"查询权限表失败: {str(e)}")
        
        try:
            role_permissions = db.session.query(RolePermission, Role.name, Permission.name).join(Role).join(Permission).all()
        except Exception as e:
            log_error(f"查询角色权限关联表失败: {str(e)}")
        
        try:
            user_roles = db.session.query(UserRole, EmployeeInfo.name, Role.name).join(EmployeeInfo).join(Role).all()
        except Exception as e:
            log_error(f"查询用户角色关联表失败: {str(e)}")
        
        try:
            logs = SystemLog.query.order_by(SystemLog.action_time.desc()).limit(50).all()
        except Exception as e:
            log_error(f"查询系统日志表失败: {str(e)}")
        
        return jsonify({
            'success': True,
            'data': {
                'roles': [{'id': r.role_id, 'name': r.name, 'description': r.description} for r in roles],
                'permissions': [{'id': p.permission_id, 'name': p.name, 'description': p.description} for p in permissions],
                'role_permissions': [{'role': rp[1], 'permission': rp[2]} for rp in role_permissions],
                'user_roles': [{'employee': ur[1], 'role': ur[2]} for ur in user_roles],
                'logs': [{'id': l.log_id, 'employee_id': l.employee_id, 'action_type': l.action_type, 'table': l.table_name, 'time': l.action_time.strftime('%Y-%m-%d %H:%M:%S')} for l in logs]
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询系统表失败: {str(e)}',
            'data': {
                'roles': [],
                'permissions': [],
                'role_permissions': [],
                'user_roles': [],
                'logs': []
            }
        })

@api_test_bp.route('/full_chain_test', methods=['GET', 'POST'])
def full_chain_test():
    """全链路测试：按顺序执行所有测试"""
    results = []
    steps = []
    log_info("========== 开始全链路测试 ==========")
    
    try:
        # 1. 基础数据生成
        res = _test_create_drug()
        results.append(res)
        steps.append(f"1. 创建药品: {'成功' if res['success'] else '失败'}")
        
        res = _test_create_supplier()
        results.append(res)
        steps.append(f"2. 创建供应商: {'成功' if res['success'] else '失败'}")
        
        res = _test_create_customer()
        results.append(res)
        steps.append(f"3. 创建客户: {'成功' if res['success'] else '失败'}")
        
        res = _test_create_warehouse()
        results.append(res)
        steps.append(f"4. 创建仓库: {'成功' if res['success'] else '失败'}")
        
        # 检查基础数据是否成功，如果失败则中止
        if not all(r['success'] for r in results):
            return jsonify({'success': False, 'message': '基础数据生成失败，中止测试', 'steps': steps})

        # 获取生成的ID用于后续流程
        drug_id = results[0]['data']['drug_id']
        drug_name = results[0]['data']['name']
        supplier_id = results[1]['data']['supplier_id']
        customer_id = results[2]['data']['customer_id']
        warehouse_id = results[3]['data']['warehouse_id']

        # 2. 业务流程测试
        res = _test_stock_in(drug_id, supplier_id, warehouse_id)
        results.append(res)
        steps.append(f"5. 入库测试: {'成功' if res['success'] else '失败'}")
        
        # 库存盘点
        inventory = Inventory.query.filter_by(drug_id=drug_id, warehouse_id=warehouse_id).first()
        if inventory:
            check = InventoryCheck(
                drug_id=drug_id,
                warehouse_id=warehouse_id,
                checked_quantity=inventory.quantity,
                actual_quantity=inventory.quantity,
                diff_reason="全链路测试盘点",
                check_date=datetime.now().date(),
                employee_id=1
            )
            db.session.add(check)
            db.session.commit()
            steps.append("6. 库存盘点: 成功")
        
        # 退货一部分
        return_qty = 10
        if inventory and inventory.quantity >= return_qty:
            return_stock = ReturnStock(
                drug_id=drug_id,
                supplier_id=supplier_id,
                quantity=return_qty,
                reason="全链路测试退货",
                return_date=datetime.now().date(),
                employee_id=1
            )
            db.session.add(return_stock)
            inventory.quantity -= return_qty
            db.session.commit()
            steps.append(f"7. 退货{return_qty}个: 成功")
        
        # 销售一部分
        res = _test_sales(drug_id, customer_id, warehouse_id)
        results.append(res)
        steps.append(f"8. 销售测试: {'成功' if res['success'] else '失败'}")
        
        # 销售退货一部分
        if res['success']:
            sale_id = res['data']['sales_id']
            sale = Sales.query.get(sale_id)
            if sale:
                sales_return = SalesReturn(
                    sales_id=sale_id,
                    quantity=2,
                    reason="全链路测试销售退货",
                    return_date=datetime.now().date(),
                    employee_id=1
                )
                db.session.add(sales_return)
                inventory = Inventory.query.filter_by(drug_id=drug_id, warehouse_id=warehouse_id).first()
                if inventory:
                    inventory.quantity += 2
                db.session.commit()
                steps.append("9. 销售退货2个: 成功")
        
        # 财务统计
        res = _test_finance_stat()
        results.append(res)
        steps.append(f"10. 财务统计: {'成功' if res['success'] else '失败'}")
        
        log_info("========== 全链路测试结束 ==========")
        
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        
        # 获取最终数据状态
        inventory = Inventory.query.filter_by(drug_id=drug_id, warehouse_id=warehouse_id).first()
        
        return jsonify({
            'success': success_count == total_count,
            'message': f'全链路测试完成: {success_count}/{total_count} 通过',
            'steps': steps,
            'data': {
                'drug_name': drug_name,
                'initial_stock': 100, # 假设入库100
                'sold': 10, # 假设销售10
                'remaining': inventory.quantity if inventory else 0
            }
        })
    except Exception as e:
        return handle_error(e, "全链路测试")

@api_test_bp.route('/batch_stock_in', methods=['POST'])
def route_batch_stock_in():
    try:
        # 简单批量生成1条入库数据
        res = _test_stock_in()
        data = res.get_json() if hasattr(res, 'get_json') else res
        return jsonify({'success': data['success'], 'message': data['message']})
    except Exception as e:
        return handle_error(e, "批量入库测试")

@api_test_bp.route('/batch_sales', methods=['POST'])
def route_batch_sales():
    try:
        # 简单批量生成1条销售数据
        res = _test_sales()
        data = res.get_json() if hasattr(res, 'get_json') else res
        return jsonify({'success': data['success'], 'message': data['message']})
    except Exception as e:
        return handle_error(e, "批量销售测试")
