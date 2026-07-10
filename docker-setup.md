# Frappe CRM Setup Guide

## Prerequisites

- Docker Desktop
- Git

---

## 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
git checkout feature/ticket-management
```

---

## 2. Start Docker Containers

```bash
cd docker
docker compose up -d
```

Wait until all containers are running.

Verify:

```bash
docker ps
```

---

## 3. Copy the Database Backup

Copy the provided SQL backup into the container.

Example:

```bash
docker cp database.sql.gz crm-frappe-1:/home/frappe/frappe-bench/sites/crm.localhost/private/backups/
```

---

## 4. Copy site_config.json

Replace the generated `site_config.json` with the provided one.

```bash
docker cp site_config.json crm-frappe-1:/home/frappe/frappe-bench/sites/crm.localhost/site_config.json
```

---

## 5. Restore the Database

Open the Frappe container:

```bash
docker exec -it crm-frappe-1 bash
```

Go to the bench:

```bash
cd ~/frappe-bench
```

Restore the backup:

```bash
bench --site crm.localhost --force restore sites/crm.localhost/private/backups/database.sql.gz
```

---

## 6. Run Database Migration

```bash
bench --site crm.localhost migrate
```

---

## 7. Build Frontend Assets

```bash
bench build
```

---

## 8. Restart Docker

Exit the container:

```bash
exit
```

Restart the services:

```bash
docker compose restart
```

---

## Login

URL:

```
http://localhost:8000
```

Username:

```
Administrator
```

Password:

```
admin
```

---

## Notes

- Branch used: `feature/ticket-management`
- Database backup contains the latest migrated data.
- No public or private uploaded files are included because the site currently has no uploaded attachments.