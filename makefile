include .env
export

all: up info

update_env_file:
	cat ./env.example > ./.env

first_start: up load_model create_airflow_connection info

up:
	echo "Start of deploying services"
	docker-compose up -d

load_model: up
	echo "Start of load LLM"
	docker-compose exec ollama ollama pull $(MODEL)

down:
	docker-compose down

create_airflow_connection: up
	echo "Start of creating connecting Airflow with PosgreSQL"
	docker-compose exec $(AIRFLOW_SERVICE) airflow connections add $(AIRFLOW_CONN_ID) \
	  --conn-type postgres \
	  --conn-host $(POSTGRES_HOST) \
	  --conn-port $(POSTGRES_PORT) \
	  --conn-login $(POSTGRES_USER) \
	  --conn-password $(POSTGRES_PASSWORD) \
	  --conn-schema $(POSTGRES_DB)

info:
	echo "Strealit app: http://localhost:8501/"	
	echo "pgAdmin4: http://localhost:8081/"
	echo "Airflow UI: http://localhost:8080/"
	echo "For help use command: make -f makefile help"

help:
	echo "- all - запуск приложений и вывод информации о доступных портах"
	echo "- first_start - первый запуск, скачивание LLM, настройка подключения Airflow к PostgreSQL"
	echo "- up - запуск приложений"
	echo "- load_model - скачивание LLM в контейнере ollama"
	echo "- down - остановка приложений"
	echo "- create_airflow_connection - подключение Airflow к PostgreSQL. Запускается только при первом запуске"
	echo "- info - информация о доступных портах"

.PHONY: all up load_model down create_airflow_connection first_start info help update_env_file