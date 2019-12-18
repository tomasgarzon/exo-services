# ExOLever QA Docker deployment

> Remember to add your user to *docker* group: `sudo usermod -aG docker $USER`

### Enter in the server and navigate to `~/server/exolever/<yourmvf>`

```
ssh ubuntu@qa.exolever.com
```

### Start a new deploy
```
./deploy.sh EXO-1273-MVF-ticket-admin-actions exo1273
```

### View logs
```
docker-compose logs
```
or 
```
docker-compose logs <container-name>
```

### Update a deploy
```
docker-compose down -v
docker-compose pull
docker-compose up -d
```

### Enter in a container
```
docker-compose exec <container-name> sh
```

### List of containers (usually you only need to enter in `service-exo-core`:
- service-exo-core
- service-exo-opportunities
- exo-backoffice
- postgres
- redis

### Tools (user: $ADMIN_EMAIL pass: $MASTER_PASSWORD)
- http://localhost:8000/tools/postgres/
