"""
CLI Runner: batch-process generated_kg/CrewAI/*.ttl → CrewAI project directories.

Pipeline: KG (.ttl) → SPARQL (Layer 1) → Pydantic IR (Layer 2) → YAML + Python (Layer 3)

Usage:
    From project root:
        python -m src.crewai.run

    Single file:
        python -m src.crewai.run path/to/file.ttl

    Or directly:
        python src/crewai/run.py
"""

import os
import sys
import shutil
import json  # Ditambahkan untuk membuat file manifest.json

# Support both `python -m` and direct script execution
try:
    from .extractor import extract_crew_project
    from .generator import generate_project
except ImportError:
    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    )
    from src.crewai.extractor import extract_crew_project
    from src.crewai.generator import generate_project


def process_single(kg_path: str, output_dir: str) -> str:
    """
    Process a single TTL file through the 3-layer pipeline.

    Args:
        kg_path:    Path to the input .ttl file
        output_dir: Directory to write the generated project

    Returns:
        The output directory path
    """
    # Layer 1: SPARQL extraction → Layer 2: Pydantic IR
    project = extract_crew_project(kg_path)

    # Layer 3: File generation (YAML + Jinja2)
    return generate_project(project, output_dir)


def main():
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    output_base = os.path.join(project_root, "output_files", "output_crewai")

    # Struktur data untuk menampung manifest hasil generasi
    manifest_data = {
        "framework": "CrewAI",
        "output_directory": "output_files/output_crewai",
        "generated_patterns": []
    }

    # ── Handle single-file mode ──
    if len(sys.argv) > 1 and sys.argv[1].endswith(".ttl"):
        kg_path = os.path.abspath(sys.argv[1])
        base_name = os.path.splitext(os.path.basename(kg_path))[0]
        # Remove _instances suffix for cleaner directory name
        dir_name = base_name.replace("_instances", "")
        output_dir = os.path.join(output_base, dir_name)

        print(f"[Processing] {kg_path}")
        process_single(kg_path, output_dir)
        print(f"[Done] → {output_dir}")
        return

    # ── Batch mode: process all TTL files ──
    kg_dir = os.path.join(project_root, "generated_kg", "CrewAI")

    if not os.path.isdir(kg_dir):
        print(f"[ERROR] KG directory not found: {kg_dir}")
        sys.exit(1)

    ttl_files = sorted(f for f in os.listdir(kg_dir) if f.endswith(".ttl"))
    if not ttl_files:
        print(f"[WARNING] No .ttl files found in {kg_dir}")
        sys.exit(0)

    # Clean output directory
    if os.path.exists(output_base):
        shutil.rmtree(output_base)
    os.makedirs(output_base, exist_ok=True)

    # Header
    print("=" * 65)
    print("  KG → SPARQL → Pydantic → CrewAI Project Generator")
    print("  Pipeline: 3-Layer Conversion (SPARQL / Pydantic / YAML+Jinja2)")
    print("=" * 65)
    print(f"  Source : {kg_dir}")
    print(f"  Output : {output_base}")
    print(f"  Files  : {len(ttl_files)} knowledge graphs")
    print("=" * 65)

    # Process each KG
    success = 0
    errors = []

    for filename in ttl_files:
        kg_path = os.path.join(kg_dir, filename)
        base_name = os.path.splitext(filename)[0]
        dir_name = base_name.replace("_instances", "")
        output_dir = os.path.join(output_base, dir_name)

        print(f"\n[Processing] {filename}")
        try:
            process_single(kg_path, output_dir)
            success += 1
            
            # Mencatat info sukses ke dalam struktur data manifest
            manifest_data["generated_patterns"].append({
                "pattern_name": dir_name,
                "source_kg": filename,
                "status": "Success",
                "relative_path": f"output_files/output_crewai/{dir_name}",
                "generated_files": ["agents.yaml", "tasks.yaml", "inputs.yaml", "crew.py", "main.py", "pyproject.toml"]
            })
            
        except Exception as e:
            print(f"  [ERROR] {e}")
            errors.append((filename, str(e)))
            
            # Mencatat info gagal ke dalam manifest
            manifest_data["generated_patterns"].append({
                "pattern_name": dir_name,
                "source_kg": filename,
                "status": "Failed",
                "error_message": str(e)
            })

    # ── MENULIS MANIFEST FILE (Tugas Utama Issue #06) ──
    manifest_path = os.path.join(output_base, "manifest.json")
    try:
        with open(manifest_path, "w", encoding="utf-8") as json_file:
            json.dump(manifest_data, json_file, indent=4)
        print(f"\n📝 [MANIFEST] Successfully generated manifest file at: {manifest_path}")
    except Exception as e:
        print(f"\n❌ [MANIFEST ERROR] Failed to create manifest file: {e}")

    # Summary
    print("\n" + "=" * 65)
    print(f"  Done. {success}/{len(ttl_files)} projects generated successfully.")
    if errors:
        print(f"  Errors ({len(errors)}):")
        for fname, err in errors:
            print(f"    - {fname}: {err}")
    print("=" * 65)


if __name__ == "__main__":
    main()