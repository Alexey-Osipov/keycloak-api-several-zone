import requests
import json
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

    def findUserByParameters(self, server, accessToken, search, realm, userName='',
                             briefRepresentation='true', email='', firstName='', lastName='', max=5):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/users'.format(server, self.port, realm)
        response = requests.request('GET', url, params={
            "username": userNameSpace,
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
                f"Не могу найти информацию по пользователю {userName} на сервере {server}. Статус: {response.status_code} Ответ "
                f"сервера: {response.request.headers}")
            print(f"Что-то пошло не так. В следующий раз точно повезёт!")
        else:
            return response.json()

    def getUserRoles(self, server, accessToken, userID, realm):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/users/{3}/role-mappings'.format(server, self.port, realm, userID)
        response = requests.request('GET', url, headers={'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 200:
            print(f"Не могу получить информацию о ролях, назначенных пользователю {userName} на сервере {server}. "
                  f"Статус: {response.status_code} Ответсервера: {response.request.headers}")
            print(f"Что-то пошло не так. В следующий раз точно повезёт!")
            raise SystemExit(400)
        else:
            return response.json()


admin_name = argv[1]  # Список ТЗ выбранных в чекбоксе
admin_password = argv[2]  # Список ТЗ выбранных в чекбоксе

kc = KeyCloak(admin_name, admin_password)

realm = argv[3]  # Выбранный Рилм
userName = argv[4]  # Имя клиента

with open(f"temp_files/find/user/{userName}.json") as values:
    data = json.load(values)

servers = data["servers"]  # Список ТЗ выбранных в чекбоксе
server_to_tz_mapping = {
    "127.0.0.1": "localhost"
}
port = '8080'
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
    # Find User
    if ' ' in userName:
        userNameSpace = userName.replace(' ', '%')
    else:
        userNameSpace = userName
    print(f"Ищем пользователя: {userName}")
    # Get User Information
    userInfo = kc.findUserByParameters(server, accessToken, userNameSpace, realm)
    if len(userInfo) > 0:
        userID = userInfo[0]['id']
        userRoles = kc.getUserRoles(server, accessToken, userID, realm)
        print(f"Пользователь {userName} найден на Тестовой Зоне: {name_tz} в Рилме: {realm}, ищем роли:")
        # Проверка наличия назначенныйх клиентскийх ролей
        if 'clientMappings' in userRoles:
            for client in userRoles["clientMappings"]:
                print(f"Назначены роли клиента: {client}")
                for mapping in userRoles["clientMappings"][client]["mappings"]:
                    role_name = mapping.get('name', 'Нет данных о названии роли')
                    role_description = mapping.get('description', 'Описание не добавлено!')
                    print(f"Роль: {role_name} создана в рамках заявки: {role_description}")
        else:
            print(f"У пользователя {userName} нет назначенных клиентских ролей.")
    else:
        print(f"Пользователя {userName} нет на Тестовой Зоне: {name_tz} в Рилме: {realm}")
