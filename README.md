# EraldForge (Termux)

EraldForge adalah kumpulan alat serbaguna Python untuk Termux dan terminal
Tool ini masih dalam pengembangan dan akan terus diperbarui
Jika ada kendala atau masalah mohon dimaklumi

![EraldForge](image/eraldforge.png)

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
Perintah Manual (Disarankan untuk menjalankannya secara manual karena dari menu terdapat masalah dan tools tidak sesuai)

Port Scanner :
```bash
cd ~/EraldForge/tools/portscan && python port_scanner.py
```
QR Code Generator :

```bash
cd ~/EraldForge/tools/qrcode && python qrcode_gen.py
```
