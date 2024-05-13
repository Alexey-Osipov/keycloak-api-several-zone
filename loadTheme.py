import glob
import os
import requests
import json
import warnings
from cryptography.utils import CryptographyDeprecationWarning
import paramiko
from scp import SCPClient
from sys import argv

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)


class Load_Theme:
    def __init__(self, admin_name, admin_password):
        self.admin_name = admin_name
        self.admin_password = admin_password

    def loadTheme(self, server_load, theme_Name, themeName, username_server):
        # Путь к локальному файлу для передачи
        local_file_path = f'./temp_files/theme/{theme_Name}/{themeName}.zip'

        # Путь на удаленном сервере, куда нужно передать файл
        remote_file_path = '/tmp'

        # Устанавливаем права на файл перед его передачей
        os.chmod(local_file_path, 0o777)

        # Команда для распаковки архивного файла на удаленном сервере
        command = f'echo {admin_password} | sudo -S -iu {username_server} unzip {remote_file_path}/{themeName}.zip -d /data/fedsso/keycloak_cin/current/themes'

        # Подключение к серверу через SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_load, 22, username=self.admin_name, password=self.admin_password)

        # Передача файла на удаленный сервер
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(local_file_path, remote_file_path)
            print(f'Архив загружен на сервер {server_load}.')

        # Выполнение команды с sudo на удаленном сервере
        stdin, stdout, stderr = ssh.exec_command(command)

        # Проверяем, возник ли конфликт при распаковке архива
        output = stderr.read().decode()

        if "replace" in output:
            # Если обнаружен конфликт, выводим сообщение
            print(f"Текущая версия темы уже есть на сервере {server_load}.")
        else:
            # Если конфликт не обнаружен, выводим результаты выполнения команды
            print(f'Тема распакована в themes на сервере {server_load}.')
            # print(output)
        ssh.close()


class KeyCloak_Token:
    def __init__(self, admin_name, admin_password, port='8080'):
        self.admin_name = admin_name
        self.admin_password = admin_password
        self.port = port

    def getTokenInfo(self, server):
        url = 'http://{0}:{1}/auth/realms/master/protocol/openid-connect/token'.format(server, self.port)
        response = requests.request('POST', url, data={
            'client_id': 'admin-cli',
            'grant_type': 'password',
            'username': self.admin_name,
            'password': self.admin_password
        },
                                    headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if response.status_code != 200:
            # print("Error")
            raise SystemExit(401)
        else:
            return response.json()

    def getClientInfo(self, server, accessToken, clientName, realm):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/clients?clientId={3}'.format(server, self.port, realm, clientName)
        response = requests.request('GET', url, headers={'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 200:
            print(
                f"Не могу получить информацию по клиенту {clientName} на сервере {name_tz}. Статус: {response.status_code} Ответ "
                f"сервера: {response.request.headers}")
            print(f"Что-то пошло не так. В следующий раз точно повезёт!")
            raise SystemExit(400)
        else:
            return response.json()

    def putClientTheme(self, server, accessToken, clientID, realm):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/clients/{3}'.format(server, self.port, realm, clientID)
        response = requests.request('PUT', url, json={
            "attributes": {
                "login_theme": themeName
            }
        },
                                    headers={'Content-Type': 'application/json',
                                             'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 204:
            print(
                f"Не могу активировать тему у клиента {clientName} на сервере {name_tz}. Статус: {response.status_code} Ответ "
                f"сервера: {response.request.headers}")
            raise SystemExit(400)
        else:
            print(f"Тема {themeName} успешно применена у клиента {clientName} на сервере {name_tz}")
            # return response.json()


admin_name = argv[1]  # Список ТЗ выбранных в чекбоксе
admin_password = argv[2]  # Список ТЗ выбранных в чекбоксе
username_server = "fedsso"

kc = KeyCloak_Token(admin_name, admin_password)
ls = Load_Theme(admin_name, admin_password)

realm = argv[3]  # Выбранный Рилм
theme_Name = argv[4]  # Имя Темы

theme_directory = f"temp_files/theme/{theme_Name}"
json_files = glob.glob(os.path.join(theme_directory, "*.json"))

if json_files:
    json_file_path = json_files[0]
    with open(json_file_path) as values:
        data = json.load(values)
else:
    print(f"Файл .json не найден в каталоге {theme_directory}")

servers = data["servers"]  # Список ТЗ выбранных в чекбоксе
themeName = data["themeName"]  # Имя Темы
server_all = []
port = '8080'
clientName = data["clientName"]  # Имя Клиента
containerId = realm

for server in servers:
    # Load archive theme on server
    if server == "127.0.0.1":
        server_all = ["127.0.0.1", "127.0.0.1"]
        name_tz = "localhost"
    elif server == "localhost":
        server_all = ["127.0.0.1", "127.0.0.1"]
        name_tz = "localhost_1"
    print(f"==========================================================================================================")
    # Get admin token
    print("Получаем токен...")
    tokenInfo = kc.getTokenInfo(server)
    if "access_token" not in tokenInfo:
        print(f"Возникла ошибка: {tokenInfo.get('error_description')}")
        raise SystemExit
    accessToken = tokenInfo.get('access_token')
    # Get Client Information
    clientInfo = kc.getClientInfo(server, accessToken, clientName, realm)
    if len(clientInfo) > 0:
        for client in clientInfo:
            clientID = client.get('id')
            print(f"Загружаем тему на сервера тестовой зоны {name_tz}")
            for server_load in server_all:
                # Upload the theme to the server from the server_all list
                ls.loadTheme(server_load, theme_Name, themeName, username_server)
            print(f"Пытаюсь применить тему...")
            # Apply theme on client
            kc.putClientTheme(server, accessToken, clientID, realm)
    else:
        print(f"Клиента {clientName} нет на тестовой зоне {name_tz}")
