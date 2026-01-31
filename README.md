# TCM Clinical Intelligent Decision Support System

## Overview

This repository contains the implementation of an undergraduate graduation project titled  
**“Design of a Traditional Chinese Medicine Clinical Intelligent Decision Support System.”**

The project aims to integrate **Traditional Chinese Medicine (TCM) clinical knowledge** with **artificial intelligence techniques** to build an intelligent system that assists doctors and patients in diagnosis, prescription recommendation, and medical information management.

The system is implemented using the **Django web framework**, combines **relational databases (MySQL)** and a **knowledge graph (Neo4j)**, and introduces **Graph Neural Networks (GNN / GCN)** to enhance clinical reasoning based on symptom–syndrome–prescription relationships.

---

## Key Features

### Intelligent Diagnosis Assistance
- Structured online inquiry for collecting patient symptoms
- Symptom normalization and multi-symptom analysis
- Knowledge graph–based matching between symptoms, syndromes, and prescriptions
- Recommendation of candidate TCM prescriptions for clinical reference

### Prescription and Medicine Recommendation
- Query of classical TCM prescriptions with composition and indications
- Single-herb query with effects, indications, and usage
- Doctors can modify system recommendations and generate empirical prescriptions
- Empirical prescriptions can be stored to improve future diagnosis support

### Multi-Role User Management
The system supports three user roles:

- **Administrator**
  - User and doctor management
  - Doctor qualification review
  - System content management

- **Doctor**
  - Online consultation and appointment handling
  - Assisted diagnosis and prescription generation
  - Maintenance of empirical prescriptions

- **Patient**
  - Online inquiry and appointment booking
  - Personal health record management
  - Intelligent diagnosis and medicine consultation

---

## System Architecture

```
Frontend (HTML / CSS / JavaScript)
        ↓
Backend (Django)
        ↓
Data Layer
  - MySQL (structured system data)
  - Neo4j (TCM knowledge graph)
        ↓
AI Module
  - Graph Neural Network (GCN)
```

---

## Repository Structure

```
.
├── IM_Sys/                # Main Django system code
│   ├── adminApp/          # Administrator module
│   ├── DoctorApp/         # Doctor module
│   ├── UserApp/           # Patient module
│   ├── templates/         # HTML templates
│   └── static/            # Static resources (CSS / JS / images)
│
├── gnn/                   # Graph Neural Network module
│   ├── GNN.py
│   ├── graph_data.pt
│   └── test.py
│
├── MySQL数据库/           # MySQL database schema and sample data
├── 图数据库/              # Neo4j knowledge graph construction data
├── crawler.py             # Web crawler for TCM data collection
├── code.txt               # Auxiliary or experimental code
├── data.xlsx              # TCM prescription or herb data
└── .gitignore
```

---

## Technologies Used

- **Programming Language**: Python
- **Backend Framework**: Django
- **Frontend**: HTML, CSS, JavaScript
- **Relational Database**: MySQL
- **Graph Database**: Neo4j
- **AI Techniques**:
  - Knowledge Graph Modeling
  - Graph Convolutional Networks (GCN)
  - Symptom normalization and matching
- **Data Acquisition**: Web crawling and Excel-based data integration

---

## How to Run (Basic)

```bash
# Install required dependencies
pip install django neo4j torch

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

> Note: Neo4j must be running and properly configured before starting the system.

---

## Academic Background

This project is based on the undergraduate thesis:

**Design of a Traditional Chinese Medicine Clinical Intelligent Decision Support System**  
China University of Petroleum (East China)  
Major: Intelligent Science and Technology  
Author: Kaiyue Yang  
Year: 2024

---

## Disclaimer

- This system is developed for **educational and research purposes only**
- It is **not intended for real clinical diagnosis**
- All diagnostic results are provided for reference only

---

## License

This project is intended for academic use only.  
Commercial use is not permitted without explicit authorization.
