from flask import Flask, render_template, request, send_from_directory
import subprocess
import os
import json
import logging

# Определение класса фильтрации сообщений
class CodeFilter(logging.Filter):
    def filter(self, record):
        # Исключаем сообщения с кодом состояния 304
        return "304" not in record.getMessage()

# Создаем фильтр
code_filter = CodeFilter()

app = Flask(__name__)
app.debug = True

# Настройка логирования
logging.basicConfig(filename='./logs/keycloak_ui_app.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Получаем логгер для модуля werkzeug
werkzeug_logger = logging.getLogger('werkzeug')
# Добавляем фильтр к логгеру
werkzeug_logger.addFilter(code_filter)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/createclient', methods=['GET', 'POST'])
def createclient():
    if request.method == 'POST':
        var1 = request.form.get('admin_name')
        var2 = request.form.get('admin_password')
        var3 = request.form.get('realm')
        var4 = request.form.get('clientName')
        var5 = request.form.getlist('server')
        var6 = request.form.get('description')
        var7 = request.form.get('redirectUris')
        roles_input = request.form.get('roles')
        var8 = roles_input.split(',') if roles_input else []
        var9 = request.form.get("publicClient")
        var10 = request.form.get("clientSecret")
        var11 = request.form.get("tokenExchange")
        data = {
            "servers": var5,
            "description": var6,
            "redirectUris": var7,
            "roles": var8,
            "publicClient": var9,
            "clientSecret": var10,
            "tokenExchange": var11
        }

        # Записываем данные в файл JSON
        with open(f'temp_files/client/{var4}.json', 'w') as file:
            json.dump(data, file)

        result = subprocess.run(['python3', './createClient.py', var1, var2, var3, var4],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            output = result.stdout.decode().split('\n')
            logging.info(f'Клиент {var4} успешно создан на серверах {var5}: Пользователь {var1}')
            return render_template('result.html', output=output)
        else:
            error = result.stderr.decode()
            logging.error(f'Ошибка при создании клиента: {error}')
            return f"Error: {error}"

    return render_template('createclient.html')


@app.route('/createuser', methods=['GET', 'POST'])
def createuser():
    if request.method == 'POST':
        var1 = request.form.get('admin_name')
        var2 = request.form.get('admin_password')
        var3 = request.form.get('realm')
        var4 = request.form.get('userName')
        var5 = request.form.getlist('server')
        var6 = request.form.get('email')
        var7 = request.form.get('owner')
        var8 = request.form.get("purpose")
        var9 = request.form.get("task")
        roles_input = request.form.get('roles')
        var10 = roles_input.split(',') if roles_input else []
        var11 = request.form.get('clientName')
        var12 = request.form.get('userPass')
        data = {
            "servers": var5,
            "userPass": var12,
            "email": var6,
            "owner": var7,
            "purpose": var8,
            "task": var9,
            "clientName": var11,
            "roles": var10
        }

        # Записываем данные в файл JSON
        with open(f'temp_files/user/{var4}.json', 'w') as file:
            json.dump(data, file)

        result = subprocess.run(['python3', './createUser.py', var1, var2, var3, var4],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            output = result.stdout.decode().split('\n')
            logging.info(f'Пользователь {var4} успешно создан на серверах {var5}: Пользователь {var1}')
            return render_template('result.html', output=output)
        else:
            error = result.stderr.decode()
            logging.error(f'Ошибка при создании пользователя: {error}')
            return f"Error: {error}"

    return render_template('createuser.html')

@app.route('/loadtheme', methods=['GET', 'POST'])
def loadtheme():
    if request.method == 'POST':
        var1 = request.form.get('admin_name')
        var2 = request.form.get('admin_password')
        var3 = request.form.get('realm')
        var5 = request.form.getlist('server')
        var6 = request.form.get('clientName')
        var7 = request.files['file']
        file_name = var7.filename
        theme_file_name = os.path.splitext(file_name)[0]

        # Сохраняем полученный файл во временную папку
        theme_path = f'./temp_files/theme/{var6}'

        # Проверяем существование директории, и если ее нет, создаем
        if not os.path.exists(theme_path):
            os.makedirs(theme_path)
        var7.save(os.path.join(theme_path, file_name))


        # Сохраняем данные по клиенту
        data = {
            "themeName": theme_file_name,
            "servers": var5,
            "clientName": var6
        }

        # Записываем данные в файл JSON
        with open(f'temp_files/theme/{var6}/{theme_file_name}.json', 'w') as file:
            json.dump(data, file)

        result = subprocess.run(['python3', './loadTheme.py', var1, var2, var3, var6],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Удаляем архив с темой
        # os.remove(os.path.join(theme_path, theme_file.filename))

        if result.returncode == 0:
            output = result.stdout.decode().split('\n')
            logging.info(f'Тема {theme_file_name} применена на серверах {var5} у клиента {var6}: Пользователь {var1}')
            return render_template('result.html', output=output)
        else:
            error = result.stderr.decode()
            logging.error(f'Ошибка при загрузке темы клиента: {error}')
            return f"Error: {error}"

    return render_template('loadtheme.html')

@app.route('/finduser', methods=['GET', 'POST'])
def finduser():
    if request.method == 'POST':
        var1 = request.form.get('admin_name')
        var2 = request.form.get('admin_password')
        var3 = request.form.get('realm')
        var4 = request.form.get('userName')
        var5 = request.form.getlist('server')

        data = {
            "servers": var5,
            "userName": var4
        }

        # Записываем данные в файл JSON
        with open(f'temp_files/find/user/{var4}.json', 'w') as file:
            json.dump(data, file)

        result = subprocess.run(['python3', './findUser.py', var1, var2, var3, var4],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            output = result.stdout.decode().split('\n')
            logging.info(f'Выполнен поиск пользователя {var4} на серверах {var5} в рилме {var3}: Пользователь {var1}')
            return render_template('result.html', output=output)
        else:
            error = result.stderr.decode()
            logging.error(f'Ошибка при поиске пользователя: {error} Пользователь {var1}')
            return f"Error: {error}"

    return render_template('finduser.html')


@app.route('/findclient', methods=['GET', 'POST'])
def findclient():
    if request.method == 'POST':
        var1 = request.form.get('admin_name')
        var2 = request.form.get('admin_password')
        var3 = request.form.get('realm')
        var4 = request.form.get('clientName')
        var5 = request.form.getlist('server')

        data = {
            "servers": var5,
            "clientName": var4
        }

        # Записываем данные в файл JSON
        with open(f'temp_files/find/client/{var4}.json', 'w') as file:
            json.dump(data, file)

        result = subprocess.run(['python3', './findClient.py', var1, var2, var3, var4],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            output = result.stdout.decode().split('\n')
            logging.info(f'Выполнен поиск клиента {var4} на серверах {var5} в рилме {var3}: Пользователь {var1}')
            return render_template('result.html', output=output)
        else:
            error = result.stderr.decode()
            logging.error(f'Ошибка при поиске клиента: {error}: Пользователь {var1}')
            return f"Error: {error}"

    return render_template('findclient.html')

@app.route('/loadmodule', methods=['GET', 'POST'])
def loadmodule():
    if request.method == 'POST':
        var1 = request.form.get('admin_name')
        var2 = request.form.get('admin_password')
        var3 = request.form.getlist('server')
        var4 = request.files['file']
        file_name = var4.filename
        module_file_name = os.path.splitext(file_name)[0]

        # Сохраняем полученный файл во временную папку
        module_path = f'./temp_files/module/{module_file_name}'

        # Проверяем существование директории, и если ее нет, создаем
        if not os.path.exists(module_path):
            os.makedirs(module_path)
        var4.save(os.path.join(module_path, file_name))

        # Сохраняем данные по клиенту
        data = {
            "themeName": module_file_name,
            "servers": var3,
            "file_name": file_name
        }

        # Записываем данные в файл JSON
        with open(f'temp_files/module/{module_file_name}/{module_file_name}.json', 'w') as file:
            json.dump(data, file)

        result = subprocess.run(['python3', './loadModule.py', var1, var2, module_file_name],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Удаляем архив с темой
        # os.remove(os.path.join(theme_path, theme_file.filename))

        if result.returncode == 0:
            output = result.stdout.decode().split('\n')
            logging.info(
                f'Модуль {module_file_name} загружен на серверах {var3}: Пользователь {var1}')
            return render_template('result.html', output=output)
        else:
            error = result.stderr.decode()
            logging.error(f'Ошибка при загрузке модуля клиента: {error}')
            return f"Error: {error}"

    return render_template('loadmodule.html')

# Настройки запуска на сервере
if __name__ == '__main__':
    app.run()
    # app.run(host='SERVER_IP_ADDRESS', port=YOUR_PORT_NUMBER)
