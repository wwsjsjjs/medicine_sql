"""
API测试路由
提供测试数据生成、批量操作测试等功能
"""

from flask import Blueprint, jsonify, request, render_template
from models import db, DrugInfo, EmployeeInfo, CustomerInfo, SupplierInfo
from models import StockIn, Sales, Inventory, Warehouse
from datetime import datetime, timedelta
import random

api_test_bp = Blueprint('api_test', __name__, url_prefix='/api/test')


@api_test_bp.route('/')
def index():
    """测试控制台页面"""
    return render_template('testing/test_console.html')


@api_test_bp.route('/generate_drug', methods=['POST'])
def generate_drug():
    """生成测试药品数据"""
    try:
        count = request.json.get('count', 1)
        drugs = []
        
        drug_names = ['阿莫西林胶囊', '头孢克肟片', '布洛芬缓释胶囊', '感冒灵颗粒', '板蓝根颗粒']
        specs = ['0.25g*24粒', '10g*10袋', '0.3g*12粒', '100mg*30片']
        manufacturers = ['扬子江药业集团', '同仁堂集团', '三九医药', '华润医药']
        
        for i in range(count):
            drug = DrugInfo(
                name=f"{random.choice(drug_names)}_测试{i+1}",
                spec=random.choice(specs),
                manufacturer=random.choice(manufacturers),
                approval_number=f"国药准字Z{random.randint(20000000, 29999999)}",
                category='处方' if random.random() > 0.5 else '非处方',
                unit='盒',
                purchase_price=round(random.uniform(5, 50), 2),
                sale_price=round(random.uniform(10, 100), 2),
                expiry_date=datetime.now().date() + timedelta(days=365),
                status='在售'
            )
            db.session.add(drug)
            drugs.append(drug.name)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功生成 {count} 条药品数据',
            'data': drugs
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'生成失败: {str(e)}'
        }), 500


@api_test_bp.route('/generate_customer', methods=['POST'])
def generate_customer():
    """生成测试客户数据"""
    try:
        count = request.json.get('count', 1)
        customers = []
        
        names = ['华康医院', '同仁医院', '第一人民医院', '中医院', '康复中心']
        contacts = ['张三', '李四', '王五', '赵六']
        
        for i in range(count):
            customer = CustomerInfo(
                name=f"{random.choice(names)}_测试{i+1}",
                type='批发' if random.random() > 0.5 else '零售',
                contact=random.choice(contacts),
                phone=f"138{random.randint(10000000, 99999999)}",
                address=f"测试地址{i+1}"
            )
            db.session.add(customer)
            customers.append(customer.name)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功生成 {count} 条客户数据',
            'data': customers
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'生成失败: {str(e)}'
        }), 500


@api_test_bp.route('/batch_stock_in', methods=['POST'])
def batch_stock_in():
    """批量入库测试"""
    try:
        count = request.json.get('count', 10)
        
        # 获取所有药品、供应商、仓库
        drugs = DrugInfo.query.filter_by(status='在售').all()
        suppliers = SupplierInfo.query.all()
        warehouses = Warehouse.query.all()
        
        if not drugs or not suppliers or not warehouses:
            return jsonify({
                'success': False,
                'message': '缺少必要的基础数据（药品/供应商/仓库）'
            }), 400
        
        stock_ins = []
        
        for i in range(count):
            drug = random.choice(drugs)
            supplier = random.choice(suppliers)
            warehouse = random.choice(warehouses)
            quantity = random.randint(50, 500)
            unit_price = round(random.uniform(5, 100), 2)
            
            stock_in = StockIn(
                drug_id=drug.drug_id,
                supplier_id=supplier.supplier_id,
                warehouse_id=warehouse.warehouse_id,
                quantity=quantity,
                unit_price=unit_price,
                total_amount=quantity * unit_price,
                stock_in_date=datetime.now().date(),
                remark='批量测试入库'
            )
            db.session.add(stock_in)
            
            # 更新库存
            inventory = Inventory.query.filter_by(
                drug_id=drug.drug_id,
                warehouse_id=warehouse.warehouse_id
            ).first()
            
            if inventory:
                inventory.quantity += quantity
            else:
                inventory = Inventory(
                    drug_id=drug.drug_id,
                    warehouse_id=warehouse.warehouse_id,
                    quantity=quantity,
                    last_updated=datetime.now()
                )
                db.session.add(inventory)
            
            stock_ins.append(f"{drug.name} x {quantity}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功创建 {count} 条入库记录',
            'data': stock_ins[:10]  # 只返回前10条
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'批量入库失败: {str(e)}'
        }), 500


@api_test_bp.route('/batch_sales', methods=['POST'])
def batch_sales():
    """批量销售测试"""
    try:
        count = request.json.get('count', 10)
        
        # 获取有库存的药品和客户
        inventories = Inventory.query.filter(Inventory.quantity > 0).all()
        customers = CustomerInfo.query.all()
        
        if not inventories or not customers:
            return jsonify({
                'success': False,
                'message': '缺少必要的基础数据（库存/客户）'
            }), 400
        
        sales_list = []
        
        for i in range(count):
            inventory = random.choice(inventories)
            customer = random.choice(customers)
            
            # 随机销售数量（不超过库存）
            max_qty = min(inventory.quantity, 50)
            if max_qty <= 0:
                continue
                
            quantity = random.randint(1, max_qty)
            
            drug = DrugInfo.query.get(inventory.drug_id)
            
            sale = Sales(
                drug_id=drug.drug_id,
                customer_id=customer.customer_id,
                quantity=quantity,
                unit_price=drug.sale_price,
                total_amount=quantity * drug.sale_price,
                sales_date=datetime.now().date()
            )
            db.session.add(sale)
            
            # 扣减库存
            inventory.quantity -= quantity
            inventory.last_updated = datetime.now()
            
            sales_list.append(f"{drug.name} x {quantity}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功创建 {count} 条销售记录',
            'data': sales_list[:10]
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'批量销售失败: {str(e)}'
        }), 500


@api_test_bp.route('/full_chain_test', methods=['POST'])
def full_chain_test():
    """全链路测试：创建药品 -> 入库 -> 销售 -> 查看报表"""
    try:
        steps = []
        
        # 1. 创建测试药品
        drug = DrugInfo(
            name=f"全链路测试药品_{datetime.now().strftime('%H%M%S')}",
            spec='0.25g*24粒',
            manufacturer='测试厂家',
            approval_number=f"国药准字Z{random.randint(20000000, 29999999)}",
            category='处方',
            unit='盒',
            purchase_price=10.00,
            sale_price=20.00,
            expiry_date=datetime.now().date() + timedelta(days=365),
            status='在售'
        )
        db.session.add(drug)
        db.session.flush()
        steps.append(f"✓ 创建药品: {drug.name}")
        
        # 2. 获取或创建供应商和仓库
        supplier = SupplierInfo.query.first()
        if not supplier:
            supplier = SupplierInfo(
                name='测试供应商',
                contact='张三',
                phone='13800138000',
                address='测试地址'
            )
            db.session.add(supplier)
            db.session.flush()
        steps.append(f"✓ 使用供应商: {supplier.name}")
        
        warehouse = Warehouse.query.first()
        if not warehouse:
            warehouse = Warehouse(
                name='测试仓库',
                address='测试地址',
                capacity=10000
            )
            db.session.add(warehouse)
            db.session.flush()
        steps.append(f"✓ 使用仓库: {warehouse.name}")
        
        # 3. 创建入库记录
        quantity = 100
        stock_in = StockIn(
            drug_id=drug.drug_id,
            supplier_id=supplier.supplier_id,
            warehouse_id=warehouse.warehouse_id,
            quantity=quantity,
            unit_price=10.00,
            total_amount=1000.00,
            stock_in_date=datetime.now().date(),
            remark='全链路测试入库'
        )
        db.session.add(stock_in)
        
        # 4. 更新库存
        inventory = Inventory(
            drug_id=drug.drug_id,
            warehouse_id=warehouse.warehouse_id,
            quantity=quantity,
            last_updated=datetime.now()
        )
        db.session.add(inventory)
        steps.append(f"✓ 入库成功: {quantity} 盒")
        
        # 5. 获取或创建客户
        customer = CustomerInfo.query.first()
        if not customer:
            customer = CustomerInfo(
                name='测试客户',
                type='零售',
                contact='李四',
                phone='13900139000',
                address='测试地址'
            )
            db.session.add(customer)
            db.session.flush()
        steps.append(f"✓ 使用客户: {customer.name}")
        
        # 6. 创建销售记录
        sale_quantity = 10
        sale = Sales(
            drug_id=drug.drug_id,
            customer_id=customer.customer_id,
            quantity=sale_quantity,
            unit_price=20.00,
            total_amount=200.00,
            sales_date=datetime.now().date()
        )
        db.session.add(sale)
        
        # 7. 扣减库存
        inventory.quantity -= sale_quantity
        inventory.last_updated = datetime.now()
        steps.append(f"✓ 销售成功: {sale_quantity} 盒，剩余库存: {inventory.quantity}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '全链路测试完成',
            'steps': steps,
            'data': {
                'drug_id': drug.drug_id,
                'drug_name': drug.name,
                'initial_stock': quantity,
                'sold': sale_quantity,
                'remaining': inventory.quantity
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'全链路测试失败: {str(e)}',
            'steps': steps
        }), 500


@api_test_bp.route('/stats', methods=['GET'])
def get_stats():
    """获取系统统计信息"""
    try:
        stats = {
            'drugs': DrugInfo.query.count(),
            'employees': EmployeeInfo.query.count(),
            'customers': CustomerInfo.query.count(),
            'suppliers': SupplierInfo.query.count(),
            'warehouses': Warehouse.query.count(),
            'stock_ins': StockIn.query.count(),
            'sales': Sales.query.count(),
            'total_inventory': db.session.query(db.func.sum(Inventory.quantity)).scalar() or 0
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计信息失败: {str(e)}'
        }), 500
