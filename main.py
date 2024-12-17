from flask import Flask, request, jsonify, send_file
import mysql.connector
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta

app = Flask(__name__)

# Подключение к базе данных
def get_db_connection():
    return mysql.connector.connect(
        host="sql7.freesqldatabase.com",
        user="sql7752598",
        password="4adxPLpy5I",
        database="sql7752598",
        port=3306
    )

# Получение расписания на день
@app.route('/schedule/day', methods=['GET'])
def get_day_schedule():
    group_id = request.args.get('group_id')
    teacher_id = request.args.get('teacher_id')
    room_id = request.args.get('room_id')
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))

    query = """
    SELECT 
        l.id, 
        s.SubjectName, 
        g.group_name, 
        t.Name, 
        r.RoomNumber, 
        l.day, 
        lt.lesson_type
    FROM Lesson l
    JOIN Subjects s ON l.SubjectID = s.id
    JOIN Groups g ON l.GroupID = g.id
    JOIN Teachers t ON l.TeacherID = t.id
    JOIN Rooms r ON l.RoomID = r.id
    LEFT JOIN Lesson_Type lt ON l.lesson_type = lt.id
    JOIN Day d ON l.day = d.id
    WHERE d.day_date = %s
    """

    # Добавление фильтрации по группе, преподавателю или кабинету
    filters = []
    params = [date]
    if group_id:
        filters.append("l.GroupID = %s")
        params.append(group_id)
    if teacher_id:
        filters.append("l.TeacherID = %s")
        params.append(teacher_id)
    if room_id:
        filters.append("l.RoomID = %s")
        params.append(room_id)

    if filters:
        query += " AND " + " AND ".join(filters)

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, params)
    lessons = cursor.fetchall()
    cursor.close()
    connection.close()

    return jsonify(lessons)

# Получение расписания на неделю
@app.route('/schedule/week', methods=['GET'])
def get_week_schedule():
    group_id = request.args.get('group_id')
    teacher_id = request.args.get('teacher_id')
    room_id = request.args.get('room_id')
    start_date = request.args.get('start_date', datetime.now().strftime('%Y-%m-%d'))

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = start_date + timedelta(days=6)  # неделя — 7 дней

    query = """
    SELECT 
        l.id, 
        s.SubjectName, 
        g.group_name, 
        t.Name, 
        r.RoomNumber, 
        d.day_date, 
        lt.lesson_type
    FROM Lesson l
    JOIN Subjects s ON l.SubjectID = s.id
    JOIN Groups g ON l.GroupID = g.id
    JOIN Teachers t ON l.TeacherID = t.id
    JOIN Rooms r ON l.RoomID = r.id
    LEFT JOIN Lesson_Type lt ON l.lesson_type = lt.id
    JOIN Day d ON l.day = d.id
    WHERE d.day_date BETWEEN %s AND %s
    """

    # Добавление фильтрации
    filters = []
    params = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
    if group_id:
        filters.append("l.GroupID = %s")
        params.append(group_id)
    if teacher_id:
        filters.append("l.TeacherID = %s")
        params.append(teacher_id)
    if room_id:
        filters.append("l.RoomID = %s")
        params.append(room_id)

    if filters:
        query += " AND " + " AND ".join(filters)

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, params)
    lessons = cursor.fetchall()
    cursor.close()
    connection.close()

    return jsonify(lessons)

# Экспорт расписания в CSV
@app.route('/schedule/export', methods=['GET'])
def export_schedule():
    group_id = request.args.get('group_id')
    teacher_id = request.args.get('teacher_id')
    room_id = request.args.get('room_id')
    start_date = request.args.get('start_date', datetime.now().strftime('%Y-%m-%d'))

    # Формируем расписание (например, за неделю)
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = start_date + timedelta(days=6)

    query = """
    SELECT 
        l.id, 
        s.SubjectName, 
        g.group_name, 
        t.Name, 
        r.RoomNumber, 
        d.day_date, 
        lt.lesson_type
    FROM Lesson l
    JOIN Subjects s ON l.SubjectID = s.id
    JOIN Groups g ON l.GroupID = g.id
    JOIN Teachers t ON l.TeacherID = t.id
    JOIN Rooms r ON l.RoomID = r.id
    LEFT JOIN Lesson_Type lt ON l.lesson_type = lt.id
    JOIN Day d ON l.day = d.id
    WHERE d.day_date BETWEEN %s AND %s
    """

    filters = []
    params = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
    if group_id:
        filters.append("l.GroupID = %s")
        params.append(group_id)
    if teacher_id:
        filters.append("l.TeacherID = %s")
        params.append(teacher_id)
    if room_id:
        filters.append("l.RoomID = %s")
        params.append(room_id)

    if filters:
        query += " AND " + " AND ".join(filters)

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, params)
    lessons = cursor.fetchall()
    cursor.close()
    connection.close()

    # Экспорт в CSV
    df = pd.DataFrame(lessons)
    csv_output = StringIO()
    df.to_csv(csv_output, index=False)
    csv_output.seek(0)

    return send_file(csv_output, mimetype='text/csv', as_attachment=True, download_name='schedule.csv')

if __name__ == '__main__':
    app.run(debug=True)