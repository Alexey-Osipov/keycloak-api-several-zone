import random
import requests
import json
import os
from sys import argv



class KeyCloak:
    def __init__(self, admin_name, admin_password):
        self.admin_name = admin_name
        self.admin_password = admin_password

    def getTokenInfo(self, server):
        url = 'http://{0}:{1}/auth/realms/master/protocol/openid-connect/token'.format(server, port)
        response = requests.request('POST', url, data={
            'username': self.admin_name,
            'password': self.admin_password,
            'grant_type': 'password',
            'client_id': 'admin-cli'
        },
                                    headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if response.status_code != 200:
            # print("Error")
            raise SystemExit(401)
        else:
            return response.json()


    def createUser(self, server, accessToken, userName, realm, owner, purpose, task, enabled='true', temporary='false'):
        # Проверяем наличие файла пользователя
        user_file_path = f"temp/user/{userName}.json"
        if os.path.exists(user_file_path):
            with open(user_file_path, 'r') as file:
                data = json.load(file)
                if "userPass" in data:
                    password = data.get("userPass", generatePassword())
        if password == "":
            password = generatePassword()

        url = 'http://{0}:{1}/auth/admin/realms/{2}/users'.format(server, port, realm)
        response = requests.request('POST', url, json={
            "username": userName,
            "enabled": enabled,
            "credentials": [{
                "type": "password",
                "temporary": temporary,
                "value": password
            }],
            "attributes": {
                "owner": owner,
                "purpose": purpose,
                "task": task
            }
        },
                                    headers={'Content-Type': 'application/json',
                                             'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code == 409:
            print(f"Пользователь {userName} уже существует в реалме {realm} на сервере {server}")
            return response.status_code
        if response.status_code != 201:
            # print(response.request.url)        # - раскомменти для дебаггинга
            # print(response.request.body)       # - раскомменти для дебаггинга
            # print(response.request.headers)    # - раскомменти для дебаггинга
            print(f"Не получилось создать пользователя {userName} на сервере {server} Статус: {response.status_code} Ответ сервера: {response.request.body}")
        else:
            print(f"Пользователь {userName} успешно создан на сервере {server}. Пароль: {password}")
            return response.status_code

    def getClientInfo(self, server, accessToken, clientName, realm):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/clients?clientId={3}'.format(server, port, realm, clientName)
        response = requests.request('GET', url, headers={'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 200:
            print(f"Не могу получить информацию по клиенту {clientName} на сервере {server}. Статус: {response.status_code} Ответ сервера: {response.request.body}")
            print(f"Что-то пошло не так. В следующий раз точно повезёт!")
            raise SystemExit(400)
        else:
            return response.json()

    def findUserByParameters(self, server, accessToken, search, realm, userName = '',
                             briefRepresentation='true', email='', firstName='', lastName='', max=5):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/users'.format(server, port, realm)
        response = requests.request('GET', url, params={
                                                                    "username": userName,
                                                                    "briefRepresentation": briefRepresentation,
                                                                    "email": email,
                                                                    "firstName": firstName,
                                                                    "lastName": lastName,
                                                                    "max": max,
                                                                    "search": search
                                                                },
                                    headers={'Content-Type': 'application/json',
                                             'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 200:
            # print(response.request.url)        # - раскомменти для дебаггинга
            # print(response.request.body)       # - раскомменти для дебаггинга
            # print(response.request.headers)    # - раскомменти для дебаггинга
            print(f"Не могу найти информацию по пользователю {userName} на сервере {server}. Статус: {response.status_code} Ответ "
                  f"сервера: {response.request.headers}")
            print(f"Что-то пошло не так. В следующий раз точно повезёт!")
        else:
            return response.json()

    def getUserRoles(self, server, accessToken, userID, realm):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/users/{3}/role-mappings'.format(server, port, realm, userID)
        response = requests.request('GET', url, headers={'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 200:
            print(f"Не могу получить информацию о ролях, назначенных пользователю {userName} на сервере {server}. "
                  f"Статус: {response.status_code} Ответсервера: {response.request.headers}")
            print(f"Что-то пошло не так. В следующий раз точно повезёт!")
            raise SystemExit(400)
        else:
            return response.json()

    def getClientLevelRoles(self, server, accessToken, userID, clientID, realm):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/users/{3}/role-mappings/clients/{4}/available'.format(server, port, realm,
                                                                                                       userID, clientID)
        response = requests.request('GET', url, headers={'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 200:
            # print(response.request.url)        # - раскомменти для дебаггинга
            # print(response.request.body)       # - раскомменти для дебаггинга
            # print(response.request.headers)    # - раскомменти для дебаггинга
            print(f"Не могу получить информацию о ролях клиента {clientName} на сервере {server}. "
                  f"Статус: {response.status_code} Ответсервера: {response.request.headers}")
        else:
            return response.json()

    def setClientRoleToUser(self, server, accessToken, clientID, roleName, userID, role, realm):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/users/{3}/role-mappings/clients/{4}'.format(server, port, realm, userID,
                                                                                             clientID)
        name_role = role['name']
        response = requests.request('POST', url, json=[role],
                                    headers={'Content-Type': 'application/json',
                                             'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code == 409:
            print(f"Роли {name_role} уже назначена пользователю {userName}")
            return response.status_code
        if response.status_code != 204:
            print(f"Не могу назначить роли {name_role} пользователю {userName} на сервере: {server}. "
                  f"Статус: {response.status_code} Ответсервера: {response.request.headers}")
        else:
            print(f"Роли {name_role} успешно назначена пользователю {userName} на сервере {server}")
            return response.status_code


def generatePassword(length=15):
    chars = '*!&$#?=@abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    password = ''
    for _ in range(length):
        password += random.choice(chars)
    return password


admin_name = argv[1]      # Список ТЗ выбранных в чекбоксе
admin_password = argv[2]      # Список ТЗ выбранных в чекбоксе


kc = KeyCloak(admin_name, admin_password)
realm = argv[3]         # Выбранный Рилм
userName = argv[4]      # Имя клиента

with open(f"temp/user/{userName}.json") as values:
    data = json.load(values)

servers = data["servers"]               # Список ТЗ выбранных в чекбоксе
port = '8080'
email = data["email"]                   # Email пользователя
owner = data["owner"]                   # Ответственный за ТУЗ - email
purpose = data["purpose"]               # Описание назначения ТУЗ
task = data["task"]                     # Задача по которой создается ТУЗ
roles = data["roles"]                   # Список назначаемых ролей clientName
clientName = data["clientName"]         # Клиент

containerId = realm

for server in servers:
    print("===========================================================================================================")
    # Get admin token
    print("Получаем токен...")
    tokenInfo = kc.getTokenInfo(server)
    accessToken = tokenInfo.get('access_token')
    print("Успех! Токен получен")
    # Get Client Information
    clientInfo = kc.getClientInfo(server, accessToken, clientName, realm)
    clientID = clientInfo[0].get('id')
    # Create User
    if userName:
        print(f"Создаем пользователя...{userName} на сервере {server}")
        status_code = kc.createUser(server, accessToken, userName, realm, owner, purpose, task)
        # Get User Information
        userInfo = kc.findUserByParameters(server, accessToken, userName, realm)
        userID = userInfo[0]['id']
        if roles:
            # Set role to user
            print("Пытаемся назначать роли пользователю...")
            availableClientRoles = kc.getClientLevelRoles(server, accessToken, userID, clientID, realm)
            for role in roles:
                for availableRole in availableClientRoles:
                    if role.lower() == availableRole['name'].lower():
                        kc.setClientRoleToUser(server, accessToken, clientID, roles, userID, availableRole, realm)
                    #else:
                    #    print(f'Роль {role} уже назначена пользователю {userName}')
    else:
        print("Создание пользователя не требуется...")
    print("Готово. Вы великолепны!")
