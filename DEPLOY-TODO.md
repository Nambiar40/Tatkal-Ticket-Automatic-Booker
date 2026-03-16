# Railway Django + Postgres + Redis Deploy

## Steps:
- [x] 1. Create requirements.txt, runtime.txt, railway.toml (app config)
- [ ] 2. Git add/commit/push to GitHub main
- [ ] 3. railway.app: New Project → Deploy from GitHub repo (Tatkal-Ticket-Automatic-Booker)
- [ ] 4. Add Postgres plugin (link DATABASE_URL)
- [ ] 5. Add Redis plugin (link REDIS_URL → CELERY_BROKER_URL=redis://${{Redis.REDIS_URL}})
- [ ] 6. Railway dashboard: Variables → SECRET_KEY (generate new)
- [ ] 7. Railway shell: `python manage.py migrate`, `python manage.py createsuperuser`, `python manage.py collectstatic --noinput`
- [ ] 8. Live! Generate Railway domain.

