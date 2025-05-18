from tool.base import *
from Data.path_and_time import *
from Data.Data import *

"""
    тесты не зависящие от поискового запроса (можно задать в переменных начинающихся на search в Data)
    - проверка статус-кода
    - времени ответа сервера
    - заголовков
    - типа данных ответа (json)
"""


def send_message_start():
    """
    Отправляем сообщение в канал ММ
    """
    logger.info(f"Отправляю сообщение в канал мм")
    root_id = send_message_mt(channel_id=MATTERMOST_ID,
                              message=f'Регресс-тесты (api) для {env.split("/")[2]} - запущены')
    return root_id


def unauth_request():
    """
    Тесты эндпоинтов на факт их закрытия авторизацией
    :return:
    """
    unauth()


def auth():
    """
    Авторизуемся
    """
    token_endpoint = 'login/'
    flag = 'login'
    headers_login = headers_post_options
    token = request_post(login_data, token_endpoint, headers_login, None, flag)
    return token


def check_auth(file_path=AllForTasks.file_path):
    """
    Проверяем успешность авторизации
    """
    logger.info(f"Проверяем авторизацию")
    global check
    check = True
    try:
        with open(file_path, 'r') as log_file:
            for line in log_file:
                if 'ERROR' in line:
                    check = False
                    send_message_file_mt(channel_id=MATTERMOST_ID,
                                         message=f'Ошибка авторизации',
                                         file_path=AllForTasks.file_path,
                                         filename=AllForTasks.filename,
                                         root_id=root_id)
                    break
    except FileNotFoundError:
        print(f"Файл логов не найден: {file_path}")
        check = False


def map_rus():
    """
    Тесты модуля "Карта" по запросу из search в Data
    """
    logger.info(f"Начинаю тесты карты")
    endpoint = endpoints['map_endpoint']
    data = Search.search['search']
    type_module = 'Карта'
    headers_map = headers_get_head_options
    response = request_get(token, endpoint, type_module, headers_map, data)
    return response


def get_uid_on_map(response):
    """
    Получаем uid-ы регионов, аггломераций и городов по запросу из search в Data
    необходимы для фунцкии raiting_in_map
    """
    logger.info(f"Забираю уиды регионов, аггл и городов")
    # Создаем три списка для хранения uid
    city, region, aggl = get_uids_map(response)
    return city, region, aggl


def raiting_in_map(city, region, aggl):
    """
    Проверяем рейтинги всех ЮЛ по запросу на карте по каждому уровню зума
    """
    logger.info(f"Начинаю тесты рейтинга юл на карте")
    endpoint_detail_info = endpoints['rating_legal_person_in_map_endpoint']
    headers_raiting_in_map = headers_get_head_options
    data = create_objects_in_map(city, region, aggl)
    for item in data:
        data = item['params']
        type = item['type']
        request_get(token, endpoint_detail_info, type, headers_raiting_in_map, data)


def charts():
    """
    Тесты модуля "Статистика" по запросу из search в Data
    """
    logger.info(f"Начинаю тесты статистики")
    endpoint = endpoints['chart_endpoint']
    data = Search.search['search']
    type = 'Статистика в поиске по компетенциям'
    headers_charts = headers_get
    request_get(token, endpoint, type, headers_charts, data)


def graph_ak_ko():
    """
    Тесты модулей "Граф АК", "Граф КО" по запросу из search в Data
    с различными лимитами - 1-10, 20, 50, 100
    различным периодом - 2000 - 2024
    """
    logger.info(f"Начинаю тесты графов АК/КО")
    data = data_params_graph_ak_ko()
    headers_graph_ak_ko = headers_get_head_options
    for item in data:
        endpoint = item['endpoint']
        data = item['params']
        type = item['type']
        request_get(token, endpoint, type, headers_graph_ak_ko, data)


def raiting_and_search_legal_physical():
    """
    Тесты для 200 записей в рейтингах ЮЛ/ФЛ (offset) с сортировкой по всем столбцам
    - рейтинги по запросу из search в Data
    - поиск по ЮЛ из search_org в Data
    - поиск по ФЛ из search_person в Data
    """
    logger.info(f"Начинаю тесты рейтингов из компетенций и поиска юл/фл")
    data = data_params_person_raiting_search()
    headers_raiting_and_search_legal_physical = headers_get_post_head_options
    for item in data:
        endpoint = item['endpoint']
        params = item['params']
        type_ = item['type']
        request_get_raiting_and_search(token, endpoint, type_, headers_raiting_and_search_legal_physical, params)
    return data


def get_uid_legal_person(data):
    """
    Получаем списки из uid-ов ЮЛ из рейтинга по запросу из search в Data
    для дальнейших тестов профиле ЮЛ по запросу.

    :param data: Данные для получения uid-ов
    :param person_type: Тип лица ('legal' для ЮЛ, 'physical' для ФЛ)
    :return: uids, uid_one, uid_ten
    """
    return get_uids_from_rating(data[0], token, 'legal')


def get_uid_physical_person(data):
    """
    Получаем списки из uid-ов ФЛ из рейтинга по запросу из search в Data
    для дальнейших тестов профиле ФЛ по запросу.

    :param data: Данные для получения uid-ов
    :param person_type: Тип лица ('legal' для ЮЛ, 'physical' для ФЛ)
    :return: uids, uid_one, uid_ten
    """
    return get_uids_from_rating(data[48], token, 'physical')  # для полного списка кейсов orderings и hirsh в Data


# Для быстроты тестирования (проход не по всем кейсам)
# def get_uid_physical_person(data):
#     """
#     Получаем списки из uid-ов ФЛ из рейтинга по запросу из search в Data
#     для дальнейших тестов профиле ФЛ по запросу.
#
#     :param data: Данные для получения uid-ов
#     :param person_type: Тип лица ('legal' для ЮЛ, 'physical' для ФЛ)
#     :return: uids, uid_one, uid_ten
#     """
#     return get_uids_from_rating(data[4], token, 'physical')  # для мин-ого списка кейсов orderings и hirsh в Data


def legal_person_profile(uids_legal_person):
    """
    Тесты профиля ЮЛ по запросу и без:
    - Карточка ЮЛ по запросу и без
    - Статистика в карточке ЮЛ по запросу и без
    - Лицензии ЮЛ
    - Клинические исследования ЮЛ
    """
    logger.info(f"Начинаю тесты профиля ЮЛ")
    legal_person(token, uids_legal_person)


def physical_person_profile(uids_physical_person):
    """
    Тесты профиля ФЛ по запросу и без:
    - Карточка ФЛ по запросу и без
    - Список дублей ФЛ
    - Тесты профилей дублей ФЛ
    - Позиция автора в публикации по запросу и без запроса
    - Граф соавторов по запросу и без запроса
    """
    logger.info(f"Начинаю тесты профиля ФЛ")
    physical_person(token, uids_physical_person)


def snippets_legal_person(uids_ten_legal_person):
    """
    Тесты сниппетов (публикации, НИОКР, диссертации, патенты, гранты, РИД, ИКРБС, ЦКП, УНУ):
    - ограничение по проверкам - 10 профилей ЮЛ
    - в профиле ЮЛ по запросу
    - в профиле ЮЛ без запроса
    - глубина проверок - 5 страниц каждого сниппета
    """
    logger.info(f"Начинаю тесты сниппетов сущностей в профилях ЮЛ")
    snippets(token, uids_ten_legal_person, 'Сниппеты ЮЛ')


def snippets_physical_person(uids_ten_physical_person):
    """
    Тесты сниппетов (публикации, НИОКР, диссертации, патенты, гранты, РИД, ИКРБС, ЦКП, УНУ):
    - ограничение по проверкам - 10 профилей ФЛ
    - в профиле ФЛ по запросу
    - в профиле ФЛ без запроса
    - глубина проверок - 5 страниц каждого сниппета
    """
    logger.info(f"Начинаю тесты сниппетов сущностей в профилях ФЛ")
    snippets(token, uids_ten_physical_person, 'Сниппеты ФЛ')


def sciworks():
    """
    Тесты Поиска по документам (+таб) по запросу из search в Data
    """
    logger.info(f"Начинаю тесты Поиска по документам")
    return sciwork(token)


def sciwork_filters(filters_in_sciwork):
    """
    Тесты фильтров в поиске по документам по запросу из search в Data
    """
    logger.info(f"Начинаю тесты фильтров в поиске по документам")
    logger.debug(f'По запросу есть данные по этим документам - {filters_in_sciwork}. Проверяем фильтры только в них')
    endpoint = endpoints['sciwork_filters']
    type = 'Фильтры в поиске по документам'
    for key, data in Filters.data.items():
        if key in filters_in_sciwork:
            request_get(token, endpoint, type, headers_get_head_options, data)


def doccards(uids_cards):
    """
    Тесты карточек документов. В проверках участвуют до 100 карточек сущностей по запросу
    (до 5-ти страниц в поиске по документам)
    """
    logger.info("Начинаю тесты карточек сущностей")
    card_types = Cards.card_types
    doccard(token, uids_cards, card_types)


def params_for_result_document():
    """
    Генерируем общие параметры для выгрузки Excel
    """
    logger.info(f"Начинаю генерацию общих параметров для выгрузки эксель")
    base_params = generate_dicts()
    logger.debug(f'Общие параметры (base_params) - {base_params}')
    return base_params


def result_document_competency(base_params):
    """
    Тесты выгрузки Excel из рейтингов ЮЛ/ФЛ в компетенциях
    """
    logger.info(f"Начинаю тесты выгрузки эксель из рейтингов ЮЛ/ФЛ в компетецниях")
    headers_search_doc = headers_post
    headers_load_doc = headers_get_put_delete
    result_document(base_params,
                    'competency',
                    'Выгрузка Excel из рейтинга ЮЛ/ФЛ',
                    token,
                    headers_search_doc,
                    headers_load_doc,
                    'search')


def result_document_search_org(base_params):
    """
    Тесты выгрузки Excel из поиска по ЮЛ
    """
    logger.info(f"Начинаю тесты выгрузки эксель из поиска ЮЛ")
    headers_search_doc = headers_post
    headers_load_doc = headers_get_put_delete
    result_document(base_params,
                    'org',
                    'Выгрузка Excel из поиска по ЮЛ',
                    token,
                    headers_search_doc,
                    headers_load_doc,
                    'search_org')


def result_document_search_person(base_params):
    """
    Тесты выгрузки Excel из поиска по ФЛ
    """
    logger.info(f"Начинаю тесты выгрузки эксель из поиска ФЛ")
    headers_search_doc = headers_post
    headers_load_doc = headers_get_put_delete
    result_document(base_params,
                    'person',
                    'Выгрузка Excel из поиска по ФЛ',
                    token,
                    headers_search_doc,
                    headers_load_doc,
                    'search_person')


def result_document_search_legal_person_profile(base_params, uid_legal_person):
    """
    Выгрузка Excel из профиля ЮЛ по запросу
    """
    logger.info(f"Начинаю тесты выгрузки эксель из профиля ЮЛ по запросу")
    headers_search_doc = headers_post
    headers_load_doc = headers_get_put_delete
    result_document(base_params,
                    'doc',
                    'Выгрузка Excel из профиля ЮЛ по запросу',
                    token,
                    headers_search_doc,
                    headers_load_doc,
                    'search',
                    uid_legal_person,
                    'org_uid')


def result_document_search_physical_person_profile(base_params, uid_physical_person):
    """
    Выгрузка Excel из профиля ФЛ по запросу
    """
    logger.info(f"Начинаю тесты выгрузки эксель из профиля ФЛ по запросу")
    headers_search_doc = headers_post
    headers_load_doc = headers_get_put_delete
    result_document(base_params,
                    'doc',
                    'Выгрузка Excel из профиля ФЛ по запросу',
                    token,
                    headers_search_doc,
                    headers_load_doc,
                    'search',
                    uid_physical_person,
                    'person_uid')


def result_document_legal_person_profile(base_params, uid_legal_person):
    """
    Выгрузка Excel из профиля ЮЛ без запроса
    """
    logger.info(f"Начинаю тесты выгрузки эксель из профиля ЮЛ без запроса")
    # result_document(base_params, 'doc', token,'', uids_legal_person, 'org_uid')
    headers_search_doc = headers_post
    headers_load_doc = headers_get_put_delete
    result_document(base_params,
                    'doc',
                    'Выгрузка Excel из профиля ЮЛ без запроса',
                    token,
                    headers_search_doc,
                    headers_load_doc,
                    None,
                    uid_legal_person,
                    'org_uid')


def result_document_physical_person_profile(base_params, uid_physical_person):
    """
    Выгрузка Excel из профиля ФЛ без запроса
    """
    logger.info(f"Начинаю тесты выгрузки эксель из профиля ФЛ без запроса")
    headers_search_doc = headers_post
    headers_load_doc = headers_get_put_delete
    result_document(base_params,
                    'doc',
                    'Выгрузка Excel из профиля ФЛ без запроса',
                    token,
                    headers_search_doc,
                    headers_load_doc,
                    None,
                    uid_physical_person,
                    'person_uid')


def out_of_search():
    data = {
        'person_self': {
            'hand': endpoints['person_self_endpoint'],
            'type': 'Личный кабинет, Мой профиль'
        },
        'organization_self': {
            'hand': endpoints['organization_self_endpoint'],
            'type': 'Личный кабинет, Моя организация'
        },
        'user_documents': {
            'hand': endpoints['user_documents_endpoint'],
            'type': 'Личный кабинет, Мои документы',
            'params': {'page': '1', 'limit': '10'}
        },
        'main_page_charts': {
            'hand': endpoints['main_page_charts_endpoint'],
            'type': 'Диаграмма Статистика "Используемые источники данных за последние 10 лет"',
        },
        'work_counts': {
            'hand': endpoints['work_counts_endpoint'],
            'type': 'Информация для пользователей на Главной странице'
        },
        'news': {
            'hand': endpoints['news_endpoint'],
            'type': 'Бегущая строка новостей'
        }
    }
    for key, value in data.items():
        hand = value['hand']
        type_ = value['type']
        params = value.get('params')
        request_get(token, hand, type_,  headers_get, params)


def all_data():
    """
    Инициализируем все параметры расширенного поиска
    """
    data = []
    for key, value in advanced_search.items():
        if isinstance(value, list):  # Проверяем, является ли значение списком
            data.extend(value)
        else:
            data.append(value)
    logger.debug(f'Параметры расширенного поиска - {data}')
    return data


def map_advanced_search(data_search):
    """
       Тесты модуля "Карта" по запросу из search в Data с параметрами расширенного поиска
       """
    logger.info(f"Начинаю тесты карты с параметрами расширенного поиска")
    endpoint = endpoints['map_endpoint']
    type = 'Карта'
    # responses = []  # Список для хранения ответов
    for data in data_search:  # Перебираем каждый элемент списка all_data
        request_get(token, endpoint, type, data)


def sciwork_advanced_search(data_search):
    """
    Тесты Поиска по документам (+таб) по запросу из search в Data с параметрами расширенного поиска
    """
    logger.info(f"Начинаю тесты Таба в Поиске по документам с параметрами расширенного поиска")
    # Главная
    endpoint = endpoints['sciwork_tabs_endpoint']
    type = 'Таб - Поиск по документам'
    for data in data_search:  # Перебираем каждый элемент списка all_data
        request_get(token, endpoint, type, data)


def sciwork_filters_advanced_search(data_search, filters_in_sciwork):
    """
    Тесты фильтров в поиске по документам по запросу из search в Data с параметрами расширенного поиска
    """
    logger.info(f"Начинаю тесты фильтров в поиске по документам  с параметрами расширенного поиска")
    endpoint = endpoints['sciwork_filters']
    type = 'Фильтры в поиске по документам'
    logger.debug(f"Создаем список из параметров, содержащий тип фильтра, поисковый запрос и "
                 f"параметры расширенного поиска")
    dates = []
    types = [item.split('_')[1] for item in filters_in_sciwork]
    logger.debug(f'Будем проверять фильтры только в - {types}')
    for filter_name, filter_value in Filters.types.items():
        for filter_key, filter_val in filter_value.items():
            for item in data_search:
                dates.append({filter_key: filter_val, **item})
    logger.debug(f"Параметры для фильтров с расширенными параметрами - {dates}")
    for data in dates:
        if data['types'] in types:
            request_get(token, endpoint, type, data)


def send_message_end(file_path=AllForTasks.file_path):
    with open(file_path, 'r+') as log_file:
        content = log_file.read()
        if content:
            logger.info(f"Отправляю сообщение и лог ошибок в канал ММ")
            send_message_file_mt(channel_id=MATTERMOST_ID, message=f'Тестирование завершено',
                                 file_path=AllForTasks.file_path,
                                 filename=AllForTasks.filename,
                                 root_id=root_id)
            log_file.seek(0)
            log_file.truncate()
        else:
            logger.info(f"Отправляю сообщение в канал ММ")
            send_message_mt(channel_id=MATTERMOST_ID,
                            message=f'Тестирование завершено.\nБаги не обнаружены.',
                            root_id=root_id)


if __name__ == "__main__":
    root_id = send_message_start()
    token = auth()
    check_auth()
    if check:
        response_map = map_rus()
        city, region, aggl = get_uid_on_map(response_map)
        raiting_in_map(city, region, aggl)
        charts()
        graph_ak_ko()
        response_with_uids = raiting_and_search_legal_physical()
        uids_legal_person, uid_legal_person, uids_ten_legal_person = get_uid_legal_person(response_with_uids)
        uids_physical_person, uid_physical_person, uids_ten_physical_person = get_uid_physical_person(response_with_uids)
        legal_person_profile(uids_legal_person)
        physical_person_profile(uids_physical_person)
        snippets_legal_person(uids_ten_legal_person)
        snippets_physical_person(uids_ten_physical_person)
        uids_cards, filters_in_sciwork = sciworks()
        sciwork_filters(filters_in_sciwork)
        doccards(uids_cards)
        base_params = params_for_result_document()
        result_document_competency(base_params)
        result_document_search_org(base_params)
        result_document_search_person(base_params)
        result_document_search_legal_person_profile(base_params, uids_legal_person)
        result_document_search_physical_person_profile(base_params, uids_physical_person)
        result_document_legal_person_profile(base_params, uids_legal_person)
        result_document_physical_person_profile(base_params, uids_physical_person)
        out_of_search()

        # Проход со всеми возможными параметрами расширенного фильтра
        # data_search = all_data()
        # map_advanced_search(data_search)
        # raiting_in_map_advanced_search(city, region, aggl)
        # charts_advanced_search()
        # graph_ak_ko_advanced_search()
        # raiting_and_search_legal_physical_advanced_search()
        # legal_person_profile_advanced_search()
        # physical_person_profile_advanced_search()
        # snippets_legal_person_advanced_search()
        # snippets_physical_person_advanced_search()
        # sciwork_advanced_search(data_search)
        # sciwork_filters_advanced_search(data_search, filters_in_sciwork)
        # result_document_competency_advanced_search()
        # result_document_search_org_advanced_search()
        # result_document_search_person_advanced_search()
        # result_document_search_legal_person_profile_advanced_search()
        # result_document_search_physical_person_profile_advanced_search()
        # result_document_legal_person_profile_advanced_search()
        # result_document_physical_person_profile_advanced_search()
        unauth_request()

    send_message_end()
