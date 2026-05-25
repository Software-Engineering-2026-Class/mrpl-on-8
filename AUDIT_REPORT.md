# LAPORAN AUDIT SISTEM KODE PROGRAM

**Pipeline Generasi Repositori CrewAI Berbasis Knowledge Graph**

**Identitas Cabang Kode:** `Branch-Rayyan`  
**Sistem Operasi Evaluasi:** Windows OS (PowerShell Environment)  
**Lingkungan Eksekusi:** Lingkungan Virtual Terisolasi (Python 3.12, venv)  
**Status Audit:** **LOLOS DENGAN CATATAN (PASS WITH CONDITIONS)**

---

## 1. PENDAHULUAN DAN ARSITEKTUR PIPELINE

Laporan audit ini disusun untuk mengevaluasi fungsionalitas, struktur antarmuka, serta keandalan sistem otomatisasi multi-agen `mrpl-on-8` pada cabang `Branch-Rayyan`. Proyek ini mengimplementasikan pendekatan _metaprogramming_ tingkat lanjut, di mana kode aplikasi diekstrak dan dibangun secara otomatis oleh mesin generator berdasarkan pemodelan data semantik yang deklaratif.

Proses konversi data pada sistem ini berjalan melalui **Strategi Konversi 3-Layer**:

1. **Layer 1 (Blueprint Semantik):** Mengurai dokumen triplestore Semantik Web lokal (`.ttl`) menggunakan pustaka `rdflib` dan kueri deklaratif SPARQL.
2. **Layer 2 (Inspeksi & Validasi):** Memvalidasi skema, tipe data, dan kelengkapan atribut wajib objek agen menggunakan Pydantic Models (`models.py`).
3. **Layer 3 (Pabrikasi Kode):** Mengawinkan objek data yang telah tervalidasi ke dalam mesin templat Jinja2 (`generator.py` & `templates/`) untuk merender struktur repositori aplikasi CrewAI yang fungsional.

### Hasil Verifikasi Eksekusi Otomatisasi (Generasi Awal)

Eksekusi terhadap skrip utama penyerapan data semantik berhasil berjalan tanpa adanya hambatan interupsi sistem:

- **Perintah:** `python src/crewai/run.py`
- **Metrik Keberhasilan:** **16/16 berkas Knowledge Graph** berhasil diurai secara penuh dari direktori sumber `.\generated_kg\CrewAI\` dan berhasil merender seluruh sub-proyek kustom ke dalam direktori luaran `.\output_files\output_crewai\`.
- **Kebutuhan Kredensial:** Layer pabrikasi ini berjalan 100% secara lokal pada mesin Windows tanpa memerlukan kunci API eksternal (_LLM API Keys_).

---

## 2. DOKUMENTASI POLA KNOWLEDGE GRAPH (KG) YANG DIDUKUNG

Berdasarkan hasil analisis struktur ekstraktor pada file `extractor.py` serta skema data di `models.py`, mesin generasi ini dikonfigurasi untuk mengenali dan mengekstrak pola graf spesifik yang memiliki hubungan semantik searah dengan arsitektur multi-agen:

### A. Pola Pemetaan Kelas Ontologis (_Ontological Class Mapping_)

Mesin ekstraksi memetakan relasi subjek-predikat-objek graf triplestore Semantik Web secara langsung menjadi entitas objek pemrograman CrewAI:

- **`Crew` Individual:** Mengidentifikasi instansiasi graf terpadu untuk dikonversi menjadi nama kelas pengendali utama proyek (contoh: `game-builder-crew_instances.ttl` diubah menjadi kelas `GameBuilderCrew`).
- **`Agent` Components:** Node graf yang memiliki deklarasi properti kemampuan kustom dikonversi menjadi parameter agen, termasuk penguraian string panjang untuk pengisian atribut `role`, `backstory`, and `goal`.
- **`Task` Components:** Node relasional yang mendeklarasikan tataan fungsi instruksional dipetakan secara terpisah untuk kemudian disematkan pada konfigurasi tugas agen yang bersangkutan.

### B. Pola Alur Kerja Sekuensial Berorientasi Dependensi (_Directed Workflow Sequencing_)

Sistem ini mendukung pengenalan pola graf berarah (_Directed Graph_) yang merepresentasikan urutan eksekusi tugas. Ekstraktor SPARQL melacak properti relasional antar-tugas (misalnya tugas A mendahului atau menjadi prasyarat tugas B) untuk dikonversikan menjadi **Langkah Alur Kerja** (_Workflow Steps_). Berdasarkan log eksekusi, sistem berhasil mengekstrak variasi jumlah langkah kerja secara dinamis, contohnya:

- `CopyCrew`: 5 Agen, 6 Tugas, **6 Workflow Steps**.
- `GameBuilderCrew`: 3 Agen, 3 Tugas, **3 Workflow Steps**.

### C. Pola Atribut Pengikatan Properti Data (_Data Property Binding_)

Sistem mendukung penuh penguraian data literal (string, integer, boolean) dari graf pengetahuan untuk menentukan penataan fungsi runtime agen, seperti status pelacakan detail instruksi (`verbose=True`), hingga penugasan perkakas (_tool configuration_) yang diurai langsung dari graf node.

---

## 3. SPESIFIKASI ANTARMUKA INPUT DAN OUTPUT (DATA BOUNDARIES)

Sistem ini memiliki dua batasan wilayah data (_data boundaries_) yang beroperasi pada fasa yang berbeda:

### A. Spesifikasi Antarmuka pada Lapisan Generasi (Generation Phase)

- **Batas Input (Data Ingestion):**
  - **Format Berkas:** Teks terstruktur _Terse RDF Triple Language_ dengan ekstensi **`.ttl`**.
  - **Lokasi Target:** `.\generated_kg\CrewAI\`
- **Batas Output (Code Generation):**
  - **Format Berkas:** Multi-file terstruktur yang membangun struktur cetak biru (_Scaffold Fingerprint_) aplikasi siap rilis di dalam direktori `.\output_files\output_crewai\<nama-proyek-graf>\`.

### B. Spesifikasi Antarmuka pada Lapisan Eksekusi (Runtime Phase)

- **Batas Input (Variables Ingestion):**
  - **Format:** Pasangan kunci-nilai (_key-value pairs_) bertipe _Dictionary_ yang disuplai melalui berkas `inputs.yaml` atau diinterpolasikan ke metode `kickoff(inputs=inputs)`.
  - **Contoh Muatan Input:** `{"topic": "Developing a 2D Platformer Game"}`.
- **Batas Output (Execution Artifact):**
  - **Format:** Log konsol interaktif (_Markdown Trace String_) yang menampilkan proses pemikiran berantai (_Chain of Thought_) dari para agen serta hasil akhir berupa berkas kode program fungsional hasil produksi kolaborasi agen (contoh: Game buatan agen tersimpan di direktori kerja lokal).

---

## 4. TEMUAN KEKURANGAN KRITIS DAN CACAT ARSITEKTUR

Selama pengujian runtime end-to-end pada modul proyek hasil generasi (`game-builder-crew`), sistem mengalami kendala operasional serius yang mengungkap celah defisit arsitektur pada lapisan dasar generator.

### ⚠️ TEMUAN SEVERITAS TINGGI: Kerentanan Terhadap Overload Hulu & Ketiadaan Toleransi Kesalahan API Terhadap Lonjakan Permintaan Eksternal (HTTP 503 / 429 Vulnerability)

#### Kronologi Kegagalan Eksekusi:

Pada saat pengujian fungsionalitas runtime menggunakan skrip entry-point (`python main.py`), proyek yang dihasilkan mencoba mengeksekusi rantai agen secara berurutan. Agen pertama berhasil melakukan pemanggilan hulu untuk menghasilkan draf awal program. Namun, ketika proses berlanjut ke agen berikutnya dalam sistem sekuensial, eksekusi terhenti secara paksa akibat penolakan dari server pusat penyedia model LLM dengan pesan kesalahan teknis:
`ServerError: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}`

#### Analisis Akar Masalah Teknis (_Root Cause Analysis_):

1. **Ketiadaan Logika Pengulangan Otomatis (_No Retry/Backoff Mechanism_):** Kode program Python yang diproduksi secara otomatis oleh mesin generator (`crew.py` hasil render templat Jinja2) tidak dilengkapi dengan blok penanganan eksepsi (_exception handling_) jaringan. Proyek hasil generasi berasumsi bahwa setiap infrastruktur hulu API akan selalu merespons secara instan. Ketika server LLM mengalami lonjakan beban (_traffic spike_) atau pembatasan laju (_rate limiting_), kesalahan HTTP 503 atau 429 langsung merembet ke lapisan atas dan mematikan paksa seluruh proses instansiasi _thread_ asyncio.
2. **Defisit Penanganan Keadaan Agen (_Lack of State Persistence_):** Rangkaian tugas pada proyek hasil perancah ini berjalan secara sekuensial linier tanpa adanya penyimpanan keadaan berkala (_checkpointing_). Konsekuensinya, hasil kerja bernilai tinggi dari agen pertama langsung hilang dari memori runtime akibat sistem mengalami _crash_ pada tugas kedua. Sistem terpaksa harus mengulang seluruh proses alur kerja agen dari fasa awal, yang memicu kerentanan redundansi pemanggilan data eksternal.

---

## 5. RENCANA AKSI DAN REKOMENDASI MITIGASI

Untuk memperbaiki kelemahan di atas dan memastikan proyek hasil generasi memiliki kualitas standar produksi (_production-grade resilience_), langkah perbaikan struktural berikut harus segera diimplementasikan pada repositori utama:

### A. Mitigasi Runtime Segera (Workaround Eksekusi)

Selama pengujian darurat untuk membuktikan keandalan sistem multi-agen, pengalihan beban kerja sementara ke infrastruktur model _lightweight_ terbukti sukses melompati dinding antrean beban hulu.

- **Tindakan Pemulihan:** Mengubah tataan spesifikasi model tujuan ke versi yang memiliki batas limitasi kuota lebih longgar dan efisien (contoh: bermigrasi dari model tingkat lanjutan utama ke varian model _Flash-Lite_). Langkah ini terbukti sukses mengeksekusi pipeline hingga tuntas (_Task Completed_) dengan hasil akhir berupa kode program game Snake yang valid menggunakan pustaka `pygame`.

### B. Perbaikan Struktural: Modifikasi Berkas Cetak Biru Generator

Akar masalah harus diperbaiki langsung pada sumbernya, yaitu memodifikasi file template Jinja2 (`src/crewai/templates/crew.py.j2`) agar setiap aplikasi multi-agen yang dilahirkan secara otomatis memiliki sistem kekebalan terhadap gangguan jaringan eksternal.

1. **Injeksi Parameter Toleransi Kesalahan pada LLM Inisialisator:**
   Ubah logika dasar generator pada templat agar selalu menyuntikkan parameter batas toleransi kegagalan (`max_retries`) dan penyesuaian tenggat waktu tunggu (_timeout limits_) saat menginisialisasi modul LLM bawaan:
   ```python
   # Rekomendasi perubahan pada templat crew.py.j2 hasil modifikasi
   # Memaksa objek LLM CrewAI untuk mengaktifkan ketahanan bawaan
   self.llm = LLM(
       model=self.model_name,
       max_retries=5,             # Otomatis melakukan percobaan ulang hingga 5 kali jika server hulu sibuk (HTTP 503/429)
       request_timeout=60          # Batas toleransi waktu tunggu respons jaringan eksternal (detik)
   )
   ```
2. **Penerapan Pola Desain Backoff Jeda Eksponensial (_Exponential Backoff Policy_):**
   Memastikan generator menyuntikkan fungsi penundaan waktu yang meningkat secara eksponensial di antara percobaan ulang (_retries_). Langkah ini krusial untuk mencegah sistem melakukan penyerangan _request_ secara bertubi-tubi (_spamming_) ke server hulu saat status jaringan sedang memulihkan diri dari _overload_.

3. **Implementasi Pembuatan _Checkpoint_ Penyimpanan Statis Proyek:**
   Mengubah skema definisi penataan fungsi `@crew` pada templat agar secara berkala mengekspor luaran teks sementara dari setiap tugas (_Task Output_) ke dalam folder berkas log lokal. Dengan demikian, jika sistem mati di tengah proses pengerjaan tugas kompleks, orkestrator dapat melanjutkan pengerjaan dari titik kegagalan terakhir (_recovery point_) tanpa harus mengulang proses penalaran agen dari fasa awal.
