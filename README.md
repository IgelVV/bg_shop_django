# bg_shop_django

## Installation
- install docker
- install git
- git clone
- docker compose up
- docker exec bash script to load init db data from fixtures `scripts/init_load_data.sh`

## Dev run
- starting Docker 
```shell
sudo systemctl start docker
```

- starting RabbitMQ
```shell
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
```

- starting Celery worker in proj directory
(in prod Daemonization instead)
```shell
celery -A bg_shop worker -l info
```

- run django server
```shell
py manage.py runserver
```

---
### run Dockerfile (cheat sheet)

- build and run
```shell
docker build . -t bg_shop
```
```shell
docker run --rm --name bg -v ./bg_shop/database:/app/database -p 8000:8000 -d -e "DJANGO_DEBUG=1" bg_shop
```
or use docker compose
```shell
docker compose up --build -d
```

- open bash interactively
```shell
docker exec -it bg bash
```
or
```shell
docker compose exec -it app bash
```

- inside container (first run)
```shell
bash scripts/init_load_data.sh
```

- logs 
```shell
docker logs bg
```
or
```shell
docker compose logs -f
```


## Dev Notes (Cheat sheet)
- get select related cache
```python
obj._state.fields_cache
``` 
- get prefetch related cache
```python
obj._prefetched_objects_cache
```
- "How to see the raw SQL queries Django is running?"
```python
from django.db import reset_queries
from django.db import connection

reset_queries()
# Run your query here
print(connection.queries)
```

### Testing

- To carry out testing without starting Celery.
```shell
py manage.py test --exclude-tag=celery
```

## Name

## Description

## Badges

## Visuals

## Usage

## Support

## Roadmap

## Contributing

## Authors and acknowledgment

## License

## Project status
