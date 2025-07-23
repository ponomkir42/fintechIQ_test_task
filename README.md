# Blacklist service

Тестовое задание по вакансии https://novosibirsk.hh.ru/vacancy/122550433
Текст задания можно посмотреть в task_conditions.md

Запуск сервиса:
1. Скачать данный репозиторий: `git clone https://github.com/ponomkir42/fintechiq_test_task.git`
2. Убедиться, что на машине установлен Docker и Docker compose ( https://docs.docker.com/compose/install/linux/ )
3. Создать файл `.env` в корневой директории проекта и заполнить его данными ( пример данных находится в `.env-example`)
4. Запустить контейнеры: `docker compose up -d --build`
5. Логи: `docker compose logs -f`

Запуск тестов (контейнеры должны быть запущены):
`docker compose exec -it api uv run pytest src`
