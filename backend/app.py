from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import models
import csv
from io import StringIO, BytesIO

app = Flask(__name__)
CORS(app)

@app.route('/classes', methods=['GET'])
def get_classes():
    return jsonify(models.get_all_classes())

@app.route('/classes/number/<int:class_number>', methods=['GET'])
def get_class_by_number(class_number):
    return jsonify(models.get_class_by_number(class_number))

@app.route('/classes/destination/<destination>', methods=['GET'])
def get_class_by_destination(destination):
    return jsonify(models.get_class_by_destination(destination))

@app.route('/classes', methods=['POST'])
def add_class():
    data = request.json
    models.add_class(data)
    return jsonify({'status': 'Class added'})

@app.route('/classes/<int:class_id>', methods=['DELETE'])
def delete_class(class_id):
    models.delete_class(class_id)
    return jsonify({'status': 'Class deleted'})

@app.route('/tickets/stats', methods=['GET'])
def get_ticket_stats():
    return jsonify(models.get_ticket_stats())

@app.route('/tickets/purchase', methods=['POST'])
def purchase_ticket():
    data = request.json
    # 兼容 seat_type 字段
    result = models.purchase_ticket_with_check(data['class_id'], data['user_name'], data.get('seat_type', 'window-front'))
    if result:
        return jsonify({'status': 'Ticket purchased'})
    else:
        return jsonify({'status': 'No tickets available'}), 400

@app.route('/tickets/refund/<int:ticket_id>', methods=['DELETE'])
def refund_ticket(ticket_id):
    # 获取身份，前端需传递身份参数，或通过请求头/参数传递
    role = request.args.get('role', 'user')
    # 查询票据对应班次出发时间
    from models import get_ticket_class_departure_time
    dep_time = get_ticket_class_departure_time(ticket_id)
    if role != 'admin' and dep_time:
        from datetime import datetime, timedelta
        now = datetime.now()
        # 兼容 dep_time 时区问题
        if isinstance(dep_time, str):
            try:
                dep_time = datetime.strptime(dep_time, '%Y-%m-%d %H:%M:%S')
            except Exception:
                pass
        if dep_time - now <= timedelta(hours=12):
            return jsonify({'status': '退票失败，发车前12小时内不可退票'}), 400
    models.refund_ticket(ticket_id)
    return jsonify({'status': 'Ticket refunded'})

@app.route('/tickets/export', methods=['GET'])
def export_tickets():
    user_name = request.args.get('user_name')
    if user_name:
        tickets = models.get_tickets_by_name(user_name)
    else:
        tickets = models.export_tickets()
    # 直接输出csv格式
    si = StringIO()
    if tickets:
        # 中文表头，增加座位类型
        fieldnames = ['票ID', '购票人', '座位类型', '购票时间', '班次号', '起点站', '终点站']
        writer = csv.DictWriter(si, fieldnames=fieldnames)
        writer.writeheader()
        for t in tickets:
            writer.writerow({
                '票ID': t.get('id'),
                '购票人': t.get('user_name'),
                '座位类型': t.get('seat_type'),
                '购票时间': t.get('purchase_time'),
                '班次号': t.get('class_number'),
                '起点站': t.get('route_start'),
                '终点站': t.get('route_end')
            })
    else:
        si.write('无数据')
    si.seek(0)
    # 兼容 Excel 中文，添加 BOM 头，并用 BytesIO 返回
    output = '\ufeff' + si.getvalue()
    mem = BytesIO(output.encode('utf-8-sig'))
    mem.seek(0)
    return send_file(
        mem,
        mimetype='text/csv',
        as_attachment=True,
        download_name='tickets.csv'
    )

@app.route('/classes/<int:class_id>', methods=['PUT'])
def update_class(class_id):
    data = request.json
    models.update_class(class_id, data)
    return jsonify({'status': 'Class updated'})

@app.route('/classes/import', methods=['POST'])
def import_classes():
    class_list = request.json.get('class_list', [])
    models.import_classes(class_list)
    return jsonify({'status': 'Classes imported', 'count': len(class_list)})

@app.route('/classes/import-csv', methods=['POST'])
def import_classes_csv():
    if 'file' not in request.files:
        return jsonify({'status': 'No file uploaded'}), 400
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({'status': 'Only CSV files allowed'}), 400
    content = file.stream.read().decode('utf-8-sig')  # 使用 utf-8-sig 解码，避免 BOM 头
    stream = StringIO(content)
    reader = csv.DictReader(stream)
    class_list = [row for row in reader]
    models.import_classes(class_list)
    return jsonify({'status': 'Classes imported', 'count': len(class_list)})

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if models.check_admin_login(username, password):
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'fail'}), 401

@app.route('/user/register', methods=['POST'])
def user_register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if models.register_user(username, password):
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'fail'}), 400

@app.route('/user/login', methods=['POST'])
def user_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if models.check_user_login(username, password):
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'fail'}), 401

@app.route('/tickets/class/<int:class_id>', methods=['GET'])
def get_tickets_by_class(class_id):
    return jsonify(models.get_tickets_by_class(class_id))

@app.route('/tickets/user/<user_name>', methods=['GET'])
def get_tickets_by_name(user_name):
    return jsonify(models.get_tickets_by_name(user_name))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
