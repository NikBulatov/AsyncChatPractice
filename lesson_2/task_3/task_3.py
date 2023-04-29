# 3. Задание на закрепление знаний по модулю yaml. Написать скрипт, автоматизирующий
# сохранение данных в файле YAML-формата. Для этого:
#   a. Подготовить данные для записи в виде словаря, в котором первому ключу
#       соответствует список, второму — целое число, третьему — вложенный словарь, где
#       значение каждого ключа — это целое число с юникод-символом, отсутствующим в
#       кодировке ASCII (например, €);
#   b. Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml.
#       При этом обеспечить стилизацию файла с помощью параметра default_flow_style, а
#       также установить возможность работы с юникодом: allow_unicode = True;
#   c. Реализовать считывание данных из созданного файла и проверить, совпадают ли они
#       с исходными.

import yaml

DATA = {'items': ['computer', 'printer', 'keyboard', 'mouse'],
        'items_quantity': 4,
        'items_ptice': {'computer': '200€-1000€',
                        'printer': '100€-300€',
                        'keyboard': '5€-50€',
                        'mouse': '4€-7€'}
        }


def save_data_to_yaml(data: dict):
    with open("result.yaml", "x") as file_in:
        yaml.dump(data, file_in, default_flow_style=False, allow_unicode=True, sort_keys=False)


def read_from_yaml(file: str):
    with open(file, "r") as file_out:
        return yaml.load(file_out, Loader=yaml.SafeLoader)


if __name__ == "__main__":
    save_data_to_yaml(DATA)
    print(DATA == read_from_yaml("result.yaml"))
