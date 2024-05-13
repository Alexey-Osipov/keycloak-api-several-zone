import requests
import uuid
import json
import os
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

    def createClient(self, server, accessToken, clientName, description, realm, redirectUris, typeClient,
                     enabled='true', consentRequired='false',
                     protocol="openid-connect", bearerOnly='false', standardFlowEnabled='true',
                     implicitFlowEnabled='false', directAccessGrantsEnabled='true',
                     authorizationServicesEnabled='false',
                     serviceAccountsEnabled='false',
                     clientAuthenticatorType="client-secret", fullScopeAllowed="false"):

        # Проверяем наличие секрета в файле для данного клиента
        secret_file_path = f"temp_files/client/{clientName}.json"
        if os.path.exists(secret_file_path):
            with open(secret_file_path, 'r') as file:
                data = json.load(file)
                if "clientSecret" in data:
                    secret = data.get("clientSecret", str(uuid.uuid4()))
        if secret == "":
            secret = secret_client

        url = 'http://{0}:{1}/auth/admin/realms/{2}/clients'.format(server, self.port, realm)
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
            print(f"Клиент {clientName} уже существует на Тестовой Зоне: {name_tz}")
            return response.status_code
        if response.status_code != 201:
            # print(response.request.url)        # - раскомменти для дебаггинга
            # print(response.request.body)       # - раскомменти для дебаггинга
            # print(response.request.headers)    # - раскомменти для дебаггинга
            print(f"Не получилось создать клиента {clientName} на Тестовой Зоне: {name_tz}.")
        else:
            if typeClient == "false":
                print(f"Клиент {clientName} создан. Client_secret: {secret}")
            else:
                print(f"Клиент Public: {clientName} создан.")

    def getClientInfo(self, server, accessToken, clientName, realm):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/clients?clientId={3}'.format(server, self.port, realm, clientName)
        response = requests.request('GET', url, headers={'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 200:
            print(
                f"Не могу получить информацию по клиенту {clientName} на Тестовой Зоне: {name_tz}. "
                f"Статус: {response.status_code} Ответ сервера: {response.request.headers}")
            print(f"Что-то пошло не так. В следующий раз точно повезёт!")
            raise SystemExit(400)
        else:
            return response.json()

    def createRole(self, server, accessToken, clientID, roleName, description, realm, composite='false',
                   clientRole='false'):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/clients/{3}/roles'.format(server, self.port, realm, clientID)
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
            print(
                f"Не получилось создать роль {clientRole} на Тестовой Зоне: {name_tz}. Статус: {response.status_code} "
                f"Ответ сервера: {response.request.headers}")
        else:
            print(f"Роль {roleName} успешно создана у клиента {clientName}")
            return response.status_code

    def putPermissions(self, server, accessToken, clientID, realm, enabled='true'):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/clients/{3}/management/permissions'.format(server, self.port, realm,
                                                                                               clientID)
        response = requests.request('PUT', url, json={
            "enabled": enabled
        },
                                    headers={'Content-Type': 'application/json',
                                             'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 200:
            print(f"Не получилось включить ТЕ у клиента {clientName}")
            raise SystemExit(400)
        else:
            return response.json()

    def getpolicyInfo(self, server, accessToken, clientID_rm, realm, tokenExchange):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/clients/{3}/authz/resource-server/policy?' \
              'first=0&max=11&permission=false&name={4}' \
              ''.format(server, self.port, realm, clientID_rm, tokenExchange)
        response = requests.request('GET', url, headers={'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 200:
            print(f"Политики Token-exchange для клента {tokenExchange} не найдено")
            raise SystemExit(400)
        else:
            return response.json()

    def putApplyTE(self, server, accessToken, clientID_rm, realm, tokenexchangeID):
        url = 'http://{0}:{1}/auth/admin/realms/{2}/clients/{3}/authz/resource-server/permission/scope/{4}'.format(
            server, self.port, realm, clientID_rm, tokenexchangeID)
        response = requests.request('PUT', url, json={
            "decisionStrategy": "AFFIRMATIVE",
            "description": "",
            "id": tokenexchangeID,
            "name": "token-exchange.permission.client.{}".format(clientID),
            "policies": [
                policyID
            ],
            "type": "scope"
        },
                                    headers={'Content-Type': 'application/json',
                                             'Authorization': 'Bearer {0}'.format(accessToken)})
        if response.status_code != 201:
            print(f"Не получилось включить ТЕ у клиента {clientName} с клиентом {tokenExchange}")
            print(response.status_code)
            print(response.request.url)  # - раскомменти для дебаггинга
            print(response.request.body)  # - раскомменти для дебаггинга
            print(response.request.headers)  # - раскомменти для дебаггинга
            raise SystemExit(400)
        else:
            print(f"Token exchange включен у клиента {clientName} с клиентом {tokenExchange}")
            return response.status_code


admin_name = argv[1]  # Список ТЗ выбранных в чекбоксе
admin_password = argv[2]  # Список ТЗ выбранных в чекбоксе
secret_client = str(uuid.uuid4())

kct = KeyCloak_Token(admin_name, admin_password)
realm = argv[3]  # Выбранный Рилм
clientName = argv[4]  # Имя клиента

with open(f"temp_files/client/{clientName}.json") as values:
    data = json.load(values)

servers = data["servers"]  # Список ТЗ выбранных в чекбоксе
server_to_tz_mapping = {
    "127.0.0.1": "localhost"
}
redirectUris = data["redirectUris"]  # Параметр redirectUris
roles = data["roles"]  # Список ролей необходимо создать
description = data["description"]  # Описание к клиенту
typeClient = data["publicClient"]  # Тип клиента
tokenExchange = data["tokenExchange"]  # Настроить ТЕ
clientNameRM = "realm-management"
containerId = realm

for server in servers:
    name_tz = server_to_tz_mapping.get(server, None)
    print("===========================================================================================================")
    # Get admin token
    print("Получаем токен...")
    tokenInfo = kct.getTokenInfo(server)
    if "access_token" not in tokenInfo:
        print(f"Возникла ошибка: {tokenInfo.get('error_description')}")
        raise SystemExit
    accessToken = tokenInfo.get('access_token')
    # Display brief info
    print(
        f"Выполняем регистрацию клиента {clientName}. С созданием клиентских ролей: {roles}. В Тестовой Зоне: {name_tz} "
        f"Рилма: {realm} ")
    # Create Client
    print("Создаем клиента...")
    kct.createClient(server, accessToken, clientName, description, realm, redirectUris, typeClient)
    # Get Client Information
    clientInfo = kct.getClientInfo(server, accessToken, clientName, realm)
    clientID = clientInfo[0].get('id')
    # Create role
    if not roles:
        print("Создание ролей не требуется.")
    else:
        print("Создаем роли...")
        for roleName in roles:
            status_code = kct.createRole(server, accessToken, clientID, roleName, description, containerId)
    # Token-exchange api-gateway
    if not tokenExchange:
        print("Настройка Token Exchange не требуется.")
    else:
        print(f"Настройка Token Exchange {clientName} c {tokenExchange}")
        permissionsInfo = kct.putPermissions(server, accessToken, clientID, realm)
        tokenexchangeID = permissionsInfo.get('scopePermissions', {}).get('token-exchange')
        clientInfo_rm = kct.getClientInfo(server, accessToken, clientNameRM, realm)
        clientID_rm = clientInfo_rm[0].get('id')
        policy_api_gw = kct.getpolicyInfo(server, accessToken, clientID_rm, realm, tokenExchange)
        if len(policy_api_gw) > 0:
            policyID = policy_api_gw[0].get('id')
            kct.putApplyTE(server, accessToken, clientID_rm, realm, tokenexchangeID)
        else:
            print(f"Политика Token Exchange для клента {tokenExchange} не найдена на Тестовой Зоне: {name_tz}")
