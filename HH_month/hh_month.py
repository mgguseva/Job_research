import requests
import time
import json
from datetime import datetime, timedelta

# специализация "Информационные технологии, интернет, телеком"
IT = 1
# специализация "Искусство, развлечения, масс-медиа"
MEDIA = 11
# специализация "Безопасность"
SECURITY = 8
# специализация "Государственная служба, некоммерческие организации"
PUBLIC_SERVICE = 16

# место поиска (Россия)
AREA = 113

# список всех вакансий
vacancies = []

# cобираем данные с 5 мая 2022 года (API выдает данные только за 30 дней),
# итерируясь по 1 часу из-за ограничения на количество данных по 2000 записей за запрос

START_TIME = datetime(year=2022, month=5, day=5)
END_TIME = datetime(year=2022, month=6, day=4)


def get_page(modifiedFrom: datetime):
    """
    Создаем метод для получения страницы со списком вакансий.
    Аргументы:
        page - Индекс страницы, начинается с 0. Значение по умолчанию 0, т.е. первая страница
    """
    modifiedTo = modifiedFrom + timedelta(hours=1)
    publications = []
    page = 0
    while True:
        # Справочник для параметров GET-запроса
        params = {
            'specialization':  PUBLIC_SERVICE,  # специализация
            'area': AREA,  # место
            'page': page,  # Индекс страницы поиска на HH
            'per_page': 100,  # Кол-во вакансий на 1 странице
            'date_from': f"{modifiedFrom.strftime('%Y-%m-%d')}T{modifiedFrom.strftime('%X')}",
            'date_to': f"{modifiedTo.strftime('%Y-%m-%d')}T{modifiedTo.strftime('%X')}"
        }

        req = requests.get('https://api.hh.ru/vacancies', params) # Посылаем запрос к API
        if not req.ok:
            raise Exception(f"Error! Got status code: {req.status_code}")
        elif req.json()["found"] == 0 or req.json()["found"] == len(publications):
            break
        else:
            items = req.json()['items']
            publications += items
            time.sleep(0.25)
            page += 1
    return publications


if __name__ == '__main__':
    while START_TIME < END_TIME:
        try:
            vacancies += get_page(START_TIME)
        except Exception as e:
            print(e)
            with open('backup.json', 'w') as file:
                json.dump(vacancies, file)
                break
        START_TIME += timedelta(hours=1)
        print(START_TIME)
    with open('hh_PUBLIC_SERVICE_month.json', 'w') as file:
        json.dump(vacancies, file)

