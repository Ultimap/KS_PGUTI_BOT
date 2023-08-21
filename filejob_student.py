from datetime import datetime
from parse_student import parse_student
import pytz

weekday = ['Понедельник', 'Вторник', "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]


def now_day():
    return datetime.today().now(pytz.timezone('Europe/Samara')).weekday()


def get_table(url, name):
    parse_student(url, name)
    file = open(f'table/{name}.txt', encoding='utf-8')
    content = file.read()
    file.close()
    file_clear = ['[', ']', '\'', '\\t', '\\r', '\\n', '\\n ', ' \\n', 'None', ',']
    for x in file_clear:
        content = content.replace(x, '')
    content = content.replace('Кабинет:', '\n🏢 Аудитория:')
    content = content.replace('неделя', 'неделя\n')
    content = content.replace('ентерпослекабинета', '\n')
    content = content.replace('ентерпередзначкомпрепода', '\n')
    content = content.replace(' 🕒', '\n🕒')
    content = content.replace('🎓 ', '🎓')
    content = content.replace('1 08:00', '🕒 08:00')
    content = content.replace('Онлайн подключение', '👨‍💻 Онлайн подключение\n🎓')
    content = content.replace('🎓👨‍💻 Онлайн подключение', '👨‍💻 Онлайн подключение')
    content = content.replace('09:30 ', '09:30\n🎓')
    return content


def send_all_week(url, name):
    content = get_table(url, name)
    govnocab = ['Понедельник', 'Вторник', "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    normcab = ['\n📅 Понедельник', '\n📅 Вторник', '\n📅 Среда', '\n📅 Четверг', '\n📅 Пятница', '\n📅 Суббота',
               '\n📅 Воскресенье']

    for x, y in zip(govnocab, normcab):
        content = content.replace(x, y)
    return content


def get_week_day(now):
    return weekday[now]


def send_this_day(url, name):
    content = get_table(url, name)
    if content.find(get_week_day(now_day())) == -1:
        return 'Выходной'
    first_symbol = content.find(get_week_day(now_day()))
    try:
        last_symbol = content.find(get_week_day(now_day() + 1))
        return '\n📅 ' + content[first_symbol:last_symbol]
    except:
        return "Выходной"


def send_next_day(url, name):
    content = get_table(url, name)
    now = now_day()
    if now == 6:
        now = -1
    if content.find(get_week_day(now + 1)) == -1:
        return 'Выходной'
    first_symbol = content.find(get_week_day(now + 1))
    try:
        last_symbol = content.find(get_week_day(now + 2))
        if content.find(get_week_day(now + 2)) == -1:
            step = 2
            while True:
                last_symbol = content.find(get_week_day(now + step+1))
                step += 1
                if last_symbol != -1:
                    break
        return '\n📅 ' + content[first_symbol:last_symbol]
    except:
        return '\n📅 ' + content[first_symbol:]

