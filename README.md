# 📊 DataPulse Backend

A FastAPI-powered backend for **DataPulse** – a smart analytics platform that connects to retail sales portals, analyzes data continuously, and delivers actionable business recommendations.

---

## 🔍 Key Features
- Real-time & historical sales data ingestion
- Predictive analytics and trend detection
- Competitor benchmarking (coming soon)
- Personalized KPI dashboards and reports
- Multi-language support (Arabic + English)
- Subscription model with auto-scaling usage tiers

---

## 🚀 Tech Stack
- **Backend**: FastAPI, Python 3.11
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Auth**: OAuth2 + JWT
- **Async Tasks**: Celery + Redis
- **Containerized**: Docker + Docker Compose

---

## 🛠️ Local Setup

```bash
git clone https://github.com/tarigelamin1997/datapulse-backend.git
cd datapulse-backend
cp .env.example .env
docker-compose up --build
