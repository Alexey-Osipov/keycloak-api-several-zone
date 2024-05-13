#!/bin/bash

# Переменные для пути к файлу main.py и имени процесса
MAIN_FILE="./main.py"
PROCESS_NAME="flask_kc_ui_app"

start() {
    # Запуск Flask приложения в фоновом режиме с помощью nohup
    nohup python3 "$MAIN_FILE" > /dev/null 2>&1 &
    # Сохранение PID процесса
    echo $! > "$PROCESS_NAME.pid"
    echo "Keycloak Admin UI приложение запущено."
}

stop() {
    # Проверка наличия PID файла
    if [ -f "$PROCESS_NAME.pid" ]; then
        # Чтение PID из файла
        PID=$(cat "$PROCESS_NAME.pid")
        # Остановка процесса
        kill $PID
        # Удаление PID файла
        rm "$PROCESS_NAME.pid"
        echo "Keycloak Admin UI приложение остановлено."
    else
        echo "PID файла не найдено. Возможно, приложение не запущено."
    fi
}

status() {
    # Проверка наличия PID файла
    if [ -f "$PROCESS_NAME.pid" ]; then
        # Чтение PID из файла
        PID=$(cat "$PROCESS_NAME.pid")
        # Проверка наличия процесса с заданным PID
        if ps -p $PID > /dev/null; then
            echo "Keycloak Admin UI приложение запущено (PID: $PID)."
        else
            echo "Keycloak Admin UI приложение не запущено."
            # Удаление PID файла, если процесс не найден
            rm "$PROCESS_NAME.pid"
        fi
    else
        echo "PID файла не найдено. Возможно, приложение не запущено."
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    *)
        echo "Использование: $0 {start|stop|status}"
        exit 1
        ;;
esac

exit 0
