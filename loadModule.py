import glob
import os
import json
import time
import paramiko
import requests
from scp import SCPClient
from sys import argv


class Load_Module:
    def __init__(self, admin_name, admin_password):
        self.admin_name = admin_name
        self.admin_password = admin_password

    def loadModule(self, server_load, module_file_name):
        local_file_path = f'./temp_files/module/{module_file_name}/{module_file_name}.jar' # Путь к локальному файлу для передачи
        os.chmod(local_file_path, 0o666)    # Устанавливаем права на файл перед его передачей
        remote_file_path = '/tmp'   # Путь на удаленном сервере, куда нужно передать файл
        keycloak_url = f"http://{server_load}:8080/auth/realms/master/health/check"  # URL сервера Keycloak
        num_retries = 3             # Количество попыток
        retry_interval = 10         # Интервал между попытками (в секундах)

        # Команды на удаленном сервере
        command_cp = f'echo {admin_password} | sudo -S -iu {username_server} cp {remote_file_path}/{module_file_name}' \
                     f'.jar -d /data/fedsso/keycloak_cin/current/providers'
        command_ls_name = f'echo {admin_password} | sudo -S -iu {username_server} ls {providers_dir}/{new_jar_name}'
        # print(f'Префикс {jar_prefix}')
        command_ls_list = f'echo {admin_password} | sudo -S -iu {username_server} ls {providers_dir}/'
        command_rebuild = f'echo {admin_password} | sudo -S -iu {username_server} /data/fedsso/keycloak_cin/current' \
                          f'/keycloak-ctl.sh rebuild'

        # Подключение к серверу через SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_load, 22, username=self.admin_name, password=self.admin_password)

        # Проверяем, есть ли уже новый файл JAR на удаленном сервере
        stdin, stdout, stderr = ssh.exec_command(command_ls_name)
        stdout_data = stdout.read().decode()
        # print(f'command_ls_name {stdout_data}')
        if new_jar_name in stdout_data:
            print(f'Новый файл JAR {new_jar_name} уже существует на удаленном сервере {server_load}.')
        else:
            # Передача файла на удаленный сервер
            with SCPClient(ssh.get_transport()) as scp:
                scp.put(local_file_path, remote_file_path)
                print(f'Модуль загружен на сервер {server_load}.')

            # Выполнение команды с sudo на удаленном сервере
            stdin, stdout, stderr = ssh.exec_command(command_cp)

            # Проверяем, возник ли конфликт при распаковке архива
            output = stderr.read().decode()
            # print(f'command_cp {output}')

            # Получаем список всех файлов JAR на удаленном сервере с указанным префиксом
            stdin, stdout, stderr = ssh.exec_command(command_ls_list)
            stdout_data = stdout.read().decode()
            # print(f'command_ls_list {stdout_data}')
            jar_files = stdout_data.split()

            # Создадим новый список с отфильтрованными именами файлов
            filtered_jar_files = []

            # Переберём список jar_files
            for jar_file in jar_files:
                # Проверим, содержит ли имя файла префикс jar_prefix
                if jar_prefix in jar_file:
                    # Отрежем расширение .jar
                    filtered_jar_files.append(jar_file)

            # Выведем новый список
            # print(f'filtered_jar_files {filtered_jar_files}')

            for jar_file_del in filtered_jar_files:
                if jar_file_del != new_jar_name:
                    # Создадим команду rm для удаления файла
                    command_rm = f'echo {admin_password} | sudo -S -iu {username_server} rm {providers_dir}/' \
                                 f'{jar_file_del}'

                    # Удаляем файл старой версии
                    stdin, stdout, stderr = ssh.exec_command(command_rm)
                    stdout_data = stdout.read().decode()

                    # Выведем вывод удаления
                    # print(f'Вывод удаления {stdout_data}')

                    # Выведем сообщение об удалении файла
                    print(f'Удалили предыдущую версию модуля: {jar_file_del} на сервере {server_load}')

                    # Удалим файл JAR из списка после его удаления
                    filtered_jar_files.remove(jar_file_del)

                    #------------------- ТУТ Ребилд---------------------------
                    # Выполняем ребилд Keycloak
                    stdin, stdout, stderr = ssh.exec_command(command_rebuild)
                    stdout_data = stdout.read().decode()
                    # print(f'Вывод ребилда {stdout_data}')
                    print(f'Выполняем ребилд Keycloak на сервере {server_load}')
                    # ------------------- ТУТ Ребилд---------------------------

                    # Выполняем цикл с попытками
                    for attempt in range(1, num_retries + 1):
                        try:
                            # Отправляем запрос HTTP и получаем ответ
                            response = requests.get(keycloak_url)

                            # Проверяем код состояния ответа
                            if response.status_code != 200:
                                raise Exception(
                                    f"Не удалось получить данные о состоянии работоспособности Keycloak, "
                                    f"необходим анализ логов на сервере {server_load}.")

                            # Получаем JSON-данные из ответа
                            json_data = response.json()

                            # Извлекаем список nodeNames
                            nodeNames = json_data['details']['infinispan']['nodeNames']

                            # Выводим вывод health check
                            print(f'Список серверов в кластере: {nodeNames}')

                            # Выходим из цикла с попытками, если запрос был успешным
                            break

                        except Exception as e:
                            # Если возникло исключение, выводим сообщение и ждем перед следующей попыткой
                            print(f"Попытка {attempt} из {num_retries} не удалась: {e}")
                            time.sleep(retry_interval)

                    # Если ни одна из попыток не удалась, выводим исключение
                    if attempt == num_retries:
                        raise Exception(
                                    f"Не удалось получить данные о состоянии работоспособности Keycloak, "
                                    f"необходим анализ логов на сервере {server_load}.")

            # Закрываем соединение SSH
            ssh.close()


admin_name = argv[1]  # Имя пользователя
admin_password = argv[2]  # Пароль пользователя
module_file_name = argv[3]  # Название модуля без jar
username_server = "fedsso"

lm = Load_Module(admin_name, admin_password)

module_directory = f"temp_files/module/{module_file_name}"
json_files = glob.glob(os.path.join(module_directory, "*.json"))
providers_dir = '/data/fedsso/keycloak_cin/current/providers'

if json_files:
    json_file_path = json_files[0]
    with open(json_file_path) as values:
        data = json.load(values)
else:
    print(f"Файл .json не найден в каталоге {module_directory}")

servers = data["servers"]                   # Список ТЗ выбранных в чекбоксе
new_jar_name = data["file_name"]            # Имя файла с jar
jar_prefix = new_jar_name.rsplit('-', maxsplit=1)[0]
server_all = []

for server in servers:
    # Load archive theme on server
    if server == "sib-fsso-app2a.megafon.ru":
        server_all = ["sib-fsso-app1a.megafon.ru", "sib-fsso-app2a.megafon.ru"]
        name_tz = "Alfa"
    elif server == "vlg-fsso-app2b.megafon.ru":
        server_all = ["vlg-fsso-app1b.megafon.ru", "vlg-fsso-app2b.megafon.ru"]
        name_tz = "Beta"
    elif server == "vlg-fsso-app2e.megafon.ru":
        server_all = ["vlg-fsso-app1e.megafon.ru", "vlg-fsso-app2e.megafon.ru"]
        name_tz = "Epsilon"
    elif server == "vlg-fsso-app2k.megafon.ru":
        server_all = ["vlg-fsso-app1k.megafon.ru", "vlg-fsso-app2k.megafon.ru"]
        name_tz = "Kappa"
    elif server == "vlg-fsso-app2l.megafon.ru":
        server_all = ["vlg-fsso-app1l.megafon.ru", "vlg-fsso-app2l.megafon.ru"]
        name_tz = "Lambda"
    elif server == "vlg-fsso-app2n.megafon.ru":
        server_all = ["vlg-fsso-app1n.megafon.ru", "vlg-fsso-app2n.megafon.ru"]
        name_tz = "Nuy"
    elif server == "sib-fsso-app2r.megafon.ru":
        server_all = ["sib-fsso-app1r.megafon.ru", "sib-fsso-app2r.megafon.ru"]
        name_tz = "Rho"
    elif server == "vlg-fsso-app2s.megafon.ru":
        server_all = ["vlg-fsso-app2s.megafon.ru", "vlg-fsso-app1.megafon.ru"]
        name_tz = "Sandbox"
    elif server == "sib-fsso-app2w.megafon.ru":
        server_all = ["sib-fsso-app1w.megafon.ru", "sib-fsso-app2w.megafon.ru", "sib-fsso-app3w.megafon.ru",
                      "sib-fsso-app4w.megafon.ru", "sib-fsso-app5w.megafon.ru", "sib-fsso-app6w.megafon.ru",
                      "sib-fsso-app7w.megafon.ru", "sib-fsso-app8w.megafon.ru"]
        name_tz = "WF"
    print(f"==========================================================================================================")
    # Выполняем загрузку модуля на сервера
    print(f"Загружаем модуль {new_jar_name} на сервера тестовой зоны {name_tz}")
    for server_load in server_all:
        lm.loadModule(server_load, module_file_name)
