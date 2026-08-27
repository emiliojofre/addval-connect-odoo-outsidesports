#!/usr/bin/env bash
# add-submodule.sh — Agrega repos como submódulos de forma interactiva
set -euo pipefail

# Colores
R='\033[0;31m'; G='\033[0;32m'; Y='\033[1;33m'; B='\033[0;34m'; C='\033[0;36m'; N='\033[0m'
info()  { echo -e "${C}ℹ ${N}$1"; }
ok()    { echo -e "${G}✔ ${N}$1"; }
warn()  { echo -e "${Y}⚠ ${N}$1"; }
err()   { echo -e "${R}✖ ${N}$1" >&2; }

# --- Verificar que estamos en un repo git ---
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  err "No estás dentro de un repositorio git."
  exit 1
fi
ROOT="$(git rev-parse --show-toplevel)"
ok "Repositorio detectado: ${B}$ROOT${N}"

# --- Normaliza una URL (acepta https o ssh) ---
detect_branch() {
  local url="$1"
  git ls-remote --symref "$url" HEAD 2>/dev/null \
    | awk '/^ref:/ {sub("refs/heads/","",$2); print $2; exit}'
}

add_one() {
  local url path branch
  read -rp "$(echo -e "${C}URL del repo (vacío para terminar): ${N}")" url
  [[ -z "$url" ]] && return 1

  # nombre por defecto = nombre del repo sin .git
  local default_name
  default_name="$(basename "$url" .git)"
  read -rp "$(echo -e "${C}Carpeta destino [${default_name}]: ${N}")" path
  path="${path:-$default_name}"

  if [[ -e "$path" ]]; then
    err "La ruta '$path' ya existe. Se omite."
    return 0
  fi

  # detectar rama por defecto del remoto
  info "Detectando rama por defecto..."
  local detected
  detected="$(detect_branch "$url" || true)"
  read -rp "$(echo -e "${C}Rama [${detected:-default}]: ${N}")" branch
  branch="${branch:-$detected}"

  info "Agregando submódulo..."
  if [[ -n "$branch" ]]; then
    git submodule add -b "$branch" "$url" "$path"
  else
    git submodule add "$url" "$path"
  fi
  ok "Submódulo '${B}$path${N}' agregado (rama: ${branch:-default})."
}

echo -e "\n${B}=== Agregar submódulos ===${N}\n"
COUNT=0
while add_one; do
  COUNT=$((COUNT+1))
  echo
done

if (( COUNT > 0 )); then
  echo
  info "Inicializando y actualizando submódulos..."
  git submodule update --init --recursive
  ok "$COUNT submódulo(s) agregados."
  echo -e "\n${Y}No olvides commitear:${N}"
  echo -e "  git commit -m \"Add ${COUNT} submodule(s)\""
else
  warn "No se agregó ningún submódulo."
fi
