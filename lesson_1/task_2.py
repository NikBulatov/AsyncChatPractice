"""
2. Каждое из слов «class», «function», «method» записать в байтовом формате
без преобразования в последовательность кодов
не используя методы encode и decode)
и определить тип, содержимое и длину соответствующих переменных.

Подсказки:
--- b'class' - используйте маркировку b''
--- используйте списки и циклы, не дублируйте функции
"""

STR_LIST = [b'class', b'function', b'method']

if __name__ == "__main__":
    for element in STR_LIST:
        print(type(element), element, "Length:", len(element))
