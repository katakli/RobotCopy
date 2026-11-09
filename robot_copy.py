#!/usr/bin/env python3
"""Robot Copy — rsync için sade, koyu temalı bir Linux arayüzü.

Klasör yedekleme / senkronizasyon; yerel, SSH veya SMB (ağ paylaşımı) hedefleri.
Lisans: MIT
"""
import tkinter as tk
from tkinter import filedialog, scrolledtext
import subprocess
import threading
import os
import re
import shutil
import tempfile
from datetime import datetime

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

PENCERE_BASLIK = "Robot Copy"
PENCERE_EN     = 720
PENCERE_BOY    = 820


class RobotCopyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(PENCERE_BASLIK)
        self.root.geometry(f"{PENCERE_EN}x{PENCERE_BOY}")
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
        self.opt_eta = tk.BooleanVar(value=True)   # --info=progress2
        self.opt_log = tk.BooleanVar(value=True)

        self.islemiyor = False
        self.proses    = None

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
                        font=("Sans", 9))

    def _button(self, master, text, command, accent=False, state=tk.NORMAL, width=None):
        kw = dict(text=text, command=command, state=state,
                  relief=tk.FLAT, cursor="hand2",
                  font=("Sans", 9), padx=12, pady=5, borderwidth=0)
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
                              font=("Sans", 9), relief=tk.FLAT, borderwidth=0)

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

        # Kaynak
        self._section(main, 1, "KAYNAK KLASÖR")
        kk = self._card(main, 2)
        self._entry(kk, self.kaynak_yol).grid(row=0, column=0, sticky="ew", ipady=4, padx=(0, 8))
        self._button(kk, "  Gözat", lambda: self._klasor_sec(self.kaynak_yol)).grid(row=0, column=1)

        # Hedef
        self._section(main, 3, "HEDEF KLASÖR")
        hk = self._card(main, 4)
        self._entry(hk, self.hedef_yol).grid(row=0, column=0, sticky="ew", ipady=4, padx=(0, 8))
        self._button(hk, "  Gözat", lambda: self._klasor_sec(self.hedef_yol)).grid(row=0, column=1)
        self._button(hk, "Ağ paylaşımı…", self._ag_dialog).grid(row=0, column=2, padx=(8, 0))
        tk.Label(hk, text="Yerel/bağlı klasör ya da uzak yol: kullanıcı@sunucu:/yol/klasör",
                 bg=BG2, fg=FG2, font=("Sans", 8)).grid(row=1, column=0, columnspan=2,
                                                          sticky="w", pady=(6, 0))

        # Seçenekler
        self._section(main, 5, "SEÇENEKLER")
        opt = self._card(main, 6)
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
        btn_card.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(10, 4))
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
                 font=("Sans", 8)).grid(row=8, column=0, columnspan=3, sticky="w", pady=(2, 4))

        # Çıktı
        self._section(main, 9, "ÇIKTI")
        main.rowconfigure(10, weight=1)
        self.cikti = scrolledtext.ScrolledText(
            main, height=20, font=("Monospace", 9),
            bg=BG2, fg=FG, insertbackground=ACCENT,
            selectbackground="#4a2800",
            relief=tk.FLAT, highlightthickness=1,
            highlightbackground=BORDER,
            state=tk.DISABLED, wrap=tk.WORD)
        self.cikti.grid(row=10, column=0, columnspan=3, sticky="nsew")

        self._log_toggle()

    def _klasor_sec(self, degisken):
        baslangic = degisken.get()
        if not os.path.isdir(baslangic):
            baslangic = os.path.expanduser("~")
        yol = filedialog.askdirectory(initialdir=baslangic)
        if yol:
            degisken.set(os.path.normpath(yol))

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
        if not (s and p and k and mnt):
            durum.set("Sunucu, paylaşım, kullanıcı ve bağlama klasörü boş bırakılamaz.")
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
        if not shutil.which("rsync"):
            raise ValueError("rsync bulunamadı. Kur: sudo pacman -S rsync")
        kaynak = self.kaynak_yol.get().strip()
        hedef  = self.hedef_yol.get().strip()
        if not kaynak or not hedef:
            raise ValueError("Kaynak ve hedef klasör boş bırakılamaz.")

        # Sondaki "/" kaynağın İÇERİĞİNİ hedefe kopyalar (robocopy davranışı)
        kaynak = os.path.join(kaynak, "")
        if not hedef.endswith("/"):
            hedef += "/"

        komut = ["rsync", "-a", "--human-readable", "--info=name1"]
        if self.opt_mir.get(): komut += ["--delete"]
        if self.opt_fft.get(): komut += ["--modify-window=2"]
        if self.opt_z.get():   komut += ["--partial"]
        if self.opt_eta.get(): komut += ["--info=progress2"]
        if self.opt_log.get() and self.log_yolu.get().strip():
            komut += [f"--log-file={self.log_yolu.get().strip()}"]
        komut += [kaynak, hedef]
        return komut

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
            while True:
                veri = os.read(fd, 4096)
                if not veri:
                    break
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
                    if "%" in satir and ("to-chk" in satir or "xfr#" in satir):
                        self.root.after(0, self.durum_var.set, satir.strip())
                    else:
                        self.root.after(0, self._yaz, satir + "\n")
            self.proses.wait()
            self.root.after(0, self._bitis, self.proses.returncode)
        except Exception as e:
            self.root.after(0, self._yaz, f"[HATA] {e}\n", RED)
            self.root.after(0, self._bitis, -99)

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
    kok = tk.Tk()
    RobotCopyGUI(kok)
    kok.mainloop()
