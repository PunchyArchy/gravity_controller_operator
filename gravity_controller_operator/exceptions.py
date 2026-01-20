class UnknownController(Exception):
    # Исключение, возникающее при неизвестном имени терминала
    def __init__(self, contr_name=None, contr_list=[]):
        text = f'Контроллер {contr_name} не обнаружен! Создайте класс с контроллером ' \
               'в директории controllers, укажите его модель через атрибут ' \
               'model, затем добавьте этот класс в список ' \
               f'AVAILABLE_CONTROLLERS {tuple(contr_list)}'
        super().__init__(text)
