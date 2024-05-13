import random
import requests
import json
import os
from sys import argv


class KeyCloak:
    def __init__(self, admin_name, admin_password, port='8080'):
        self.admin_name = admin_name
        self.admin_password = admin_password
        self.port = port

    def getTokenInfo(self, server):
        url = 'http://{0}:{1}/auth/realms/master/protocol/openid-connect/token'.format(server, self.port)
        response = requests.request('POST', url, data={
            'username': self.admin_name,
            'password': self.admin_password,
            'grant_type': 'password',
            'client_id': 'admin-cli'
        },
                                    headers={'Content-Type': 'application/x-www-form-urlencoded'})
        return response.json()

    def createUser(self, server, accessToken, userName, realm, owner, purpose, task, enabled='true', temporary='false'):
        # Проверяем наличие файла пользователя
        user_file_path = f"temp_files/user/{userName}.json"
        if os.path.exists(user_file_path):
            with open(user_file_path, 'r') as file:
                data = json.load(file)
                if "userPass" in data:
                    password = data.get("userPass", generatePassword())
        if password == "":
            password = password_user

        url = 'http://{0}:{1}/auth/admin/realms/{2}/users'.format(server, self.port, realm)
        response = requests.request('POST', url, json={
            "username": userName,
            "email": email,
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
            print(f"Пользователь {userName} уже существует в реалме {realm} на Тестовой Зоне: {name_tz}.")
            return response.status_code
        if response.status_code != 201:
            # print(response.request.url)        # - раскомменти для дебаггинга
            # print(response.request.body)       # - раскомменти для дебаггинга
            # print(response.request.headers)    # - раскомменти для дебаггинга
            print(
                f"Не получилось создать пользователя {userName} на Тестовой Зоне: {name_tz}. Статус: "
                f"{response.status_code} Ответ сервера: {response.request.body}")
        else:
            print(f"Пользователь {userName} успешно создан. Пароль: {password}")
            return response.status_code

    def getClientInfo(self, server, accessToken, clientName, realm):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/clients?clientId={3}'.format(server, self.port, realm, clientName)
        response = requests.request('GET', url, headers={'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 200:
            print(
                f"Не могу получить информацию по клиенту {clientName} на Тестовой Зоне: {name_tz}. Статус: "
                f"{response.status_code} Ответ сервера: {response.request.body}")
            print(f"Что-то пошло не так. В следующий раз точно повезёт!")
            raise SystemExit(400)
        else:
            return response.json()

    def findUserByParameters(self, server, accessToken, search, realm, userName='',
                             briefRepresentation='true', email='', firstName='', lastName='', max=5):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/users'.format(server, self.port, realm)
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
            print(
                f"Не могу найти информацию по пользователю {userName} Тестовой Зоне: {name_tz}. Статус: "
                f"{response.status_code} Ответ сервера: {response.request.headers}")
            print(f"Что-то пошло не так. В следующий раз точно повезёт!")
        else:
            return response.json()

    def getUserRoles(self, server, accessToken, userID, realm):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/users/{3}/role-mappings'.format(server, self.port, realm, userID)
        response = requests.request('GET', url, headers={'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 200:
            print(f"Не могу получить информацию о ролях, назначенных пользователю {userName} на Тестовой Зоне: "
                  f"{name_tz}. Статус: {response.status_code} Ответсервера: {response.request.headers}")
            print(f"Что-то пошло не так. В следующий раз точно повезёт!")
            raise SystemExit(400)
        else:
            return response.json()

    def getClientRoles(self, server, accessToken, clientID, realm):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/clients/{3}/roles'.format(server, self.port, realm, clientID)
        response = requests.request('GET', url, headers={'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 200:
            print(f"Не могу получить информацию о ролях, назначенных пользователю {userName} на Тестовой Зоне: "
                  f"{name_tz}. Статус: {response.status_code} Ответсервера: {response.request.headers}")
            print(f"Что-то пошло не так. В следующий раз точно повезёт!")
            raise SystemExit(400)
        else:
            return response.json()

    def getClientLevelRoles(self, server, accessToken, userID, clientID, realm):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/users/{3}/role-mappings/clients/{4}/available'.format(server, self.port,
                                                                                                          realm,
                                                                                                          userID,
                                                                                                          clientID)
        response = requests.request('GET', url, headers={'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 200:
            # print(response.request.url)        # - раскомменти для дебаггинга
            # print(response.request.body)       # - раскомменти для дебаггинга
            # print(response.request.headers)    # - раскомменти для дебаггинга
            print(f"Не могу получить информацию о ролях клиента {clientName} на Тестовой Зоне: {name_tz}. "
                  f"Статус: {response.status_code} Ответсервера: {response.request.headers}")
        else:
            return response.json()

    def setClientRoleToUser(self, server, accessToken, clientID, roleName, userID, role, realm):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/users/{3}/role-mappings/clients/{4}'.format(server, self.port, realm,
                                                                                                userID,
                                                                                                clientID)
        name_role = role['name']
        response = requests.request('POST', url, json=[role],
                                    headers={'Content-Type': 'application/json',
                                             'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code == 409:
            print(f"Роли {name_role} уже назначена пользователю {userName}")
            return response.status_code
        if response.status_code != 204:
            print(f"Не могу назначить роли {name_role} пользователю {userName} на Тестовой Зоне: {name_tz}. "
                  f"Статус: {response.status_code} Ответсервера: {response.request.headers}")
        else:
            print(f"Роли {name_role} успешно назначена пользователю {userName} на Тестовой Зоне: {name_tz}")
            return response.status_code


def generatePassword(length=16):
    chars = '*!&$#?=@abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    password = ''
    for _ in range(length):
        password += random.choice(chars)
    return password


admin_name = argv[1]  # Список ТЗ выбранных в чекбоксе
admin_password = argv[2]  # Список ТЗ выбранных в чекбоксе
password_user = generatePassword()

kc = KeyCloak(admin_name, admin_password)
realm = argv[3]  # Выбранный Рилм
userName = argv[4]  # Имя клиента

with open(f"temp_files/user/{userName}.json") as values:
    data = json.load(values)

servers = data["servers"]  # Список ТЗ выбранных в чекбоксе
server_to_tz_mapping = {
    "127.0.0.1": "localhost"
}
email = data["email"]  # Email пользователя
owner = data["owner"]  # Ответственный за ТУЗ - email
purpose = data["purpose"]  # Описание назначения ТУЗ
task = data["task"]  # Задача по которой создается ТУЗ
roles = data["roles"]  # Список назначаемых ролей clientName
clientName = data["clientName"]  # Клиент

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
    if not clientInfo:
        print(f"Указанный {clientName} клиент не найден")
        print(f"Создаем пользователя...{userName} на Тестовой Зоне: {name_tz}")
        status_code = kc.createUser(server, accessToken, userName, realm, owner, purpose, task)
    else:
        # Create User
        clientID = clientInfo[0].get('id')
        if userName:
            print(f"Создаем пользователя... {userName} на Тестовой Зоне: {name_tz}")
            status_code = kc.createUser(server, accessToken, userName, realm, owner, purpose, task)

            # Get User Information
            userInfo = kc.findUserByParameters(server, accessToken, userName, realm)
            userID = userInfo[0]['id']
            userRoles = kc.getUserRoles(server, accessToken, userID, realm)

            # Получение словаря с информацией о ролях из userRoles
            if "clientMappings" in userRoles and clientName in userRoles["clientMappings"]:
                roles_info = userRoles["clientMappings"][clientName]["mappings"]
            else:
                roles_info = []
            role_names = [role["name"].lower() for role in roles_info]

            # Получение словаря с информацией о ролях из clientRoles
            clientRoles = kc.getClientRoles(server, accessToken, clientID, realm)
            client_role_list = [role['name'] for role in clientRoles]

            # Находим все совпадения ролей
            print("Пытаемся назначать роли пользователю...")
            matching_roles = [role_name for role_name in role_names if role_name.lower() in client_role_list]
            if matching_roles:
                for matching_role in matching_roles:
                    print(f"Роль {matching_role} уже назначена пользователю")

            # Формируем новый список без совпадений
            new_roles = [role for role in roles if role not in matching_roles]

            # Назначаем роли пользователю, если новые роли есть
            if new_roles:
                availableClientRoles = kc.getClientLevelRoles(server, accessToken, userID, clientID, realm)
                for role in new_roles:
                    role_found = False
                    for availableRole in availableClientRoles:
                        if role.lower() == availableRole['name'].lower():
                            role_found = True
                            kc.setClientRoleToUser(server, accessToken, clientID, roles, userID, availableRole, realm)
                    if not role_found:
                        print(f"Роль {role} отсутствует у клиента {clientName}")
            else:
                print("Нет новых ролей для назначения пользователю")
        else:
            print("Создание пользователя не требуется...")
    print("Готово. Вы великолепны!")
