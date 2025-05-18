endpoints = {
        'token_endpoint': 'login/',  # Авторизация в ИАС
        'map_endpoint': 'map/legal-person/',  # Карта по запросу
        'rating_legal_person_in_map_endpoint': 'map/legal-person/detail_info/',  # Рейтинг ЮЛ по запросу в карте
        'chart_endpoint': 'service/charts/',  # Статистика по запросу
        'rating_legal_person_endpoint': 'organizations/',  # Рейтинг ЮЛ по запросу, Поиск ЮЛ
        'rating_physical_person_endpoint': 'persons/',  # Рейтинг ФЛ по запросу, Поиск по ФЛ
        'synonym_endpoint': 'synonym/',  # синонимы
        'graph_author_teams_endpoint': 'service/graph/author-teams/scipub/',  # граф соавторов и АК
        'graph_organization_teams_endpoint': 'service/graph/organization-teams/scipub/',  # граф КО
        'legal_person_card_endpoint': 'organizations/card/',  # Профиль ЮЛ
        'physical_person_card_endpoint': 'persons/card/',   # Профиль ФЛ
        'getDocCard_endpoint': 'card/getDocCard/',  # Карточки сущностей
        'citation_dynamics': 'sciwork/sci_pub/',  # Динамика цитирования (карточка публикации)
        'sciwork_tabs_endpoint': 'sciwork/tabs/',  # табы в поиске по документам
        'sciwork_scipub_endpoint': 'sciwork/scipub/',  # Поиск по документам - публикации
        'sciwork_niokr_endpoint': 'sciwork/niokr/',  # Поиск по документам - ниокр
        'sciwork_diss_endpoint': 'sciwork/diss/',  # Поиск по документам - диссертации
        'sciwork_grant_endpoint': 'sciwork/grant/',  # Поиск по документам - гранты
        'sciwork_patent_endpoint': 'sciwork/patent/',  # Поиск по документам - патенты
        'sciwork_ckp_endpoint': 'sciwork/ckp/',  # Поиск по документам - цкп
        'sciwork_usu_endpoint': 'sciwork/usu/',  # Поиск по документам - уну
        'sciwork_rid_endpoint': 'sciwork/rid/',  # Поиск по документам - рид
        'sciwork_ikrbs_endpoint': 'sciwork/ikrbs/',  # Поиск по документам - икрбс
        'sciwork_filters': 'sciwork/filter/schema/',  # Поиск по документам - фильтры
        'result_document_generate_endpoint': 'document/search-result-document/',  # Формирование файла выгрузки Excel
        'result_document_load_endpoint': 'documents/user-documents/', # Выгрузка файла Excel + размещение файла в Моих документах
        'person_self_endpoint': 'getPersonSelf/',  # Личный кабинет, Мой профиль
        'organization_self_endpoint': 'getOrganizationSelf/',  # Личный кабинет, Моя организация
        'user_documents_endpoint': 'document/user-documents/',  # Личный кабинет, Мои документы
        'main_page_charts_endpoint': 'service/charts/main-page/',  # Диаграмма Статистика "Используемые источники данных за последние 10 лет" на Главной
        'work_counts_endpoint': 'reports/work-counts/',  # Информация для пользователей на Главной странице
        'news_endpoint': 'news/new/'  # Бегущая строка новостей
    }