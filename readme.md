# 🔔 Webhook Delivery Platform

A Django-based webhook delivery system supporting reliable ingestion, delivery retries, and subscription management.

---

## 🚀 Live Demo

👉 [Website demo video](https://drive.google.com/file/d/1bMm3WNYwfUEEZJSEu8rkGqt0UxoimqEd/view?usp=sharing)
   
---

## 📦 Tech Stack & Architecture

| Component         | Choice                 |
|------------------|------------------------|
| Framework        | Django + DRF           |
| Database         | PostgreSQL             |
| Async Queueing   | Celery with Redis      |
| Retry Strategy   | Exponential backoff    |
| Deployment       | Docker + Vercel (via webhook trigger) |

### 🔧 Architecture Highlights

- **Django Rest Framework** for API handling
- **Celery** to manage asynchronous webhook deliveries and retries
- **Redis** as the Celery broker
- **PostgreSQL** as the production-grade relational database
- **Docker Compose** for reproducible local development
- **Exponential Backoff** retry policy for webhook delivery failures

---

## 🐳 Local Setup with Docker
   [Website setup in mcbook video](https://drive.google.com/file/d/1jPyDo9JC7OZp22KM4K-1bhRwibD6jYvT/view?usp=sharing)
### 1. Clone the repository

```bash
git clone https://github.com/himanshp1656/himanshu-project.git
cd himanshu-project
docker-compose up --build
```
App: http://localhost:8000

all apis:
api/subscriptions

api/subscriptions/segwise4

ingest/segwise4/

api/subscriptions/segwise4/logs

api/deliveries/uuid

We covered every part in the video trying to host this website now i will share the link if i find a free hosting that can host docker-compose 
 [Website demo video](https://drive.google.com/file/d/1bMm3WNYwfUEEZJSEu8rkGqt0UxoimqEd/view?usp=sharing)
