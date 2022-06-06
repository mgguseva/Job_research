import requests
import json
import time
import math
from datetime import datetime, timedelta
from tqdm import tqdm

# cобираем данные с 5 мая 2022 года (по дате раньше API не выдает данные),
# итерируясь по 1 часу из-за ограничения на количество данных по 10000 записей за запрос

start_time = datetime(year=2022, month=5, day=5)
end_time = datetime(year=2022, month=6, day=4)
vacancies = []

"""Функция, которая записывает в vacancies полученные данные по запросу к API "Работа России"""

def getDay(modifiedFrom: datetime):
    modifiedTo = modifiedFrom + timedelta(hours=3)
    params = {
        'modifiedFrom': f"{modifiedFrom.strftime('%Y-%m-%d')}T{modifiedFrom.hour}:00:00Z",
        'modifiedTo': f"{modifiedTo.strftime('%Y-%m-%d')}T{modifiedTo.hour}:00:00Z",
        'limit': 100,
        'offset': 0
    }

    req = requests.get('http://opendata.trudvsem.ru/api/v1/vacancies', params)
    if req.json()['results']:
        vacancies = req.json()['results']['vacancies']
    else:
        vacancies = []
    total = int(req.json()['meta']['total'])
    if total > 10000:
        raise Exception('total more than 10000')
    numbers = math.ceil(total / 100)
    for number in tqdm(range(numbers)):
        time.sleep(0.3)
        params['offset'] += 1
        req = requests.get('http://opendata.trudvsem.ru/api/v1/vacancies', params)
        if req.json()['results']:
            vacancies += req.json()['results']['vacancies']
    return vacancies


if __name__ == '__main__':
    while start_time < end_time:
        try:
            vacancies += getDay(start_time)
        except Exception as e:
            print(e)
            with open('backup.json', 'w') as file:
                json.dump(vacancies, file)
                break
        start_time += timedelta(hours=3)
        print(start_time)
    with open('RR_all_data_month.json', 'w') as file:
        json.dump(vacancies, file)