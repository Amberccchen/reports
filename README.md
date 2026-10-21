# reports

Private source of the encrypted report pages served at https://amberccchen.github.io/reports/.
This repo stays private; `tools/deploy.sh` copies only the built, encrypted pages into the
public user-site repo `Amberccchen.github.io` (folder `reports/`), which GitHub Pages serves.

Every page here is ciphertext (PBKDF2-SHA256, 600k iterations + AES-256-GCM) with a
small in-browser decryptor. The key is not stored in this repo. After entering the
key once, it is kept in `sessionStorage` for that tab, so the index and every report
open without asking again.

## Adding a report

1. Put the report's plaintext files in `<src>/<slug>/` (`index.html` plus any images
   or other files it references) outside this repo, and add an entry to
   `<src>/manifest.json` (`slug`, `title`, `date`, `summary`, optional `source`).
2. Build and publish, then commit here:

   ```
   REPORTS_KEY='...' tools/deploy.sh <src> <public-clone>
   git add -A && git commit -m "Add <slug>" && git push
   ```

Local files referenced by a report are inlined into the encrypted page, so no
plaintext asset is ever published. Plaintext sources must never be committed here.
