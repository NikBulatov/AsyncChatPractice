"""
4. Преобразовать слова «разработка», «администрирование», «protocol»,
«standard» из строкового представления в байтовое и выполнить
обратное преобразование (используя методы encode и decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
"""

STRING_LIST = ['разработка', 'администрирование', 'protocol', 'standard']

BYTE_ELEMENTS = [word.encode() for word in STRING_LIST]
STRING_ELEMENTS = [bytes_str.decode() for bytes_str in BYTE_ELEMENTS]

if __name__ == "__main__":
    print(*STRING_LIST)
    print()
    print(*BYTE_ELEMENTS)
    print()
    print(*STRING_ELEMENTS)
