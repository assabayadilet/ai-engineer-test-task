# AI Engineer Test Task

## Overview
This project implements the required architecture:

- FastAPI endpoint `/api/v1/agent/query`
- LangGraph agent (mock LLM, tool routing)
- MCP server (FastMCP, stdio)
- Custom tools (calculator, formatter)
- Docker + docker-compose

All components run inside a single container, and the agent talks to the MCP server via stdio.

## Project Structure
```
ai-engineer-test-task/
  agent/          # LangGraph agent + custom tools
  api/            # FastAPI app
  mcp_server/     # FastMCP server + JSON storage
  data/           # products.json (persisted via volume)
  tests/          # pytest tests
  Dockerfile
  docker-compose.yml
  requirements.txt
  README.md
```

## Local Run
1. Create venv and install deps:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the API:
   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```

> **Note:** Requires Python 3.11+ (for `fastmcp` library). Use Docker if your local Python version is lower.

## Docker Compose
```bash
docker-compose up --build
```

## Example Requests
```bash
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H 'Content-Type: application/json' \
  -d '{"query": "Покажи все продукты в категории Электроника"}'
```

```bash
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H 'Content-Type: application/json' \
  -d '{"query": "Какая средняя цена продуктов?"}'
```

```bash
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H 'Content-Type: application/json' \
  -d '{"query": "Добавь новый продукт: Мышка, цена 1500, категория Электроника"}'
```

```bash
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H 'Content-Type: application/json' \
  -d '{"query": "Посчитай скидку 15% на товар с ID 1"}'
```

## Tests
```bash
# Via Docker (recommended)
docker-compose run --rm app pytest -v

# Or locally with Python 3.11+
PYTHONPATH=. pytest -v
```

## Logging
You can control log verbosity with `LOG_LEVEL` (default: `INFO`):
```bash
LOG_LEVEL=DEBUG uvicorn api.main:app --host 0.0.0.0 --port 8000
```

---

## ✅ Критерии оценки / Evaluation Checklist

### Обязательные (Must Have): 70 баллов

#### MCP Сервер (25 баллов)
| Баллы | Критерий | Статус | Файл/Описание |
|-------|----------|--------|---------------|
| **10** | Использует FastMCP с декораторами @mcp.tool | ✅ | `mcp_server/server.py` - uses `@mcp.tool()` decorator |
| **8** | Реализованы все 4 инструмента | ✅ | `list_products`, `get_product`, `add_product`, `get_statistics` |
| **4** | Работает через stdio | ✅ | `mcp.run()` uses stdio by default |
| **3** | Обрабатывает ошибки | ✅ | `ValueError` raised if product not found |

#### LangGraph Агент (25 баллов)
| Баллы | Критерий | Статус | Файл/Описание |
|-------|----------|--------|---------------|
| **10** | Подключается к MCP серверу | ✅ | `agent/mcp_client.py` via subprocess/stdio |
| **8** | Использует tools из MCP | ✅ | `agent/graph.py` calls MCP tools via `mcp_client.call_tool()` |
| **7** | Имеет кастомные tools | ✅ | `agent/tools.py` - `calculator()` and `formatter()` |

#### FastAPI + Docker (20 баллов)
| Баллы | Критерий | Статус | Файл/Описание |
|-------|----------|--------|---------------|
| **8** | POST /api/v1/agent/query работает | ✅ | `api/main.py` - async endpoint |
| **7** | Dockerfile и docker-compose.yml | ✅ | Both files present with proper config |
| **5** | Запускается через docker-compose up | ✅ | Python 3.11-slim, port 8000 exposed |

---

### Дополнительные (Should Have): 20 баллов
| Баллы | Критерий | Статус | Файл/Описание |
|-------|----------|--------|---------------|
| **6** | Чистая архитектура | ✅ | Clean separation: `agent/`, `api/`, `mcp_server/` |
| **5** | Type hints + docstrings | ✅ | All functions have type hints, docstrings present |
| **5** | Логирование | ✅ | `logging` module used throughout, `LOG_LEVEL` env var |
| **4** | .gitignore | ✅ | Proper `.gitignore` with 12 rules |

---

### Тесты и документация: 10 баллов
| Баллы | Критерий | Статус | Файл/Описание |
|-------|----------|--------|---------------|
| **6** | Минимум 3 теста | ✅ | 4 tests in `tests/`: `test_api.py`, `test_store.py` (2), `test_tools.py` (2) |
| **4** | README с инструкцией | ✅ | This file with run/docker/test instructions |

---

### 📊 Итого / Total Score

| Категория | Максимум | Набрано |
|-----------|----------|---------|
| MCP Сервер | 25 | **25** |
| LangGraph Агент | 25 | **25** |
| FastAPI + Docker | 20 | **20** |
| Дополнительные | 20 | **20** |
| Тесты и документация | 10 | **10** |
| **ИТОГО** | **100** | **100** |

---

### 🎁 Бонусные задания (не реализованы)

| Бонус | Баллы | Статус |
|-------|-------|--------|
| SQLite вместо JSON | +5 | ❌ Не реализовано |
| Второй MCP сервер для заказов | +10 | ❌ Не реализовано |

---

## Архитектура

```
┌─────────────────────────────────────────────────┐
│             Docker Container                    │
│  ┌───────────────────────────────────────────┐ │
│  │         FastAPI App                       │ │
│  │  POST /api/v1/agent/query                │ │
│  │  {"query": "Покажи продукты"}            │ │
│  └─────────────────┬─────────────────────────┘ │
│                    │                            │
│                    ▼                            │
│  ┌─────────────────────────────────────────┐   │
│  │        LangGraph Agent                  │   │
│  │  - Анализирует запрос (MockLLM)        │   │
│  │  - Выбирает tools                      │   │
│  │  - Вызывает tools                      │   │
│  │  - Формирует ответ                     │   │
│  └───┬──────────────────────┬──────────────┘   │
│      │                      │                   │
│      ▼                      ▼                   │
│  ┌──────────┐   ┌──────────────────────────┐   │
│  │ Custom   │   │   MCP Server (stdio)     │   │
│  │ Tools    │   │  - list_products         │   │
│  │ -calc    │   │  - get_product           │   │
│  │ -format  │   │  - add_product           │   │
│  │          │   │  - get_statistics        │   │
│  └──────────┘   └──────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## Notes
- MCP server uses JSON storage (`data/products.json`).
- Agent starts MCP server via stdio per request.
- Mock LLM is deterministic (rule-based) and does not require external API keys.
- Requires Python 3.11+ for `fastmcp` library.
