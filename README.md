# 🛠️ EraldForge (Termux)

EraldForge adalah koleksi multitools Python modular yang dirancang khusus untuk Termux/terminal. Penekanan utama proyek ini adalah pada aspek ethical dan non-intrusive, dengan semua fitur sensitif memerlukan konfirmasi pengguna.


#
🔄 Pembaruan Manual

Jika pembaruan otomatis gagal, gunakan perintah tunggal ini untuk memperbarui ke versi terbaru dan menjalankannya:
cd ~/EraldForge && git reset --hard && git pull origin main && python3 eraldforge.py

### ⚠️ Pemecahan Masalah: Eksekusi Tools Manual

Jika tool seperti Port Scanner atau QR Code Generator gagal dijalankan dari menu utama, eksekusi manual file Python-nya secara langsung:
Tools yang Gagal
Perintah Manual

Port Scanner dan QR Code Generator
```bash
cd ~/EraldForge/tools/portscan && python port_scanner.py
cd ~/EraldForge/tools/qrcode && python qrcode_gen.py
