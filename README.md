# 🛠️ EraldForge (Termux)

EraldForge adalah koleksi multitools Python modular yang dirancang khusus untuk Termux/terminal. Penekanan utama proyek ini adalah pada aspek ethical dan non-intrusive, dengan semua fitur sensitif memerlukan konfirmasi pengguna.

### ⚠️ Pemecahan Masalah: Eksekusi Tools Manual

Jika tool seperti Port Scanner atau QR Code Generator gagal dijalankan dari menu utama, eksekusi manual file Python-nya secara langsung:
Tools yang Gagal
Perintah Manual

Port Scanner dan QR Code Generator
```bash
cd ~/EraldForge/tools/portscan && python port_scanner.py
cd ~/EraldForge/tools/qrcode && python qrcode_gen.py
