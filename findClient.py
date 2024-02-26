import requests
import uuid
import json
from sys import argv

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
            print(f"Не могу получить информацию по клиенту {clientName} на сервере {server}. Статус: {response.status_code} Ответ "
                  f"сервера: {response.request.headers}")
            print(f"Что-то пошло не так. В следующий раз точно повезёт!")
            raise SystemExit(400)
        else:
            return response.json()


username = argv[1]      # Список ТЗ выбранных в чекбоксе
password = argv[2]      # Список ТЗ выбранных в чекбоксе

kct = KeyCloak_Token(username, password)
client_secret = str(uuid.uuid4())

realm = argv[3]         # Выбранный Рилм
clientName = argv[4]    # Имя клиента


with open(f"temp/find/client/{clientName}.json") as values:
    data = json.load(values)

servers = data["servers"]               # Список ТЗ выбранных в чекбоксе
port = '8080'
containerId = realm

for server in servers:
    print("===========================================================================================================")
    # Get admin token
    print("Получаем токен...")
    tokenInfo = kct.getTokenInfo(server)
    accessToken = tokenInfo.get('access_token')
    print("Успех! Токен получен")
    # Get Client Information
    clientInfo = kct.getClientInfo(server, accessToken, clientName, realm)
    if len(clientInfo) > 0 and clientInfo[0].get('clientId') == clientName:
        clientID = clientInfo[0].get('id')
        description = clientInfo[0].get('description')
        print(f"Клиент {clientName} был создан по заявке {description} на сервере {server}")
    else:
        print(f"Клиента {clientName} нет на сервере {server}")