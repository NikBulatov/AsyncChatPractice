# b. Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой
# функции реализовать получение данных через вызов функции get_data(), а также
# сохранение подготовленных данных в соответствующий CSV-файл;

import csv
from task_1_1 import get_data


def write_to_csv(out_file):
    data = get_data()
    with open(out_file, 'w', encoding='utf-8') as file:
        csv_writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
        for row in data:
            csv_writer.writerow(row)
