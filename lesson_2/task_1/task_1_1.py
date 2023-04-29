# Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с
# данными, их открытие и считывание данных. В этой функции из считанных данных
# необходимо с помощью регулярных выражений извлечь значения параметров
# «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения
# каждого параметра поместить в соответствующий список. Должно получиться четыре
# списка — например, os_prod_list, os_name_list, os_code_list, os_type_list. В этой же
# функции создать главный список для хранения данных отчета — например, main_data
# — и поместить в него названия столбцов отчета в виде списка: «Изготовитель
# системы», «Название ОС», «Код продукта», «Тип системы». Значения для этих
# столбцов также оформить в виде списка и поместить в файл main_data (также для
# каждого файла);



import re

MANUFACTURER_PATTERN = re.compile(r"(Изготовитель системы:)([-.,\w\s]+)")
OS_NAME_PATTERN = re.compile(r"(Название ОС:)([-.,\w\s]+)")
CODE_PRODUCT_PATTERN = re.compile(r"(Код продукта:)([-.,\w\s]+)")
TYPE_SYSTEM_PATTERN = re.compile(r"(Тип системы:)([-.,\w\s]+)")
HEADERS = ["Изготовитель системы", "Название ОС", "Код продукта", "Тип системы"]


def get_data():
    main_data, manufacturers_list, os_names_list, codes_product_list, types_system_list = [HEADERS], [], [], [], []

    for i in range(1, 4):
        with open(f"info_{i}.txt", encoding="cp1251") as f:
            data = f.readlines()
            for line in data:
                manufacturer_items = MANUFACTURER_PATTERN.search(line)
                os_name_items = OS_NAME_PATTERN.search(line)
                code_product_items = CODE_PRODUCT_PATTERN.search(line)
                type_system_items = TYPE_SYSTEM_PATTERN.search(line)

                if manufacturer_items:
                    manufacturer_data = manufacturer_items.group(2).strip()
                    manufacturers_list.append(manufacturer_data)

                if os_name_items:
                    os_name_data = os_name_items.group(2).strip()
                    os_names_list.append(os_name_data)

                if code_product_items:
                    code_product_data = code_product_items.group(2).strip()
                    codes_product_list.append(code_product_data)

                if type_system_items:
                    type_system_data = type_system_items.group(2).strip()
                    types_system_list.append(type_system_data)

    for i in range(0, 3):
        row_data = [manufacturers_list[i], os_names_list[i], codes_product_list[i], types_system_list[i]]
        main_data.append(row_data)
    return main_data


if __name__ == "__main__":
    print(get_data())
