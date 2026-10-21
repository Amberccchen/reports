# reports

Encrypted report pages served by GitHub Pages at https://amberccchen.github.io/reports/.

Every page here is ciphertext (PBKDF2-SHA256, 600k iterations + AES-256-GCM) with a
small in-browser decryptor. The key is not stored in this repo. After entering the
key once, it is kept in `sessionStorage` for that tab, so the index and every report
open without asking again.

## Adding a report

1. Put the report's plaintext files in `<src>/<slug>/` (`index.html` plus any images
   or other files it references) outside this repo, and add an entry to
   `<src>/manifest.json` (`slug`, `title`, `date`, `summary`, optional `source`).
2. Build, commit and push in one step:

   ```
   REPORTS_KEY='...' MSG='Add <slug>' tools/deploy.sh <src>
   ```

Local files referenced by a report are inlined into the encrypted page, so no
plaintext asset is ever published. Plaintext sources must never be committed here.
