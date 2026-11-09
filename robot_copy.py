#!/usr/bin/env python3
"""Robot Copy — rsync için sade, koyu temalı bir Linux arayüzü.

Klasör yedekleme / senkronizasyon; yerel, SSH veya SMB (ağ paylaşımı) hedefleri.
Lisans: MIT
"""
try:
    import tkinter as tk
    from tkinter import filedialog, scrolledtext
except ImportError:  # arka planda (zamanlı) çalışırken tkinter gerekmez
    tk = filedialog = scrolledtext = None
import argparse
import hashlib
import json
import subprocess
import threading
import os
import re
import shutil
import sys
import tempfile
import time
import unicodedata
from datetime import datetime, timedelta

BG      = "#1a1a1a"
BG2     = "#242424"
BG3     = "#2e2e2e"
FG      = "#e0e0e0"
FG2     = "#888888"
ACCENT  = "#d4720a"
ACCENT2 = "#a35508"
BORDER  = "#3a3a3a"
RED     = "#e05555"
GREEN   = "#6abf8e"
ORANGE  = "#d4720a"

# Logo renkleri (mavi robot)
LOGO_MAVI  = "#3b82f6"
LOGO_KOYU  = "#1d4ed8"
LOGO_ACIK  = "#7cc4ff"
LOGO_GOZ   = "#e8f4ff"
LOGO_PUPIL = "#0b1f4d"

# Pencere / görev çubuğu simgesi (assets/robot-copy.svg'den üretilmiş PNG, base64)
SIMGE_PNG_64 = (
    "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"
    "Aut6cmm04HmyAAAAAElFTkSuQmCC"
)
SIMGE_PNG_32 = (
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABmJLR0QA/wD/AP+gvaeTAAADG0lE"
    "QVRYhe1WS0tVURT+1j4vu/nWfJs5KDVpUjaQdGCjIDIrqlFBEVQ0qaBBpHCpZgZFED0G0Q8Isowa"
    "WBSlYaEUVniDIl+JhWFi3ujuc85qoNZ9HG/n3BtR4Dfa7LX293177bXPPsD/DH83p/u7OT0ZDjWZ"
    "xaaJ8wwwgD2JclCiC0908WZitM2ybD+9jq7/NQPHH/ESReAlgPzZqXFVYpW/gca8colEDCgKroaJ"
    "A0CuVHENzJ435NlAcxevB6MQQC8D0wxMA+glQm7zEzR45UsKzZ3c09zJPclwJHQEfxK/vYbLmt5n"
    "SjNUpqh2TO7HD0EfACxt6l8THbNMYWqqPjjQVv4lHv+8TbN0Y18Wa8YFMO8EJ1gpIhvg24q09g/c"
    "qXa8IY4Gijb1+DQl7bWaohVml2Ubmk8DkbcGZ2bIoMTEyERITodGpTVVPdpeE4zOc9yZQmmnFF0t"
    "yK/MN/TFumdxACAi6It15C3P04WhFiiUdtIpz9EAEe/OKM5IIZHwh/IXlyBkFmakCEG7XBtgGzmq"
    "ntQzEQHVUGFb9hLH2NygtDFQA+AsZh6XmK1XFQtsWTuTfuOZif5R21McBCptDDwGwCT4yFBbVS8i"
    "KkDYA6AOQH20eG46oWWrgWwxhlRzBC3bDOSkket4GOoA1DPT3rmJnwaYad6aVxYJGBqw7+Ap7D3g"
    "h6EBVUXCdTwa4VquDnp4nGEzcOzobrA9Mx4cZ9fxeHBlYHDcxpX7Ejtqa8EALt+TGP5su467MkDg"
    "mI9EODr6THT0mQnHwxGuFV6B1rDxYVdM3nEuWsuxVUsa35gFlXmKkWpEzK8sEaivVOL+Rj19a+P5"
    "gBUx9/3rd4wFPlkjtypijtyxB4SCEflNlkUb2LJWxepyJY48UJgVayAUlBACQ075zk1o49Lk6KTf"
    "l7nIENovwasPJJ69i99cr4YixS1pYfLDRIgtnHHKd6xm9fbX+pRU7xJRXUZxpq77NHh9F9hmhIJy"
    "Rtzmh0M3KzYAFHM352f1syh5ETgkII7aNkoJHL/20QZAlhAYZgutw+0rLjqJL2AB/wR+ACEaNItp"
    "9abpAAAAAElFTkSuQmCC"
)

PENCERE_BASLIK = "Robot Copy"
PENCERE_EN     = 720
PENCERE_BOY    = 900

UYGULAMA    = "robot-copy"
YENI_ETIKET = "(Yeni yedekleme)"

# Zamanlı yedekte hedef bunlardan biri olarak kaydedildiyse ve şu an bağlı değilse yedek atlanır.
AG_DOSYA_SISTEMLERI = {"cifs", "smb3", "nfs", "nfs4", "fuse.sshfs", "fuse.rclone", "davfs"}

SIKLIKLAR = [("gunluk", "Günlük"), ("haftalik", "Haftalık"),
             ("iki_haftalik", "İki haftalık"), ("aylik", "Aylık")]
GUNLER = [("Pazartesi", "Mon"), ("Salı", "Tue"), ("Çarşamba", "Wed"), ("Perşembe", "Thu"),
          ("Cuma", "Fri"), ("Cumartesi", "Sat"), ("Pazar", "Sun")]
GUN_TR_EN = dict(GUNLER)
GUN_EN_TR = {en: tr for tr, en in GUNLER}
SISTEM_KLASORLERI = {"/", "/home", "/root", "/usr", "/etc", "/var", "/bin", "/sbin", "/lib",
                     "/boot", "/dev", "/proc", "/sys", "/run", "/tmp", "/opt", "/mnt", "/media"}
IKI_HAFTA_ESIGI_GUN = 13   # iki haftalıkta: son başarılı yedekten en az bu kadar gün geçmeli


# ══════════════════════════════════════════════════════════════════
#  ÇEKİRDEK — arayüzden bağımsız (zamanlı yedek tkinter olmadan çalışır)
# ══════════════════════════════════════════════════════════════════
def _xdg(degisken, varsayilan):
    return os.environ.get(degisken) or os.path.expanduser(varsayilan)


def ayar_dizini():
    return os.path.join(_xdg("XDG_CONFIG_HOME", "~/.config"), UYGULAMA)


def durum_dizini():
    return os.path.join(_xdg("XDG_STATE_HOME", "~/.local/state"), UYGULAMA)


def systemd_dizini():
    return os.path.join(_xdg("XDG_CONFIG_HOME", "~/.config"), "systemd", "user")


def _json_oku(yol):
    try:
        with open(yol, encoding="utf-8") as f:
            veri = json.load(f)
        return veri if isinstance(veri, dict) else {}
    except FileNotFoundError:
        return {}
    except ValueError:      # bozuk dosya: üzerine yazılmadan önce yedeğini al
        try:
            os.replace(yol, yol + ".bozuk")
        except OSError:
            pass
        return {}
    except OSError:
        return {}


def _json_yaz(yol, veri):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    gecici = yol + ".tmp"
    with open(gecici, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)
    os.replace(gecici, yol)


def profilleri_yukle():
    return _json_oku(os.path.join(ayar_dizini(), "profiller.json"))


def profilleri_kaydet(profiller):
    _json_yaz(os.path.join(ayar_dizini(), "profiller.json"), profiller)


def profil_kimligi(ad):
    """Birim adlarında kullanılacak güvenli ve ada özgü kimlik (ascii ad + kısa özet)."""
    cevir = str.maketrans("ıİğĞüÜşŞöÖçÇ", "iIgGuUsSoOcC")
    ascii_ad = unicodedata.normalize("NFKD", ad.translate(cevir)).encode("ascii", "ignore").decode()
    temiz = re.sub(r"[^a-z0-9]+", "-", ascii_ad.lower()).strip("-")[:24] or "profil"
    return f"{temiz}-{hashlib.sha1(ad.encode('utf-8')).hexdigest()[:6]}"


def uzak_mi(yol):
    """kullanıcı@sunucu:/yol ya da sunucu:/yol biçimindeki (SSH) hedef."""
    return re.match(r"^(?:[^/@:\s]+@)?[^/@:\s]+:", yol.strip()) is not None


_FSYNC = {}


def rsync_fsync_var_mi():
    """Kurulu rsync --fsync seçeneğini biliyor mu (3.2.4+)?"""
    if "var" not in _FSYNC:
        try:
            cikti = subprocess.run(["rsync", "--help"], capture_output=True, text=True, timeout=10)
            _FSYNC["var"] = "--fsync" in (cikti.stdout + cikti.stderr)
        except (OSError, subprocess.SubprocessError):
            _FSYNC["var"] = False
    return _FSYNC["var"]


def rsync_komutu(kaynak, hedef, mir=True, fft=True, z=True, eta=True,
                 log_yolu=None, arka_plan=False, izinsiz=None):
    if not shutil.which("rsync"):
        raise ValueError("rsync bulunamadı. Kur: sudo pacman -S rsync")
    kaynak = (kaynak or "").strip()
    hedef = (hedef or "").strip()
    if not kaynak or not hedef:
        raise ValueError("Kaynak ve hedef klasör boş bırakılamaz.")

    # Sondaki "/" kaynağın İÇERİĞİNİ hedefe kopyalar (robocopy davranışı)
    kaynak = os.path.join(kaynak, "")
    if not hedef.endswith("/"):
        hedef += "/"

    komut = ["rsync", "-a", "--human-readable", "--itemize-changes"]
    # Ağ paylaşımları (SMB/NFS) Linux izin ve sahiplik bilgisini saklamaz: her çalıştırmada
    # "izin farklı" diye dosya listelenmesin.
    if izinsiz is None:
        izinsiz = not uzak_mi(hedef) and fs_turu(hedef) in AG_DOSYA_SISTEMLERI
    if izinsiz:
        komut += ["--no-perms", "--no-owner", "--no-group"]
        # Ağ paylaşımına yazılan veri önce bellekte bekler; rsync dosya tarihini ayarladıktan sonra
        # sunucu veriyi alınca tarihi "şimdi" yapar → dosya her seferinde "değişmiş" görünür.
        # --fsync veriyi tarih ayarlanmadan önce sunucuya yazdırır.
        if rsync_fsync_var_mi():
            komut += ["--fsync"]
    if mir:
        komut += ["--delete"]
    if fft:
        komut += ["--modify-window=2"]
    if z:
        komut += ["--partial"]
    if eta and not arka_plan:
        komut += ["--info=progress1"]   # dosya başına yüzde ve hız
    if not arka_plan:
        komut += ["--info=stats2"]   # rapordaki "değişmeyen" sayısı için toplam dosya sayısı
    if log_yolu:
        komut += [f"--log-file={log_yolu}"]
    if arka_plan and uzak_mi(hedef):
        komut += ["-e", "ssh -o BatchMode=yes"]   # şifre sorup takılmasın
    komut += [kaynak, hedef]
    return komut


def satir_coz(satir):
    """rsync --itemize-changes satırını (tür, ad) olarak çözer. tür: yeni | guncel | silinen.
    Klasör ve diğer satırlar için None döner."""
    m = re.match(r"^\*deleting\s+(.*)$", satir)
    if m:
        return ("silinen", m.group(1)) if not m.group(1).endswith("/") else None
    m = re.match(r"^([<>ch.])([fdLDS])(\S{9}) (.*)$", satir)
    if not m or m.group(2) != "f" or m.group(1) not in "<>":
        return None
    return ("yeni" if "+" in m.group(3) else "guncel"), m.group(4)


def fs_turu(yol):
    """Yolun bulunduğu dosya sisteminin türü (ör. ext4, cifs); bilinmiyorsa ''.
    Yalnızca /proc/self/mountinfo okunur, yola hiç dokunulmaz: yavaş ya da kopmuş
    bir ağ paylaşımında bile anında döner, arayüzü dondurmaz."""
    try:
        yol = os.path.normpath(os.path.abspath(yol))
        en_iyi, tur = "", ""
        with open("/proc/self/mountinfo", encoding="utf-8", errors="replace") as f:
            for satir in f:
                sol, ayrac, sag = satir.partition(" - ")
                if not ayrac:
                    continue
                alanlar = sol.split()
                if len(alanlar) < 5:
                    continue
                nokta = re.sub(r"\\([0-7]{3})", lambda m: chr(int(m.group(1), 8)), alanlar[4])
                if (yol == nokta or yol.startswith(nokta.rstrip("/") + "/")) and len(nokta) >= len(en_iyi):
                    en_iyi, tur = nokta, sag.split()[0]
        return tur
    except (OSError, IndexError):
        return ""


def hedef_hazir_mi(profil):
    """(hazır_mı, neden). Bağlı olmayan ağ paylaşımına yanlışlıkla yazılmasını önler."""
    hedef = profil.get("hedef", "").strip()
    if uzak_mi(hedef):
        return True, ""
    beklenen = profil.get("hedef_fs", "")
    if beklenen in AG_DOSYA_SISTEMLERI and fs_turu(hedef) != beklenen:
        return False, f"Hedef bağlı değil (beklenen: {beklenen}). Ağ paylaşımını bağla."
    h = hedef.rstrip("/") or "/"
    if os.path.isdir(h) or os.path.isdir(os.path.dirname(h)):
        return True, ""
    return False, "Hedef klasör bulunamadı."


def _durum_yolu():
    return os.path.join(durum_dizini(), "son_calisma.json")


def son_calisma(kimlik):
    deger = _json_oku(_durum_yolu()).get(kimlik)
    try:
        return datetime.fromisoformat(deger) if deger else None
    except (ValueError, TypeError):
        return None


def son_calisma_yaz(kimlik):
    veri = _json_oku(_durum_yolu())
    veri[kimlik] = datetime.now().isoformat(timespec="seconds")
    _json_yaz(_durum_yolu(), veri)


# ── zamanlama → systemd ──────────────────────────────────────────
def zamanlama_dogrula(z):
    try:
        saat, dakika = int(z["saat"]), int(z["dakika"])
        ay_gunu = int(z.get("ay_gunu", 1))
    except (KeyError, TypeError, ValueError):
        raise ValueError("Saat ve dakika sayı olmalı.") from None
    if z.get("sikllik") not in dict(SIKLIKLAR):
        raise ValueError("Geçersiz sıklık.")
    if not 0 <= saat <= 23:
        raise ValueError("Saat 0–23 arasında olmalı.")
    if not 0 <= dakika <= 59:
        raise ValueError("Dakika 0–59 arasında olmalı.")
    if z["sikllik"] in ("haftalik", "iki_haftalik") and z.get("gun") not in GUN_EN_TR:
        raise ValueError("Geçersiz gün.")
    if z["sikllik"] == "aylik" and not 1 <= ay_gunu <= 28:
        raise ValueError("Ayın günü 1–28 arasında olmalı.")


def takvim_ifadesi(z):
    """systemd OnCalendar ifadesi. İki haftalık: her hafta tetiklenir, 14 günlük aralığı çalıştırıcı denetler."""
    zamanlama_dogrula(z)
    sa = f"{int(z['saat']):02d}:{int(z['dakika']):02d}:00"
    s = z["sikllik"]
    if s == "gunluk":
        return f"*-*-* {sa}"
    if s in ("haftalik", "iki_haftalik"):
        return f"{z['gun']} *-*-* {sa}"
    return f"*-*-{int(z['ay_gunu']):02d} {sa}"


def zamanlama_ozeti(z):
    if not z:
        return "Zamanlama: kapalı"
    try:
        zamanlama_dogrula(z)
    except ValueError:
        return "Zamanlama: bozuk kayıt"
    ad = dict(SIKLIKLAR)[z["sikllik"]]
    saat = f"{int(z['saat']):02d}:{int(z['dakika']):02d}"
    if z["sikllik"] in ("haftalik", "iki_haftalik"):
        return f"Zamanlama: {ad}, {GUN_EN_TR[z['gun']]} {saat}"
    if z["sikllik"] == "aylik":
        return f"Zamanlama: {ad}, ayın {int(z['ay_gunu'])}. günü {saat}"
    return f"Zamanlama: {ad}, {saat}"


def _sd_alinti(metin):
    """systemd ExecStart argümanı için tırnak ve kaçış."""
    return '"' + metin.replace("\\", "\\\\").replace('"', '\\"').replace("%", "%%").replace("$", "$$") + '"'


def birim_metinleri(ad, kimlik, z, python, betik):
    aciklama = " ".join(ad.split()).replace("%", "%%")
    hizmet = (
        "[Unit]\n"
        f"Description=Robot Copy yedeklemesi: {aciklama}\n\n"
        "[Service]\n"
        "Type=oneshot\n"
        f"ExecStart={_sd_alinti(python)} {_sd_alinti(betik)} --kimlik {_sd_alinti(kimlik)}\n"
    )
    zamanlayici = (
        "[Unit]\n"
        f"Description=Robot Copy zamanlayıcısı: {aciklama}\n\n"
        "[Timer]\n"
        f"OnCalendar={takvim_ifadesi(z)}\n"
        "Persistent=true\n\n"
        "[Install]\n"
        "WantedBy=timers.target\n"
    )
    return hizmet, zamanlayici


def birim_adi(ad):
    return f"{UYGULAMA}-{profil_kimligi(ad)}"


def _systemctl(*argumanlar):
    return subprocess.run(["systemctl", "--user", *argumanlar],
                          capture_output=True, text=True, timeout=30)


def zamanlamayi_uygula(ad, z):
    """Birim dosyalarını yazıp zamanlayıcıyı etkinleştirir. (başarılı_mı, mesaj) döner."""
    if not shutil.which("systemctl"):
        return False, "systemctl bulunamadı (systemd gerekli)."
    try:
        kimlik = profil_kimligi(ad)
        hizmet, zamanlayici = birim_metinleri(ad, kimlik, z, sys.executable, os.path.abspath(__file__))
        dizin = systemd_dizini()
        os.makedirs(dizin, exist_ok=True)
        birim = birim_adi(ad)
        for uzanti, icerik in ((".service", hizmet), (".timer", zamanlayici)):
            with open(os.path.join(dizin, birim + uzanti), "w", encoding="utf-8") as f:
                f.write(icerik)
        for adim in (("daemon-reload",), ("enable", birim + ".timer"), ("restart", birim + ".timer")):
            r = _systemctl(*adim)
            if r.returncode != 0:
                return False, (r.stderr or r.stdout or f"systemctl {adim[0]} başarısız").strip()
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        return False, str(e)
    return True, "Zamanlayıcı etkinleştirildi."


def zamanlamayi_kapat(ad):
    birim = birim_adi(ad)
    var_mi = shutil.which("systemctl") is not None
    try:
        if var_mi:
            _systemctl("disable", "--now", birim + ".timer")
        for uzanti in (".timer", ".service"):
            try:
                os.remove(os.path.join(systemd_dizini(), birim + uzanti))
            except FileNotFoundError:
                pass
        if var_mi:
            _systemctl("daemon-reload")
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)
    return True, "Zamanlama kapatıldı."


# ── arka planda (arayüzsüz) çalıştırma ───────────────────────────
def bildirim(baslik, govde):
    if shutil.which("notify-send"):
        try:
            subprocess.run(["notify-send", "-a", "Robot Copy", "-i", UYGULAMA, baslik, govde],
                           timeout=10, check=False)
        except (OSError, subprocess.SubprocessError):
            pass


def zamanli_calistir(kimlik=None, ad=None, kapi=True):
    """Kayıtlı yedeklemeyi arayüzsüz çalıştırır. Çıkış kodu: 0 başarılı/atlandı, 75 hedef hazır değil, diğerleri hata."""
    profiller = profilleri_yukle()
    if ad is None:
        ad = next((a for a in profiller if profil_kimligi(a) == kimlik), None)
    if ad is None or ad not in profiller:
        print(f"Kayıtlı yedekleme bulunamadı: {kimlik or ad}", file=sys.stderr)
        return 2
    p = profiller[ad]
    kimlik = profil_kimligi(ad)
    z = p.get("zamanlama") or {}

    if kapi and z.get("sikllik") == "iki_haftalik":
        son = son_calisma(kimlik)
        if son and datetime.now() - son < timedelta(days=IKI_HAFTA_ESIGI_GUN):
            print(f"{ad}: iki haftalık aralık dolmadı, bu hafta atlandı.")
            return 0

    if not os.path.isdir(p.get("kaynak", "")):
        bildirim(f"{ad}: yedek alınamadı", "Kaynak klasör bulunamadı.")
        print(f"{ad}: kaynak klasör bulunamadı: {p.get('kaynak')}", file=sys.stderr)
        return 3
    hazir, neden = hedef_hazir_mi(p)
    if not hazir:
        bildirim(f"{ad}: yedek atlandı", neden)
        print(f"{ad}: yedek atlandı. {neden}", file=sys.stderr)
        return 75   # EX_TEMPFAIL: sonraki zamanlamada yeniden denenir

    if p.get("log") and p.get("log_yolu"):
        log_yolu = p["log_yolu"]
    else:
        log_yolu = os.path.join(durum_dizini(), kimlik + ".log")
    try:
        os.makedirs(os.path.dirname(log_yolu) or ".", exist_ok=True)
        komut = rsync_komutu(p["kaynak"], p["hedef"], p.get("mir", True), p.get("fft", True),
                             p.get("z", True), False, log_yolu, arka_plan=True)
    except (ValueError, OSError) as e:
        print(f"{ad}: {e}", file=sys.stderr)
        bildirim(f"{ad}: yedek alınamadı", str(e))
        return 1
    kod = subprocess.run(komut).returncode
    if kod in (0, 24):   # 24: kopyalama sırasında kaybolan dosyalar, zararsız
        son_calisma_yaz(kimlik)
        bildirim(f"{ad}: yedek tamamlandı", "Yedekleme başarıyla bitti.")
        return 0
    bildirim(f"{ad}: yedekleme hatası", f"rsync çıkış kodu {kod}. Ayrıntı için log dosyasına bak.")
    return kod


def cli(argv):
    ap = argparse.ArgumentParser(
        prog=UYGULAMA,
        description="Robot Copy — rsync arayüzü. Argümansız çalıştırılırsa arayüz açılır.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--kimlik", help="(zamanlayıcı kullanır) profil kimliğiyle arka planda yedekle")
    g.add_argument("--profil", help="kayıtlı yedeklemeyi adıyla arka planda çalıştır")
    g.add_argument("--liste", action="store_true", help="kayıtlı yedeklemeleri listele")
    a = ap.parse_args(argv)
    if a.liste:
        for ad, p in sorted(profilleri_yukle().items()):
            print(f"{ad}\t{zamanlama_ozeti(p.get('zamanlama'))}\t{p.get('kaynak')} -> {p.get('hedef')}")
        return 0
    if a.profil:
        return zamanli_calistir(ad=a.profil, kapi=False)
    return zamanli_calistir(kimlik=a.kimlik)


class RobotCopyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(PENCERE_BASLIK)
        try:
            self._simgeler = [tk.PhotoImage(data=d) for d in (SIMGE_PNG_64, SIMGE_PNG_32)]
            self.root.iconphoto(True, *self._simgeler)
        except tk.TclError:
            pass  # PNG desteklemeyen eski Tk: varsayılan simge kalır
        yukseklik = min(PENCERE_BOY, max(680, self.root.winfo_screenheight() - 80))
        self.root.geometry(f"{PENCERE_EN}x{yukseklik}")
        self.root.resizable(True, True)
        self.root.minsize(560, 680)
        self.root.configure(bg=BG)

        home = os.path.expanduser("~")
        self.kaynak_yol = tk.StringVar(value=home)
        self.hedef_yol  = tk.StringVar(value="")
        self.log_yolu   = tk.StringVar(value=os.path.join(home, "Yedek_Raporu.txt"))

        self.opt_mir = tk.BooleanVar(value=True)   # --delete
        self.opt_fft = tk.BooleanVar(value=True)   # --modify-window=2
        self.opt_z   = tk.BooleanVar(value=True)   # --partial
        self.opt_eta = tk.BooleanVar(value=True)   # --info=progress1 (dosya başına)
        self.opt_log = tk.BooleanVar(value=True)

        self.islemiyor = False
        self.proses    = None
        self.profil_ad    = tk.StringVar(value=YENI_ETIKET)
        self.profil_bilgi = tk.StringVar(value="")

        self._arayuz_olustur()

    def _yuvarlak_dikdortgen(self, canvas, x1, y1, x2, y2, r, **kw):
        p = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2,
             x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        return canvas.create_polygon(p, smooth=True, **kw)

    def _logo_ciz(self, canvas, w, h):
        """Mavi robot kafası, anteni yukarı ok. 40x40'lık tasarım alanı w/h'ye ölçeklenir.
        Geometri assets/robot-copy.svg ile aynıdır."""
        k = min(w, h) / 40.0

        def s(*v):
            return [x * k for x in v]

        # anten: gövde + yukarı ok ucu
        canvas.create_line(*s(20, 8, 20, 13), fill=LOGO_ACIK,
                           width=max(1, 2 * k), capstyle=tk.ROUND)
        canvas.create_polygon(*s(20, 2, 15.5, 8.5, 24.5, 8.5), fill=LOGO_ACIK, outline="")
        # kulaklar
        self._yuvarlak_dikdortgen(canvas, *s(3, 19, 7, 27), 1.5 * k,
                                  fill=LOGO_KOYU, outline="")
        self._yuvarlak_dikdortgen(canvas, *s(33, 19, 37, 27), 1.5 * k,
                                  fill=LOGO_KOYU, outline="")
        # kafa
        self._yuvarlak_dikdortgen(canvas, *s(7, 13, 33, 33), 5 * k,
                                  fill=LOGO_MAVI, outline=LOGO_KOYU,
                                  width=max(1, 1.5 * k))
        # gözler
        for gx in (15, 25):
            canvas.create_oval(*s(gx - 3, 19, gx + 3, 25), fill=LOGO_GOZ, outline="")
            canvas.create_oval(*s(gx - 1.2, 20.8, gx + 1.2, 23.2),
                               fill=LOGO_PUPIL, outline="")
        # ağız
        self._yuvarlak_dikdortgen(canvas, *s(14, 28, 26, 30.5), 1.2 * k,
                                  fill=LOGO_GOZ, outline="")

    def _entry(self, master, textvariable):
        return tk.Entry(master, textvariable=textvariable,
                        bg=BG3, fg=FG, insertbackground=ACCENT,
                        relief=tk.FLAT, highlightthickness=1,
                        highlightbackground=BORDER, highlightcolor=ACCENT,
                        disabledbackground=BG2, disabledforeground=FG2,
                        font=("Sans", 9))

    def _button(self, master, text, command, accent=False, state="normal", width=None):
        kw = dict(text=text, command=command, state=state,
                  relief=tk.FLAT, cursor="hand2",
                  font=("Sans", 9), padx=12, pady=5, borderwidth=0,
                  highlightthickness=1, highlightbackground=master.cget("bg"),
                  highlightcolor=ACCENT)
        if width:
            kw["width"] = width
        if accent:
            kw.update(bg=ACCENT, fg="#1a1a1a", activebackground=ACCENT2, activeforeground=FG)
        else:
            kw.update(bg=BG3, fg=FG, activebackground=BORDER, activeforeground=FG)
        return tk.Button(master, **kw)

    def _check(self, master, text, variable):
        return tk.Checkbutton(master, text=text, variable=variable,
                              bg=BG2, fg=FG, selectcolor=BG3,
                              activebackground=BG2, activeforeground=FG,
                              font=("Sans", 9), relief=tk.FLAT, borderwidth=0,
                              highlightthickness=1, highlightbackground=master.cget("bg"),
                              highlightcolor=ACCENT)

    def _section(self, master, row, title):
        fr = tk.Frame(master, bg=BG)
        fr.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(10, 2))
        tk.Label(fr, text=title, bg=BG, fg=ACCENT,
                 font=("Sans", 8, "bold")).pack(side=tk.LEFT, padx=(2, 8))
        tk.Frame(fr, bg=BORDER, height=1).pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _card(self, master, row):
        fr = tk.Frame(master, bg=BG2, padx=12, pady=10)
        fr.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(0, 2))
        fr.columnconfigure(0, weight=1)
        return fr

    def _arayuz_olustur(self):
        main = tk.Frame(self.root, bg=BG, padx=16, pady=12)
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(1, weight=1)

        hdr = tk.Frame(main, bg=BG)
        hdr.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        cv = tk.Canvas(hdr, width=40, height=40, bg=BG, highlightthickness=0)
        cv.pack(side=tk.LEFT, padx=(0, 10))
        self._logo_ciz(cv, 40, 40)
        tk.Label(hdr, text="Robot Copy",
                 bg=BG, fg=FG, font=("Sans", 12, "bold")).pack(side=tk.LEFT, anchor="w")

        # Kayıtlı yedeklemeler
        self._section(main, 1, "KAYITLI YEDEKLEMELER")
        pk = self._card(main, 2)
        sat = tk.Frame(pk, bg=BG2)
        sat.grid(row=0, column=0, sticky="ew")
        sat.columnconfigure(0, weight=1)
        self.profil_menu = tk.OptionMenu(sat, self.profil_ad, YENI_ETIKET)
        self.profil_menu.config(bg=BG3, fg=FG, activebackground=BORDER, activeforeground=FG,
                                relief=tk.FLAT, borderwidth=0, highlightthickness=1,
                                highlightbackground=BORDER, highlightcolor=ACCENT,
                                font=("Sans", 9), anchor="w", padx=10, pady=5, cursor="hand2")
        self.profil_menu["menu"].config(bg=BG3, fg=FG, activebackground=ACCENT,
                                        activeforeground="#1a1a1a", borderwidth=0,
                                        font=("Sans", 9))
        self.profil_menu.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._button(sat, "Kaydet", self._profil_kaydet).grid(row=0, column=1, padx=(0, 6))
        self._button(sat, "Zamanla…", self._zamanla_dialog).grid(row=0, column=2, padx=(0, 6))
        self._button(sat, "Sil", self._profil_sil).grid(row=0, column=3)
        tk.Label(pk, textvariable=self.profil_bilgi, bg=BG2, fg=FG2, font=("Sans", 8),
                 wraplength=640, justify="left", anchor="w").grid(
            row=1, column=0, sticky="ew", pady=(6, 0))
        self._profil_menusu_yenile()
        self._profil_bilgi_guncelle()

        # Kaynak
        self._section(main, 3, "KAYNAK KLASÖR")
        kk = self._card(main, 4)
        self._entry(kk, self.kaynak_yol).grid(row=0, column=0, sticky="ew", ipady=4, padx=(0, 8))
        self._button(kk, "  Gözat", lambda: self._klasor_sec(self.kaynak_yol)).grid(row=0, column=1)

        # Hedef
        self._section(main, 5, "HEDEF KLASÖR")
        hk = self._card(main, 6)
        self._entry(hk, self.hedef_yol).grid(row=0, column=0, sticky="ew", ipady=4, padx=(0, 8))
        self._button(hk, "  Gözat", lambda: self._klasor_sec(self.hedef_yol)).grid(row=0, column=1)
        self._button(hk, "Ağ paylaşımı…", self._ag_dialog).grid(row=0, column=2, padx=(8, 0))
        tk.Label(hk, text="Yerel/bağlı klasör ya da uzak yol: kullanıcı@sunucu:/yol/klasör",
                 bg=BG2, fg=FG2, font=("Sans", 8)).grid(row=1, column=0, columnspan=2,
                                                          sticky="w", pady=(6, 0))

        # Seçenekler
        self._section(main, 7, "SEÇENEKLER")
        opt = self._card(main, 8)
        opt.columnconfigure(0, weight=1)
        opt.columnconfigure(2, weight=1)

        mir_fr = tk.Frame(opt, bg=BG2)
        mir_fr.grid(row=0, column=0, columnspan=4, sticky="w", pady=2)
        self._check(mir_fr, "--delete – Ayna yedek (hedefte fazla dosyalar silinir)",
                    self.opt_mir).pack(side=tk.LEFT)
        tk.Label(mir_fr, text="varsayılan", bg="#3a2000", fg=ACCENT,
                 font=("Sans", 8), padx=6, pady=1).pack(side=tk.LEFT, padx=8)

        self._check(opt, "--partial – Devam eden mod", self.opt_z).grid(row=1, column=0, sticky="w", pady=2)
        self._check(opt, "FAT zaman toleransı", self.opt_fft).grid(row=1, column=2, sticky="w", pady=2)
        self._check(opt, "İlerleme / kalan süre", self.opt_eta).grid(row=2, column=0, sticky="w", pady=2)

        log_fr = tk.Frame(opt, bg=BG2)
        log_fr.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(6, 0))
        log_fr.columnconfigure(1, weight=1)
        self._check(log_fr, "Log dosyası kaydet", self.opt_log).grid(row=0, column=0, sticky="w")
        self.log_entry = self._entry(log_fr, self.log_yolu)
        self.log_entry.grid(row=0, column=1, sticky="ew", ipady=3, padx=(8, 6))
        self._button(log_fr, "…", self._log_sec, width=2).grid(row=0, column=2)

        # Butonlar
        btn_card = tk.Frame(main, bg=BG)
        btn_card.grid(row=9, column=0, columnspan=3, sticky="ew", pady=(10, 4))
        btn_card.columnconfigure(0, weight=1)

        self.basla_btn = self._button(btn_card, "▷   Yedeklemeyi başlat", self._baslat, accent=True)
        self.basla_btn.config(font=("Sans", 10, "bold"), pady=9)
        self.basla_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.dur_btn = self._button(btn_card, "■  Durdur", self._durdur, state=tk.DISABLED)
        self.dur_btn.grid(row=0, column=1, padx=(0, 6))
        self._button(btn_card, "Temizle", self._temizle).grid(row=0, column=2)

        # Durum
        self.durum_var = tk.StringVar(value="Hazır.")
        tk.Label(main, textvariable=self.durum_var, bg=BG, fg=FG2,
                 font=("Sans", 8)).grid(row=10, column=0, columnspan=3, sticky="w", pady=(2, 4))

        # Çıktı
        self._section(main, 11, "ÇIKTI")
        main.rowconfigure(12, weight=1)
        self.cikti = scrolledtext.ScrolledText(
            main, height=20, font=("Monospace", 9),
            bg=BG2, fg=FG, insertbackground=ACCENT,
            selectbackground="#4a2800",
            relief=tk.FLAT, highlightthickness=1,
            highlightbackground=BORDER,
            state=tk.DISABLED, wrap=tk.WORD)
        self.cikti.grid(row=12, column=0, columnspan=3, sticky="nsew")
        try:   # koyu temaya uyumlu kaydırma çubuğu
            self.cikti.vbar.config(bg=BG3, troughcolor=BG2, activebackground=BORDER,
                                   highlightthickness=0, borderwidth=0, relief=tk.FLAT)
        except tk.TclError:
            pass

        self._log_toggle()

    def _klasor_sec(self, degisken):
        baslangic = degisken.get()
        if not os.path.isdir(baslangic):
            baslangic = os.path.expanduser("~")
        yol = filedialog.askdirectory(initialdir=baslangic)
        if yol:
            degisken.set(os.path.normpath(yol))

    # ── KAYITLI YEDEKLEMELER ───────────────────────────
    def _profil_verisi(self):
        hedef = self.hedef_yol.get().strip()
        return {
            "kaynak": self.kaynak_yol.get().strip(),
            "hedef": hedef,
            "hedef_fs": "" if uzak_mi(hedef) else fs_turu(hedef),
            "mir": self.opt_mir.get(), "fft": self.opt_fft.get(),
            "z": self.opt_z.get(), "eta": self.opt_eta.get(),
            "log": self.opt_log.get(), "log_yolu": self.log_yolu.get().strip(),
            "zamanlama": None,
        }

    def _profil_menusu_yenile(self):
        menu = self.profil_menu["menu"]
        menu.delete(0, "end")
        menu.add_command(label=YENI_ETIKET, command=lambda: self._profil_sec(YENI_ETIKET))
        for ad in sorted(profilleri_yukle(), key=str.casefold):
            menu.add_command(label=ad, command=lambda a=ad: self._profil_sec(a))

    def _profil_bilgi_guncelle(self):
        ad = self.profil_ad.get()
        if ad == YENI_ETIKET:
            self.profil_bilgi.set("Kaynak ve hedefi seçip “Kaydet” ile kayıtlı bir yedekleme oluştur.")
            return
        p = profilleri_yukle().get(ad) or {}
        metin = zamanlama_ozeti(p.get("zamanlama"))
        son = son_calisma(profil_kimligi(ad))
        if son:
            metin += f"   ·   Son arka plan yedeği: {son:%d.%m.%Y %H:%M}"
        self.profil_bilgi.set(metin)

    def _profil_sec(self, ad):
        self.profil_ad.set(ad)
        p = profilleri_yukle().get(ad) if ad != YENI_ETIKET else None
        if p:
            self.kaynak_yol.set(p.get("kaynak", ""))
            self.hedef_yol.set(p.get("hedef", ""))
            self.opt_mir.set(bool(p.get("mir", True)))
            self.opt_fft.set(bool(p.get("fft", True)))
            self.opt_z.set(bool(p.get("z", True)))
            self.opt_eta.set(bool(p.get("eta", True)))
            self.opt_log.set(bool(p.get("log", True)))
            if p.get("log_yolu"):
                self.log_yolu.set(p["log_yolu"])
            self._log_toggle()
        self._profil_bilgi_guncelle()

    def _ad_sor(self, baslik, baslangic=""):
        dlg = tk.Toplevel(self.root)
        dlg.title(baslik)
        dlg.configure(bg=BG2)
        dlg.resizable(False, False)
        dlg.transient(self.root)
        sonuc = {"ad": None}
        var = tk.StringVar(value=baslangic)
        tk.Label(dlg, text="Yedeklemenin adı (ör. Bebek):", bg=BG2, fg=FG,
                 font=("Sans", 9)).pack(padx=16, pady=(16, 4), anchor="w")
        giris = self._entry(dlg, var)
        giris.config(width=36)
        giris.pack(padx=16, fill=tk.X, ipady=4)

        def tamam(_=None):
            sonuc["ad"] = " ".join(var.get().split())
            dlg.destroy()

        bf = tk.Frame(dlg, bg=BG2)
        bf.pack(padx=16, pady=14, anchor="e")
        self._button(bf, "İptal", dlg.destroy).pack(side=tk.LEFT, padx=(0, 8))
        self._button(bf, "Kaydet", tamam, accent=True).pack(side=tk.LEFT)
        dlg.bind("<Return>", tamam)
        dlg.bind("<Escape>", lambda e: dlg.destroy())
        giris.focus_set()
        giris.select_range(0, tk.END)
        self.root.wait_window(dlg)
        return sonuc["ad"]

    def _onay_sor(self, metin, evet="Sil"):
        dlg = tk.Toplevel(self.root)
        dlg.title("Onay")
        dlg.configure(bg=BG2)
        dlg.resizable(False, False)
        dlg.transient(self.root)
        sonuc = {"evet": False}
        tk.Label(dlg, text=metin, bg=BG2, fg=FG, font=("Sans", 9), wraplength=360,
                 justify="left").pack(padx=18, pady=(18, 8), anchor="w")

        def tamam(_=None):
            sonuc["evet"] = True
            dlg.destroy()

        bf = tk.Frame(dlg, bg=BG2)
        bf.pack(padx=18, pady=(6, 16), anchor="e")
        self._button(bf, "İptal", dlg.destroy).pack(side=tk.LEFT, padx=(0, 8))
        self._button(bf, evet, tamam, accent=True).pack(side=tk.LEFT)
        dlg.bind("<Escape>", lambda e: dlg.destroy())
        self.root.wait_window(dlg)
        return sonuc["evet"]

    def _profil_kaydet(self):
        veri = self._profil_verisi()
        if not veri["kaynak"] or not veri["hedef"]:
            self.profil_bilgi.set("Kaydetmek için kaynak ve hedef klasörü doldur.")
            return
        mevcut = self.profil_ad.get()
        ad = self._ad_sor("Yedeklemeyi kaydet", "" if mevcut == YENI_ETIKET else mevcut)
        if not ad:
            return
        profiller = profilleri_yukle()
        if ad in profiller and ad != mevcut:
            if not self._onay_sor(f"“{ad}” zaten kayıtlı. Üzerine yazılsın mı?", "Üzerine yaz"):
                return
        veri["zamanlama"] = (profiller.get(ad) or {}).get("zamanlama")
        profiller[ad] = veri
        try:
            profilleri_kaydet(profiller)
        except OSError as e:
            self.profil_bilgi.set(f"Kaydedilemedi: {e}")
            return
        self.profil_ad.set(ad)
        self._profil_menusu_yenile()
        self._profil_bilgi_guncelle()
        self._yaz(f"[✓] Yedekleme kaydedildi: {ad}\n", GREEN)

    def _profil_sil(self):
        ad = self.profil_ad.get()
        if ad == YENI_ETIKET:
            return
        if not self._onay_sor(f"“{ad}” kayıtlı yedeklemesi (varsa zamanlaması da) silinsin mi?"):
            return
        profiller = profilleri_yukle()
        if (profiller.get(ad) or {}).get("zamanlama"):
            zamanlamayi_kapat(ad)
        profiller.pop(ad, None)
        try:
            profilleri_kaydet(profiller)
        except OSError as e:
            self.profil_bilgi.set(f"Silinemedi: {e}")
            return
        self.profil_ad.set(YENI_ETIKET)
        self._profil_menusu_yenile()
        self._profil_bilgi_guncelle()
        self._yaz(f"[✓] Yedekleme silindi: {ad}\n", GREEN)

    def _zamanla_dialog(self):
        ad = self.profil_ad.get()
        profiller = profilleri_yukle()
        if ad == YENI_ETIKET or ad not in profiller:
            self.profil_bilgi.set("Önce yedeklemeyi “Kaydet” ile kaydet, sonra zamanla.")
            return
        if getattr(self, "_zamanla_pencere", None) and self._zamanla_pencere.winfo_exists():
            self._zamanla_pencere.lift()
            return
        z = profiller[ad].get("zamanlama") or {}
        dlg = tk.Toplevel(self.root)
        self._zamanla_pencere = dlg
        dlg.title(f"Zamanla — {ad}")
        dlg.configure(bg=BG)
        dlg.resizable(False, False)
        dlg.transient(self.root)

        sik = tk.StringVar(value=z.get("sikllik", "gunluk"))
        saat = tk.IntVar(value=int(z.get("saat", 23)))
        dak = tk.IntVar(value=int(z.get("dakika", 0)))
        gun = tk.StringVar(value=GUN_EN_TR.get(z.get("gun"), "Pazartesi"))
        ay = tk.IntVar(value=int(z.get("ay_gunu", 1)))
        durum = tk.StringVar(value=zamanlama_ozeti(z or None))

        kart = tk.Frame(dlg, bg=BG2, padx=14, pady=12)
        kart.pack(fill=tk.X, padx=14, pady=(14, 6))
        tk.Label(kart, text="SIKLIK", bg=BG2, fg=ACCENT,
                 font=("Sans", 8, "bold")).grid(row=0, column=0, columnspan=4, sticky="w")
        for i, (anahtar, etiket) in enumerate(SIKLIKLAR):
            tk.Radiobutton(kart, text=etiket, value=anahtar, variable=sik,
                           bg=BG2, fg=FG, selectcolor=BG3, activebackground=BG2,
                           activeforeground=FG, highlightthickness=0, borderwidth=0,
                           font=("Sans", 9)).grid(row=1, column=i, sticky="w", padx=(0, 12), pady=(4, 0))

        def spin(ust, var, alt, ust_sinir):
            sb = tk.Spinbox(ust, from_=alt, to=ust_sinir, textvariable=var, width=4, wrap=True,
                            bg=BG3, fg=FG, insertbackground=ACCENT, buttonbackground=BORDER,
                            relief=tk.FLAT, highlightthickness=1, highlightbackground=BORDER,
                            highlightcolor=ACCENT, disabledbackground=BG2, disabledforeground=FG2,
                            font=("Sans", 9))
            sb.pack(side=tk.LEFT)
            return sb

        zr = tk.Frame(kart, bg=BG2)
        zr.grid(row=2, column=0, columnspan=4, sticky="w", pady=(12, 0))
        tk.Label(zr, text="Saat:", bg=BG2, fg=FG2, font=("Sans", 9)).pack(side=tk.LEFT, padx=(0, 4))
        spin(zr, saat, 0, 23)
        tk.Label(zr, text=":", bg=BG2, fg=FG2).pack(side=tk.LEFT, padx=2)
        spin(zr, dak, 0, 59)
        tk.Label(zr, text="Gün:", bg=BG2, fg=FG2, font=("Sans", 9)).pack(side=tk.LEFT, padx=(18, 4))
        gun_menu = tk.OptionMenu(zr, gun, *[t for t, _ in GUNLER])
        gun_menu.config(bg=BG3, fg=FG, activebackground=BORDER, activeforeground=FG,
                        disabledforeground=FG2, relief=tk.FLAT, borderwidth=0,
                        highlightthickness=1, highlightbackground=BORDER,
                        font=("Sans", 9), width=9, anchor="w")
        gun_menu["menu"].config(bg=BG3, fg=FG, activebackground=ACCENT,
                                activeforeground="#1a1a1a", borderwidth=0, font=("Sans", 9))
        gun_menu.pack(side=tk.LEFT)
        tk.Label(zr, text="Ayın günü:", bg=BG2, fg=FG2, font=("Sans", 9)).pack(side=tk.LEFT, padx=(18, 4))
        ay_spin = spin(zr, ay, 1, 28)

        def alanlari_guncelle(*_):
            s = sik.get()
            gun_menu.config(state="normal" if s in ("haftalik", "iki_haftalik") else "disabled")
            ay_spin.config(state="normal" if s == "aylik" else "disabled")

        sik.trace_add("write", alanlari_guncelle)
        alanlari_guncelle()

        tk.Label(dlg, text=("İki haftalık: zamanlayıcı her hafta çalışır, son yedekten 14 gün geçmişse yedek alır.\n"
                            "Bilgisayar o saatte kapalıysa kaçan yedek, oturum açıldığında yapılır.\n"
                            "Hedef bir ağ paylaşımıysa ve bağlı değilse yedek atlanır, bildirimle haber verilir."),
                 bg=BG, fg=FG2, font=("Sans", 8), justify="left",
                 wraplength=470).pack(anchor="w", padx=16, pady=(2, 0))

        def uygula():
            zam = {"sikllik": sik.get(), "gun": GUN_TR_EN.get(gun.get(), "Mon")}
            try:
                zam.update(saat=saat.get(), dakika=dak.get(), ay_gunu=ay.get())
                zamanlama_dogrula(zam)
            except tk.TclError:
                durum.set("Saat, dakika ve gün sayı olmalı.")
                return
            except ValueError as e:
                durum.set(str(e))
                return
            ok, mesaj = zamanlamayi_uygula(ad, zam)
            if ok:
                kayitlar = profilleri_yukle()
                if ad in kayitlar:
                    kayitlar[ad]["zamanlama"] = zam
                    profilleri_kaydet(kayitlar)
                durum.set(zamanlama_ozeti(zam) + " — etkinleştirildi.")
                self._yaz(f"[✓] {ad}: {zamanlama_ozeti(zam)}\n", GREEN)
            else:
                durum.set(f"Etkinleştirilemedi: {mesaj}")
                self._yaz(f"[HATA] Zamanlama: {mesaj}\n", RED)
            self._profil_bilgi_guncelle()

        def kapat():
            ok, mesaj = zamanlamayi_kapat(ad)
            if ok:
                kayitlar = profilleri_yukle()
                if ad in kayitlar:
                    kayitlar[ad]["zamanlama"] = None
                    profilleri_kaydet(kayitlar)
                durum.set("Zamanlama kapatıldı.")
                self._yaz(f"[✓] {ad}: zamanlama kapatıldı.\n", GREEN)
            else:
                durum.set(f"Kapatılamadı: {mesaj}")
            self._profil_bilgi_guncelle()

        bf = tk.Frame(dlg, bg=BG)
        bf.pack(fill=tk.X, padx=14, pady=(10, 4))
        bf.columnconfigure(0, weight=1)
        self._button(bf, "Etkinleştir", uygula, accent=True).grid(
            row=0, column=0, sticky="ew", padx=(0, 6))
        self._button(bf, "Zamanlamayı kapat", kapat).grid(row=0, column=1, padx=(0, 6))
        self._button(bf, "Kapat", dlg.destroy).grid(row=0, column=2)
        tk.Label(dlg, textvariable=durum, bg=BG, fg=ORANGE, font=("Sans", 9),
                 wraplength=470, justify="left").pack(anchor="w", padx=16, pady=(4, 14))

    # ── AĞ PAYLAŞIMI (SMB/CIFS) BAĞLA / AYIR ───────────
    def _ag_dialog(self):
        if getattr(self, "_ag_pencere", None) and self._ag_pencere.winfo_exists():
            self._ag_pencere.lift()
            return
        dlg = tk.Toplevel(self.root)
        self._ag_pencere = dlg
        dlg.title("Ağ paylaşımı")
        dlg.configure(bg=BG)
        dlg.resizable(False, False)
        dlg.transient(self.root)

        sunucu    = tk.StringVar(value="")
        paylasim  = tk.StringVar(value="")
        kullanici = tk.StringVar(value="")
        sifre     = tk.StringVar(value="")
        baglama   = tk.StringVar(value="/mnt/nas")
        durum     = tk.StringVar(value="")

        kart = tk.Frame(dlg, bg=BG2, padx=14, pady=12)
        kart.pack(fill=tk.X, padx=14, pady=(14, 6))
        kart.columnconfigure(1, weight=1)

        alanlar = [("Sunucu:", sunucu, False), ("Paylaşım:", paylasim, False),
                   ("Kullanıcı:", kullanici, False), ("Şifre:", sifre, True),
                   ("Bağlama klasörü:", baglama, False)]
        for i, (etiket, var, gizli) in enumerate(alanlar):
            tk.Label(kart, text=etiket, bg=BG2, fg=FG2, font=("Sans", 9),
                     anchor="w").grid(row=i, column=0, sticky="w", pady=4, padx=(0, 10))
            e = self._entry(kart, var)
            e.config(width=32)
            if gizli:
                e.config(show="•")
            e.grid(row=i, column=1, sticky="ew", ipady=3)

        tk.Label(dlg, text="Şifre kaydedilmez; bağlama sırasında geçici bir dosyada tutulup hemen silinir.",
                 bg=BG, fg=FG2, font=("Sans", 8), wraplength=380,
                 justify="left").pack(anchor="w", padx=16)

        btn_fr = tk.Frame(dlg, bg=BG)
        btn_fr.pack(fill=tk.X, padx=14, pady=(10, 4))
        btn_fr.columnconfigure(0, weight=1)
        self._button(btn_fr, "Bağla", lambda: self._ag_baglan(
            sunucu, paylasim, kullanici, sifre, baglama, durum),
            accent=True).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._button(btn_fr, "Ayır", lambda: self._ag_ayir(baglama, durum)).grid(
            row=0, column=1, padx=(0, 6))
        self._button(btn_fr, "Kapat", dlg.destroy).grid(row=0, column=2)

        tk.Label(dlg, textvariable=durum, bg=BG, fg=ORANGE, font=("Sans", 9),
                 wraplength=380, justify="left").pack(anchor="w", padx=16, pady=(4, 14))

    def _yetkili_calistir(self, argv, basari_mesaji, durum, temizle=None):
        durum.set("Yetki bekleniyor…")

        def is_():
            try:
                s = subprocess.run(["pkexec"] + argv, capture_output=True, text=True)
                rc = s.returncode
                hata = (s.stderr or s.stdout or "").strip()
            except Exception as e:
                rc, hata = -1, str(e)
            finally:
                if temizle:
                    temizle()
            self.root.after(0, self._yetkili_bitti, rc, hata, basari_mesaji, durum)

        threading.Thread(target=is_, daemon=True).start()

    def _yetkili_bitti(self, rc, hata, basari_mesaji, durum):
        if rc == 0:
            durum.set(basari_mesaji)
            self._yaz(f"[✓] {basari_mesaji}\n", GREEN)
        elif rc in (126, 127):
            durum.set("Yetkilendirme iptal edildi veya reddedildi.")
        else:
            ipucu = ""
            if "not supported by the system" in hata or "No such device" in hata:
                ipucu = " Kernel güncellendiyse bilgisayarı yeniden başlat."
            elif "busy" in hata:
                ipucu = " Klasör kullanımda: terminali/dosya yöneticisini o klasörden çıkar."
            durum.set(f"Hata (kod {rc}).{ipucu}")
            self._yaz(f"[HATA] {hata}\n", RED)

    def _ag_baglan(self, sunucu, paylasim, kullanici, sifre, baglama, durum):
        s, p, k = sunucu.get().strip(), paylasim.get().strip(), kullanici.get().strip()
        pw, mnt = sifre.get(), baglama.get().strip()
        # Yazım hatalarını düzelt: "smb://", baştaki/sondaki "/" ve "\\" işaretleri
        s = re.sub(r"^(smb:)?[/\\]+", "", s).strip("/\\ ")
        p = p.replace("\\", "/").strip("/ ")
        paylasim.set(p)
        sunucu.set(s)
        if not (s and p and k and mnt):
            durum.set("Sunucu, paylaşım, kullanıcı ve bağlama klasörü boş bırakılamaz.")
            return
        if "/" in s:
            durum.set("Sunucu alanına yalnızca adres yaz (ör. 192.168.3.180).")
            return
        if not mnt.startswith("/") or os.path.normpath(mnt) in SISTEM_KLASORLERI:
            durum.set("Bağlama klasörü olarak sistem klasörü kullanılamaz. Boş bir klasör yaz (ör. /mnt/nas).")
            return
        if not shutil.which("pkexec"):
            durum.set("pkexec bulunamadı (polkit kurulu olmalı).")
            return
        if not shutil.which("mount.cifs"):
            durum.set("cifs-utils kurulu değil: sudo pacman -S cifs-utils")
            return
        if os.path.ismount(mnt):
            durum.set("Bu klasöre zaten bir paylaşım bağlı.")
            return

        fd, cred = tempfile.mkstemp(prefix="cred_", dir=os.environ.get("XDG_RUNTIME_DIR") or None)
        with os.fdopen(fd, "w") as f:
            f.write(f"username={k}\npassword={pw}\n")
        os.chmod(cred, 0o600)

        opts = f"credentials={cred},uid={os.getuid()},gid={os.getgid()}"
        betik = 'mkdir -p "$1" && mount -t cifs "$2" "$1" -o "$3"'

        def sil():
            try:
                os.remove(cred)
            except OSError:
                pass

        self._yetkili_calistir(["sh", "-c", betik, "_", mnt, f"//{s}/{p}", opts],
                               f"Bağlandı: {mnt}", durum, temizle=sil)

    def _ag_ayir(self, baglama, durum):
        mnt = baglama.get().strip()
        if self.islemiyor:
            durum.set("Yedekleme sürerken paylaşım ayrılamaz.")
            return
        if not os.path.ismount(mnt):
            durum.set("Bu klasöre bağlı bir paylaşım yok.")
            return
        self._yetkili_calistir(["umount", mnt], f"Ayrıldı: {mnt}", durum)

    def _log_sec(self):
        yol = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Metin dosyası", "*.txt"), ("Tüm dosyalar", "*.*")],
            initialfile="Yedek_Raporu.txt")
        if yol:
            self.log_yolu.set(yol)

    def _log_toggle(self):
        self.log_entry.config(state=tk.NORMAL if self.opt_log.get() else tk.DISABLED)

    def _komut_olustur(self):
        log = self.log_yolu.get().strip() if self.opt_log.get() else None
        return rsync_komutu(self.kaynak_yol.get(), self.hedef_yol.get(),
                            self.opt_mir.get(), self.opt_fft.get(), self.opt_z.get(),
                            self.opt_eta.get(), log)

    def _baslat(self):
        if self.islemiyor:
            return
        try:
            komut = self._komut_olustur()
        except ValueError as e:
            self._yaz(f"[HATA] {e}\n", RED)
            return
        self.islemiyor = True
        self.basla_btn.config(state=tk.DISABLED, bg=ACCENT2)
        self.dur_btn.config(state=tk.NORMAL)
        self.durum_var.set("Yedekleme devam ediyor…")
        self._yaz(f"\n{'='*60}\n[{datetime.now():%Y-%m-%d %H:%M:%S}] Başlatılıyor\n")
        self._yaz("Komut: " + " ".join(f'"{k}"' if " " in k else k for k in komut) + "\n")
        self._yaz(f"{'='*60}\n")
        threading.Thread(target=self._calistir, args=(komut,), daemon=True).start()

    def _calistir(self, komut):
        try:
            self.proses = subprocess.Popen(
                komut, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0)
            fd = self.proses.stdout.fileno()
            tampon = ""
            self._dosya_say = ""
            self._ilr_aktif = False
            self._durum_taban = "Çalışıyor"
            self._basla_zaman = self._son_cikti = time.time()
            self.root.after(0, self._izle)
            self.sayac = {"yeni": 0, "guncel": 0, "silinen": 0, "toplam": None, "veri": None}
            while True:
                veri = os.read(fd, 4096)
                if not veri:
                    break
                self._son_cikti = time.time()
                tampon += veri.decode("utf-8", "replace")
                while True:
                    m = re.search(r"[\r\n]", tampon)
                    if not m:
                        break
                    satir = tampon[:m.start()]
                    tampon = tampon[m.end():]
                    if not satir.strip():
                        continue
                    # rsync ilerleme satırı \r ile gelir → durum çubuğuna yaz
                    if re.match(r"^\s*[\d.,]+[KMGTkmgt]?B?\s+\d+%", satir):
                        self.root.after(0, self._ilerleme, satir.strip())
                        continue
                    m = re.match(r"^Number of files: ([\d.,]+)(?: \(reg: ([\d.,]+))?", satir)
                    if m:
                        self.sayac["toplam"] = int((m.group(2) or m.group(1)).replace(",", "").replace(".", ""))
                        continue
                    m = re.match(r"^Total transferred file size: (.+?) bytes", satir)
                    if m:
                        self.sayac["veri"] = m.group(1)
                        continue
                    if re.match(r"^(Number of |Total file size|Literal data|Matched data|File list |Total bytes )", satir):
                        continue   # ayrıntılı istatistik: rapora yalnızca gerekenler alınır
                    cozum = satir_coz(satir)
                    if cozum:
                        tur, ad = cozum
                        self.sayac[tur] += 1
                        simge, renk = {"yeni": ("+ yeni      ", GREEN),
                                       "guncel": ("~ güncel    ", ORANGE),
                                       "silinen": ("- silindi   ", RED)}[tur]
                        self.root.after(0, self._yaz_dosya, simge + ad, renk, tur != "silinen")
                    elif re.match(r"^[<>ch.]d\S{9} ", satir):
                        self.root.after(0, self._yaz, "  klasör     " + satir[12:] + "\n", FG2)
                    else:
                        self.root.after(0, self._yaz, satir + "\n")
            self.proses.wait()
            self.root.after(0, self._bitis, self.proses.returncode)
        except Exception as e:
            self.root.after(0, self._yaz, f"[HATA] {e}\n", RED)
            self.root.after(0, self._bitis, -99)

    def _yaz_dosya(self, metin, renk, ilerlemeli):
        """Dosya satırını yazar; ilerlemeli ise satırın sonu canlı yüzde için işaretlenir."""
        self._yaz(metin, renk)
        self.cikti.config(state=tk.NORMAL)
        if ilerlemeli:
            self.cikti.mark_set("ilr", "end-1c")
            self.cikti.mark_gravity("ilr", tk.LEFT)
            self.cikti.tag_configure("ilr_gri", foreground=FG2)
            self.cikti.insert("ilr", "   başlıyor… (NAS yanıtı bekleniyor)", "ilr_gri")
            self._ilr_aktif = True
        else:
            self._ilr_aktif = False
        self.cikti.insert(tk.END, "\n")
        self.cikti.config(state=tk.DISABLED)

    def _ilerleme(self, satir):
        m = re.match(r"^\s*([\d.,]+\S*?)\s+(\d+)%\s+(\S+/s)\s+(\S+)(?:.*to-chk=(\d+)/(\d+))?", satir)
        if not m:
            return
        boyut, yuzde, hiz, sure, kalan, toplam = m.groups()
        # Satırın sonundaki yüzde: dosya kopyalandıkça canlı güncellenir
        if getattr(self, "_ilr_aktif", False):
            tam = int(yuzde) >= 100
            self.cikti.config(state=tk.NORMAL)
            self.cikti.delete("ilr", "ilr lineend")
            self.cikti.tag_configure("ilr_gri", foreground=FG2)
            self.cikti.tag_configure("ilr_yesil", foreground=GREEN)
            self.cikti.insert("ilr", f"   %{yuzde}  {boyut}  {hiz}", "ilr_yesil" if tam else "ilr_gri")
            self.cikti.config(state=tk.DISABLED)
            if tam:
                self._ilr_aktif = False
        c = getattr(self, "sayac", None) or {}
        if kalan is not None and toplam and int(toplam):
            self._dosya_say = f"  ·  işlenen {int(toplam) - int(kalan)}/{toplam}"
        self._durum_taban = (f"%{yuzde}  ·  {hiz}  ·  kalan {sure}{getattr(self, '_dosya_say', '')}"
                             f"   |   yeni {c.get('yeni', 0)} · güncellenen {c.get('guncel', 0)}"
                             f" · silinen {c.get('silinen', 0)}")

    @staticmethod
    def _yazma_kuyrugu_mb():
        """Bellekte olup henüz diske/NAS'a yazılmamış veri (MB). Okunamazsa None."""
        try:
            toplam = 0
            with open("/proc/meminfo") as f:
                for satir in f:
                    if satir.startswith(("Dirty:", "Writeback:")):
                        toplam += int(satir.split()[1])
            return toplam / 1024
        except (OSError, ValueError):
            return None

    def _izle(self):
        """Çalışırken her saniye durum çubuğunu tazeler: geçen süre, yazma kuyruğu, sessizlik."""
        if not self.islemiyor:
            return
        gecen = int(time.time() - self._basla_zaman)
        sessiz = int(time.time() - self._son_cikti)
        parca = [self._durum_taban, f"geçen {gecen // 60}:{gecen % 60:02d}"]
        kuyruk = self._yazma_kuyrugu_mb()
        if kuyruk is not None and kuyruk >= 1:
            parca.append(f"NAS/diske yazılmayı bekleyen {kuyruk:.0f} MB")
        if sessiz >= 5:
            parca.append(f"{sessiz} sn çıktı yok (tarama ya da yazma sürüyor)")
        self.durum_var.set("  ·  ".join(parca))
        self.root.after(1000, self._izle)

    def _rapor_yaz(self):
        c = getattr(self, "sayac", None)
        if not c:
            return
        toplam = c["yeni"] + c["guncel"] + c["silinen"]
        satirlar = [("Yeni (hedefe eklendi)", c["yeni"], GREEN),
                    ("Güncellenen (değişti)", c["guncel"], ORANGE)]
        if c.get("toplam") is not None:
            satirlar.append(("Değişmeyen (aynı kaldı)", max(0, c["toplam"] - c["yeni"] - c["guncel"]), FG))
        satirlar.append(("Silinen (hedefte fazlaydı)", c["silinen"], RED))
        if c.get("veri"):
            satirlar.append(("Aktarılan veri", f"{c['veri']}B", FG2))
        gen = max(len(a) for a, _, _ in satirlar)
        self._yaz("\n── RAPOR ─────────────────────────\n", FG2)
        for ad, deger, renk in satirlar:
            self._yaz(f"  {ad.ljust(gen)} : {deger}\n", renk)
        if toplam == 0:
            self._yaz("  Değişiklik yok: hedef kaynakla aynı.\n", FG2)
        self._yaz("──────────────────────────────────\n", FG2)

    def _durdur(self):
        if self.proses and self.islemiyor:
            self.proses.terminate()
            self._yaz("\n[DURDURULDU] Kullanıcı tarafından iptal edildi.\n", ORANGE)

    def _bitis(self, kod):
        self.islemiyor = False
        self.proses    = None
        self.basla_btn.config(state=tk.NORMAL, bg=ACCENT)
        self.dur_btn.config(state=tk.DISABLED)
        if kod in (0, 24):   # 24: kopyalama sırasında kaybolan dosyalar, zararsız
            self.durum_var.set(f"Başarıyla tamamlandı (kod {kod}).")
            self._yaz(f"\n[✓] Senkronizasyon tamamlandı (çıkış kodu {kod}).\n", GREEN)
            self._rapor_yaz()
        elif kod < 0:
            self.durum_var.set("Durduruldu / hata oluştu.")
        else:
            self.durum_var.set(f"Hata ile bitti (kod {kod}).")
            self._yaz(f"\n[!] Yedekleme hata ile bitti (çıkış kodu {kod}).\n", RED)
        if self.opt_log.get() and self.log_yolu.get().strip():
            self._yaz(f"[i] Log: {self.log_yolu.get().strip()}\n", FG2)

    def _yaz(self, metin, renk=None):
        self.cikti.config(state=tk.NORMAL)
        if renk:
            tag = f"c{renk.replace('#','')}"
            self.cikti.tag_configure(tag, foreground=renk)
            self.cikti.insert(tk.END, metin, tag)
        else:
            self.cikti.insert(tk.END, metin)
        self.cikti.see(tk.END)
        self.cikti.config(state=tk.DISABLED)

    def _temizle(self):
        self.cikti.config(state=tk.NORMAL)
        self.cikti.delete("1.0", tk.END)
        self.cikti.config(state=tk.DISABLED)
        self.durum_var.set("Hazır.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.exit(cli(sys.argv[1:]))
    if tk is None:
        sys.exit("tkinter bulunamadı. Kur: sudo pacman -S tk")
    kok = tk.Tk()
    RobotCopyGUI(kok)
    kok.mainloop()
