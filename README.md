# MyRecipe

MyRecipe is a website to store and share your recipes. It is mobile-oriented and aims for simplicity.

Available at [myrecipe.qchateau.ovh](https://myrecipe.qchateau.fr).

# Backup

## Database

Use crontab to dump the DB

```
docker exec -t my-recipe-db-1 pg_dumpall -c -U postgres > ./backup/my_recipe_pgdump_$(date +\%Y_\%m_\%d"_"\%H_\%M_\%S).sql
```

## Media

```
docker cp my-recipe-backend-1:/media/ ./backup/
```

# Restore

## Database

```
$ docker exec -it my-recipe-db-1 psql -U postgres
postgres=# DROP SCHEMA public CASCADE;
postgres=# CREATE SCHEMA public;
$ docker exec -i my-recipe-db-1 psql -U postgres < ./<dump>.sql
```

## Media

```
docker cp ./media/ my-recipe-backend-1:/
```
