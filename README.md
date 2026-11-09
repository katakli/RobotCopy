<p align="center">
  <img src="assets/robot-copy.svg" width="120" alt="Robot Copy logosu">
</p>

# Robot Copy

`rsync` için sade, koyu temalı bir Linux arayüzü. Bir klasörü yerel diske, SSH ile uzak bir makineye ya da SMB ağ paylaşımına yedekler / senkronize eder.

*A small dark-themed Linux GUI for `rsync`: back up or mirror a folder to a local disk, an SSH host, or an SMB network share.*

## Özellikler

- Kaynak ve hedef klasör seçimi
- Ayna modu (`--delete`), devam eden kopyalama (`--partial`), FAT zaman toleransı, ilerleme/kalan süre
- Canlı çıktı, durdurma düğmesi, isteğe bağlı log dosyası
- Dahili **ağ paylaşımı bağla / ayır** penceresi (SMB/CIFS, `pkexec` ile yetkilendirme)
- Koyu tema, tek dosya, ek Python paketi gerektirmez

## Gereksinimler

- Python 3 ve `tkinter`
- `rsync`
- Ağ paylaşımı penceresi için: `cifs-utils` ve `polkit`

```bash
# Arch
sudo pacman -S python tk rsync cifs-utils polkit
# Debian / Ubuntu
sudo apt install python3-tk rsync cifs-utils policykit-1
# Fedora
sudo dnf install python3-tkinter rsync cifs-utils polkit
```

## Çalıştırma

```bash
python3 robot_copy.py
```

Uygulama menüsüne eklemek için (yalnızca mevcut kullanıcı için kurar):

```bash
bash install.sh              # kur
bash install.sh --uninstall  # kaldır
```

## Hedef türleri

| Hedef | Örnek |
| --- | --- |
| Yerel / bağlı klasör | `/mnt/yedek/proje` |
| SSH ile uzak makine | `kullanıcı@sunucu:/yol/klasör` |
| SMB paylaşımı | "Ağ paylaşımı…" ile bağlayıp bağlama klasörünü seç |

`smb://` adresleri doğrudan kullanılamaz; rsync bunları tanımaz. Paylaşımı önce bağlayın.

## Dikkat

- **Ayna modu (`--delete`) varsayılan olarak açıktır.** Hedefte, kaynakta olmayan dosyalar silinir. Hedef klasörün doğru yer olduğundan emin olun.
- rsync tek iş parçacığıyla çalışır; robocopy'deki `/MT`, `/R`, `/W` karşılıkları yoktur.
- Ağ paylaşımı şifresi kaydedilmez. Bağlama sırasında yalnızca kullanıcıya özel izinli geçici bir dosyada tutulur ve işlem bitince silinir.

## Lisans

[MIT](LICENSE)
