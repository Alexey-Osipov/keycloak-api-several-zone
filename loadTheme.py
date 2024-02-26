import requests
import json
import paramiko
from scp import SCPClient
from sys import argv


class Load_Theme:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def loadTheme(self, server):
        # Путь к локальному файлу для передачи
        local_file_path = f'./temp/theme/{themeName}/{themeName}.zip'

        # Путь на удаленном сервере, куда нужно передать файл
        remote_file_path = '/tmp/'

        # Команда для распаковки архивного файла на удаленном сервере
        command = f'sudo -iu {username_server} unzip {remote_file_path} -d /data/fedsso/'

        # Подключение к серверу через SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server, 22, username, password)

        # Передача файла на удаленный сервер
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(local_file_path, remote_file_path)

        # Выполнение команды с sudo на удаленном сервере
        stdin, stdout, stderr = ssh.exec_command(command)

        # Вывод результатов выполнения команды
        print(stdout.read().decode())
        print(stderr.read().decode())

        # Закрытие подключения
        ssh.close()


class KeyCloak_Token:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def getTokenInfo(self, server):
        url = 'http://{0}:{1}/auth/realms/master/protocol/openid-connect/token'.format(server, port)
        response = requests.request('POST', url, data={
            'client_id': 'admin-cli',
            'grant_type': 'password',
            'username': self.username,
            'password': self.password
        },
                                    headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if response.status_code != 200:
            # print("Error")
            raise SystemExit(401)
        else:
            return response.json()

    def getClientInfo(self, server, accessToken, clientName, realm):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/clients?clientId={3}'.format(server, port, realm, clientName)
        response = requests.request('GET', url, headers={'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 200:
            print(
                f"Не могу получить информацию по клиенту {clientName} на сервере {server}. Статус: {response.status_code} Ответ "
                f"сервера: {response.request.headers}")
            print(f"Что-то пошло не так. В следующий раз точно повезёт!")
            raise SystemExit(400)
        else:
            return response.json()

    def putClientTheme(self, server, accessToken, clientID, realm):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/clients/{3}'.format(server, port, realm, clientID)
        response = requests.request('PUT', url, data={
            "attributes": {
                "login_theme": themeName
            }
        },
                                    headers={'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 204:
            print(
                f"Не могу активировать тему у клиента {clientName} на сервере {server}. Статус: {response.status_code} Ответ "
                f"сервера: {response.request.headers}")
            raise SystemExit(400)
        else:
            print(f"Тема {themeName} успешно применена у клиента {clientName} на сервере {server}")
            return response.json()


username = argv[1]  # Список ТЗ выбранных в чекбоксе
password = argv[2]  # Список ТЗ выбранных в чекбоксе

kc = KeyCloak_Token(username, password)
ls = Load_Theme(username, password)


realm = argv[3]  # Выбранный Рилм
themeName = argv[4]  # Имя Темы

with open(f"temp/theme/{themeName}.json") as values:
    data = json.load(values)

servers = data["servers"]           # Список ТЗ выбранных в чекбоксе
port = '8080'
clientName = data["clientName"]     # Имя Клиента
containerId = realm

for server in servers:
    print("===========================================================================================================")
    # Load archive theme on server
    ls.loadTheme(server)
    # Get admin token
    print("Получаем токен...")
    tokenInfo = kc.getTokenInfo(server)
    accessToken = tokenInfo.get('access_token')
    print("Успех! Токен получен")
    # Get Client Information
    clientInfo = kc.getClientInfo(server, accessToken, clientName, realm)
    clientID = clientInfo[0].get('id')
    print(f"Получили ClientID: {clientID}")
    # Put Client Theme
    putTheme = kc.putClientTheme(server, accessToken, clientID, realm)
