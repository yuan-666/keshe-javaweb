from db_config import get_db_connection

def get_all_classes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM class_info")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_class_by_number(class_number):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM class_info WHERE class_number = %s", (class_number,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def get_class_by_destination(destination):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM class_info WHERE route_end = %s", (destination,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def add_class(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO class_info (class_number, departure_time, route_start, route_end, travel_time, capacity)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data['class_number'], data['departure_time'], data['route_start'],
        data['route_end'], data['travel_time'], data['capacity']
    ))
    conn.commit()
    cursor.close()
    conn.close()

def delete_class(class_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM class_info WHERE id = %s", (class_id,))
    conn.commit()
    cursor.close()
    conn.close()

def get_ticket_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.class_number, c.route_start, c.route_end, COUNT(t.id) AS tickets_sold
        FROM class_info c
        LEFT JOIN ticket_info t ON c.id = t.class_id
        GROUP BY c.id
    """)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def update_class(class_id, data):
    from datetime import datetime
    conn = get_db_connection()
    cursor = conn.cursor()
    # departure_time 兼容各种格式，转为 %Y-%m-%d %H:%M:%S
    dep = data['departure_time']
    try:
        # 支持 'Tue, 01 Jul 2025' 这种格式
        if len(dep) <= 20 and ',' in dep:
            dep = datetime.strptime(dep, '%a, %d %b %Y').strftime('%Y-%m-%d 00:00:00')
        elif 'T' in dep:
            # 兼容 '2025-07-01T08:00' 前端 date-picker
            dep = dep.replace('T', ' ') + ':00' if len(dep) == 16 else dep.replace('T', ' ')
        elif len(dep) == 10:
            dep = dep + ' 00:00:00'
    except Exception:
        pass
    cursor.execute('''
        UPDATE class_info SET class_number=%s, departure_time=%s, route_start=%s, route_end=%s, travel_time=%s, capacity=%s
        WHERE id=%s
    ''', (
        data['class_number'], dep, data['route_start'],
        data['route_end'], data['travel_time'], data['capacity'], class_id
    ))
    conn.commit()
    cursor.close()
    conn.close()

# 批量导入班次信息，class_list为list of dict
def import_classes(class_list):
    conn = get_db_connection()
    cursor = conn.cursor()
    for data in class_list:
        # 只导入班次信息，不导入票据或用户信息
        class_number = data.get('class_number') or data.get('班次号') or ''
        departure_time = data.get('departure_time') or data.get('出发时间') or ''
        route_start = data.get('route_start') or data.get('起点站') or ''
        route_end = data.get('route_end') or data.get('终点站') or ''
        travel_time = data.get('travel_time') or data.get('行车时间') or ''
        capacity = data.get('capacity') or data.get('额定载客量') or ''
        # 针对导出csv的情况，尝试从 purchase_time、user_name 等字段推断出班次信息
        if not (class_number and route_start and route_end):
            continue  # 跳过不完整行
        # 如果没有 departure_time、travel_time、capacity，给默认值
        if not departure_time:
            departure_time = '2025-01-01 00:00:00'
        if not travel_time:
            travel_time = 60
        if not capacity:
            capacity = 100
        # class_number 统一转为字符串，避免数据库类型冲突
        class_number = str(class_number)
        # 检查班次是否已存在，避免重复导入
        cursor.execute('SELECT COUNT(*) FROM class_info WHERE class_number=%s AND route_start=%s AND route_end=%s', (class_number, route_start, route_end))
        exists = cursor.fetchone()[0]
        if exists:
            continue
        cursor.execute('''
            INSERT INTO class_info (class_number, departure_time, route_start, route_end, travel_time, capacity)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            class_number, departure_time, route_start,
            route_end, travel_time, capacity
        ))
    conn.commit()
    cursor.close()
    conn.close()

# 购票时校验余票
def purchase_ticket_with_check(class_id, user_name, seat_type):
    conn = get_db_connection()
    try:
        conn.start_transaction()
        cursor = conn.cursor(dictionary=True)
        # 检查余票并加锁（如需按座位类型统计可扩展）
        cursor.execute("SELECT capacity, (SELECT COUNT(*) FROM ticket_info WHERE class_id=%s) AS sold FROM class_info WHERE id=%s FOR UPDATE", (class_id, class_id))
        row = cursor.fetchone()
        # 检查单人是否已购票
        cursor.execute("SELECT COUNT(*) AS cnt FROM ticket_info WHERE class_id=%s AND user_name=%s FOR UPDATE", (class_id, user_name))
        already = cursor.fetchone()['cnt']
        if row and row['sold'] < row['capacity'] and already == 0:
            cursor.execute("INSERT INTO ticket_info (class_id, user_name, seat_type) VALUES (%s, %s, %s)", (class_id, user_name, seat_type))
            conn.commit()
            result = True
        else:
            conn.rollback()
            result = False
        cursor.close()
    except Exception:
        conn.rollback()
        result = False
    finally:
        conn.close()
    return result

def purchase_ticket(class_id, user_name, seat_type):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ticket_info (class_id, user_name, seat_type) VALUES (%s, %s, %s)", (class_id, user_name, seat_type))
    conn.commit()
    cursor.close()
    conn.close()

def refund_ticket(ticket_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ticket_info WHERE id = %s", (ticket_id,))
    conn.commit()
    cursor.close()
    conn.close()

def export_tickets():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.id, t.user_name, t.seat_type, t.purchase_time, c.class_number, c.route_start, c.route_end
        FROM ticket_info t
        JOIN class_info c ON t.class_id = c.id
    """)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def check_admin_login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admin_user WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user is not None

def check_user_login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user is not None

def register_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        result = True
    except Exception:
        result = False
    cursor.close()
    conn.close()
    return result

def get_tickets_by_class(class_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT t.id, t.user_name, t.seat_type, t.purchase_time, t.class_id, c.class_number, c.route_start, c.route_end
        FROM ticket_info t
        JOIN class_info c ON t.class_id = c.id
        WHERE t.class_id = %s
        ORDER BY t.purchase_time DESC
    ''', (class_id,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_tickets_by_name(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT t.id, t.user_name, t.seat_type, t.purchase_time, t.class_id, c.class_number, c.route_start, c.route_end
        FROM ticket_info t
        JOIN class_info c ON t.class_id = c.id
        WHERE t.user_name = %s
        ORDER BY t.purchase_time DESC
    ''', (name,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_ticket_class_departure_time(ticket_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT c.departure_time FROM ticket_info t
        JOIN class_info c ON t.class_id = c.id
        WHERE t.id = %s
    ''', (ticket_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row and row['departure_time']:
        from datetime import datetime
        # 兼容数据库返回 datetime 或字符串
        dep_time = row['departure_time']
        if isinstance(dep_time, str):
            try:
                return datetime.strptime(dep_time, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    return datetime.strptime(dep_time, '%Y-%m-%dT%H:%M')
                except ValueError:
                    return None
        else:
            return dep_time
    return None
