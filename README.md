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
(only if DEBUG=True)
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
### Front
Colors:
- ![#221E1F](https://placehold.co/10x10/221E1F/221E1F.png)`#221E1F`
- ![#2a211d](https://placehold.co/10x10/2a211d/2a211d.png)`#2a211d`
- ![#342923](https://placehold.co/10x10/342923/342923.png)`#342923`+
- ![#281911](https://placehold.co/10x10/281911/281911.png)`#281911`
- ![#B0A38D](https://placehold.co/10x10/B0A38D/B0A38D.png)`#B0A38D`+
- ![#D8C3A2](https://placehold.co/10x10/D8C3A2/D8C3A2.png)`#D8C3A2`+
- ![#DCBE66](https://placehold.co/10x10/DCBE66/DCBE66.png)`#DCBE66`+
- ![#EECD5E](https://placehold.co/10x10/EECD5E/EECD5E.png)`#EECD5E`+

Additional
- ![#D8C3A2](https://placehold.co/10x10/D8C3A2/D8C3A2.png)`#D8C3A2`
- ![#978E71](https://placehold.co/10x10/978E71/978E71.png)`#978e71`
- ![#a2d8cb](https://placehold.co/10x10/a2d8cb/a2d8cb.png)`#a2d8cb`
- ![#71978e](https://placehold.co/10x10/71978e/71978e.png)`#71978e`
- ![#4a827d](https://placehold.co/10x10/4a827d/4a827d.png)`#4a827d`+
- ![#5ba099](https://placehold.co/10x10/5ba099/5ba099.png)`#5ba099`+
- ![#dfeceb](https://placehold.co/10x10/dfeceb/dfeceb.png)`#dfeceb`+
- ![#d8a2d1](https://placehold.co/10x10/d8a2d1/d8a2d1.png)`#d8a2d1`+


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
