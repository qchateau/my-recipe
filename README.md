# MyRecipe

MyRecipe is a website to store and share your recipes. It is mobile-oriented and aims for simplicity.

Available at [myrecipe.qchateau.ovh](https://myrecipe.qchateau.fr).

# Backup

Use crontab to dump the DB and sync to GDrive

```
0 2 * * 0 /usr/bin/docker exec -t my-recipe_db_1 pg_dumpall -c -U postgres > ~/backups/my_recipe_pgdump_$(date +\%Y_\%m_\%d"_"\%H_\%M_\%S).sql; clone copy ~/backups/ gdrive:backup/my-recipe/
```
