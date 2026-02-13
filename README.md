# Dynamic Pricing AI SaaS

## System Architecture Diagram + Service Communication Flow

---

## 🏗 System Architecture (Microservice View)

```
                   ┌──────────────────────┐
                   │      Frontend        │
                   │  (Admin Dashboard)   │
                   └─────────┬────────────┘
                             │
                             ▼
                   ┌──────────────────────┐
                   │     API Gateway      │
                   │  Nginx + Traefik     │
                   └─────────┬────────────┘
                             │
                             ▼
                   ┌──────────────────────┐
                   │     Pricing API      │
                   │      FastAPI         │
                   └─────────┬────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐     ┌──────────────┐
│ Auth Service │    │ Pricing Core │     │ Admin Config │
│  Keycloak    │    │ FastAPI      │     │ FastAPI      │
└──────────────┘    └──────┬───────┘     └──────────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   Event Bus (Kafka)  │
                 └─────────┬────────────┘
                           │
   ┌──────────────┬────────┼────────┬──────────────┐
   ▼              ▼        ▼        ▼              ▼
┌────────┐  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Scraper │  │Demand  │ │Feature │ │Optimizer│ │ Agent  │
│Service │  │Service │ │Service │ │Service │ │Service │
└────────┘  └────────┘ └────────┘ └────────┘ └────────┘
```

---

## 🔄 Service Responsibilities

| Service | Responsibility |
|--------|---------------|
| API Gateway | Traffic control, routing |
| Keycloak | Authentication & Tenant Identity |
| Pricing API | Public pricing endpoints |
| Scraper Service | Competitor pricing ingestion |
| Demand Service | Demand forecasting |
| Feature Service | Feature engineering |
| Optimization Service | Price optimization |
| Agent Service | Auto decision engine |
| Kafka | Event orchestration |

---

## ⚡ Service Communication Flow

### 1️⃣ Competitor Update Flow

```
Scraper Service
      │
      ▼
Publish → CompetitorPriceUpdated (Kafka)
      │
      ▼
Feature Service consumes
      │
      ▼
FeatureUpdated event
```

---

### 2️⃣ Demand Prediction Flow

```
Sales Data → Demand Service
        │
        ▼
ForecastReady event
        │
        ▼
Optimizer Service
```

---

### 3️⃣ Pricing Decision Flow

```
FeatureUpdated
DemandForecastReady
InventoryChanged
        │
        ▼
PriceDecisionRequested
        │
        ▼
Optimizer Service
        │
        ▼
PriceOptimized event
```

---

### 4️⃣ AI Agent Flow

```
PriceOptimized
        │
        ▼
Agent Service
        │
        ├── Validate Risk
        ├── Apply Guardrails
        └── Decide Auto / Manual
        │
        ▼
FinalPricePublished
```

---

### 5️⃣ Frontend Query Flow

```
Frontend → API Gateway
         → Pricing API
         → Redis Cache
         → PostgreSQL
         → Return Price
```

---

## 🧠 ML Decision Pipeline

```
Raw Data
  │
  ▼
Feature Service
  │
  ▼
Demand Model
  │
  ▼
Elasticity Model
  │
  ▼
Optimization Engine
  │
  ▼
AI Agent
  │
  ▼
Final Price
```

---

## 🧱 Data Flow Layers

| Layer | Storage |
|------|---------|
| Transactional | PostgreSQL |
| Feature Store | PostgreSQL |
| Cache | Redis |
| Event Streaming | Kafka |
| Model Artifacts | Object Storage |

---

## 🧩 Infrastructure Layer

```
Podman → Container Runtime
Harbor → Image Registry
K3s → Orchestration
Helm → Application Packaging
ArgoCD → GitOps Deployment
Vault → Secrets Management
```

---

## 📡 Observability Flow

```
Services → OpenTelemetry
         → Prometheus (metrics)
         → Loki (logs)
         → Grafana (visualization)
         → Sentry (errors)
```

---

## 🔐 Security Flow

```
User → Keycloak Login
     → JWT
     → API Gateway
     → Pricing API
     → Tenant Context
```

---

## 🔁 Decision Loop

```
Market Changes
    │
    ▼
Events
    │
    ▼
ML Prediction
    │
    ▼
Optimization
    │
    ▼
AI Agent
    │
    ▼
Publish Price
    │
    ▼
Measure Outcome
    │
    ▼
Feedback Loop
```

