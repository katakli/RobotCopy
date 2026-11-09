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
- **Kayıtlı yedeklemeler**: kaynak, hedef ve seçenekleri ada kaydet (ör. “Bebek”), listeden seçince hepsi gelsin
- **Zamanlı yedekleme** (systemd): günlük, haftalık, iki haftalık, aylık; uygulama kapalıyken de çalışır
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

## Zamanlı yedekleme

Bir yedeklemeyi kaydet, sonra “Zamanla…” ile sıklığı seç. Uygulama `~/.config/systemd/user/` altına bir kullanıcı zamanlayıcısı yazar; arayüz açık olmak zorunda değildir.

- Bilgisayar o saatte kapalıysa kaçan yedek açılışta yapılır (`Persistent=true`).
- Kullanıcı zamanlayıcıları oturum açıkken çalışır. Oturum kapalıyken de çalışsın istersen: `loginctl enable-linger $USER`
- İki haftalık: zamanlayıcı her hafta tetiklenir, son başarılı yedekten 14 günden az geçmişse atlanır.
- Hedef bir ağ paylaşımıysa ve o an bağlı değilse yedek **atlanır** ve bildirim gelir (bağlı olmayan klasöre yanlışlıkla yazılmaz). Paylaşımı kendin bağlamış olmalısın; şifre kaydedilmediği için uygulama kendisi bağlayamaz.
- Arka plan yedeği şifre soramaz: SSH hedeflerinde anahtar tabanlı giriş gerekir.
- Komut satırı: `robot-copy --liste`, `robot-copy --profil "Bebek"`
- Ayarlar `~/.config/robot-copy/profiller.json` içinde tutulur.

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
