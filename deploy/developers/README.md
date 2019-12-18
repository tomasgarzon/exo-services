# ExO Lever Developers Docker deployment

### To install docker
```
wget -qO- https://get.docker.com/ | sh
```

### To install docker-compose
```
sudo curl -L https://github.com/docker/compose/releases/download/1.21.0/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

> Remember to add your user to *docker* group: `sudo usermod -aG docker $USER`

### Login into docker
```
docker login
```

### navigate to `~/projects/exo-services/deploy/developers/`


> Remember to set the correctly environment branch variables in `.env` file

### Start a deploy (use `-d` for background)
```
docker-compose up

```
### Update a deploy
```
docker-compose down -v
docker-compose pull
docker-compose up -d
```

### View logs
```
docker-compose logs
```
or
```
docker-compose logs <container-name>
```

### Enter in a container
```
docker-compose exec <container-name> sh
```

### List of containers:
- service-exo-core
- service-exo-medialibrary
- service-exo-opportunities
- service-exo-website
- service-exo-mail
- ...

### Tools (user: $ADMIN_EMAIL pass: $MASTER_PASSWORD)
- http://localhost:8000/tools/postgres/
- http://localhost:8000/tools/rabbitmq/

### Build local repo

Uncomment the `build` part of the container and comment the `image`, check that the path is correct and run:

```
docker-compose build
```

```
docker-compose build service-exo-core
```
