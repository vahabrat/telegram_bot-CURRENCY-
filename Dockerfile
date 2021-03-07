FROM python:3.8
# копирует файл зависимостей в наш образ
COPY /requirements.txt /app/requirements.txt
# задаем рабочую директорию
WORKDIR /app
# запускаем команду которая установит все зависимости для нашего проекта
RUN pip install -r /app/requirements.txt
# копируем все остальные файлы нашего приложения в рабочую директорию
COPY . /app
# запyскаем наше приложение
CMD python /app/main.py