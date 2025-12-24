// 测试数据生成器
const TestDataGenerator = {
    // 随机地址列表
    addresses: [
        '北京市朝阳区建国路88号',
        '上海市浦东新区世纪大道1000号',
        '广州市天河区天河路123号',
        '深圳市南山区科技园南区',
        '杭州市西湖区文三路456号',
        '成都市武侯区人民南路789号',
        '南京市鼓楼区中山路321号',
        '武汉市洪山区珞喻路654号',
        '西安市雁塔区小寨东路147号',
        '重庆市渝中区解放碑步行街'
    ],

    // 随机电话号码列表
    phones: [
        '13800138001', '13800138002', '13800138003', '13800138004', '13800138005',
        '13900139001', '13900139002', '13900139003', '13900139004', '13900139005',
        '15800158001', '15800158002', '15800158003', '15800158004', '15800158005',
        '18600186001', '18600186002', '18600186003', '18600186004', '18600186005'
    ],

    // 随机姓名列表
    names: [
        '张三', '李四', '王五', '赵六', '钱七',
        '孙八', '周九', '吴十', '郑一', '陈二',
        '刘明', '黄亮', '杨强', '林伟', '朱华'
    ],

    // 随机公司名称
    companies: [
        '华康医药有限公司', '康源药业集团', '健民制药厂',
        '同仁堂医药连锁', '九州大药房', '国药集团',
        '扬子江药业', '三九医药', '华润医药', '仁和药业'
    ],

    // 随机药品名称
    drugNames: [
        '阿莫西林胶囊', '头孢克肟片', '布洛芬缓释胶囊',
        '感冒灵颗粒', '板蓝根颗粒', '维生素C片',
        '阿司匹林肠溶片', '复方甘草片', '藿香正气水',
        '双黄连口服液', '急支糖浆', '三九感冒灵'
    ],

    // 随机规格
    specs: [
        '0.25g*24粒', '10g*10袋', '0.3g*12粒',
        '100mg*30片', '50mg*12片', '10ml*10支',
        '3g*10袋', '120ml', '100片'
    ],

    // 随机生产厂家
    manufacturers: [
        '扬子江药业集团', '同仁堂集团', '三九医药',
        '999医药', '华润医药', '石药集团',
        '齐鲁制药', '恒瑞医药', '天士力'
    ],

    // 获取随机项
    getRandom: function(arr) {
        return arr[Math.floor(Math.random() * arr.length)];
    },

    // 生成随机价格
    randomPrice: function(min, max) {
        return (Math.random() * (max - min) + min).toFixed(2);
    },

    // 生成随机数量
    randomQuantity: function(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    },

    // 生成随机日期（返回yyyy-MM-dd）
    randomDate: function(startOffsetDays, endOffsetDays) {
        const now = new Date();
        const min = startOffsetDays || 0;
        const max = endOffsetDays || 365;
        const offset = Math.floor(Math.random() * (max - min + 1)) + min;
        const d = new Date(now.getTime() + offset * 24 * 60 * 60 * 1000);
        const yyyy = d.getFullYear();
        const mm = String(d.getMonth() + 1).padStart(2, '0');
        const dd = String(d.getDate()).padStart(2, '0');
        return `${yyyy}-${mm}-${dd}`;
    },

    // 快速填充表单
    fillForm: function(formType) {
        switch(formType) {
            case 'drug':
                return {
                    name: this.getRandom(this.drugNames),
                    spec: this.getRandom(this.specs),
                    manufacturer: this.getRandom(this.manufacturers),
                    approval_number: '国药准字Z' + Math.floor(Math.random() * 1000000),
                    unit: '盒',
                    purchase_price: this.randomPrice(5, 50),
                    sale_price: this.randomPrice(10, 100),
                    // 保质期：6-24 个月随机
                    shelf_life_months: this.randomQuantity(6, 24)
                };
            
            case 'employee':
                return {
                    name: this.getRandom(this.names),
                    phone: this.getRandom(this.phones),
                    account: 'user' + Math.floor(Math.random() * 1000),
                    password: '123456',
                    department: null, // 让下拉随机
                    role_id: null      // 让下拉随机
                };
            
            case 'customer':
                return {
                    name: this.getRandom(this.companies),
                    contact: this.getRandom(this.names),
                    phone: this.getRandom(this.phones),
                    address: this.getRandom(this.addresses)
                };
            
            case 'supplier':
                return {
                    name: this.getRandom(this.companies),
                    contact: this.getRandom(this.names),
                    phone: this.getRandom(this.phones),
                    address: this.getRandom(this.addresses),
                    qualification_no: 'YL' + Math.floor(Math.random() * 100000)
                };
            
            case 'warehouse':
                return {
                    name: this.getRandom(['主仓库', '分仓库', '冷链仓库', '中药仓库']),
                    address: this.getRandom(this.addresses)
                };
            
            case 'stock_in':
                return {
                    drug_id: null,          // 下拉随机
                    supplier_id: null,      // 下拉随机
                    warehouse_id: null,     // 下拉随机
                    quantity: this.randomQuantity(50, 500),
                    stock_in_date: this.randomDate(-3, 0),
                    remark: '测试入库'
                };
            
            case 'sales':
                return {
                    drug_id: null,      // 下拉随机
                    customer_id: null,  // 下拉随机
                    quantity: this.randomQuantity(1, 50),
                    sales_date: this.randomDate(-3, 0)
                };
        }
    }
};

// 表单快速填充功能
function quickFill(formType) {
    const data = TestDataGenerator.fillForm(formType);
    
    for (let key in data) {
        // 优先匹配下拉框，随机选项或指定值
        const selectEl = document.querySelector(`select[name="${key}"]`);
        if (selectEl) {
            // 如果 data 中有明确值，用该值；否则随机选可选项（跳过空选）
            if (data[key]) {
                selectEl.value = data[key];
            } else {
                const options = Array.from(selectEl.options).filter(o => o.value);
                if (options.length > 0) {
                    const rand = options[Math.floor(Math.random() * options.length)].value;
                    selectEl.value = rand;
                }
            }
            selectEl.dispatchEvent(new Event('change'));
            continue;
        }

        const input = document.querySelector(`[name="${key}"]`);
        if (input) {
            input.value = data[key];
            input.dispatchEvent(new Event('change'));
            input.dispatchEvent(new Event('input'));
        }
    }
    
    // 显示提示
    showNotification('已自动填充测试数据', 'success');
}

// 通知提示
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#48bb78' : '#4299e1'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 输入验证辅助函数
const Validators = {
    // 电话号码验证
    phone: function(value) {
        const pattern = /^1[3-9]\d{9}$/;
        return pattern.test(value);
    },

    // 邮箱验证
    email: function(value) {
        const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return pattern.test(value);
    },

    // 价格验证
    price: function(value) {
        const num = parseFloat(value);
        return !isNaN(num) && num >= 0;
    },

    // 数量验证
    quantity: function(value) {
        const num = parseInt(value);
        return !isNaN(num) && num > 0;
    }
};

// 为表单添加实时验证
function addFormValidation() {
    // 电话号码验证
    document.querySelectorAll('input[name="phone"]').forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && !Validators.phone(this.value)) {
                this.style.borderColor = '#f56565';
                showNotification('请输入正确的手机号码格式', 'error');
            } else {
                this.style.borderColor = '#e2e8f0';
            }
        });
    });

    // 价格验证
    document.querySelectorAll('input[name*="price"]').forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && !Validators.price(this.value)) {
                this.style.borderColor = '#f56565';
                showNotification('请输入正确的价格', 'error');
            } else {
                this.style.borderColor = '#e2e8f0';
            }
        });
    });

    // 数量验证
    document.querySelectorAll('input[name="quantity"]').forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && !Validators.quantity(this.value)) {
                this.style.borderColor = '#f56565';
                showNotification('请输入正确的数量（正整数）', 'error');
            } else {
                this.style.borderColor = '#e2e8f0';
            }
        });
    });
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addFormValidation);
} else {
    addFormValidation();
}
