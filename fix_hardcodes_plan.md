# Fix Hardcoded Values in All .py Files

Replace hardcoded paths, API keys, filenames, and configuration values in Python files with environment variables, CLI arguments, or configurable constants loaded from `.env` / `os.environ`.

## Summary of Hardcodes Found

### 1. `Script/run_prompt.py` — **Most critical**
| Line | Hardcode | Current Value | Fix |
|------|----------|---------------|-----|
| 7 | `OPENAI_API_KEY` | `"your_api_key_here"` set inline | Load from `.env` via `dotenv` / `os.environ` (remove `os.environ[...] =` line) |
| 8 | `prompt_file` | `"analysis.prompt.md"` | Load from env `PROMPT_FILE` with default |
| 9 | `ontology_file` | `"agentic-o.ttl"` | Load from env `ONTOLOGY_FILE` with default |
| 10 | `model_name` | `"gpt-5-mini"` | Load from env `MODEL_NAME` with default |
| 24 | `outdir` | `"agent-o"` | Load from env `OUTPUT_DIR` with default |

---

### 2. `analytics.py` — **Moderate**
| Line | Hardcode | Current Value | Fix |
|------|----------|---------------|-----|
| 13-14 | fallback file | `"agentO.ttl"` | Use configurable constant |
| 129 | folder paths | `"generated_kg"`, `"output_files"` | Accept CLI args with defaults |

---

### 3. `scripts/normalize_kg.py` — **Minor**
| Line | Hardcode | Current Value | Fix |
|------|----------|---------------|-----|
| 39 | `KG_DIR` | `Path(__file__) / .. / generated_kg / CrewAI` | Already relative to project; acceptable but can be overridden via env |

---

### 4. `scripts/add_kickoff_inputs.py` — **Minor**
| Line | Hardcode | Current Value | Fix |
|------|----------|---------------|-----|
| 13 | `TTL_DIR` | `os.path.join(... "generated_kg", "CrewAI")` | Same as above; override via env |

---

### 5. `src/crewai/run.py` — **Minor**
| Line | Hardcode | Current Value | Fix |
|------|----------|---------------|-----|
| 56 | `output_base` | `os.path.join(project_root, "output_files", "output_crewai")` | Load from env `OUTPUT_BASE` with default |
| 79 | `kg_dir` | `os.path.join(project_root, "generated_kg", "CrewAI")` | Load from env `KG_DIR` with default |
| 96 | `separator_length` | `65` | Already a variable — fine |

---

### 6. `src/crewai/extractor.py`, `src/crewai/generator.py`, `src/crewai/models.py` — **No actionable hardcodes**

These files contain SPARQL queries with ontology IRIs (e.g. `http://www.w3id.org/agentic-ai/onto#`) and known tool/provider mappings. These are **semantic constants** that should NOT be externalized — they're part of the domain logic, not deployment configuration.

---

### 7. `setup.py` — **Obfuscated/encoded, skip**

This file is base64+zlib encoded and auto-generated. Not modifiable.

## Proposed Changes

### [Component 1] `Script/run_prompt.py`

#### [MODIFY] [run_prompt.py](file:///run/media/ajipratama53/Data/VSCode/Python/mrpl-on-7/mrpl-on-8/Script/run_prompt.py)

- Remove the inline `os.environ["OPENAI_API_KEY"] = "..."` line
- Add `from dotenv import load_dotenv` and call `load_dotenv()`
- Load `OPENAI_API_KEY` from env (fail if missing)
- Replace `prompt_file`, `ontology_file`, `model_name`, `outdir` with `os.environ.get(...)` calls with sensible defaults

---

### [Component 2] `analytics.py`

#### [MODIFY] [analytics.py](file:///run/media/ajipratama53/Data/VSCode/Python/mrpl-on-7/mrpl-on-8/analytics.py)

- Replace `"agentO.ttl"` fallback with a configurable constant `FALLBACK_TTL`
- Add `argparse` to accept `kg_folder` and `output_folder` as CLI args with defaults

---

### [Component 3] `scripts/add_kickoff_inputs.py`

#### [MODIFY] [add_kickoff_inputs.py](file:///run/media/ajipratama53/Data/VSCode/Python/mrpl-on-7/mrpl-on-8/scripts/add_kickoff_inputs.py)

- Load `TTL_DIR` from env `TTL_DIR` with existing value as default

---

### [Component 4] `scripts/normalize_kg.py`

#### [MODIFY] [normalize_kg.py](file:///run/media/ajipratama53/Data/VSCode/Python/mrpl-on-7/mrpl-on-8/scripts/normalize_kg.py)

- Load `KG_DIR` from env `KG_DIR` with existing value as default

---

### [Component 5] `src/crewai/run.py`

#### [MODIFY] [run.py](file:///run/media/ajipratama53/Data/VSCode/Python/mrpl-on-7/mrpl-on-8/src/crewai/run.py)

- Load `output_base` from env `OUTPUT_BASE` with existing value as default
- Load `kg_dir` from env `KG_DIR` with existing value as default

## Verification Plan

### Manual Verification
- Run `python -c "import ast; ast.parse(open('file').read())"` on each modified file to verify syntax
- Verify that default values match original behavior (no functional change when env vars are not set)
