from flask import Flask, render_template, request, send_from_directory
import subprocess
import os
import json

app = Flask(__name__)
app.debug = True

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
        data = {
            "servers": var5,
            "description": var6,
            "redirectUris": var7,
            "roles": var8,
            "publicClient": var9,
            "clientSecret": var10

        }

        # Записываем данные в файл JSON
        with open(f'temp/{var4}.json', 'w') as file:
            json.dump(data, file)

        result = subprocess.run(['python3', './createClient.py', var1, var2, var3, var4],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            output = result.stdout.decode().split('\n')
            return render_template('result.html', output=output)
        else:
            error = result.stderr.decode()
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
        with open(f'temp/user/{var4}.json', 'w') as file:
            json.dump(data, file)

        result = subprocess.run(['python3', './createUser.py', var1, var2, var3, var4],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            output = result.stdout.decode().split('\n')
            return render_template('result.html', output=output)
        else:
            error = result.stderr.decode()
            return f"Error: {error}"

    return render_template('createuser.html')

@app.route('/loadtheme', methods=['GET', 'POST'])
def loadtheme():
    if request.method == 'POST':
        var1 = request.form.get('admin_name')
        var2 = request.form.get('admin_password')
        var3 = request.form.get('realm')
        var4 = request.form.get('themeName')
        var5 = request.form.getlist('server')
        var6 = request.form.get('clientName')
        theme_file = request.files['file']

        # Сохраняем полученный файл во временную папку
        filename = f"{var4}.zip"
        theme_path = f'./temp/theme/{var4}/'
        theme_file.save(os.path.join(theme_path, filename))

        # Сохраняем данные по клиенту
        data = {
            "themeName": var4,
            "servers": var5,
            "clientName": var6,
        }

        # Записываем данные в файл JSON
        with open(f'temp/theme/{var6}.json', 'w') as file:
            json.dump(data, file)

        result = subprocess.run(['python3', './loadTheme.py', var1, var2, var3, var4],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Удаляем архив с темой
        os.remove(os.path.join(theme_path, theme_file.filename))

        if result.returncode == 0:
            output = result.stdout.decode().split('\n')
            return render_template('result.html', output=output)
        else:
            error = result.stderr.decode()
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
        with open(f'temp/find/user/{var4}.json', 'w') as file:
            json.dump(data, file)

        result = subprocess.run(['python3', './findUser.py', var1, var2, var3, var4],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            output = result.stdout.decode().split('\n')
            return render_template('result.html', output=output)
        else:
            error = result.stderr.decode()
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
        with open(f'temp/find/client/{var4}.json', 'w') as file:
            json.dump(data, file)

        result = subprocess.run(['python3', './findClient.py', var1, var2, var3, var4],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            output = result.stdout.decode().split('\n')
            return render_template('result.html', output=output)
        else:
            error = result.stderr.decode()
            return f"Error: {error}"

    return render_template('findclient.html')

# Настройки запуска на сервере
if __name__ == '__main__':
    app.run()
    # app.run(host='SERVER_IP_ADDRESS', port=YOUR_PORT_NUMBER)
