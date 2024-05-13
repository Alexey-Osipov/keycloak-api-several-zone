import requests
import uuid
import json
from sys import argv


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
        return response.json()

    def getClientInfo(self, server, accessToken, clientName, realm):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/clients?first=0&max=51&clientId={3}&search=true'.format(server,
                                                                                                            self.port, realm,
                                                                                                            clientName)
        response = requests.request('GET', url, headers={'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 200:
            print(
                f"Не могу получить информацию по клиенту {clientName} на сервере {server}. Статус: {response.status_code} Ответ "
                f"сервера: {response.request.headers}")
            print(f"Что-то пошло не так. В следующий раз точно повезёт!")
            raise SystemExit(400)
        else:
            return response.json()

    def getClientRole(self, server, accessToken, clientID, realm):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/clients/{3}/roles'.format(server, self.port, realm, clientID)
        response = requests.request('GET', url, headers={'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 200:
            print(f"Поиск ролей у клиента {clientName} на сервере {server}. Статус: {response.status_code} Ответ "
                  f"сервера: {response.request.headers}")
            print(f"Что-то пошло не так. В следующий раз точно повезёт!")
            raise SystemExit(400)
        else:
            return response.json()


admin_name = argv[1]  # Список ТЗ выбранных в чекбоксе
admin_password = argv[2]  # Список ТЗ выбранных в чекбоксе

kc = KeyCloak_Token(admin_name, admin_password)
client_secret = str(uuid.uuid4())

realm = argv[3]  # Выбранный Рилм
clientName = argv[4]  # Имя клиента

with open(f"temp_files/find/client/{clientName}.json") as values:
    data = json.load(values)

servers = data["servers"]  # Список ТЗ выбранных в чекбоксе
server_to_tz_mapping = {
    "127.0.0.1": "localhost"
}
containerId = realm

for server in servers:
    name_tz = server_to_tz_mapping.get(server, None)
    print("===========================================================================================================")
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
            description = client.get('description')
            print(f"Клиент {client.get('clientId')} был создан по заявке {description} на Тестовой Зоне: {name_tz} в "
                  f"Рилме: {realm}")
            clientRoles = kc.getClientRole(server, accessToken, clientID, realm)
            # Перебор значений клиента и ролей
            for role in clientRoles:
                role_name = role.get('name')
                role_description = role.get('description', 'Описание не добавлено!')
                print(f"У клиента {client.get('clientId')} есть роль: {role_name} description {role_description}")
    else:
        print(f"Клиента {clientName} нет на Тестовой Зоне: {name_tz} в Рилме: {realm}")
