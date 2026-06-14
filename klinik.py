from collections import deque

# DAFTAR GEJALA ATAU KELUHAN YANG DIKATEGORIKAN KRITIS/GAWAT DARURAT
KELUHAN_KRITIS = [
    "patah tulang", "sesak nafas", "sesak napas", "tidak sadar",
    "pingsan", "serangan jantung", "stroke", "pendarahan",
    "kecelakaan", "luka berat", "kejang"
]

BATAS_USIA_LANSIA = 60
SENTINEL_BATAL = ""


def input_batal(prompt, tipe=str):
    """
    Input dengan opsi batal. Kembalikan (nilai, True) jika valid,
    atau (None, False) jika user membatalkan (input kosong / ketik 'batal').
    """
    while True:
        raw = input(prompt).strip()
        if raw.lower() in ("", "batal"):
            print("↩️  Operasi dibatalkan, kembali ke menu utama.")
            return None, False
        if tipe == int:
            try:
                return int(raw), True
            except ValueError:
                print("❌ Harus berupa angka bulat. Coba lagi atau tekan Enter untuk batal.")
        else:
            return raw, True


def hitung_kode_prioritas(usia, keluhan, is_darurat):
    """
    Menentukan kategori antrean dasar:
      - P (PRIORITAS) : Semua Lansia (>60 thn) ATAU semua orang yang darurat/kritis.
      - R (REGULER)   : Orang di bawah 60 tahun yang sakit biasa.
    """
    keluhan_lower = keluhan.lower()
    faktor_kritis = any(k in keluhan_lower for k in KELUHAN_KRITIS)
    is_lansia = usia > BATAS_USIA_LANSIA

    if is_lansia or is_darurat or faktor_kritis:
        return "P"
    else:
        return "R"


def label_kode(kode):
    """Menggunakan label deskriptif untuk kode prioritas agar mudah dibaca di terminal."""
    return {
        "P": "🟡 PRIORITAS",
        "R": "🔵 REGULER (SABAR/ANTRE)",
    }.get(kode, "TIDAK DIKETAHUI")


class SistemManajemenKlinik:
    def __init__(self):
        self.pasien_db = {}
        self.counter_id_pasien = 1

        self.antrian_p = deque()
        self.antrian_r = deque()
        
        self.counter_p = 1
        self.counter_r = 1

        self.riwayat_tindakan = {}
        self.total_pasien_dilayani = 0
        self.log_transaksi = []

    def daftarkan_pasien_baru(self, nama, usia, keluhan, is_darurat=False):
        """Mendaftarkan pasien baru dan otomatis menyusun urutan prioritas medis yang sangat presisi."""
        id_pasien = f"ID-{self.counter_id_pasien:03d}"
        self.counter_id_pasien += 1

        kode = hitung_kode_prioritas(usia, keluhan, is_darurat)
        
        keluhan_lower = keluhan.lower()
        faktor_kritis = any(k in keluhan_lower for k in KELUHAN_KRITIS)
        is_gawat = is_darurat or faktor_kritis
        is_lansia = usia > BATAS_USIA_LANSIA

        self.pasien_db[id_pasien] = {
            "nama"      : nama,
            "usia"      : usia,
            "keluhan"   : keluhan,
            "is_darurat": is_darurat,
            "kode"      : kode,
        }
        print(f"\n✅ Pasien terdaftar → ID: {id_pasien} | Status: {label_kode(kode)}")

        pasien_antrian = {"id_pasien": id_pasien, "nama": nama, "usia": usia}

        # ========================================================
        # LOGIKA PERURUTAN PRESISI DI ANTREAN PRIORITAS (P)
        # ========================================================
        if kode == "P":
            pasien_antrian["nomor_antrian"] = f"P-{self.counter_p:03d}"
            self.counter_p += 1
            
            # KONDISI 1: Lansia + Gawat Darurat -> Wajib menempati urutan paling depan
            if is_lansia and is_gawat:
                idx_sisip = 0
                for p in self.antrian_p:
                    p_db = self.pasien_db[p["id_pasien"]]
                    p_kritis = any(k in p_db["keluhan"].lower() for k in KELUHAN_KRITIS)
                    p_gawat = p_db["is_darurat"] or p_kritis
                    p_lansia = p_db["usia"] > BATAS_USIA_LANSIA
                    if p_lansia and p_gawat:
                        idx_sisip += 1
                    else:
                        break
                self.antrian_p.insert(idx_sisip, pasien_antrian)
                print(f"   → 🔥 LANSIA KRITIS! Antrian {pasien_antrian['nomor_antrian']} langsung diposisikan di kelompok terdepan.")
            
            # KONDISI 2: Muda + Gawat Darurat -> Harus berada di bawah Lansia Gawat, tapi di atas Lansia Biasa
            elif (not is_lansia) and is_gawat:
                idx_sisip = 0
                for p in self.antrian_p:
                    p_db = self.pasien_db[p["id_pasien"]]
                    p_kritis = any(k in p_db["keluhan"].lower() for k in KELUHAN_KRITIS)
                    p_gawat = p_db["is_darurat"] or p_kritis
                    p_lansia = p_db["usia"] > BATAS_USIA_LANSIA
                    
                    if (p_lansia and p_gawat) or ((not p_lansia) and p_gawat):
                        idx_sisip += 1
                    else:
                        break
                self.antrian_p.insert(idx_sisip, pasien_antrian)
                print(f"   → 🚑 MUDA KRITIS! Antrian {pasien_antrian['nomor_antrian']} disisipkan setelah kelompok Lansia Kritis.")
            
            # KONDISI 3: Lansia + Sakit Biasa -> Berada di paling belakang antrean Prioritas
            else:
                self.antrian_p.append(pasien_antrian)
                print(f"   → 👵 LANSIA SAKIT BIASA! Antrian {pasien_antrian['nomor_antrian']} masuk antrean Prioritas posisi belakang.")
                
        # ========================================================
        # KONDISI 4: Muda + Sakit Biasa -> Antre Normal Paling Belakang di Reguler (R)
        # ========================================================
        else: 
            pasien_antrian["nomor_antrian"] = f"R-{self.counter_r:03d}"
            self.counter_r += 1
            self.antrian_r.append(pasien_antrian)
            print(f"   → Antrian {pasien_antrian['nomor_antrian']} (Mengantre normal di reguler)")

    def _alasan_prioritas(self, usia, keluhan, is_darurat):
        """Membuat string alasan mengapa pasien mendapat prioritas tertentu."""
        alasan = []
        if is_darurat:
            alasan.append("kondisi darurat")
        if usia > BATAS_USIA_LANSIA:
            alasan.append(f"lansia ({usia} thn)")
        keluhan_lower = keluhan.lower()
        for k in KELUHAN_KRITIS:
            if k in keluhan_lower:
                alasan.append(f"keluhan kritis ({k})")
                break
        return ", ".join(alasan) if alasan else "-"

    def cari_data_pasien(self, id_pasien):
        """Mencari data pasien berdasarkan ID, O(1)."""
        if id_pasien not in self.pasien_db:
            print("❌ ID pasien tidak ditemukan.")
            return None
        p = self.pasien_db[id_pasien]
        print(f"\n📄 DATA PASIEN ({id_pasien})")
        print(f"   Nama    : {p['nama']}")
        print(f"   Usia    : {p['usia']} tahun")
        print(f"   Keluhan : {p['keluhan']}")
        print(f"   Status  : {label_kode(p['kode'])}")
        return p

    def tampilkan_seluruh_pasien(self):
        """Menampilkan semua pasien yang terdaftar."""
        print("\n📋 DAFTAR SELURUH PASIEN TERDAFTAR")
        if not self.pasien_db:
            print("   (Belum ada pasien terdaftar)")
            return
        for id_p, d in self.pasien_db.items():
            print(f"   {id_p} | {d['nama']:<20} | {d['usia']:>3} thn | {label_kode(d['kode'])}")

    def perbarui_data_pasien(self, id_pasien, nama_baru, usia_baru, keluhan_baru):
        """Memperbarui data pasien dan kalkulasi ulang kode prioritas."""
        if id_pasien not in self.pasien_db:
            print("❌ ID pasien tidak ditemukan.")
            return
        p = self.pasien_db[id_pasien]
        p["nama"]    = nama_baru
        p["usia"]    = usia_baru
        p["keluhan"] = keluhan_baru
        p["kode"]    = hitung_kode_prioritas(usia_baru, keluhan_baru, p["is_darurat"])
        print(f"Base data {id_pasien} diperbarui. Status baru: {label_kode(p['kode'])}")

    def panggil_pasien_berikutnya(self):
        """Memanggil pasien berikutnya dengan sistem berjenjang: Prioritas (P) → Reguler (R)."""
        print("\n📢 PANGGILAN ANTRIAN")
        for antrian, kode in [(self.antrian_p, "P"), (self.antrian_r, "R")]:
            if antrian:
                pasien = antrian.popleft()
                p_data = self.pasien_db[pasien["id_pasien"]]
                print(f"🔊 {pasien['nomor_antrian']} → {pasien['nama']} ({pasien['id_pasien']})")
                print(f"   Status  : {label_kode(kode)}")
                print(f"   Keluhan : {p_data['keluhan']}")
                alasan = self._alasan_prioritas(p_data["usia"], p_data["keluhan"], p_data["is_darurat"])
                if alasan != "-":
                    print(f"   Alasan  : {alasan}")
                print("   → Silakan menuju Ruang Pemeriksaan.")
                return pasien["id_pasien"]

        print("📭 Semua antrian kosong.")
        return None

    def tampilkan_kondisi_antrian(self):
        """Menampilkan kondisi antrean Prioritas dan Reguler secara rinci."""
        print("\n" + "="*60)
        print(" STATUS ANTRIAN SAAT INI")
        print("="*60)

        grupan = [
            ("🟡 P — PRIORITAS (LANSIA / GAWAT)", self.antrian_p),
            ("🔵 R — REGULER (MUDA SAKIT BIASA)", self.antrian_r),
        ]
        for judul, antrian in grupan:
            print(f"\n{judul} (Total: {len(antrian)} pasien)")
            if not antrian:
                print("   (Kosong)")
            else:
                for i, pasien in enumerate(antrian, 1):
                    p = self.pasien_db[pasien["id_pasien"]]
                    alasan = self._alasan_prioritas(p["usia"], p["keluhan"], p["is_darurat"])
                    print(f"   {i}. [{pasien['nomor_antrian']}] {pasien['nama']} (Usia: {p['usia']} thn) | Detail: {alasan}")
        print("="*60)

    def catat_tindakan_medis(self, id_pasien, diagnosa, resep, tindakan, biaya):
        """Memasukkan rekam medis baru ke tumpukan (Stack) riwayat tindakan pasien."""
        if id_pasien not in self.pasien_db:
            print("❌ Pasien tidak ditemukan, tindakan dibatalkan.")
            return
        self.riwayat_tindakan.setdefault(id_pasien, [])
        catatan = {"diagnosa": diagnosa, "resep": resep, "tindakan": tindakan, "biaya": biaya}
        self.riwayat_tindakan[id_pasien].append(catatan)
        self.log_transaksi.append({"id_pasien": id_pasien, "nominal": biaya})
        self.total_pasien_dilayani += 1
        print(f"✅ Tindakan medis untuk {self.pasien_db[id_pasien]['nama']} berhasil disimpan.")

    def tampilkan_riwayat_terakhir(self, id_pasien):
        """Melihat rekam medis terakhir tanpa menghapusnya (Konsep Peek pada Stack)."""
        if id_pasien not in self.riwayat_tindakan or not self.riwayat_tindakan[id_pasien]:
            print("⚠️  Belum ada riwayat tindakan untuk pasien ini.")
            return
        terakhir = self.riwayat_tindakan[id_pasien][-1]
        print(f"\n⚕️  RIWAYAT MEDIS TERAKHIR ({id_pasien})")
        print(f"   Diagnosa : {terakhir['diagnosa']}")
        print(f"   Resep    : {terakhir['resep']}")
        print(f"   Tindakan : {terakhir['tindakan']}")
        print(f"   Biaya    : Rp{terakhir['biaya']:,}")

    def cetak_struk_pembayaran(self, id_pasien):
        """Menampilkan struk pembayaran formal berdasarkan transaksi terakhir pasien (Peek Stack)."""
        if id_pasien not in self.pasien_db:
            print("❌ ID pasien tidak ditemukan.")
            return
        if id_pasien not in self.riwayat_tindakan or not self.riwayat_tindakan[id_pasien]:
            print("⚠️  Pasien ini belum memiliki catatan tindakan medis / biaya.")
            return
        
        pasien = self.pasien_db[id_pasien]
        terakhir = self.riwayat_tindakan[id_pasien][-1] # Peek data teratas stack
        
        print("\n" + "==========================================")
        print("          KLINIK SEHAT BERSAMA            ")
        print("       Jl. Raya Jambi No. 12, Kota Jambi  ")
        print("==========================================")
        print(f" ID Pasien   : {id_pasien}")
        print(f" Nama Pasien : {pasien['nama']}")
        print(f" Usia        : {pasien['usia']} tahun")
        print("------------------------------------------")
        print(f" Diagnosa    : {terakhir['diagnosa']}")
        print(f" Tindakan    : {terakhir['tindakan']}")
        print(f" Obat/Resep  : {terakhir['resep']}")
        print("------------------------------------------")
        print(f" TOTAL BIAYA             : Rp{terakhir['biaya']:,}")
        print("==========================================")
        print("     Terima Kasih Atas Kunjungan Anda     ")
        print("       Semoga Lekas Sembuh & Sehat        ")
        print("==========================================")

    def batalkan_tindakan_terakhir(self, id_pasien):
        """Membatalkan rekam medis paling atas dari Stack (Konsep Undo LIFO)."""
        if id_pasien not in self.riwayat_tindakan or not self.riwayat_tindakan[id_pasien]:
            print("❌ Tidak ada tindakan yang bisa dibatalkan untuk pasien ini.")
            return
        dibatalkan = self.riwayat_tindakan[id_pasien].pop()
        for i in reversed(range(len(self.log_transaksi))):
            if self.log_transaksi[i]["id_pasien"] == id_pasien:
                self.log_transaksi.pop(i)
                self.total_pasien_dilayani -= 1
                break
        print(f"✅ [UNDO] Tindakan '{dibatalkan['diagnosa']}' untuk {id_pasien} berhasil dihapus.")

    def tampilkan_laporan_harian(self, kriteria_sort):
        """Menghasilkan data statistik keuangan harian dan pengurutan daftar pasien."""
        print("\n" + "="*50)
        print("  📊 LAPORAN & STATISTIK HARIAN KLINIK")
        print("="*50)
        print(f"Total Pasien Dilayani : {self.total_pasien_dilayani} pasien")

        print(f"\n--- Daftar Pasien (Urut: {kriteria_sort}) ---")
        if not self.pasien_db:
            print("Belum ada pasien terdaftar.")
        else:
            if kriteria_sort == "Nama":
                pasien_terurut = sorted(self.pasien_db.items(), key=lambda x: x[1]["nama"].lower())
            else:
                pasien_terurut = sorted(self.pasien_db.items(), key=lambda x: x[0])
            for id_p, d in pasien_terurut:
                print(f"   {id_p} | {d['nama']:<20} | {d['usia']:>3} thn | {label_kode(d['kode'])}")

        print("\n--- Log Transaksi Keuangan ---")
        if not self.log_transaksi:
            print("Belum ada transaksi.")
        else:
            total = 0
            for t in self.log_transaksi:
                print(f"   {t['id_pasien']} → Rp{t['nominal']:,}")
                total += t["nominal"]
            print(f"💰 Total Pemasukan Hari Ini: Rp{total:,}")


if __name__ == "__main__":
    klinik = SistemManajemenKlinik()

    while True:
        print("\n" + "="*50)
        print("   SISTEM INTEGRASI KLINIK SEHAT BERSAMA   ")
        print("="*50)
        print(" [1]  Daftarkan Pasien Baru")
        print(" [2]  Panggil Pasien Berikutnya")
        print(" [3]  Cari Data Pasien by ID")
        print(" [4]  Perbarui Data Pasien")
        print(" [5]  Tampilkan Seluruh Pasien")
        print(" [6]  Catat Tindakan Medis & Biaya")
        print(" [7]  Lihat Riwayat Medis Terakhir")
        print(" [8]  Batalkan Tindakan Terakhir (Undo)")
        print(" [9]  Tampilkan Status Antrian")
        print(" [10] Laporan & Statistik Harian")
        print(" [11] Cetak Struk Pembayaran Pasien")
        print(" [0]  Keluar Aplikasi")
        print("==================================================")
        print("  ℹ️  Pada setiap input, tekan Enter kosong / ketik 'batal' untuk membatalkan.")
        print("-"*50)

        pilihan = input("Pilih menu (0-11): ").strip()

        if pilihan == "1":
            print("\n─── DAFTARKAN PASIEN BARU ───")

            nama, ok = input_batal("Nama Pasien         : ")
            if not ok: continue

            usia, ok = input_batal("Usia Pasien (tahun) : ", tipe=int)
            if not ok: continue

            keluhan, ok = input_batal("Keluhan Medis       : ")
            if not ok: continue

            print("Kondisi darurat? Contoh keluhan darurat:", ", ".join(KELUHAN_KRITIS[:5]), "...")
            darurat_raw, ok = input_batal("Darurat? (y/n)      : ")
            if not ok: continue
            is_darurat = darurat_raw.lower() == "y"

            klinik.daftarkan_pasien_baru(nama, usia, keluhan, is_darurat)

        elif pilihan == "2":
            klinik.panggil_pasien_berikutnya()

        elif pilihan == "3":
            print("\n─── CARI DATA PASIEN ───")
            id_cari, ok = input_batal("ID Pasien (cth: ID-001) : ")
            if not ok: continue
            klinik.cari_data_pasien(id_cari.upper())

        elif pilihan == "4":
            print("\n─── PERBARUI DATA PASIEN ───")
            id_up, ok = input_batal("ID Pasien yang diperbarui : ")
            if not ok: continue
            id_up = id_up.upper()
            if id_up not in klinik.pasien_db:
                print("❌ ID tidak ditemukan.")
                continue

            nama_n, ok = input_batal("Nama Baru     : ")
            if not ok: continue

            usia_n, ok = input_batal("Usia Baru     : ", tipe=int)
            if not ok: continue

            keluhan_n, ok = input_batal("Keluhan Baru  : ")
            if not ok: continue

            klinik.perbarui_data_pasien(id_up, nama_n, usia_n, keluhan_n)

        elif pilihan == "5":
            klinik.tampilkan_seluruh_pasien()

        elif pilihan == "6":
            print("\n─── CATAT TINDAKAN MEDIS ───")
            id_medis, ok = input_batal("ID Pasien yang diperiksa : ")
            if not ok: continue
            id_medis = id_medis.upper()
            if id_medis not in klinik.pasien_db:
                print("❌ ID tidak ditemukan.")
                continue

            diagnosa, ok = input_batal("Diagnosa Medis  : ")
            if not ok: continue

            resep, ok = input_batal("Resep Obat      : ")
            if not ok: continue

            tindakan, ok = input_batal("Tindakan        : ")
            if not ok: continue

            biaya, ok = input_batal("Biaya (Rp)      : ", tipe=int)
            if not ok: continue

            klinik.catat_tindakan_medis(id_medis, diagnosa, resep, tindakan, biaya)

        elif pilihan == "7":
            print("\n─── RIWAYAT MEDIS TERAKHIR ───")
            id_view, ok = input_batal("ID Pasien : ")
            if not ok: continue
            klin微k.tampilkan_riwayat_terakhir(id_view.upper())

        elif pilihan == "8":
            print("\n─── BATALKAN TINDAKAN TERAKHIR (UNDO) ───")
            id_undo, ok = input_batal("ID Pasien : ")
            if not ok: continue
            klinik.batalkan_tindakan_terakhir(id_undo.upper())

        elif pilihan == "9":
            klinik.tampilkan_kondisi_antrian()

        elif pilihan == "10":
            print("\n─── LAPORAN HARIAN ───")
            print("[A] Urutkan Alfabetis Nama")
            print("[B] Urutkan Berdasarkan ID Pasien")
            krt, ok = input_batal("Pilih kriteria (A/B) atau Enter untuk batal : ")
            if not ok: continue
            krt = krt.upper()
            if krt == "A":
                klinik.tampilkan_laporan_harian("Nama")
            elif krt == "B":
                klinik.tampilkan_laporan_harian("ID Pasien")
            else:
                print("Pilihan tidak valid, tampil urutan default (ID).")
                klinik.tampilkan_laporan_harian("ID Pasien")
                
        elif pilihan == "11":
            print("\n─── CETAK STRUK PEMBAYARAN PASIEN ───")
            id_struk, ok = input_batal("ID Pasien : ")
            if not ok: continue
            klinik.cetak_struk_pembayaran(id_struk.upper())

        elif pilihan == "0":
            print("\nTerima kasih! Sistem Klinik Sehat Bersama ditutup. 👋")
            break

        else:
            print("❌ Pilihan tidak valid. Masukkan angka 0 - 11.")