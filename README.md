# 🚀 AI-Agentic Career Guidance & Opportunity Navigator (AI-Career-Guidance-Agent)

An AI-driven multi-agent career guidance system designed for personalized academic, career pathway, skill gap, and opportunity navigation.

---

## 🏗️ Architecture & Developer Work Allocation Matrix

The project is built on **Flask** using a **modular blueprint architecture** and **Flask-SQLAlchemy**. This clean boundary separation allows **4 developers** to work concurrently on separate directories without git merge conflicts.

```
AI_Career_Guidance_Agent/
├── app.py                      # Flask Application Factory & Central Blueprint Registration
├── config.py                   # Environment Configuration (Dev, Test, Prod)
├── db.py                       # Shared Flask-SQLAlchemy Database Instance
├── requirements.txt            # Python Dependencies
├── .env.example                # Environment Variable Template
├── README.md                   # Documentation & Developer Guide
│
├── 👤 profile/                 # [Dev 1] Student Profile & Interest Intelligence
│   ├── routes.py
│   ├── models.py
│   └── services.py
│
├── 🗺️ career/                  # [Dev 2] Career Pathway Guidance
│   ├── routes.py
│   ├── models.py
│   └── services.py
│
├── 🎓 education/               # [Dev 2] Education Pathway Guidance
│   ├── routes.py
│   ├── models.py
│   └── services.py
│
├── 💼 opportunities/           # [Dev 3] Jobs, Govt Jobs, Exams, Internships & Scholarships
│   ├── routes.py
│   ├── models.py
│   └── services.py
│
├── ⚖️ eligibility/             # [Dev 2] Eligibility Checking Engine
│   ├── routes.py
│   └── services.py
│
├── ⚡ skill_gap/               # [Dev 3] Skill Gap Analysis Engine
│   ├── routes.py
│   └── services.py
│
├── 📅 planner/                 # [Dev 4] Personalized Career Action Planner
│   ├── routes.py
│   ├── models.py
│   └── services.py
│
├── 🔔 notifications/           # [Dev 4] Personalized Notifications System
│   ├── routes.py
│   └── services.py
│
├── 🤖 agents/                  # [Dev 4] Multi-Agent Orchestrator & Base Agent Class
│   ├── orchestrator.py
│   ├── base_agent.py
│   └── routes.py
│
├── templates/                  # Jinja2 Layout Templates
├── static/                     # CSS & JS Frontend Assets
└── tests/                      # Pytest Automated Test Suite
```

---

## 👥 Module Work Breakdown for 4 Developers

| Developer | Assigned Modules | Focus Areas & Responsibilities |
|---|---|---|
| **Developer 1** | `profile/` | Student onboarding, interest extraction, academic background profiling, and `StudentProfile` model. |
| **Developer 2** | `career/`, `education/`, `eligibility/` | Career & degree roadmaps, course recommendations, and rule-based/AI eligibility verification logic. |
| **Developer 3** | `opportunities/`, `skill_gap/` | Opportunity scraping/aggregation (Jobs, Govt Exams, Internships, Scholarships) and skills gap matrix calculation. |
| **Developer 4** | `planner/`, `notifications/`, `agents/` | Action milestone generator, deadline alerts dispatch, multi-agent orchestration & sub-agent routing. |

---

## 🔄 How Modules Connect & Workflow Flow

```
+-----------------------------------------------------------------------------------+
|                                 USER / STUDENT                                    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
                      +-------------------------------------+
                      |    1. Student Profile Intelligence  |
                      |              (profile/)             |
                      +-------------------------------------+
                                         |
            +----------------------------+----------------------------+
            |                            |                            |
            v                            v                            v
+-----------------------+    +-----------------------+    +-----------------------+
|  2. Career Pathways   |    | 3. Education Pathways |    |    4. Opportunities   |
|       (career/)       |    |      (education/)     |    |    (opportunities/)   |
+-----------------------+    +-----------------------+    +-----------------------+
            |                            |                            |
            +----------------------------+----------------------------+
                                         |
                                         v
                      +-------------------------------------+
                      |    5. Skill Gap Analysis Engine     |
                      |            (skill_gap/)             |
                      +-------------------------------------+
                                         |
                                         v
                      +-------------------------------------+
                      |    6. Eligibility Checking Engine   |
                      |           (eligibility/)            |
                      +-------------------------------------+
                                         |
                                         v
                      +-------------------------------------+
                      |   7. Career Action Planner          |
                      |             (planner/)              |
                      +-------------------------------------+
                                         |
                                         v
                      +-------------------------------------+
                      |    8. Multi-Agent Orchestrator      |
                      |              (agents/)              |
                      +-------------------------------------+
                                         |
                                         v
                      +-------------------------------------+
                      |    9. Personalized Notifications    |
                      |           (notifications/)          |
                      +-------------------------------------+
```

---

## ⚡ Quick Start Guide

### 1. Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
```

### 3. Run Application
```bash
python app.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser.

### 4. Run Automated Tests
```bash
pytest
```
