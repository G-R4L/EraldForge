# EraldForge (Termux)

EraldForge adalah koleksi multitools Python modular yang dirancang khusus untuk Termux/terminal. Penekanan utama proyek ini adalah pada aspek ethical dan non-intrusive, dengan semua fitur sensitif memerlukan konfirmasi pengguna.

### 🚀 Cara Install & Menjalankannya
```bash 
git clone https://github.com/G-R4L/EraldForge.git
cd EraldForge
bash install.sh
python eraldforge.py
```

### 🔄 Pembaruan Manual

Jika pembaruan otomatis gagal, gunakan perintah tunggal ini untuk memperbarui ke versi terbaru dan menjalankannya:
```bash
cd ~/EraldForge && git reset --hard && git pull origin main && python3 eraldforge.py
````
### ⚠️ Pemecahan Masalah: Eksekusi Tools Manual

Jika tool seperti Port Scanner atau QR Code Generator gagal dijalankan dari menu utama, eksekusi manual file Python-nya secara langsung:
Tools yang Gagal
Perintah Manual

Port Scanner
```bash
cd ~/EraldForge/tools/portscan && python port_scanner.py
```
QR Code Generator
```
cd ~/EraldForge/tools/qrcode && python qrcode_gen.py
```
