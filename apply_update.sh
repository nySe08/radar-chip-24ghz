#!/usr/bin/env bash
# apply_update.sh - commit and push the "tape-out-ready" update of radar-chip-24ghz.
#
# Run from the repository root (the folder that contains .git), after unzipping the update there:
#     unzip -o radar_repo_update.zip -d .
#     bash apply_update.sh
#
# Nothing is committed or pushed until you confirm.
set -euo pipefail
[ -d .git ] || { echo "Run this from the repository root (the folder that contains .git)."; exit 1; }

echo "== 1. Folders the new README refers to"
missing=0
for d in model lo_core lna rx_tile tx tx/post_layout tx_ch/layout signoff floorplan phased_chip cdlsim top docs/img; do
  if [ -d "$d" ]; then echo "   ok       $d/"; else echo "   MISSING  $d/"; missing=1; fi
done
[ "$missing" = 1 ] && echo "   -> Add the missing folder(s), or delete their line from README.md (Repository layout) before confirming."

echo "== 2. Ignore rules for generated files"
touch .gitignore
add_ignore() { grep -qxF "$1" .gitignore || echo "$1" >> .gitignore; }
for p in "__pycache__/" "*.pyc" "tx/_tx.spice" "tx/tx_out.txt" "tx/tx_wave.txt" "tx/.spiceinit" "floorplan/*.gds" "tx/post_layout/_*.spice" "tx/post_layout/*.txt" "tx/post_layout/.spiceinit" "drc_*/" "lvs_*/" "pex_out/"; do
  add_ignore "$p"
done
echo "   .gitignore updated"

echo "== 3. Large untracked files (GitHub rejects files over 100 MB)"
big=$(git ls-files --others --exclude-standard | while IFS= read -r f; do
        [ -f "$f" ] && [ "$(du -k "$f" | cut -f1)" -gt 20480 ] && echo "$f"; done || true)
if [ -n "$big" ]; then
  echo "   Over 20 MB, kept out of the repository (added to .gitignore):"
  printf '%s\n' "$big" | sed 's/^/     /'
  printf '%s\n' "$big" >> .gitignore
else
  echo "   none"
fi

echo "== 4. Changes to commit"
git add -A
git status --short | head -100
echo "   ($(git status --short | wc -l | tr -d ' ') files in total)"
read -r -p "Commit and push these changes? [y/N] " answer
if [ "$answer" != "y" ] && [ "$answer" != "Y" ]; then
  echo "Stopped. The changes are staged but not committed; 'git reset' unstages them."
  exit 0
fi
git commit -q -m "TX channel v2: post-layout re-tune, sign-off passed, post-layout and stability reproduction; README: block-level sign-off end point"
git push
echo "Pushed. Suggested repository description (GitHub > About > edit):"
echo "  Open-source 24 GHz FMCW radar transceiver (2TX/4RX) in IHP SG13G2 SiGe BiCMOS: all blocks signed off with open-source EDA"
