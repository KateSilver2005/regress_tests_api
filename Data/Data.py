from .endpoints import *


class Search:
    search = {
        'search': {'search': 'CRISPR'},
        # 'search': {'search': 'TRNA ANTICODON CLEAVAGE BY TARGET-ACTIVATED CRISPR-CAS13A EFFECTOR'}, # запрос для поиска по компетенциям
        'search_org': {'search': 'Сеченовский университет'},  # запрос для поиска по справочнику организаций
        'search_person': {'search': 'Макаров Валентин Владимирович'}  # запрос для поиска по справочнику ученых
    }
    # поиск по документам
    sciwork_search = {**search['search'], **{'page': '1'}}


# Расширенный поиск
distances = list(range(0, 11))
advanced_search = {
    'fulltext': {**Search.search['search'], 'fulltext': 'true'},
    'synonym': {**Search.search['search'], 'synonym': 'true'},
    'distance': [{**Search.search['search'], 'distance': distance} for distance in distances],
    'synonym_fulltext': {**Search.search['search'], 'synonym': 'true', 'fulltext': 'true'},
    'fulltext_distance': [{**Search.search['search'], 'fulltext': 'true', 'distance': distance} for distance in
                          distances]
}

# class Sciwork:



class Raiting:
    # Список значений сортировки для рейтингов и поиска по ФЛ/ЮЛ (полный список кейсов)
    orderings = ['-summary', 'summary', '-sci_pub', 'sci_pub', '-niokr', 'niokr', '-diss', 'diss', '-grant', 'grant',
                 '-patent', 'patent', '-ckp', 'ckp', '-usu', 'usu', '-rid', 'rid', '-ikrbs', 'ikrbs', '-name', 'name',
                 '-profile_percent', 'profile_percent']

    # Индекс Хирша для ФЛ
    hirsh = ['True', 'False']

    # Для быстроты тестирования (проход не по всем кейсам)
    # # Список значений сортировки для рейтингов и поиска по ФЛ/ЮЛ (минимальный список кейсов)
    # orderings = ['-curr_summary', 'curr_summary']
    # # Индекс Хирша для ФЛ
    # hirsh = ['True', 'False']


class Graphs:
    # Период для графов АК и КО
    years = [
        {'first_year': '2000', 'last_year': '2024'},
        {'first_year': '2000', 'last_year': '2008'},
        {'first_year': '2008', 'last_year': '2014'},
        {'first_year': '2014', 'last_year': '2018'},
        {'first_year': '2018', 'last_year': '2019'},
        {'first_year': '2019', 'last_year': '2020'},
        {'first_year': '2020', 'last_year': '2021'},
        {'first_year': '2021', 'last_year': '2022'},
        {'first_year': '2022', 'last_year': '2023'},
        {'first_year': '2023', 'last_year': '2024'}
    ]

    # Минимальный размер группы для графов
    limits = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '20', '50', '100']

    graph_co_authors = [{'limit': limit} for limit in limits]
    graph_co_authors_search = [{**Search.search['search'], **{'limit': limit}} for limit in limits]


class Licenses:
    """
    Сортировка в лицензиях ЮЛ:
    - issue_date - дата выдачи лицензии (-issue_date от новой (или null) до самой поздней)
    - issue_authority - орган выдавший лицензию
    -series_and_number - серия и номер лицензии
    -valid_from - период действия лицензии
    -activities - лицензируемые виды деятельности
    -suspend_authority - орган приостановивший лицензию
    -suspend_date - период приостановления лицензии
    """
    orderings_licenses = ['-issue_date', 'issue_date', '-issue_authority', 'issue_authority', '-series_and_number',
                          'series_and_number', '-valid_from', 'valid_from', '-activities', 'activities',
                          '-suspend_authority',
                          'suspend_authority', '-suspend_date', 'suspend_date']

    licenses = [
        {'limit': '15', 'offset': '0', 'ordering': ordering} for ordering in orderings_licenses]


class Ki_Lp_ki_mi:
    orderings_ki_lp = ['-date_end', 'date_end', '-number_rki', 'number_rki', '-grls_view', 'grls_view',  '-purpose',
                       'purpose',  '-state', 'state',  '-name_lp', 'name_lp',  '-area_of_use', 'area_of_use']
    orderings_ki_mi = ['-name', 'name', '-kinds', 'kinds', '-manufacturer_org_name', 'manufacturer_org_name',
                       '-legal_entity_name', 'legal_entity_name', '-permission_number', 'permission_number',
                       '-permission_date', 'permission_date', '-status_date', 'status_date']

    ki_lp = [{'limit': '5', 'offset': '0', 'ordering': ordering, **Search.search['search']} for ordering in orderings_ki_lp]

    ki_mi = [{'limit': '5', 'offset': '0', 'status_date': '2018', 'ordering': ordering} for ordering in orderings_ki_mi]



class Profile:
    # Профиль ФЛ
    # physical_person_card_search = {**Search.search['search'], **{'type': 'doc'}}  # по запросу
    # physical_person_card = {'type': 'doc'}  # без запроса
    physical_person_duplicates = {'ordering': 'person_name'}  # список дублей


class Snippets:
    # по запросу по всем сущностям
    tabs_search = {'type': 'doc'}
    tabs = {**Search.search['search'], 'type': 'doc'}
    snippets_search = {**Search.search['search'], **{'type': 'doc', 'page': '1'}}
    # без запроса по всем сущностям
    snippets_default = {'type': 'doc', 'page': '1'}


class Cards:
    card_types = [
        ('Поиск по документам - Публикации', 'scipub', 'Карточка публикации'),
        ('Поиск по документам - НИОКР', 'nioktr', 'Карточка НИОКР'),
        ('Поиск по документам - Диссертации', 'diss', 'Карточка Диссертации'),
        ('Поиск по документам - Гранты', 'grant', 'Карточка Гранта'),
        ('Поиск по документам - Патенты', 'patent', 'Карточка Патенты'),
        ('Поиск по документам - ЦКП', 'ckp', 'Карточка ЦКП'),
        ('Поиск по документам - УНУ', 'usu', 'Карточка УНУ'),
        ('Поиск по документам - РИД', 'rid', 'Карточка РИД'),
        ('Поиск по документам - ИКРБС', 'ikrbs', 'Карточка ИКРБС'),
    ]
    Data_citation_dynamics_scipub = [
        {'params': {'cumulative': 'false'}, 'type': 'Динамика цитирования (распределенная) в публикации'},
        {'params': {'cumulative': 'true'}, 'type': 'Динамика цитирования (накопительная) в публикации'},
    ]

class Sciwork:
    data = {
            "Поиск по документам - Публикации": endpoints['sciwork_scipub_endpoint'],
            "Поиск по документам - НИОКР": endpoints['sciwork_niokr_endpoint'],
            "Поиск по документам - Диссертации": endpoints['sciwork_diss_endpoint'],
            "Поиск по документам - Гранты": endpoints['sciwork_grant_endpoint'],
            "Поиск по документам - Патенты": endpoints['sciwork_patent_endpoint'],
            "Поиск по документам - ЦКП": endpoints['sciwork_ckp_endpoint'],
            "Поиск по документам - УНУ": endpoints['sciwork_usu_endpoint'],
            "Поиск по документам - РИД": endpoints['sciwork_rid_endpoint'],
            "Поиск по документам - ИКРБС": endpoints['sciwork_ikrbs_endpoint']
            }


class Filters:
    types = {
        'scipub': {'types': 'scipub'},
        'niokr': {'types': 'niokr'},
        'diss': {'types': 'diss'},
        'grant': {'types': 'grant'},
        'patent': {'types': 'patent'},
        'rid': {'types': 'rid'},
        'ikrbs': {'types': 'ikrbs'},
        'ckp': {'types': 'ckp'},
        'usu': {'types': 'usu'}
    }
    data = {
        "curr_scipub_count": {**Search.search['search'], **types['scipub']},
        "curr_niokr_count": {**Search.search['search'], **types['niokr']},
        "curr_diss_count": {**Search.search['search'], **types['diss']},
        "curr_grant_count": {**Search.search['search'], **types['grant']},
        "curr_patent_count": {**Search.search['search'], **types['patent']},
        "curr_ckp_count": {**Search.search['search'], **types['ckp']},
        "curr_usu_count": {**Search.search['search'], **types['usu']},
        "curr_rid_count": {**Search.search['search'], **types['rid']},
        "curr_ikrbs_count": {**Search.search['search'], **types['ikrbs']}
    }
