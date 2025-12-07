#!/usr/bin/env bash
# Usage: ./progress.sh <current> <total>
# Example: ./progress.sh 3 10

set -u

# --- Arguments ---
current=${1:-0}
total=${2:-10}
(( total == 0 )) && total=1

# --- Terminal & Colors ---
cols=$(tput cols 2>/dev/null || echo 80)
bold=$(tput bold 2>/dev/null || printf '')
dim=$(tput dim 2>/dev/null || printf '')
reset=$(tput sgr0 2>/dev/null || printf '')
fg_green=$(tput setaf 2 2>/dev/null || printf '')
fg_cyan=$(tput setaf 6 2>/dev/null || printf '')

# --- Spinner (middle-aligned Unicode) ---
#spinner=(◐ ◓ ◑ ◒)
spinner=(- \\ \| /) # bulletproof version
#spinner=(◢ ◣ ◤ ◥)
checkmark="[✓]"

spin="[${spinner[$(( current % ${#spinner[@]} ))]}]"

# --- Helper: repeat char ---
repeat() {
  local n=$1 char=$2 out=""
  for ((i=0; i<n; i++)); do out+="$char"; done
  printf "%s" "$out"
}

# --- Progress bar sizing ---
bar_w=$(( cols - 42 ))
(( bar_w < 10 )) && bar_w=10
(( bar_w > 40 )) && bar_w=40

percent=$(( current * 100 / total ))
filled=$(( percent * bar_w / 100 ))
empty=$(( bar_w - filled ))

# --- Draw bar ---
bar_filled=$(repeat "$filled" "█")
bar_empty=$(repeat "$empty"  "░")

printf "\r${bold}${fg_cyan}%s${reset}  [" "$spin"
printf "${fg_green}%s${reset}${dim}%s${reset}" "$bar_filled" "$bar_empty"
printf "]  %3d%%  •  ${bold}Item:${reset} %02d/%02d" "$percent" "$current" "$total"

# If finished, print newline + check
if (( current == total )); then
  printf "\r${bold}${fg_green}%s${reset}  [%s]  100%%  •  ${bold}Done!%s\n" "$checkmark" "$(repeat "$bar_w" "█")" "$reset"
fi
