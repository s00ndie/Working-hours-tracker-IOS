from datetime import datetime
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

# Імпортуємо твій клас бекенду
from .tracker import WorkTracker


class WorkTrackerApp(toga.App):

  def startup(self):
    self.tracker = WorkTracker()

    # Головний контейнер
    main_box = toga.Box(style=Pack(direction=COLUMN, padding=15))

    # --- ЕЛЕМЕНТИ ФОРМИ ---
    # Поле дати
    self.date_input = toga.TextInput(
        value=datetime.now().strftime('%d-%m-%Y'), style=Pack(padding=5)
    )

    # Поля часу
    self.start_input = toga.TextInput(
        placeholder='Start (09:00)', style=Pack(padding=5)
    )
    self.end_input = toga.TextInput(
        placeholder='Einde (18:00)', style=Pack(padding=5)
    )

    # Кнопка збереження
    save_btn = toga.Button(
        'Bewaar dag',
        on_press=self.save_record_handler,
        style=Pack(padding=5, background_color='#007aff'),
    )

    # Лічильники за місяць (статистика)
    self.stats_label = toga.Label(
        'Maandstatistiek...', style=Pack(padding=10, font_weight='bold')
    )

    # Таблиця / Список історії
    self.table = toga.Table(
        headings=['Datum', 'Tijd', 'Uren'],
        data=[],
        style=Pack(flex=1, padding=5),
    )

    # Додаємо все у головний контейнер
    main_box.add(toga.Label('Datum (DD-MM-JJJJ):'))
    main_box.add(self.date_input)
    main_box.add(toga.Label('Start- en eindtijd:'))

    time_box = toga.Box(style=Pack(direction=ROW))
    time_box.add(self.start_input)
    time_box.add(self.end_input)
    main_box.add(time_box)

    main_box.add(save_btn)
    main_box.add(self.stats_label)
    main_box.add(self.table)

    # Оновлюємо дані при старті
    self.update_ui_data()

    self.main_window = toga.MainWindow(title=self.formal_name)
    self.main_window.content = main_box
    self.main_window.show()

  def update_ui_data(self):
    # Оновлюємо таблицю
    records = self.tracker.get_all_records()
    table_data = []
    for r in records:
      table_data.append(
          (r['date'], f"{r['start_time']}-{r['end_time']}", str(r['total_hours']))
      )
    self.table.data = table_data

    current_month = datetime.now().strftime('%Y-%m')
    stats = self.tracker.get_monthly_stats(current_month)
    self.stats_label.text = (
        f"Dagen: {stats['total_days']} | Uren: {stats['total_hours']}"
    )

  def save_record_handler(self, widget):
    date_str = self.date_input.value
    start_str = self.start_input.value
    end_str = self.end_input.value

    if not start_str or not end_str:
      return

    try:
      self.tracker.add_record(date_str, start_str, end_str)
      # Очищаємо поля часу
      self.start_input.value = ''
      self.end_input.value = ''
      # Оновлюємо інтерфейс
      self.update_ui_data()
    except Exception as e:
      print(f'Fout: {e}')


def main():
  return WorkTrackerApp('Work Tracker', 'com.bohdan.worktracker')