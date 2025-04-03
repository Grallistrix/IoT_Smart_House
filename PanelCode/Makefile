# Nazwa usługi
SERVICE=hello-world

# Uruchomienie kontenera
run: down
	docker-compose up

# Zatrzymanie i usunięcie kontenera
down:
	docker-compose down

# Usunięcie obrazu
clean:
	docker rmi hello-world || true

# Uruchomienie od nowa (stop + run)
restart: down run

# Całkowite usunięcie WSZYSTKICH kontenerów i obrazów Dockera
purge:
	docker stop $$(docker ps -aq) || true
	docker rm $$(docker ps -aq) || true
	docker rmi $$(docker images -q) || true
	docker volume rm $$(docker volume ls -q) || true
	docker network prune -f || true
