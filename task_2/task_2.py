# 2. Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с
# информацией о заказах. Написать скрипт, автоматизирующий его заполнение данными. Для этого:
#     a. Создать функцию write_order_to_json(), в которую передается 5 параметров — товар
#         (item), количество (quantity), цена (price), покупатель (buyer), дата (date). Функция
#         должна предусматривать запись данных в виде словаря в файл orders.json. При
#         записи данных указать величину отступа в 4 (ident) пробельных символа;
#     b. Проверить работу программы через вызов функции write_order_to_json() с передачей
#         в нее значений каждого параметра.

from datetime import date as date_
import json


def write_order_to_json(item: str,
                        quantity: int,
                        price: float,
                        buyer: str,
                        date: str):
    with open("orders.json", "r") as file_out:
        orders = json.load(file_out)

    with open("orders.json", "w") as file_in:
        order_list = orders["orders"]
        order_list.append({
            "item": item,
            "quantity": quantity,
            "price": price,
            "buyer": buyer,
            "date": date
        })
        json.dump(orders, file_in, sort_keys=True, indent=4)
        print(orders, type(orders))


if __name__ == "__main__":
    write_order_to_json("T-Short", 50, 355.6591, "Nikitos", date_(2023, 12, 4).strftime("%Y.%m.%d"))
    write_order_to_json("Scarf", 50, 1000., "Nikitos", date_(2023, 12, 4).strftime("%Y.%m.%d"))
