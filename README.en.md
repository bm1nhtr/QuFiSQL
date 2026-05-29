# [QuFiSQL] MySQL Console Application - Quant Finance

> **French version (full documentation):** [README.md](README.md)

Command-line Python application for managing **clients** at a wealth-management firm. Connects to a MySQL database and provides an interactive console menu (CRUD, search, statistics, client detail with related data).

**Tech stack:** Python 3.10+, MySQL 8+, Poetry, `mysql-connector-python`, `python-dotenv`

---

## Table of contents

- [Quick Start](#quick-start)
  - [Where to begin?](#where-to-begin)
  - [Step A — Database](#step-a--database)
  - [Step B — Python application](#step-b--python-application)
  - [Checklist](#checklist)
- [Detailed setup](#detailed-setup)
  - [Prerequisites](#prerequisites)
  - [Install Poetry (if needed)](#install-poetry-if-needed)
  - [Cross-platform notes](#cross-platform-notes)
  - [Install MySQL (if needed)](#1-install-mysql-if-needed)
  - [Run SQL scripts (details)](#2-run-sql-scripts-details)
  - [Configure `.env`](#3-configure-env)
  - [Install and run the application](#4-install-and-run-the-application)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)
  - [Project report (PDF)](#project-report)
  - [Entity-relationship diagram (ERD)](#entity-relationship-diagram-erd)
- [Project domain](#project-domain)
- [Database schema](#database-schema)
- [Project tree](#project-tree)
- [Menu features](#menu-features)
- [Development](#development)

---

## Quick Start

> Run SQL scripts in **MySQL Workbench** or the **terminal** — not in the Python IDE. The app only connects to an existing database.

### Where to begin?

| Your situation | Start here |
|----------------|------------|
| MySQL installed and running, database **not yet** created | **[Step A](#step-a--database)** — SQL scripts |
| Database `quant_finance` **already** created and populated | **[Step B](#step-b--python-application)** — `.env` + Poetry + run app |
| MySQL **not yet** installed | Install MySQL → [Detailed setup §1](#1-install-mysql-if-needed), then **Step A** → **Step B** |
| **Poetry** not installed (`poetry: command not found`) | [Install Poetry](#install-poetry-if-needed), then **Step B** |
| Error on launch | [Troubleshooting](#troubleshooting) |

### Step A — Database

From the project root (`QuFiSQL/`), run **in this order**:

**macOS / Linux / Git Bash:**
```bash
mysql -u root -p < sql/script_creation.sql
mysql -u root -p < sql/ScriptDML.sql
```

**Windows (PowerShell)** — if `<` fails, see [§2 below](#2-run-sql-scripts-details).

Quick verify:
```sql
USE quant_finance;
SELECT COUNT(*) FROM Client;       -- should return 8
SELECT COUNT(*) FROM Gestionnaire; -- should return 6
```

### Step B — Python application

**macOS / Linux:**
```bash
cp .env.example .env
```

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

Edit `.env` — set `DB_PASSWORD` (MySQL `root` password):

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=quant_finance
```

Then (requires **Poetry** — see [Install Poetry](#install-poetry-if-needed) if `poetry` is not recognized):
```bash
poetry config virtualenvs.in-project true
poetry install
poetry run python -m src
```

On success:
```
Quant Finance Console Application
Connecting to MySQL...
Connected successfully.
```

### Checklist

```
[ ] MySQL running
[ ] script_creation.sql executed
[ ] ScriptDML.sql executed
[ ] Poetry installed (`poetry --version`)
[ ] .env configured (DB_PASSWORD)
[ ] poetry install
[ ] poetry run python -m src  →  Connected successfully.
```

---

## Detailed setup

The project has **two separate parts**:

| Part | Role | Where to run |
|------|------|--------------|
| **MySQL database** | Create tables and insert data | MySQL Workbench or terminal (`mysql`) |
| **Python application** | Console menu (CRUD, search, stats) | Terminal or IDE (Cursor, VS Code, PyCharm) |

### Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.10+ | `python --version` or `python3 --version` |
| Poetry | 2.x | `poetry --version` |
| MySQL Server | 8+ | See §1 below |

### Install Poetry (if needed)

**What is Poetry?** It is the project's **Python dependency manager** (similar to `npm` for Node.js). It reads [`pyproject.toml`](pyproject.toml), creates the `.venv/` virtual environment, and installs required libraries (`mysql-connector-python`, etc.). **Step B** commands `poetry install` and `poetry run python -m src` rely on Poetry.

Check if Poetry is already installed:
```bash
poetry --version
```

If the command is not found, install Poetry:

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
Then **close and reopen** the terminal. If `poetry` is still not found, add `%APPDATA%\Python\Scripts` to the Windows PATH.

**Alternative (Windows / macOS / Linux):**
```bash
pip install poetry
# or
pip3 install poetry
```

**macOS (Homebrew):**
```bash
brew install poetry
```

**macOS / Linux (official installer):**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Full docs: [python-poetry.org](https://python-poetry.org/docs/#installation)

### Cross-platform notes

Works on **Windows 10+**, **macOS 12+** (Intel & Apple Silicon), and **Linux**. The Python code uses `pathlib` and has no OS-specific dependencies.

| Item | Windows | macOS / Linux |
|------|---------|---------------|
| Terminal | PowerShell or CMD | bash/zsh |
| Copy `.env` | `Copy-Item .env.example .env` | `cp .env.example .env` |
| Poetry interpreter | `.venv/Scripts/python.exe` | `.venv/bin/python` |
| SQL scripts (CLI) | See PowerShell alternative below | `mysql -u root -p < sql/...` |

### 1. Install MySQL (if needed)

#### Windows

**Option A — MySQL Installer (recommended)**

1. Download [MySQL Installer](https://dev.mysql.com/downloads/installer/)
2. Install **MySQL Server** (+ optional **MySQL Workbench**)
3. Set a `root` password during installation (save it for `.env`)
4. Default port: **3306**
5. Ensure MySQL is running: **Services → MySQL80**, or `Get-Service -Name "*mysql*"` in PowerShell

**Option B — XAMPP**

1. Install [XAMPP](https://www.apachefriends.org/)
2. Start **MySQL** from the XAMPP control panel
3. Default: user `root`, empty password (`DB_PASSWORD=` in `.env`)

#### macOS

**Option A — Homebrew (recommended)**

```bash
brew install mysql
brew services start mysql
mysql_secure_installation   # set root password
brew services list          # verify port 3306
```

**Option B — MySQL DMG installer**

1. Download [MySQL Community Server](https://dev.mysql.com/downloads/mysql/) for macOS
2. Set a `root` password during setup
3. Start MySQL: **System Settings → MySQL → Start**, or `mysql.server start`

**Verify connection (all OS):**

**MySQL Workbench:** open Workbench → `Local instance MySQL` → enter your `root` password.

**Terminal:**
```bash
mysql -u root -p
```
If you see the `mysql>` prompt, the connection works. Type `EXIT;` to quit.

> On macOS with Homebrew, if `mysql` is not found:  
> `echo 'export PATH="/opt/homebrew/opt/mysql/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc`  
> (Intel Macs: replace `/opt/homebrew` with `/usr/local`)

### 2. Run SQL scripts (details)

| Script | Type | Action |
|--------|------|--------|
| `sql/script_creation.sql` | DDL | Creates `quant_finance` database and 7 tables |
| `sql/ScriptDML.sql` | DML | Inserts demo data |

The file `sql/requetes.sql` contains analytical **SELECT** queries (R1–R15) — it does not create tables or data. Run it separately to test SQL queries.

#### Method 1 — MySQL Workbench (recommended for beginners, all OS)

1. Open **MySQL Workbench** and connect
2. **File → Open SQL Script…** → select `sql/script_creation.sql`
3. Click **Execute** (lightning icon) or `Ctrl+Shift+Enter` (macOS: `Cmd+Shift+Enter`)
4. Check success in the **Action Output** tab
5. Repeat with `sql/ScriptDML.sql`

#### Method 2 — Command line

From the project root (`QuFiSQL/`):

**macOS / Linux / Git Bash:**
```bash
mysql -u root -p < sql/script_creation.sql
mysql -u root -p < sql/ScriptDML.sql
```

**Windows (PowerShell)** — if `<` redirection fails:
```powershell
Get-Content sql/script_creation.sql | mysql -u root -p
Get-Content sql/ScriptDML.sql | mysql -u root -p
```

**Windows (CMD or Git Bash)** — bash syntax also works:
```bash
mysql -u root -p < sql/script_creation.sql
mysql -u root -p < sql/ScriptDML.sql
```

#### Verify data was inserted

```sql
USE quant_finance;
SELECT COUNT(*) FROM Client;       -- should return 8
SELECT COUNT(*) FROM Gestionnaire; -- should return 6
```

### 3. Configure `.env`

**macOS / Linux:** `cp .env.example .env`  
**Windows (PowerShell):** `Copy-Item .env.example .env`

Edit `.env`:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=quant_finance
```

> `.env` is never committed. Only `.env.example` is versioned.

### 4. Install and run the application

```bash
poetry config virtualenvs.in-project true
poetry install
```

**Terminal (recommended) — macOS, Linux and Windows:**
```bash
poetry run python -m src
# or
poetry run python main.py
```

**In an IDE (Cursor / VS Code / PyCharm):**
1. Open the `QuFiSQL/` folder as the project
2. Select the Python interpreter for your OS:

| OS | Interpreter path |
|----|------------------|
| Windows | `.venv/Scripts/python.exe` |
| macOS / Linux | `.venv/bin/python` |

3. Run `main.py` or execute module `src` (`python -m src`)

> On macOS, use the built-in **Terminal** (Cursor/VS Code: `` Ctrl+` ``) or the Terminal app, `cd` into `QuFiSQL/`, then run the Poetry commands above.

---

## Troubleshooting

| Error | Likely cause | Windows | macOS |
|-------|--------------|---------|-------|
| `Can't connect to MySQL server on 'localhost'` | MySQL not running | Services → MySQL80, or XAMPP | `brew services start mysql` or `mysql.server start` |
| `Access denied for user 'root'@'localhost'` | Wrong password | Check `DB_PASSWORD` in `.env` | Same |
| `Unknown database 'quant_finance'` | SQL scripts not run | Re-run `script_creation.sql` then `ScriptDML.sql` | Same |
| `Table 'quant_finance.Client' doesn't exist` | DDL not run | Run `script_creation.sql` | Same |
| `poetry: command not found` | Poetry not installed | [Install Poetry](#install-poetry-if-needed) (`pip install poetry`) | Same, or `brew install poetry` |
| `mysql: command not found` | MySQL client not in PATH | Reinstall MySQL or add to PATH | `brew install mysql` then configure PATH (see §1) |
| Empty menu / no clients | DML not run | Run `ScriptDML.sql` | Same |

**Reset the database completely (macOS / Linux / Git Bash):**
```bash
mysql -u root -p -e "DROP DATABASE IF EXISTS quant_finance;"
mysql -u root -p < sql/script_creation.sql
mysql -u root -p < sql/ScriptDML.sql
```

**Reset on PowerShell (Windows):**
```powershell
mysql -u root -p -e "DROP DATABASE IF EXISTS quant_finance;"
Get-Content sql/script_creation.sql | mysql -u root -p
Get-Content sql/ScriptDML.sql | mysql -u root -p
```

---

## Documentation

### Project report

**Main project deliverable** (French).

**[Open report (PDF) → docs/Rapport_BDD.pdf](docs/Rapport_BDD.pdf)**

| Report contents | |
|-----------------|---|
| Modelling | ERD, logical schema, data dictionary, business rules |
| SQL queries | 15 analytical queries (R1–R15) |
| Application | Python console interface description |
| Appendices | Source code, SQL scripts |

### Other resources

| Resource | Description |
|----------|-------------|
| [Report (PDF, English)](docs/BDD_report.pdf) | Complete project report |
| ERD (below) | Conceptual data model — 7 entities, relationships and cardinalities |

### Entity-relationship diagram (ERD)

![Conceptual data model — Quant Finance](docs/MCD_Quant_Finance.jpg)

The schema covers **Manager → Client → Portfolio → Position / Transaction**, with financial instruments and price history.

---

## Project domain

**Wealth management / Quantitative finance**

| Item | Description |
|------|-------------|
| Main CRUD entity | **Client** — investor managed by an assigned manager |
| Related data (read) | **Manager**, **Portfolio** |
| Full schema | 7 tables: Manager, Client, Portfolio, Instrument, Position, PriceHistory, Transaction |

The console app focuses on the `Client` table while displaying related manager and portfolio data (menu option 8).

Key business rules enforced in the schema include: unique client email, positive AUM, aggressive profiles requiring AUM ≥ €100,000, position weights between 0 and 1, and ISO 4217 currency codes. See the [French README](README.md#règles-métiers) for the full list (RM01–RM18).

---

## Database schema

| Table | Purpose |
|-------|---------|
| `Gestionnaire` | Portfolio managers |
| `Client` | Investors (main application entity) |
| `Portefeuille` | Client portfolios (NAV, strategy, currency) |
| `Instrument` | Financial instruments (stocks, bonds, ETFs, derivatives) |
| `Position` | Portfolio holdings at a valuation date |
| `PrixHistorique` | Historical price data per instrument |
| `Transaction` | Buy/sell operations on portfolios |

Full column definitions: [French README — Data dictionary](README.md#dictionnaire-des-données).

---

## Project tree

Folder layout and role of each component:

```
QuFiSQL/
├── README.md               # Full documentation (French)
├── README.en.md            # This file (English)
├── pyproject.toml
├── poetry.lock
├── .env.example
├── main.py
├── docs/
│   ├── Rapport_BDD.pdf     # Full project report (French)
│   ├── BDD_report.pdf      # Full project report (English)
│   └── MCD_Quant_Finance.jpg
├── sql/
│   ├── script_creation.sql # DDL schema
│   ├── ScriptDML.sql       # Demo data
│   └── requetes.sql        # Analytical queries R1–R15
└── src/
    ├── __main__.py
    └── app/
        ├── config.py       # Constants + .env loading
        ├── db.py           # MySQL connection
        ├── repositories/
        │   └── client_repository.py
        └── ui/
            ├── menu.py
            ├── handlers.py
            ├── prompts.py
            └── formatters.py
```

---

## Menu features

| # | Action |
|---|--------|
| 1 | Add a client |
| 2 | List all clients |
| 3 | Search by criterion (risk profile, manager, AUM range) |
| 4 | Update a client |
| 5 | Delete a client |
| 6 | Statistics and rankings |
| 7 | Keyword search |
| 8 | Client detail + manager + portfolios |
| 9 | List available managers |
| 0 | Exit |

---

## Development

```bash
poetry run ruff check .        # lint
poetry run ruff format .       # format
poetry run ruff check . --fix  # auto-fix
```

To add a menu feature: add SQL in `client_repository.py` → handler in `handlers.py` → register in `menu.py`.
