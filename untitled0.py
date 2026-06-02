from collections import deque


class SistemAntrianRumahSakit:
    def __init__(self):
        # Inisialisasi dua jenis antrian sesuai ketentuan
        self.antrian_prioritas = deque()
        self.antrian_reguler = deque()
        # Counter untuk nomor antrian unik
        self.counter_prioritas = 1
        self.counter_reguler = 1

    def tambah_pasien(self, nama, usia, is_darurat=False):
        """
        Menambahkan pasien ke antrian yang tepat berdasarkan kondisi kesehatan dan usia.
        """
        pasien = {
            "nama": nama,
            "usia": usia,
            "is_darurat": is_darurat
        }

        # Ketentuan Antrian Prioritas: Pasien darurat ATAU lansia (usia > 60)
        if is_darurat or usia > 60:
            pasien["nomor_antrian"] = f"P-{self.counter_prioritas:03d}"
            self.antrian_prioritas.append(pasien)
            self.counter_prioritas += 1
            print(f"👉 [BERHASIL] {nama} dimasukkan ke Antrian PRIORITAS ({pasien['nomor_antrian']})")
        else:
            # Antrian Reguler: Pasien umum yang mendaftar secara normal
            pasien["nomor_antrian"] = f"R-{self.counter_reguler:03d}"
            self.antrian_reguler.append(pasien)
            self.counter_reguler += 1
            print(f"👉 [BERHASIL] {nama} dimasukkan ke Antrian REGULER ({pasien['nomor_antrian']})")

    def panggil_pasien_berikutnya(self):
        """
        Memanggil pasien berikutnya dengan mendahulukan Antrian Prioritas.
        """
        print("\n📢 [PANGGILAN ANTRIAN]")
        # Cek antrian prioritas terlebih dahulu
        if self.antrian_prioritas:
            pasien = self.antrian_prioritas.popleft()
            keterangan = "Darurat" if pasien["is_darurat"] else f"Lansia ({pasien['usia']} tahun)"
            print(f"🔊 Nomor {pasien['nomor_antrian']} atas nama Kategori PRIORITAS ({keterangan})")
            print(f"   Silakan menuju ke Ruang Pemeriksaan Utama.")
            return pasien

        # Jika antrian prioritas kosong, baru panggil antrian reguler
        elif self.antrian_reguler:
            pasien = self.antrian_reguler.popleft()
            print(f"🔊 Nomor {pasien['nomor_antrian']} atas nama Kategori REGULER")
            print(f"   Silakan menuju ke Ruang Pemeriksaan.")
            return pasien

        else:
            print("📭 Semua antrian saat ini kosong.")
            return None

    def tampilkan_kondisi_antrian(self):
        """
        Menampilkan jumlah dan urutan pasien yang sedang mengantre saat ini.
        """
        print("\n============================ STATUS ANTRIAN SAAT INI ============================")

        # 1. Tampilkan Antrian Prioritas
        print(f"🔴 ANTRIAN PRIORITAS (Total: {len(self.antrian_prioritas)} pasien)")
        if not self.antrian_prioritas:
            print("   (Kosong)")
        else:
            for indeks, pasien in enumerate(self.antrian_prioritas, 1):
                kategori = "Darurat" if pasien["is_darurat"] else "Lansia"
                print(f"   {indeks}. [{pasien['nomor_antrian']}] {pasien['nama']} ({pasien['usia']} thn) - {kategori}")

        print("-" * 80)

        # 2. Tampilkan Antrian Reguler
        print(f"🔵 ANTRIAN REGULER (Total: {len(self.antrian_reguler)} pasien)")
        if not self.antrian_reguler:
            print("   (Kosong)")
        else:
            for indeks, pasien in enumerate(self.antrian_reguler, 1):
                print(f"   {indeks}. [{pasien['nomor_antrian']}] {pasien['nama']} ({pasien['usia']} thn)")

        print("=================================================================================\n")


# =================================================================================
# SIMULASI PENGGUNAAN SISTEM INTERAKTIF
# =================================================================================

if __name__ == "__main__":
    rs = SistemAntrianRumahSakit()

    while True:
        print("\n--- MENU SISTEM ANTRIAN RUMAH SAKIT ---")
        print("1. Tambah Pasien Baru")
        print("2. Panggil Pasien Berikutnya")
        print("3. Tampilkan Kondisi Antrian")
        print("4. Keluar")

        pilihan = input("Masukkan pilihan Anda: ")

        if pilihan == '1':
            nama = input("Nama Pasien: ")
            while True:
                try:
                    usia = int(input("Usia Pasien: "))
                    break
                except ValueError:
                    print("Usia harus berupa angka. Silakan coba lagi.")
            is_darurat_input = input("Apakah pasien dalam kondisi darurat? (ya/tidak): ").lower()
            is_darurat = True if is_darurat_input == 'ya' else False
            rs.tambah_pasien(nama, usia, is_darurat)
        elif pilihan == '2':
            rs.panggil_pasien_berikutnya()
        elif pilihan == '3':
            rs.tampilkan_kondisi_antrian()
        elif pilihan == '4':
            print("Terima kasih telah menggunakan sistem antrian. Sampai jumpa!")
            break
        else:
            print("Pilihan tidak valid. Silakan masukkan angka 1-4.")
