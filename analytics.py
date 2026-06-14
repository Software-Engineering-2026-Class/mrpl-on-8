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