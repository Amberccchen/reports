"""Build the encrypted reports site.

    REPORTS_KEY=... python3 -I tools/build.py <src_dir> <repo_dir>

<src_dir> is kept outside the repo (plaintext). It holds manifest.json and one
folder per report slug containing index.html plus any files it references
(images, css, js, json). Every referenced local file is inlined into the
report HTML, which is then encrypted (PBKDF2-SHA256 + AES-256-GCM) into
<repo_dir>/r/<slug>/index.html. The index page is encrypted the same way.
"""
import base64, html, json, mimetypes, os, re, shutil, sys
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ITER = 600000
TOOLS = os.path.dirname(os.path.abspath(__file__))
REF = re.compile(r'''(src|href)=(["'])(?!https?:|data:|#|mailto:|/)([^"']+)\2''')


def inline_refs(page, folder):
    def sub(m):
        attr, q, rel = m.groups()
        path = os.path.normpath(os.path.join(folder, rel.split("?")[0].split("#")[0]))
        if not path.startswith(os.path.normpath(folder) + os.sep) or not os.path.isfile(path):
            sys.exit(f"missing or outside-report file referenced: {rel} in {folder}")
        mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
        data = base64.b64encode(open(path, "rb").read()).decode()
        return f"{attr}={q}data:{mime};base64,{data}{q}"
    page = REF.sub(sub, page)
    return page.replace('loading="lazy"', "")


def encrypt(plaintext, key_text):
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(hashes.SHA256(), 32, salt, ITER).derive(key_text.encode())
    ct = AESGCM(key).encrypt(iv, plaintext.encode("utf-8"), None)
    b = lambda x: base64.b64encode(x).decode()
    return json.dumps({"s": b(salt), "i": b(iv), "n": ITER, "c": b(ct)})


def shell(title, payload, home):
    t = open(os.path.join(TOOLS, "shell.html"), encoding="utf-8").read()
    return (t.replace("__TITLE__", html.escape(title)).replace("__HOME__", home)
             .replace("__PAYLOAD__", payload))


def back_link(page):
    link = ('<a href="../../" style="position:fixed;top:10px;left:10px;z-index:9999;'
            'font:500 12px/1 system-ui,sans-serif;padding:6px 10px;border-radius:999px;'
            'background:rgba(29,33,37,.78);color:#fff;text-decoration:none">&larr; All reports</a>')
    return re.sub(r"(<body[^>]*>)", r"\1" + link, page, count=1) if "<body" in page else link + page


def index_page(m):
    e = html.escape
    items = "".join(
        f'<li><a href="r/{e(r["slug"])}/"><span class="d">{e(r.get("date", ""))}</span>'
        f'<b>{e(r["title"])}</b><span class="s">{e(r.get("summary", ""))}</span></a></li>'
        for r in sorted(m["reports"], key=lambda r: r.get("date", ""), reverse=True))
    return open(os.path.join(TOOLS, "index_template.html"), encoding="utf-8").read() \
        .replace("__TITLE__", e(m.get("site_title", "Reports"))).replace("__ITEMS__", items) \
        .replace("__COUNT__", str(len(m["reports"])))


def main():
    src, repo = sys.argv[1], sys.argv[2]
    key = os.environ.get("REPORTS_KEY") or sys.exit("set REPORTS_KEY")
    m = json.load(open(os.path.join(src, "manifest.json"), encoding="utf-8"))
    out = os.path.join(repo, "r")
    shutil.rmtree(out, ignore_errors=True)
    for r in m["reports"]:
        folder = os.path.join(src, r["slug"])
        page = inline_refs(open(os.path.join(folder, "index.html"), encoding="utf-8").read(), folder)
        os.makedirs(os.path.join(out, r["slug"]))
        with open(os.path.join(out, r["slug"], "index.html"), "w", encoding="utf-8") as f:
            f.write(shell(r["title"], encrypt(back_link(page), key), "../../"))
        print("built", r["slug"])
    with open(os.path.join(repo, "index.html"), "w", encoding="utf-8") as f:
        f.write(shell(m.get("site_title", "Reports"), encrypt(index_page(m), key), ""))
    open(os.path.join(repo, ".nojekyll"), "w").close()
    print("built index,", len(m["reports"]), "reports")


if __name__ == "__main__":
    main()
