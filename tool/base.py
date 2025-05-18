import json
import uuid
import re
from typing import List
import requests

from Data import *


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logger(name="regress", level=LogLevel.DEBUG)
env = PROD


def send_message_mt(channel_id: str,
                    message: str,
                    root_id: str = None
                    ) -> str:
    """
    Отправляет текст сообщения в mattermost
    :param channel_id: id канала в mattermost
    :param message: текст сообщения для отправки в mattermost
    :param connection_id: название подключения Airflow
    :param root_id: id сообщения для ответа в mattermost
    """
    post_message_url = f'{connection_host}/api/v4/posts'
    headers = {
        "Authorization": f"Bearer {password}",
        "Content-Type": "application/json"
    }
    data = {
        'channel_id': channel_id,
        'message': message,
        'root_id': root_id
    }
    response = requests.post(post_message_url, headers=headers, data=json.dumps(data), verify=False)
    logger.info(f"Сообщение '{message}' отправлено в канал ММ (id - {channel_id})")
    if response.status_code != 201:
        logger.error(f'Ошибка отправки сообщения в канал ММ-{channel_id}. Статус-код - {response.status_code}')

    return response.json().get('id', None)


def send_message_file_mt(channel_id: str,
                         message: str,
                         file_path: str,
                         filename: str,
                         root_id: str = None) -> str:
    """
    Отправляет текст сообщения в mattermost с прикрепленным файлом.

    :param channel_id: id канала в mattermost
    :param message: текст сообщения для отправки в mattermost
    :param file_path: путь к файлу для отправки
    :param filename: имя файла, которое будет отображаться в Mattermost
    :param root_id: id сообщения для ответа в mattermost
    """
    connection = connection_id
    post_message_url = f'{connection_host}/api/v4/posts'
    post_file_url = f'{connection_host}/api/v4/files'

    headers = {'Authorization': f"Bearer {password}"}
    files = {'files': open(file_path, 'rb')}
    data = {
        'channel_id': channel_id,
        'client_ids': uuid.uuid4()  # Здесь добавлен код для генерации UUID
    }
    params = {
        'channel_id': channel_id,
        'filename': filename
    }

    response = requests.post(post_file_url, headers=headers, files=files, data=data, params=params,
                             verify=False)
    logger.info(f"Файл '{filename}' загружен и готов для отправки в канал ММ (id - {channel_id})")

    try:
        file_infos = response.json()['file_infos'][0]
        file_ids = [file_infos['id']]
    except (KeyError, IndexError) as e:
        logger.error(f"Ошибка при загрузке файла: {response.status_code}, {response.text}, ошибка {e}")

    data = {
        'channel_id': channel_id,
        'message': message,
        'root_id': root_id,
        'file_ids': file_ids
    }

    response = requests.post(post_message_url, headers=headers, json=data, verify=False)
    if response.status_code == 201:
        logger.info(f"Файл '{filename}' и сообщение {message} отправлены в канал ММ (id - {channel_id})")
        pass
    else:
        logger.error(f'Ошибка отправки сообщения в канал ММ-{channel_id}. Статус-код - {response.status_code}')

    return response.json().get('id', None)


def unauth():
    for index, key in enumerate(endpoints):
        if index in (0, len(endpoints) - 1):  # не берем на проверку первый и последний эндпоинт
            continue
        hand = endpoints[key]
        endpoint = env+hand
        logger.debug(f"Проверяем эндпоинт {endpoint}, что он закрыт авторизацией")
        try:
            response = requests.get(endpoint, verify="")
            if response.status_code == 401:
                    logger.info(f"Эндпоинт {endpoint} закрыт авторизацией")
            else:
                logger.error(f"Тест не пройден: Эндпоинт {endpoint} вернул статус-код {response.status_code}.")
        except Exception as e:
            logger.error(f"Произошла ошибка: {e}")


def tests_time_and_headers(response,
                           expected_headers,
                           endpoint,
                           params,
                           status_code: int = None,
                           type: str = None):
    # Проверяем время ответа сервера в секундах
    time = response.elapsed.total_seconds()
    logger.info(f"Время ответа равно: {time}")
    if time > 30:
        logger.error(f"Время ответа запроса на endpoint ({endpoint}) - {type} с параметрами - "
                     f"{params} больше 30 секунд. Фактическое время - {time}")

    # Проверяем заголовки
    actual_headers = response.headers
    logger.info(f'Заголовки ответа - {actual_headers}')

    for key, expected_value in expected_headers.items():
        actual_value = actual_headers.get(key)

        # Обработка отсутствующих заголовков
        if actual_value is None:
            if status_code == 204 and key in ('content-type', 'content-length'):
                continue  # Пропускаем проверку для заголовков при статусе 204
            logger.error(
                f"Заголовок '{key}' отсутствует в ответе. Запрос на endpoint ({endpoint}) - {type} с параметрами - {params}")
            continue

        # Проверяем заголовки на соответствие
        if key == 'content-length':
            if re.match(r'^\d+$', actual_value):
                logger.debug(f"Значение заголовка '{key}' является целым числом")
            else:
                logger.error(f"Значение заголовка '{key}' не является целым числом")
        elif key == 'date':
            # Проверка даты с точностью до часа
            if not actual_value.startswith(datetime.utcnow().strftime('%a, %d %b %Y %H')):
                logger.error(
                    f"Значение заголовка '{key}' не совпадает с точностью до часа. Ожидалось: "
                    f"'{expected_value}', получено: '{actual_value}' - запрос на endpoint ({endpoint}) "
                    f"- {type} с параметрами - {params}")
            else:
                logger.debug(f"Значение заголовка '{key}' совпадает")
        elif actual_value != expected_value:
            logger.error(
                f"Значение заголовка '{key}' не совпадает. Ожидалось: '{expected_value}', "
                f"получено: '{actual_value}' - запрос на endpoint ({endpoint}) - {type} с параметрами - {params}")
        else:
            logger.debug(f"Значение заголовка '{key}' совпадает.")


def request_post(params,
                 hand,
                 headers,
                 type: str = None,
                 flag: str = None,
                 token: str = None):
    endpoint = env+hand
    logger.info(f"Получен endpoint для {env.split('/')[2]} - {hand}")
    if flag == 'login':
        try:
            logger.info(f"Авторизуемся")
            login = requests.post(endpoint, json=params, verify="")
            logger.debug(f"Отправлен запрос на endpoint ({endpoint}) с параметрами - {params}")
            status_code = login.status_code
            logger.debug(f"Получен статус-код - {status_code}")
            # Проверяем тип данных ответа
            login.json()
            # Проверяем статус-код
            if status_code != 202:
                login.raise_for_status()
            else:
                token = login.json()['token']
                logger.debug(f"Получен токен авторизации - {token}")
                # Проверяем заголовки и время ответа
                tests_time_and_headers(login, headers, endpoint, params)
                return token
        except requests.exceptions.HTTPError:
            logger.error(f'Ошибка авторизации {params["username"]}. Актуальный статус-код: {login.status_code}')
        except ValueError:
            logger.error("Ответ не в формате JSON.")
        except Exception as err:
            logger.error(f'Произошла ошибка: {err} во время авторизации')
    else:
        try:
            logger.debug(f"Формируем отчет с параметрами {params}")
            payload = {'Authorization': 'token ' + str(token)}
            result_doc = requests.post(endpoint, json=params, headers=payload, verify="")
            # Проверяем тип данных ответа
            result_doc.json()
            logger.debug(f"Отправлен запрос на endpoint ({endpoint}) с параметрами - {params}")
            status_code = result_doc.status_code
            logger.debug(f"Получен статус-код - {status_code}")
            headers = result_doc.headers
            logger.debug(f'Заголовки ответа - {headers}')
            # Проверяем статус-код
            if status_code != 201:
                result_doc.raise_for_status()
                return None
            else:
                logger.debug(f"Отчет с параметрами {params} успешно сформирован")
                # Проверяем заголовки и время ответа
                tests_time_and_headers(result_doc, headers, endpoint, params, None, type)
                response = result_doc.json()
                uid = response.get("uid")
                logger.debug(f"Получен uid для загрузки файла Excel: {uid}")
                return uid
        except requests.exceptions.HTTPError:
            logger.error(
                f'Ошибка при выполнении запроса на выгрузку с параметрами {params}. '
                f'Актуальный статус-код: {status_code}')
        except ValueError:
            logger.error("Ответ не в формате JSON.")
        except Exception as err:
            logger.error(f'Произошла ошибка: {err} во время выполнения запроса на выгрузку')


def request_get(token,
                hand,
                type,
                headers,
                params: dict = None):
    payload = {'Authorization': 'token ' + str(token)}
    endpoint = env+hand
    logger.debug(f"Отправляем и проверяем запрос get")
    logger.debug(f"Получен endpoint для {env.split('/')[2]} - {hand}")
    try:
        response = requests.get(endpoint, params=params, headers=payload, verify="")
        logger.debug(f"Отправлен запрос на endpoint ({endpoint}) - {type} с параметрами - {params}")
        # Проверяем статус-код
        status_code = response.status_code
        logger.info(f"Получен статус-код - {status_code}")
        if status_code not in (200, 206, 204):
            response.raise_for_status()
        else:
            if status_code not in (200, 206):
                tests_time_and_headers(response, headers, endpoint, params, status_code, type)
            else:
                # Проверяем заголовки и время ответа
                tests_time_and_headers(response, headers, endpoint, params, status_code, type)
                # Проверяем тип данных ответа
                response = response.json()
                logger.debug(f"Получен response")
            return response
    except ValueError:
        logger.error("Ответ не в формате JSON.")
    except requests.exceptions.HTTPError:
        logger.error(f'{type} - Ошибка при получении ответа от endpoint - {hand}  с параметрами: {params}. '
                     f'Фактический статус-код: {status_code}')
    except Exception as err:
        logger.error(f'{type} - Произошла ошибка: {err} во время отправки запроса на endpoint - {hand} '
                     f'с параметрами: {params}"')


def data_params_graph_ak_ko():
    """
    Генерируем данные для отправки запроса и проверки Графа АК, Графа КО по запросу из search в Data
    с различными лимитами - 1-10, 20, 50, 100
    различным периодом - 2000 - 2024
    """
    logger.info(f"Генерируем данные для проверки Графов АК/КО")
    endpoint = {
        'graph_author_teams_endpoint': endpoints.get('graph_author_teams_endpoint'),
        'graph_organization_teams_endpoint': endpoints.get('graph_organization_teams_endpoint')
    }
    data_graph_ak_ko = []
    for endpoint_key, endpoint_value in endpoint.items():
        for limit in Graphs.limits:
            for year in Graphs.years:
                # Создание параметров графа
                graph_params = {**Search.search['search'], **{'limit': str(limit), **year}}
                data_graph_ak_ko.append({
                    "params": graph_params,
                    "endpoint": endpoint_value,
                    "type": f"Граф {endpoint_key.split('_')[1].upper()}"
                })

    # Теперь Data_graph_ak_ko содержит все необходимые данные
    logger.debug(f"Данные для графов АК/КО - {data_graph_ak_ko}")
    return data_graph_ak_ko


def data_params_person_raiting_search():
    """
    Генерируем данные для отправки и проверки рейтингов ЮЛ/ФЛ
    по запросу в компетенциях и для поиска по ЮЛ/ФЛ
    """
    logger.debug(f"Генерируем данные для проверки рейтингов ЮЛ/ФЛ")
    # Создание списка параметров
    rating_params = []

    # Генерация параметров для юридических лиц
    for ordering in Raiting.orderings:
        rating_params.append(
            ({**{'type': 'doc', 'limit': '30', 'offset': '0', 'ordering': ordering}, **Search.search['search']},
             endpoints['rating_legal_person_endpoint'],
             'Рейтинг организаций')
        )
    for ordering in Raiting.orderings[:-2]:
        rating_params.append(
            ({**{'type': 'org', 'limit': '30', 'offset': '0', 'ordering': ordering}, **Search.search['search_org']},
             endpoints['rating_legal_person_endpoint'],
             'Поиск по организациям')
        )

    # Генерация параметров для физических лиц
    for ordering in Raiting.orderings:
        for hirsh_value in Raiting.hirsh:
            rating_params.append(
                ({**{'type': 'doc', 'limit': '30', 'offset': '0', 'ordering': ordering, 'hirsh': hirsh_value},
                  **Search.search['search']},
                 endpoints['rating_physical_person_endpoint'],
                 'Рейтинг ученых')
            )
    for ordering in Raiting.orderings[:-2]:
        for hirsh_value in Raiting.hirsh:
            rating_params.append(
                ({**{'type': 'person', 'limit': '30', 'offset': '0', 'ordering': ordering, 'hirsh': hirsh_value},
                  **Search.search['search_person']},
                 endpoints['rating_physical_person_endpoint'],
                 'Поиск по ученым')
            )
    # Создание списка data
    data = []
    # Добавление данных в общий список
    for params, endpoint, type_label in rating_params:
        data.append({
            'params': params,
            'endpoint': endpoint,
            'type': type_label
        })
    logger.debug(f"Список data: {data}")
    return data


def request_get_raiting_and_search(token, hand, type, headers, params):
    """
    Тесты для 200 записей в рейтингах ЮЛ/ФЛ (offset) с сортировкой по всем столбцам
    - рейтинги по запросу из search в Data
    - поиск по ЮЛ из search_org в Data
    - поиск по ФЛ из search_person в Data
    """
    logger.info(f"Отправляем и проверям запрос get в рейтингах ЮЛ/ФЛ и в поиске по ЮЛ/ФЛ")
    try:
        response = request_get(token, hand, type, headers, params)

        # Получаем кол-во ЮЛ/ФЛ по запросу
        count = int(response.get('count', 0))
        logger.debug(f"Получили count - {count}")

        # Получаем кол-во строк в таблице рейтинга для дальнейшего исп-ния (принимает первый offset == 0, как 30 строк)
        offset = int(params.get('offset', 0))
        logger.debug(f"Получили offset - {offset}")

        # Если количество ЮЛ/ФЛ больше 30-ти
        if count > 30:
            # Пока кол-во строк в таблице рейтинга меньше или равно кол=ву ЮЛ/ФЛ или меньше или равно 200
            while offset <= count and offset <= 200:
                params['offset'] = offset  # Обновляем offset в параметрах
                logger.debug(f"Обновили offset ({offset}) в параметрах - {params['offset']}")
                # Отправляем запрос с новым offset
                response = request_get(token, hand, type, headers, params)
                logger.debug(f"Отправили запрос с новым offset")
                logger.debug(f"Получили results")
                offset += 30  # Увеличиваем offset на 30
                logger.debug(f"offset теперь равен - {offset}")
        if offset != 0:  # если мы находимся не на первой "странице" (первые 30-ть ЮЛ/ФЛ), переходим туда
            params['offset'] = 0  # Присваиваем значение 0 в параметрах
            logger.debug(f"Устанавливаем offset в 0 и отправляем новый запрос, чтобы при сборе УИДов "
                         f"собиралось с начала списка ФЛ")
            response = request_get(token, hand, type, headers, params)  # Отправляем новый запрос с offset = 0
        return response
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")


def get_uids_from_rating(data, token, person_type):
    try:
        if person_type == 'legal':
            logger.info("Забираю уиды ЮЛ из рейтинга по компетенциям")
        elif person_type == 'physical':
            logger.info("Забираю УИДы ФЛ из рейтинга по компетенциям")
        else:
            logger.error("Некорректный тип лица")
            return None, None, None

        logger.debug(f"Получены данные для генерации уидов {person_type} - {data}")
        endpoint = data['endpoint']
        data = data['params']
        type = data['type']
        # uids = get_uids(token, endpoint, data, type)
        logger.info(f"Забираем УИДы ЮЛ/ФЛ из рейтингов")
        # Инициализируем списки для uid вне условий
        uids = []  # Список для хранения uid ЮЛ/ФЛ
        # logger.debug(f"Количество uids - {len(uids)}")
        response = request_get(token, endpoint, type, headers_get_post_head_options, data)

        # Получаем кол-во ЮЛ и ФЛ по запросу
        count = int(response.get('count', 0))
        logger.debug(f"Получили count - {count}")

        # Получаем значение кол-ва строк в таблице рейтинга для дальнейшего исп-ния
        # (принимает первый offset == 0, как 30 строк)
        offset = int(data.get('offset', 0))
        logger.debug(f"Получили offset - {offset}")

        # Функция для сбора UIDs из результатов
        def collect_uids(results):
            for result in results:
                uid = result.get('uid')
                if uid:
                    uids.append(uid)

        # Если количество ЮЛ/ФЛ больше 30-ти
        if count > 30:
            while offset < count and len(uids) < 200:
                logger.debug(f"Обновляем offset в параметры - {offset}")
                params['offset'] = offset  # Обновляем offset в параметрах
                response = request_get(token, endpoint, type, headers_get_post_head_options, params)
                logger.debug("Отправили запрос с новым offset")

                results = response.get('results', [])
                logger.debug(f"Получили results - {results}")

                collect_uids(results)

                logger.debug(f"Количество собранных UIDs - {len(uids)}")
                offset += 30  # Увеличиваем offset на 30

        else:
            results = response.get('results', [])
            logger.debug(f"Получили results - {results}")
            collect_uids(results)

        uid_one = uids[0] if uids else None
        uid_ten = uids[:10] if len(uids) >= 10 else uids

        logger.debug(f"УИДы {person_type} - {uids}")
        logger.debug(f"Первые 10-ть УИДов УИД {person_type} - {uid_ten}")
        logger.debug(f"Первый УИД {person_type} - {uid_one}")
        logger.debug(f"Количество uids - {len(uids)}")
        return uids, uid_one, uid_ten
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")


def get_uids_map(response):
    """
    Получаем uid-ы регионов, аггломераций и городов по запросу из search в Data
    необходимы для фунцкии raiting_in_map
    """
    logger.info(f"Забираем УИЛы регионов, городов и аггломераций с карты по запросу")
    city_uids = []
    region_uids = []
    aggl_uids = []
    logger.debug(f"Создаем словари для хранения списков по типам")

    # Проходим по каждому зум-уровню
    for zoom_level in response.keys():
        # Получаем данные для текущего зум-уровня
        zoom_data = response[zoom_level].get('data', [])
        for item in zoom_data:
            # Получаем тип объекта и uid
            map_obj_type = item['object']['type_map_obj']
            uid = item['object']['uid']

            # Проверяем тип и добавляем uid в соответствующий список
            if map_obj_type == 'city':
                city_uids.append(uid)
            elif map_obj_type == 'region':
                region_uids.append(uid)
            elif map_obj_type == 'aggl':
                aggl_uids.append(uid)
        logger.debug(f"Получаем список city_uids - {city_uids}")
        logger.debug(f"Получаем список region_uids - {region_uids}")
        logger.debug(f"Получаем список aggl_uids - {aggl_uids}")
    # Возвращаем три списка с собранными uid
    return city_uids, region_uids, aggl_uids


def create_objects_in_map(city, region, aggl):
    logger.info("Формируем данные для проверки рейтингов на карте по уровням зума")
    """
    Создает три словаря для поиска юридических лиц по регионам, агломерациям и городам.
    :param city: Список uid городов
    :param region: Список uid регионов
    :param aggl: Список uid агломераций
    :return: Список словарей для рейтинга
    """
    data_dicts = {
        'city': {},
        'region': {},
        'aggl': {}
    }
    lists = [region, aggl, city]

    # Заполнение словарей
    for list_name, current_list in zip(data_dicts.keys(), lists):
        current_dict = data_dicts[list_name]
        for uid in current_list:
            for ordering in Raiting.orderings:
                current_dict[(uid, ordering)] = {
                    **Search.search['search'],
                    'ordering': ordering,
                    'type_map_obj': list_name,
                    'uid': uid
                }
        logger.debug(f"Получили словарь с данными для {list_name} - {current_dict}")

    # Создание списка для рейтинга
    data_raiting_in_map = []
    for list_name, current_dict in data_dicts.items():
        for (uid, ordering), value in current_dict.items():
            data_raiting_in_map.append({
                "params": value,
                "endpoint": endpoints['rating_legal_person_in_map_endpoint'],
                "type": f'Рейтинг в карте, зум {list_name}'
            })
    logger.info(f"Получаем Data_raiting_in_map - {data_raiting_in_map}")
    return data_raiting_in_map


def generate_dicts():
    """
    Генерирует словари с различными сочетаниями параметров для параметров выгрузки Excel.
    :return: Список сгенерированных словарей
    """
    logger.info(f"Генерируем словари с параметрами для выгрузки Эксель")
    synonym_options = [False, True]
    full_text_options = [False, True]
    types_list = ["scipub", "niokr", "diss", "grant", "patent", "ckp", "usu", "rid", "ikrbs"]

    generated_dicts = []  # Список для хранения сгенерированных словарей

    # Генерируем все возможные комбинации типов
    for synonym in synonym_options:
        for full_text in full_text_options:
            # Генерация словаря с одним значением из types_list
            result_document = {
                    "synonym": synonym,
                    "full_text": full_text,
                    "types": types_list  # Одно значение из types_list
                }
            generated_dicts.append(result_document)  # Сохраняем словарь в список
    return generated_dicts  # Возвращаем список сгенерированных словарей


def result_document(base_params,
                    doc_type,
                    type,
                    token,
                    headers_generate,
                    headers_load,
                    search_key=None,
                    uids=None,
                    type_uid=None):
    """
    Общая функция для тестов выгрузки Excel из различных источников
    """

    def payload_result_document_competency(params, type, search):
        """
           Создает новый список словарей payload, добавляя к каждому словарю из params
           содержимое search и type.

           :param params: Список словарей
           :param search: Словарь с поисковым запросом
           :param type: Словарь с типом
           :return: Список словарей payload
           """
        logger.info(
            f"Приступаю к созданию нового списка словарей - прибавляю к общим параметрам содержимое search и type")
        payload = []  # Список для хранения новых словарей

        for param in params:
            new_payload = {
                **(search if search is not None else {}),
                **type,
                **param
            }
            payload.append(new_payload)  # Добавляем новый словарь в список
        # logger.debug(f"СЕЙЧАС БУДУТ ДАННЫЕ ПО ЧАСТНЫМ ПАРАМЕТРАМ")
        return payload

    logger.info(f"Приступаю к тестам - {type} - поисковой запрос: {search_key} {'с uids' if uids is not None else ''}")
    doc_type = {"type": doc_type}
    generate_endpoint = endpoints['result_document_generate_endpoint']
    load_endpoint = endpoints['result_document_load_endpoint']
    # генерируем параметры (список словарей) для выгрузки
    payloads = payload_result_document_competency(base_params, doc_type, Search.search.get(search_key) if search_key else None)
    logger.debug(f'Частные параметры - {payloads}')

    if uids:
        # Создаем новый список словарей с добавленным ключом "person_uid"
        new_payloads = []
        logger.debug(f"Сейчас буду создавать новый список словарей для профиля ЮЛ/ФЛ")
        for uid in uids[:30]:  # Проходим по первым 30 элементам списка uids
            logger.info(f"Взяли uid - {uid} для добавления в ключ 'person_uid'/'org_uid' для профиля ФЛ/ЮЛ")
            for payload in payloads:  # Каждый uid добавляем в каждый элемент payloads (каждый словарь параметров)
                new_payload = payload.copy()  # Создаем копию словаря, чтобы не изменять оригинал
                new_payload[type_uid] = uid  # Добавляем ключ "person_uid" или "org_uid" с текущим uid
                new_payloads.append(new_payload)  # Добавляем новый словарь в список
                logger.debug(f"Новый словарь списка для профиля - {new_payloads}")
        payloads = new_payloads

    for payload in payloads:
        logger.debug(f"Заходим в функцию по формированию файла Эксель из {type} - поисковой запрос: {search_key} "
                     f"{'с uids' if uids is not None else ''}")
        uid_excel = request_post(payload, generate_endpoint, headers_generate, type, None, token)  # формируем файл Excel
        if uid_excel is not None:
            download_endpoint = load_endpoint + uid_excel + '/'
            logger.debug(f"Эндпоинт для выгрузки Эксель download_endpoint - {download_endpoint}")
            logger.debug(f"Сейчас буду отправлять get-запрос для выгрузки и проверки файла")
            request_get(token, download_endpoint, type, headers_load, None)   # выгружаем файл Excel
        else:
            logger.debug(
                f"Так как по запросу {payload}, нет данных для выгрузки, выгружать нечего и проверять нечего")


def endpoint_with_uid(endpoint, uids, type=None):
    """"
    К эндпоинту добавляем УИД и другую строку в зависимости от модуля
    """
    handle_map = {
        None: "/",
        'Лицензии в профиле': '/licenses/',
        'Статистика в профиле ЮЛ': '/charts/',
        'Статистика в профиле ФЛ': '/charts/',
        'Динамика цитирования публикации': '/charts/',
        'Клинич. исслед. лекарств. препаратов ЮЛ': '/clinical-researches/',
        'Клинич. исслед. мед. изделий ЮЛ': '/kimi/',
        'Дубли ФЛ': '/duplicates/',
        'Граф соавторов': '/graph/scipub/',
        'Табы': '/tabs/',
        'Сниппет публикаций': '/snippets/sci_pub/',
        'Сниппет НИОКР': '/snippets/niokr/',
        'Сниппет Диссертации': '/snippets/diss/',
        'Сниппет Патенты': '/snippets/patent/',
        'Сниппет Гранты': '/snippets/grant/',
        'Сниппет РИД': '/snippets/rid/',
        'Сниппет ИКРБС': '/snippets/ikrbs/',
        'Сниппет ЦКП': '/snippets/ckp/',
        'Сниппет УНУ': '/snippets/usu/'
    }

    handle = handle_map.get(type)
    if handle is None:
        return None

    endpoints = [endpoint + uid + handle for uid in uids]
    logger.debug(f'Список всех энпоинтов - {endpoints}')
    return endpoints


def legal_person(token, uids):
    type_profile_search = 'Профиль ЮЛ по запросу'
    type_profile = 'Профиль ЮЛ без запроса'
    type_chart = 'Статистика в профиле ЮЛ'
    type_licenses = 'Лицензии в профиле ЮЛ'
    type_legal_ki_lp = 'Клинич. исслед. лекарств. препаратов ЮЛ'
    type_legal_ki_mi = 'Клинич. исслед. мед. изделий ЮЛ'

    data_profile_search = Search.search['search']
    data_licenses = Licenses.licenses
    data_legal_ki_lp = Ki_Lp_ki_mi.ki_lp
    data_legal_ki_mi = Ki_Lp_ki_mi.ki_mi

    legal_person_card = endpoints['legal_person_card_endpoint']
    endpoint_legal_person = endpoint_with_uid(legal_person_card, uids)
    endpoint_charts = endpoint_with_uid(legal_person_card, uids, 'Статистика в профиле ЮЛ')
    endpoint_licenses = endpoint_with_uid(legal_person_card, uids, 'Лицензии в профиле ЮЛ')
    endpoint_ki_lp = endpoint_with_uid(legal_person_card, uids, 'Клинич. исслед. лекарств. препаратов ЮЛ')
    endpoint_ki_mi = endpoint_with_uid(legal_person_card, uids, 'Клинич. исслед. мед. изделий ЮЛ')

    try:
        logger.info(f"Начинаю тесты профиля ЮЛ по запросу - основная информация ЮЛ")
        for endpoint in endpoint_legal_person:
            request_get(token, endpoint, type_profile_search, headers_get, data_profile_search)

        logger.info(f"Начинаю тесты профиля ЮЛ по запросу - статистика ЮЛ")
        for endpoint in endpoint_charts:
            request_get(token, endpoint, type_chart, headers_get, data_profile_search)

        logger.info(f"Начинаю тесты профиля ЮЛ без запроса - основная инфа ЮЛ")
        for endpoint in endpoint_legal_person:
            request_get(token, endpoint, type_profile, headers_get)

        logger.info(f"Начинаю тесты профиля ЮЛ без запроса - статистика ЮЛ")
        for endpoint in endpoint_charts:
            request_get(token, endpoint, type_chart, headers_get)

        logger.info(f"Начинаю тесты профиля ЮЛ - лицензии ЮЛ")
        logger.debug(f'Данные для лицензий - {data_licenses}')
        for license_endpoint in endpoint_licenses:  # для каждого эндпоинта лицензий с УИДом ЮЛ
            for data in data_licenses:  # для каждого payload
                limit = int(data['limit'])  # Забираем значение limit
                response = request_get(token, license_endpoint, type_licenses, headers_get, data)
                count = int(response.get('count', 0))  # Получаем кол-во лицензий ЮЛ
                logger.debug(f"Значение count - {count}")
                offset = int(response.get('offset', 0))  # Получаем значение offset (offset/limit == номер страницы)
                logger.debug(f"Значение offset - {offset}")
            if count > limit:  # Если лицензий больше лимита (15)
                offset = 15
                modified_licenses = []
                # если offset < count добавляем новые словари offset, увеличенным на 15
                while offset <= count:
                    copied_licenses = [dict(d) for d in data_licenses]  # создали копию списка словарей
                    for copied_license in copied_licenses:  # для каждого словаря в списке
                        copied_license['offset'] = str(offset)
                    modified_licenses.extend(copied_licenses)  # добавляем значение offset равным 15
                    logger.debug(f"offset теперь равен - {offset}")
                    logger.debug(f"modified_licenses - {modified_licenses}")
                    offset += 15  # увеличиваем значение offset, на следующей итерации цикла
                for licenses in modified_licenses:
                    request_get(token, license_endpoint, type_licenses,  headers_get, licenses)


        logger.info(f"Начинаю тесты профиля ЮЛ - клинические исследования лекарственных средств ЮЛ")
        for endpoint in endpoint_ki_lp:
            for data in data_legal_ki_lp:
                response = request_get(token, endpoint, type_legal_ki_lp, headers_get, data)
                logger.debug(f'Ответ по ки-лп - {response}')
        logger.info(f"Начинаю тесты профиля ЮЛ - клинические исследования мед. изделий ЮЛ")
        for endpoint in endpoint_ki_mi:
            for data in data_legal_ki_mi:
                response = request_get(token, endpoint, type_legal_ki_mi, headers_get, data)
                logger.debug(f'Ответ по ки-ми - {response}')
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")


def physical_person(token, uids):
    type_profile_search = 'Профиль ФЛ'
    type_duplicates = 'Дубли ФЛ'
    # type_profile_duplicates = 'Профиль дубля ФЛ'
    type_charts_physical_person = 'Статистика в профиле ФЛ без запроса'
    type_charts_physical_person_search = 'Статистика в профиле ФЛ по запросу'
    type_graph_author_teams_search = 'Граф соавторов по запросу'
    type_graph_author_teams = 'Граф соавторов без запроса'

    data_profile_search = Search.search['search']
    data_graph_co_authors_search = Graphs.graph_co_authors_search
    data_graph_co_authors = Graphs.graph_co_authors

    physical_person_card = endpoints['physical_person_card_endpoint']
    endpoint_physical_person = endpoint_with_uid(physical_person_card, uids)
    endpoint_duplicates = endpoint_with_uid(physical_person_card, uids, 'Дубли ФЛ')
    endpoint_charts = endpoint_with_uid(physical_person_card, uids, 'Статистика в профиле ФЛ')
    graph_co_authors = endpoint_with_uid(physical_person_card, uids, 'Граф соавторов')
    try:
        logger.info(f"Начинаю тесты профиля ФЛ - основная инфа ФЛ")
        for endpoint in endpoint_physical_person:
            request_get(token, endpoint, type_profile_search, headers_get)
        logger.info(f"Начинаю тесты профиля дубля ФЛ")
        logger.info(f"Проверяю список дублей в профилях ФЛ")
        all_uid_duplicates = []  # Создаем пустой список для хранения всех uid_duplicates
        for index, endpoint in enumerate(endpoint_duplicates):
            # Создаем пустой список для хранения uid_duplicates каждого ФЛ из uids
            unique_uid_duplicates = {}
            # Проверяем список дублей каждого ФЛ из uids
            response = request_get(token, endpoint, type_duplicates, headers_get)
            data_results = response['results']
            logger.debug(f"Забираю УИДы из списка дублей в профиле ФЛ")
            uid_duplicates = [uid['uid'] for uid in data_results]  # Собираем УИДы дублей каждого ФЛ
            unique_uid_duplicates[index] = uid_duplicates  # Сохраняем список в словаре с индексом как ключ
            logger.debug(f"Список дублей для ФЛ {index}: {uid_duplicates}")
            all_uid_duplicates.extend(uid_duplicates)  # Получаем список УИДов всех дублей всех ФЛ
        logger.debug(f'УИДы дублей - {all_uid_duplicates}')


        # logger.info(f"Проверяю профили дублей всех ФЛ")
        # # профиль дубля ФЛ
        # _, _, _, _, _, endpoint_duplicates_person = endpoint_with_uid(physical_person_duplicates_endpoint, all_uid_duplicates)
        # for endpoint in endpoint_duplicates_person:
        #     request_get(token, endpoint, type_profile_duplicates, headers_get)

        logger.info(f"Проверяю статистику в профилях всех ФЛ без запроса")
        for endpoint in endpoint_charts:
            request_get(token, endpoint, type_charts_physical_person, headers_get)

        logger.info(f"Проверяю статистику в профилях всех ФЛ по запросу")
        for endpoint in endpoint_charts:
            request_get(token, endpoint, type_charts_physical_person_search, headers_get, data_profile_search)

        logger.info(f"Проверяю МОДУЛЬ СВЯЗАННЫЕ ОРГАНИЗАЦИИ для всех ФЛ без запроса")

        logger.info(f"Проверяю граф соавторов для всех ФЛ по запросу")
        for endpoint in graph_co_authors:
            for data in data_graph_co_authors_search:
                request_get(token, endpoint, type_graph_author_teams_search, headers_get, data)

        logger.info(f"Проверяю граф соавторов для всех ФЛ без запроса")
        for endpoint in graph_co_authors:
            for data in data_graph_co_authors:
                request_get(token, endpoint, type_graph_author_teams, headers_get, data)

    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")


def snippets(token, uids, type_profile):
    def main(token: str, params: dict, endpoints: List[str], type_snippet: str, type_profile: str = None):
        """
        Общая функция для проверки сниппетов в профилях ФЛ/ЮЛ по запросу и без.
        :param token: Токен для авторизации
        :param params: Параметры запроса
        :param endpoints: Список эндпоинтов для проверки
        :param type_snippet: Тип сниппета
        :param type_profile: Тип профиля (по умолчанию None)
        """
        for endpoint in endpoints:
            if type_snippet == 'Табы':
                request_get(token, endpoint, type_snippet, headers_get, params)
            else:
                response = request_get(token, endpoint, type_snippet, headers_get, params)  # Отправляем запрос с первыми параметрами
                pages = int(response.get('total_pages', 0))
                count_doc = int(response.get('count', 0))

                logger.debug(f'Количество страниц в сниппете - {pages}')
                logger.debug(f'Общее количество документов - {count_doc}')

                if count_doc == 0:
                    logger.debug(f'Документов нет, пропускаем проверки')
                    continue  # Переходим к следующему uid

                if pages > 1:
                    # for uid in uids:
                    """Обрабатывает страницы в зависимости от количества страниц."""
                    max_page = min(pages, 5)  # Ограничиваем максимальное количество страниц до 5
                    for page in range(2, max_page + 1):
                        params['page'] = str(page)  # Обновляем значение ключа 'page'
                        logger.debug(f'Новый список параметров params - {params}')
                        logger.debug(
                            f'Получили новые параметры для отправки запроса - data_snippets_search '
                            f'{params}')
                        request_get(token, endpoint, type_snippet, headers_get, params)
                        logger.debug(f'Получили response')
                    params['page'] = 1

    try:
        type_endpoint = (
            endpoints['legal_person_card_endpoint'] if type_profile == "Сниппеты ЮЛ"
            else endpoints['physical_person_card_endpoint']
        )

        params_tabs_search = Snippets.tabs_search
        params_tabs = Snippets.tabs
        params_search_snippet = Snippets.snippets_search
        params_snippet = Snippets.snippets_default

        tabs_endpoint = endpoint_with_uid(type_endpoint, uids, 'Табы')
        snippets_scipub_endpoint = endpoint_with_uid(type_endpoint, uids, 'Сниппет публикаций')
        snippets_niokr_endpoint = endpoint_with_uid(type_endpoint, uids, 'Сниппет НИОКР')
        snippets_diss_endpoint = endpoint_with_uid(type_endpoint, uids, 'Сниппет Диссертации')
        snippets_patent_endpoint = endpoint_with_uid(type_endpoint, uids, 'Сниппет Патенты')
        snippets_grant_endpoint = endpoint_with_uid(type_endpoint, uids, 'Сниппет Гранты')
        snippets_rid_endpoint = endpoint_with_uid(type_endpoint, uids, 'Сниппет РИД')
        snippets_ikrbs_endpoint = endpoint_with_uid(type_endpoint, uids, 'Сниппет ИКРБС')
        snippets_ckp_endpoint = endpoint_with_uid(type_endpoint, uids, 'Сниппет ЦКП')
        snippets_usu_endpoint = endpoint_with_uid(type_endpoint, uids, 'Сниппет УНУ')

        snippet_data = {
            'Табы': (params_tabs, params_tabs_search, tabs_endpoint, 'табы'),
            'Публикации': (params_search_snippet, params_snippet, snippets_scipub_endpoint, 'публикации'),
            'НИОКР': (params_search_snippet, params_snippet, snippets_niokr_endpoint, 'НИОКРы'),
            'Диссертации': (params_search_snippet, params_snippet, snippets_diss_endpoint, 'диссертации'),
            'Патенты': (params_search_snippet, params_snippet, snippets_patent_endpoint, 'патенты'),
            'Гранты': (params_search_snippet, params_snippet, snippets_grant_endpoint, 'гранты'),
            'РИД': (params_search_snippet, params_snippet, snippets_rid_endpoint, 'РИДы'),
            'ИКРБС': (params_search_snippet, params_snippet, snippets_ikrbs_endpoint, 'ИКРБС'),
            'ЦКП': (params_search_snippet, params_snippet, snippets_ckp_endpoint, "ЦКП"),
            'УНУ': (params_search_snippet, params_snippet, snippets_usu_endpoint, "УНУ"),
        }

        for snippet_type, (params_search, params_default, endpoint, snippet_name) in snippet_data.items():
            if endpoint is None:
                logger.error(f"Эндпоинт - {snippet_name} не найден")
                continue
            logger.info(f"Проверяю {type_profile} - {snippet_name} по запросу")
            main(token, params_search, endpoint, f"{type_profile} - {snippet_name} по запросу", type_profile)
            logger.info(f"Проверяю {type_profile} - {snippet_name} без запроса")
            main(token, params_default, endpoint, f"{type_profile} - {snippet_name} без запроса", type_profile)


    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")


def sciwork_and_get_uids_cards(token, endpoint, type, data):
    """Собирает UID карточек сущностей из поиска по документам (максимум 5 страниц, 200 UID)."""
    try:
        uids = []
        max_uids = 200
        for page in range(1, 6):  # Итерируемся по страницам с 1 по 5
            data['page'] = str(page)
            response = request_get(token, endpoint, type, headers_get_head_options, data)
            logger.debug(f"response - {response}")

            count_doc = int(response.get('count', 0))
            logger.debug(f'Общее количество документов - {count_doc}')

            if count_doc == 0:
                break  # Прерываем цикл, если документов нет

            for result in response.get('results', []):
                uid = result.get('uid')
                if uid:  # проверяем что uid не пустой
                    uids.append(uid)
                if len(uids) >= max_uids:
                    return uids  # Возвращаем UID, если достигли лимита
            if count_doc <= (page * 20):  # Прерываем, если все документы уже получены
                break  # проверяем что количество документов меньше или равно чем количество на текущей странице

        return uids

    except requests.exceptions.HTTPError as httperr:
        logger.error(f'{httperr} - Ошибка при получении ответа от endpoint - {endpoint} с параметрами: {data}')
    except Exception as err:
        logger.error(f'{type} - Произошла ошибка: {err} во время отправки запроса на endpoint - {endpoint}')


def sciwork(token):
    try:
        logger.info(f"Начинаю тесты Таба в Поиске по документам")
        # Главная
        endpoint = endpoints['sciwork_tabs_endpoint']
        data = Search.search['search']
        type = 'Таб - Поиск по документам'
        response = request_get(token, endpoint, type, headers_get_head_options, data)
        curr_keys = [key for key, value in response['results'].items() if key.startswith('curr_') and value > 0]
        logger.info(f"Список сущностей по запросу - {curr_keys}")

        logger.info(f"Начинаю тесты сниппетов в Поиске по документам")
        uids_dict = {}
        for type_snippet, endpoint in Sciwork.data.items():
            data_sciwork = Search.sciwork_search.copy()
            uids = sciwork_and_get_uids_cards(token, endpoint, type_snippet, data_sciwork)
            uids_dict[type_snippet] = uids
        logger.info(f"Список уидов карточек - {uids_dict}")
        return uids_dict, curr_keys
    except requests.exceptions.HTTPError as httperr:
        logger.error(f'{httperr} - Ошибка при получении ответа от endpoint - {endpoint}  с параметрами: {data}')
    except Exception as err:
        logger.error(f'{type} - Произошла ошибка: {err} во время отправки запроса на endpoint - {endpoint}')


def doccard(token, uids_cards, card_types):
    global params
    for sciwork_type, card_type, log_type in card_types:
        logger.debug(f"Забираем uid-ы карточек и создаем параметры для отправки запроса для {log_type}")
        value = uids_cards.get(sciwork_type)
        if value is not None:
            params = []
            for uid in value:
                card_dict = {
                    'uid': uid,
                    'type': card_type
                }
                params.append(card_dict)
            if not params:
                logger.debug(f"{sciwork_type} по запросу нет документов. Пропускаем проверки")
        logger.debug(f'Параметры для {log_type} - {params}')
        for param in params:
            request_get(token, endpoints['getDocCard_endpoint'], log_type, headers_get_head_options, param)
        if card_type == 'scipub':
            uids_sci_pubs = value
            # Динамика цитирований в публикации
            endpoint_citation_dynamics = endpoint_with_uid(endpoints['citation_dynamics'], uids_sci_pubs,
                                                           'Динамика цитирования публикации')
            for endpoint in endpoint_citation_dynamics:
                for _ in Cards.Data_citation_dynamics_scipub:
                    request_get(token, endpoint, _['type'], headers_get_head_options, _['params'])


def sciwork_filter_advanced_search(token, endpoint, type, data_search, filters):
    logger.debug(f"Создаем список из параметров, содержащий тип фильтра, поисковый запрос и "
                 f"параметры расширенного поиска")
    dates = []
    types = [item.split('_')[1] for item in filters]
    logger.debug(f'Будем проверять фильтры только в - {types}')
    for filter_name, filter_value in Filters.types.items():
        for filter_key, filter_val in filter_value.items():
            for item in data_search:
                dates.append({filter_key: filter_val, **item})
    logger.debug(f"Параметры для фильтров с расширенными параметрами - {dates}")
    for data in dates:
        if data['types'] in types:
            request_get(token, endpoint, type, data)