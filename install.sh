#!/usr/bin/env bash
# Robot Copy kurulum betiği — uygulama menüsüne ekler / kaldırır (yalnızca bu kullanıcı için).
#   ./install.sh              kur
#   ./install.sh --uninstall  kaldır
set -euo pipefail

ADI="robot-copy"
DIZIN="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN="$HOME/.local/bin/$ADI"
IKON="$HOME/.local/share/icons/hicolor/scalable/apps/$ADI.svg"
MASAUSTU="$HOME/.local/share/applications/$ADI.desktop"

if [[ "${1:-}" == "--uninstall" ]]; then
  rm -f "$BIN" "$IKON" "$MASAUSTU"
  echo "Kaldırıldı."
else
  install -Dm755 "$DIZIN/robot_copy.py" "$BIN"
  install -Dm644 "$DIZIN/assets/$ADI.svg" "$IKON"
  mkdir -p "$(dirname "$MASAUSTU")"
  cat > "$MASAUSTU" <<EOF
[Desktop Entry]
Type=Application
Name=Robot Copy
Comment=rsync ile klasör yedekleme
Exec=$BIN
Icon=$ADI
Terminal=false
Categories=Utility;
EOF
  echo "Kuruldu: $BIN"
fi

# Menü / simge önbelleklerini yenile (hangisi varsa)
command -v update-desktop-database >/dev/null && update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
command -v gtk-update-icon-cache   >/dev/null && gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
command -v kbuildsycoca6           >/dev/null && kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
