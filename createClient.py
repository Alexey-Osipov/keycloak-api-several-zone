import requests
import uuid
import json
import os
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

    def createClient(self, server, accessToken, clientName, description, realm, redirectUris, typeClient,
                     enabled='true', consentRequired='false',
                     protocol="openid-connect", bearerOnly='false', standardFlowEnabled='true',
                     implicitFlowEnabled='false', directAccessGrantsEnabled='true',
                     authorizationServicesEnabled='false',
                     serviceAccountsEnabled='false',
                     clientAuthenticatorType="client-secret", fullScopeAllowed="false"):

        # Проверяем наличие секрета в файле для данного клиента
        secret_file_path = f"temp/{clientName}.json"
        if os.path.exists(secret_file_path):
            with open(secret_file_path, 'r') as file:
                data = json.load(file)
                if "clientSecret" in data:
                    secret = data.get("clientSecret", str(uuid.uuid4()))
        if secret == "":
            secret = str(uuid.uuid4())

        url = 'http://{0}:{1}/auth/admin/realms/{2}/clients'.format(server, port, realm)
        response = requests.request('POST', url, json={
            "clientId": clientName,
            "description": description,
            "enabled": enabled,
            "consentRequired": consentRequired,
            "protocol": "openid-connect",
            "bearerOnly": bearerOnly,
            "publicClient": typeClient,
            "standardFlowEnabled": standardFlowEnabled,
            "implicitFlowEnabled": implicitFlowEnabled,
            "directAccessGrantsEnabled": directAccessGrantsEnabled,
            "authorizationServicesEnabled": authorizationServicesEnabled,
            "serviceAccountsEnabled": serviceAccountsEnabled,
            "redirectUris": [
                redirectUris
                ],
            "clientAuthenticatorType": clientAuthenticatorType,
            "fullScopeAllowed": fullScopeAllowed,
            "secret": secret
        },
                                    headers={'Content-Type': 'application/json',
                                             'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code == 409:
            print(f"Клиент {clientName} уже существует на сервере {server}")
            return response.status_code
        if response.status_code != 201:
            # print(response.request.url)        # - раскомменти для дебаггинга
            # print(response.request.body)       # - раскомменти для дебаггинга
            # print(response.request.headers)    # - раскомменти для дебаггинга
            print(f"Не получилось создать клиента {clientName} на сервере {server}.")
        else:
            if typeClient == "false":
                print(f"Клиент {clientName} создан на сервере {server}. Client_secret: {secret}")
            else:
                print(f"Клиент Public: {clientName} создан на сервере {server}")

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

    def createRole(self, server, accessToken, clientID, roleName, description, realm, composite='false',
                   clientRole='false'):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/clients/{3}/roles'.format(server, port, realm, clientID)
        # adminToken = self.getAdminToken(server)
        # clientInfo = self.getClientInfo(server, clientName, realm)
        response = requests.request('POST', url, json={
            "name": roleName,
            "description": description,
            "composite": composite,
            "clientRole": clientRole,
            "containerId": realm
        },
                                    headers={'Content-Type': 'application/json',
                                             'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code == 409:
            print(f"Роль {roleName} уже существует у клиента {clientName}")
            return response.status_code
        if response.status_code != 201:
            # print(response.request.url)        # - раскомменти для дебаггинга
            # print(response.request.body)       # - раскомменти для дебаггинга
            # print(response.request.headers)    # - раскомменти для дебаггинга
            print(f"Не получилось создать роль {clientRole} на сервере {server}. Статус: {response.status_code} Ответ "
                  f"сервера: {response.request.headers}")
        else:
            print(f"Роль {roleName} успешно создана у клиента {clientName}")
            return response.status_code


username = argv[1]      # Список ТЗ выбранных в чекбоксе
password = argv[2]      # Список ТЗ выбранных в чекбоксе

kct = KeyCloak_Token(username, password)
realm = argv[3]         # Выбранный Рилм
clientName = argv[4]    # Имя клиента

with open(f"temp/{clientName}.json") as values:
    data = json.load(values)

servers = data["servers"]               # Список ТЗ выбранных в чекбоксе
port = '8080'
redirectUris = data["redirectUris"]     # Параметр redirectUris
roles = data["roles"]                   # Список ролей необходимо создать
description = data["description"]       # Описание к клиенту
typeClient = data["publicClient"]
containerId = realm

for server in servers:
    print("===========================================================================================================")
    # Get admin token
    print("Получаем токен...")
    tokenInfo = kct.getTokenInfo(server)
    accessToken = tokenInfo.get('access_token')
    print("Успех! Токен получен")
    # Display brief info
    print(f"###Выполняем регистрацию клиента {clientName} С созданием клиентских ролей: {roles}. В рилме: {realm} На сервере: {server}###")
    # Create Client
    print("Создаем клиента...")
    kct.createClient(server, accessToken, clientName, description, realm, redirectUris, typeClient)
    # Get Client Information
    clientInfo = kct.getClientInfo(server, accessToken, clientName, realm)
    clientID = clientInfo[0].get('id')
    # Create role
    if not roles:
        print("Создание ролей не требуется...")
    else:
        print("Создаем роли...")
        for roleName in roles:
            status_code = kct.createRole(server, accessToken, clientID, roleName, description, containerId)
