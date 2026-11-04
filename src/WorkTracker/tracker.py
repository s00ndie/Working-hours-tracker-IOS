from datetime import datetime, timedelta
import sqlite3


class WorkTracker:

  def __init__(self, db_name='work_tracker.db'):
    self.db_name = db_name
    self.init_db()

  def connect(self):
    conn = sqlite3.connect(self.db_name)
    conn.row_factory = sqlite3.Row
    return conn

  def init_db(self):
    """Створює таблицю в базі даних, якщо її ще немає"""
    conn = self.connect()
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                total_hours REAL NOT NULL
            )
        ''')
    conn.commit()
    conn.close()

  @staticmethod
  def normalize_date(date_str):
    """Повертає дату в ISO форматі YYYY-MM-DD з різних вхідних форматів."""
    for fmt in ('%d-%m-%Y', '%Y-%m-%d'):
      try:
        return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
      except ValueError:
        pass
    raise ValueError('Ongeldige datumnotatie. Gebruik DD-MM-YYYY of YYYY-MM-DD.')

  @staticmethod
  def display_date(date_str):
    """Повертає дату в читабельному форматі DD-MM-YYYY."""
    try:
      return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d-%m-%Y')
    except ValueError:
      return date_str

  def add_record(self, date_str, start_time_str, end_time_str):
    """Додає новий робочий день і рахує відпрацьовані години"""
    date_iso = self.normalize_date(date_str)
    t1 = datetime.strptime(start_time_str, '%H:%M')
    t2 = datetime.strptime(end_time_str, '%H:%M')

    # Якщо час закінчення менший за початок, це означає роботу через північ.
    if t2 < t1:
      t2 += timedelta(days=1)

    # Рахуємо різницю у годинах
    diff = t2 - t1
    total_hours = round(diff.total_seconds() / 3600, 2)

    if total_hours < 0:
      total_hours = 0

    conn = self.connect()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO work_logs (date, start_time, end_time, total_hours) '
        'VALUES (?, ?, ?, ?)',
        (date_iso, start_time_str, end_time_str, total_hours),
    )
    conn.commit()
    conn.close()
    return total_hours

  def get_all_records(self):
    """Повертає всі записи, відсортовані від найсвіжіших"""
    conn = self.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM work_logs ORDER BY date DESC, id DESC')
    records = []
    for row in cursor.fetchall():
      rec = dict(row)
      rec['date'] = self.display_date(rec['date'])
      records.append(rec)
    conn.close()
    return records

  def get_monthly_stats(self, year_month):
    """Рахує лічильники за місяць (формат 'YYYY-MM', наприклад '2026-11')"""
    conn = self.connect()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT COUNT(*), SUM(total_hours) FROM work_logs WHERE date LIKE ?',
        (f'{year_month}%',),
    )
    result = cursor.fetchone()
    conn.close()

    total_days = result[0] if result and result[0] else 0
    total_hours = round(result[1], 2) if result and result[1] else 0.0

    return {'total_days': total_days, 'total_hours': total_hours}


# --- ТЕСТУВАННЯ ЛОГІКИ (можна запустити у терміналі) ---
if __name__ == '__main__':
  tracker = WorkTracker()
  start_time_str = input('Hoe laat begon je te werken? (HH:MM) ')
  end_time_str = input('Hoe laat eindigde je met werken? (HH:MM) ')
  date_str = input('Voer de datum van het record in (DD-MM-YYYY) of laat leeg voor vandaag: ')

  if not date_str:
    date_str = datetime.now().strftime('%d-%m-%Y')

  current_month = datetime.strptime(tracker.normalize_date(date_str), '%Y-%m-%d').strftime('%Y-%m')

  print('Додаємо новий запис...')
  tracker.add_record(date_str=date_str, start_time_str=start_time_str, end_time_str=end_time_str)

  # Виведемо всі записи
  print('\nІсторія записів:')
  for rec in tracker.get_all_records():
    print(
        f"Datum: {rec['date']} | {rec['start_time']} - {rec['end_time']}"
        f" | Gewerkt: {rec['total_hours']} uuren"
    )

  # Виведемо статистику за місяць
  stats = tracker.get_monthly_stats(current_month)
  print(
      f"\nStatistieken voor {current_month}:"
      f" \n- Dagen gewerkt: {stats['total_days']} \n- Uuren gewerkt:"
      f" {stats['total_hours']} uuren"
  )