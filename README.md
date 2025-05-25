# Instruction

### 1. Create virtual environment

```bash
python -m venv pizza_env
source pizza_env/bin/activate      # macOS / Linux
pizza_env\Scripts\activate         # Windows
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file in the root directory with the following content:

```env
# --- Neo4j ---
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=your_username
NEO4J_PASSWORD=your_password
NEO4J_DB=your_namedb

# --- PostgreSQL ---
PG_USER=your_username
PG_PASSWORD=your_password
PG_HOST=localhost
PG_PORT=5432
PG_DATABASE=your_namedb

# --- API Key / OpenAI ---
api_key=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```


---
## Start application

This project requires Qdrant running in Docker.

### Option A – via `run.py` (automatic)

No manual steps needed. `run.py` will launch Qdrant automatically.

### Option B – manual start

```bash
docker-compose -f qdrant/docker-compose.yml up -d
```

Ensure Docker Desktop is running before executing the above.

---

### 3. Run the Application

```bash
python run.py
```

This will:
- Launch Qdrant if not already running
- Start FastAPI at: **http://localhost:8000/docs**
- Management Qdranr at: **http://localhost:6333/dashboard#/collections**

---



