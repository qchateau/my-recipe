# MyRecipe

MyRecipe is a website to store and share your recipes. It is mobile-oriented and aims for simplicity.

Available at [myrecipe.qchateau.ovh](https://myrecipe.qchateau.fr).

# Setup & Configuration

## 1. Environment Variables

Copy `sample.env` to `.env`:

```bash
cp sample.env .env
```

Edit `.env` to configure your environment:

| Variable | Description | Example / Default |
| --- | --- | --- |
| `DEBUG` | Enable debug mode and hot reloading | `1` |
| `HTTP_PORT` | Port exposed on host | `8080` |
| `DJANGO_SECRET` | Secret key for Django sessions and security | Random secret string |
| `GOOGLE_AUTH_CLIENT_ID` | Google OAuth 2.0 Client ID | `xxx.apps.googleusercontent.com` |
| `GOOGLE_AUTH_SECRET` | Google OAuth 2.0 Client Secret | `GOCSPX-xxx` |
| `GEMINI_API_KEY` | Google Gemini API key for AI recipe auto-fill | API key from Google AI Studio |
| `GEMINI_MODEL` | Gemini model to use | `gemini-flash-lite-latest` |

---

## 2. Google OAuth 2.0 Setup

MyRecipe uses Google accounts for user authentication:
1. Go to [Google Cloud Console > APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials).
2. Click **Create Credentials** -> **OAuth client ID**.
3. Select Application type: **Web application**.
4. Under **Authorized JavaScript origins**, add:
   - `http://localhost:8080` (or your domain)
5. Under **Authorized redirect URIs**, add:
   - `http://localhost:8080/backend/accounts/google/login/callback/`
6. Copy the **Client ID** and **Client Secret** into `.env`.

---

## 3. Gemini API Key (Recipe Auto-Fill)

To enable auto-filling recipes directly from web page URLs:
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Click **Create API Key** (free tier includes 15 requests/min and 1M tokens/min).
3. Copy the key into `GEMINI_API_KEY` in `.env`.

---

## 4. Running the Application

Start all services with Docker Compose:

```bash
docker compose -f docker-compose.yml -f docker-compose-dev.yml up -d
```

Access the application at `http://localhost:8080` (or your configured `HTTP_PORT`).

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
