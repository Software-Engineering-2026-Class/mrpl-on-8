import os
import ast
import rdflib
from pathlib import Path

class MRPLAnalytics:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        # Menargetkan folder spesifik berdasarkan arsitektur proyek
        self.output_dir = self.root_dir / "output_files"
        self.kg_dir = self.root_dir / "generated_kg"

    def verify_syntax(self):
        print(f"--- Verifikasi Sintaks Python ---")
        if not self.output_dir.exists():
            print(f"[!] Direktori {self.output_dir} tidak ditemukan.")
            return

        total_files = 0
        passed = 0
        failed = []

        # Mencari seluruh file .py di dalam folder output_files dan sub-foldernya
        for py_file in self.output_dir.rglob("*.py"):
            total_files += 1
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    source = f.read()
                
                # ast.parse melakukan pengecekan sintaks statis (tanpa eksekusi)
                ast.parse(source, filename=str(py_file))
                passed += 1
                print(f" [OK] {py_file.name} - Sintaks Valid")
            except SyntaxError as e:
                failed.append((py_file.name, str(e)))
                print(f" [X]  {py_file.name} - SINTAKS ERROR")
            except Exception as e:
                failed.append((py_file.name, f"Error membaca file: {e}"))

        print(f"\n[Ringkasan Verifikasi Sintaks]")
        print(f"Total File Python Dievaluasi : {total_files}")
        print(f"Lolos Verifikasi (Valid)     : {passed}")
        print(f"Gagal Verifikasi (Invalid)   : {len(failed)}")

        if failed:
            print("\nDetail Kegagalan Sintaks:")
            for file_name, error in failed:
                print(f" -> {file_name}: {error}")
        print("\n")

    def count_triples(self):
        print(f"--- Ekstraksi & Penghitungan Triples KG ---")
        if not self.kg_dir.exists():
            print(f"[!] Direktori {self.kg_dir} tidak ditemukan.")
            return

        total_triples = 0
        
        # Mencari seluruh file .
import glob
import re
from rdflib import Graph

def count_kg_patterns_glob(kg_folder):
    """Menghitung total pola/triple dari semua file .ttl di folder generated_kg."""
    total_triples = 0
    ttl_files = glob.glob(os.path.join(kg_folder, "**", "*.ttl"), recursive=True)
    
    if not ttl_files:
        # Fallback jika file ttl ada di root proyek
        if os.path.exists("agentO.ttl"):
            ttl_files = ["agentO.ttl"]

    for filepath in ttl_files:
        try:
            g = Graph()
            g.parse(filepath, format="turtle")
            total_triples += len(g)
        except Exception:
            continue
    return total_triples

def analyze_nested_generated_code(output_dir):
    """Menganalisis komponen kode di semua sub-folder secara rekursif."""
    stats = {}
    
    # Mencari semua file .py di dalam folder output_files beserta sub-foldernya
    py_files = glob.glob(os.path.join(output_dir, "**", "*.py"), recursive=True)
    
    if not py_files:
        return stats

    for filepath in py_files:
        # Kita skip file virtual environment jika terbawa
        if "venv" in filepath or "__pycache__" in filepath:
            continue
            
        # Ambil nama folder project + nama filenya sebagai identifier (misal: instagram_post/crew.py)
        parts = filepath.split(os.sep)
        if len(parts) >= 3:
            identifier = f"{parts[-2]}/{parts[-1]}"
        else:
            filename = os.path.basename(filepath)

        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        loc = len(lines)
        code_content = "".join(lines)
        
        # Regex pencarian komponen (Agent, Task, Tool) pada skrip Python CrewAI kelompokmu
        agents = len(re.findall(r'(@agent|Agent\()', code_content, re.IGNORECASE))
        tasks = len(re.findall(r'(@task|Task\()', code_content, re.IGNORECASE))
        tools = len(re.findall(r'(@tool|tool\b)', code_content, re.IGNORECASE))
        
        # Correctness Metrics: Validasi Sintaksis
        try:
            compile(code_content, filepath, 'exec')
            syntax_valid = True
        except SyntaxError:
            syntax_valid = False
            
        stats[identifier] = {
            "loc": loc,
            "agents": agents,
            "tasks": tasks,
            "tools": tools,
            "syntax_valid": syntax_valid,
            "status": "Success" if (syntax_valid and loc > 0) else "Failed"
        }
        
    return stats

def print_report(kg_folder, output_folder):
    print("\n==================================================")
    print("         FRAMEWORK GENERATION SUMMARY REPORT      ")
    print("==================================================")
    
    # 1. Number of KG Patterns Processed
    kg_patterns = count_kg_patterns_glob(kg_folder)
    print(f"🔹 Total KG Patterns Processed : {kg_patterns} triples")
    
    # Analisis seluruh kode di dalam sub-folder
    code_stats = analyze_nested_generated_code(output_folder)
    
    if not code_stats:
        print("\nTidak ada data kode Python tergenerasi yang ditemukan di sub-folder.")
        return

    print("--------------------------------------------------")
    print("🔹 Sample Components Generated Per File (Top 10):")
    
    total_files = len(code_stats)
    success_files = 0
    total_loc = 0
    
    # Cetak maksimal 10 file saja agar terminal tidak kepenuhan log panjang
    for i, (framework, data) in enumerate(code_stats.items()):
        if i < 10:
            print(f"     [{framework}]")
            print(f"      - Status       : {data['status']}")
            print(f"      - Extracted    : {data['agents']} agents, {data['tasks']} tasks, {data['tools']} tools")
            print(f"      - Lines of Code: {data['loc']} lines")
            print(f"      - Syntax Valid : {'YES' if data['syntax_valid'] else 'NO'}")
        
        total_loc += data["loc"]
        if data["status"] == "Success":
            success_files += 1
            
    if total_files > 10:
        print(f"   ... and {total_files - 10} more generated files.")
            
    # 2. Success / Failure Rate
    success_rate = (success_files / total_files) * 100
    failure_rate = 100 - success_rate
    
    print("--------------------------------------------------")
    print("🔹 Global Generation Metrics:")
    print(f"   - Total Python Files Generated: {total_files}")
    print(f"   - Code Syntax Success Rate    : {success_rate:.2f}%")
    print(f"   - Code Syntax Failure Rate    : {failure_rate:.2f}%")
    print(f"   - Total Lines of Code (LOC)   : {total_loc:,} lines")
    print("==================================================\n")

if __name__ == "__main__":
    # Menyesuaikan dengan path log generator kamu tadi
    print_report("generated_kg", "output_files")
