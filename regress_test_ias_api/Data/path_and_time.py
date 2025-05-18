import os
from pathlib import Path
import pendulum

class AllForTasks:
    filename = 'regress_run.log'
    # secondfile = 'report_smoke_history.log'
    # PATH = '/mnt/share/smoke_test_ias'
    current_file = Path(__file__)
    file_path = os.path.join(current_file.parent.parent, 'logs', filename)
    # secondfile_path = os.path.join(current_file.parent, secondfile)

    # Получаем текущее время
    now_old = pendulum.now()
    # Прибавляем 3 часа к текущему времени
    now_new = now_old.add(hours=3)
    # Преобразуем новое время в строку в формате "день-месяц-год час:минута:секунда"
    now = now_new.to_datetime_string()

# Mattermost
# MATTERMOST_ID = 'e7udx6mnyprsub3qq74yaru9gc'  # id канала ИАС
MATTERMOST_ID = '6dj8ezyop7r3fq4e1rfosr5cnh'  # id канала mytest_kanal
connection_id = 're4kokm7cb83immrtryih985mc'
connection_host = 'https://mt.pak-cspmz.ru'
password = 'toen7szimfbidfnebmkr5ax6qr'

# Login
login_data = {
        'username': 'qa_robot',
        'password': '@WSX2wsx'
    }

PROD = 'https://nir.pak-cspmz.ru/api/v2/'
STAGE = 'https://nir-stage.pak-cspmz.ru/api/v2/'
TEST = 'https://nirtest-portal.cspfmba.ru/api/v2/'