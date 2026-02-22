"""Markdown → WeChat Official Account HTML — Write and format 公众号 articles.

Converts Markdown to WeChat-compatible HTML using (in order of preference):
1. Official md2wechat binary (geekjourneyx/md2wechat-skill) — 38+ themes, --draft
2. md2wechat.com API (when MD2WECHAT_API_KEY is set)
3. Local fallback — built-in conversion

Install binary: python3 _scripts/md2wechat_skill.py install
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))
from config import VAULT_PATH, save_note

MD2WECHAT_API_URL = "https://www.md2wechat.com/api/convert"
THEMES = [
    "default", "bytedance", "chinese", "apple", "sports", "cyber",
    "autumn-warm", "spring-fresh", "ocean-calm",
    "minimal-gold", "minimal-green", "minimal-blue", "minimal-orange",
    "minimal-red", "minimal-navy", "minimal-gray", "minimal-sky",
    "focus-gold", "focus-green", "focus-blue", "focus-orange", "focus-red",
    "focus-navy", "focus-gray", "focus-sky",
    "elegant-gold", "elegant-green", "elegant-blue", "elegant-orange",
    "elegant-red", "elegant-navy", "elegant-gray", "elegant-sky",
    "bold-gold", "bold-green", "bold-blue", "bold-orange",
    "bold-red", "bold-navy", "bold-gray", "bold-sky",
]
BINARY_THEMES = set(THEMES)
# md2wechat.app supported themes (from API error message)
API_THEMES = {
    "default", "bytedance", "chinese", "apple", "sports", "cyber",
    "xiaomo", "shikexin",
    "minimal-gold", "minimal-green", "minimal-blue", "minimal-orange",
    "minimal-red", "minimal-navy", "minimal-gray", "minimal-sky",
    "focus-gold", "focus-green", "focus-blue", "focus-orange", "focus-red",
    "focus-navy", "focus-gray", "focus-sky",
    "elegant-gold", "elegant-green", "elegant-blue", "elegant-orange",
    "elegant-red", "elegant-navy", "elegant-gray", "elegant-sky",
    "bold-gold", "bold-green", "bold-blue", "bold-orange",
    "bold-red", "bold-navy", "bold-gray", "bold-sky",
}
# 秋日暖光 (autumn warm) → elegant-gold (warm golden tone)
THEME_ALIASES = {"autumn-warm": "elegant-gold", "秋日暖光": "elegant-gold"}


def resolve_theme_for_api(theme: str) -> str:
    """Return API-supported theme; use alias or fallback to default if not supported."""
    if theme in THEME_ALIASES:
        return THEME_ALIASES[theme]
    return theme if theme in API_THEMES else "default"


def find_md2wechat_binary() -> Optional[str]:
    """Return path to md2wechat binary if available."""
    # Check vault-local bin first
    vault_bin = Path(__file__).parent / "bin" / "md2wechat"
    if vault_bin.exists():
        return str(vault_bin)
    # Check PATH
    which = subprocess.run(["which", "md2wechat"], capture_output=True, text=True)
    if which.returncode == 0 and which.stdout.strip():
        return which.stdout.strip()
    return None


def ensure_md2wechat_config() -> bool:
    """Create ~/.config/md2wechat/config.yaml from .env if missing."""
    config_dir = Path.home() / ".config" / "md2wechat"
    config_path = config_dir / "config.yaml"
    app_id = os.getenv("WECHAT_APP_ID", "")
    app_secret = os.getenv("WECHAT_APP_SECRET", "")
    api_key = os.getenv("MD2WECHAT_API_KEY", "")
    base_url = os.getenv("MD2WECHAT_BASE_URL", "https://www.md2wechat.cn")
    if not app_id or not app_secret:
        return False
    config_dir.mkdir(parents=True, exist_ok=True)
    content = f"""wechat:
  appid: "{app_id}"
  secret: "{app_secret}"
api:
  md2wechat_key: "{api_key or ""}"
  md2wechat_base_url: "{base_url}"
  convert_mode: api
  default_theme: default
"""
    config_path.write_text(content, encoding="utf-8")
    return True


def run_binary_convert(
    md_path: Path,
    theme: str,
    output_path: Optional[Path] = None,
    draft: bool = False,
    cover_path: Optional[str] = None,
) -> Tuple[bool, str, str]:
    """Run md2wechat binary. Returns (success, html_or_msg, stderr)."""
    binary = find_md2wechat_binary()
    if not binary:
        return False, "", "md2wechat binary not found"
    ensure_md2wechat_config()
    env = os.environ.copy()
    env["WECHAT_APPID"] = os.getenv("WECHAT_APP_ID", "")
    env["WECHAT_SECRET"] = os.getenv("WECHAT_APP_SECRET", "")
    env["MD2WECHAT_API_KEY"] = os.getenv("MD2WECHAT_API_KEY", "")
    cmd = [binary, "convert", str(md_path), "--theme", theme]
    if draft and cover_path and Path(cover_path).exists():
        cmd.extend(["--draft", "--cover", str(Path(cover_path).resolve())])
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=120, cwd=str(VAULT_PATH))
        return result.returncode == 0, result.stdout, result.stderr
    out = output_path or Path(tempfile.mktemp(suffix=".html"))
    cmd.extend(["-o", str(out)])
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60, cwd=str(VAULT_PATH))
    if result.returncode != 0:
        return False, result.stdout, result.stderr
    html = out.read_text(encoding="utf-8") if out.exists() else ""
    if not output_path and out.exists():
        out.unlink(missing_ok=True)
    return True, html, result.stderr


def convert_markdown_to_wechat(markdown: str, theme: str = "default") -> dict:
    """Convert Markdown to WeChat HTML via md2wechat API or local fallback.

    Returns: {success, html, word_count, estimated_read_time_min, theme, error}
    """
    api_key = os.getenv("MD2WECHAT_API_KEY", "")
    if not api_key:
        # Fallback to local conversion
        html = _local_markdown_to_wechat_html(markdown)
        word_count = len(markdown)
        return {
            "success": True,
            "html": html,
            "word_count": word_count,
            "estimated_read_time_min": max(1, word_count // 400),
            "theme": "default",
            "error": None,
        }

    try:
        import requests
        # Normalize theme: API supports default, bytedance, chinese, apple, sports
        api_themes = {"default", "bytedance", "chinese", "apple", "sports"}
        theme_param = theme if theme in api_themes else "default"
        r = requests.post(
            MD2WECHAT_API_URL,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key,
            },
            json={"markdown": markdown, "theme": theme_param},
            timeout=30,
        )
        data = r.json()
        if data.get("code") == 0 and "data" in data:
            d = data["data"]
            return {
                "success": True,
                "html": d.get("html", ""),
                "word_count": d.get("wordCount", 0),
                "estimated_read_time_min": d.get("estimatedReadTime", 1),
                "theme": d.get("theme", theme_param),
                "error": None,
            }
        return {
            "success": False,
            "html": "",
            "word_count": 0,
            "estimated_read_time_min": 0,
            "theme": theme,
            "error": data.get("msg", str(data)),
        }
    except Exception as e:
        html = _local_markdown_to_wechat_html(markdown)
        return {
            "success": True,
            "html": html,
            "word_count": len(markdown),
            "estimated_read_time_min": max(1, len(markdown) // 400),
            "theme": "default",
            "error": f"API failed, used local: {e}",
        }


def _local_markdown_to_wechat_html(md: str) -> str:
    """Local Markdown → WeChat HTML (fallback when no API key)."""
    try:
        from wechat_official_publish import markdown_to_wechat_html
        body = markdown_to_wechat_html(md)
    except ImportError:
        body = _minimal_md_to_html(md)
    return f'<section style="font-size:16px;line-height:1.8;color:#333;max-width:750px;">\n{body}\n</section>'


def _minimal_md_to_html(md: str) -> str:
    """Minimal markdown-to-HTML when wechat_official_publish not available."""
    import html
    lines = md.split("\n")
    out = []
    for line in lines:
        s = line.strip()
        if not s:
            out.append("<p><br/></p>")
            continue
        if s.startswith("#"):
            n = 0
            while n < len(s) and s[n] == "#":
                n += 1
            n = min(n, 6)
            t = s[n:].strip()
            out.append(f"<h{n}>{html.escape(t)}</h{n}>")
            continue
        if s.startswith(">"):
            t = s[1:].strip()
            out.append(f"<blockquote><p>{html.escape(t)}</p></blockquote>")
            continue
        t = html.escape(s)
        t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)
        out.append(f"<p>{t}</p>")
    return "\n".join(out)


def copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard."""
    try:
        if sys.platform == "darwin":
            proc = subprocess.Popen(
                ["pbcopy"],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
        elif sys.platform == "linux":
            for cmd in [["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]]:
                try:
                    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                    break
                except FileNotFoundError:
                    continue
            else:
                return False
        else:
            return False
        proc.communicate(input=text.encode("utf-8"), timeout=5)
        return proc.returncode == 0
    except Exception:
        return False


def upload_wechat_draft(title: str, content: str, author: str = "", digest: str = "", thumb_media_id: str = "") -> dict:
    """Create WeChat Official Account draft via API.

    Returns: {success, draft_id, jump_url, error}
    """
    app_id = os.getenv("WECHAT_APP_ID", "")
    app_secret = os.getenv("WECHAT_APP_SECRET", "")
    access_token = os.getenv("WECHAT_ACCESS_TOKEN", "")

    if not access_token and (not app_id or not app_secret):
        return {"success": False, "draft_id": "", "jump_url": "", "error": "Set WECHAT_ACCESS_TOKEN or (WECHAT_APP_ID + WECHAT_APP_SECRET) in .env"}

    if not thumb_media_id:
        return {"success": False, "draft_id": "", "jump_url": "", "error": "Cover image required. Upload via WeChat API first to get thumb_media_id."}

    try:
        import requests
        if not access_token:
            r = requests.get(
                f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
            )
            d = r.json()
            if "access_token" not in d:
                return {"success": False, "draft_id": "", "jump_url": "", "error": str(d)}
            access_token = d["access_token"]

        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
        payload = {
            "articles": [{
                "title": title[:32],
                "author": (author or "")[:16],
                "digest": (digest or "")[:120],  # WeChat limit: 120 chars
                "content": content,
                "thumb_media_id": thumb_media_id,
                "need_open_comment": 0,
                "only_fans_can_comment": 0,
            }]
        }
        # Use ensure_ascii=False so smart quotes, em dashes, etc. render correctly in WeChat
        r = requests.post(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        d = r.json()
        if "media_id" in d:
            return {
                "success": True,
                "draft_id": d["media_id"],
                "jump_url": "https://mp.weixin.qq.com",
                "error": None,
            }
        return {
            "success": False,
            "draft_id": "",
            "jump_url": "",
            "error": f"{d.get('errcode', '')} {d.get('errmsg', str(d))}",
        }
    except Exception as e:
        return {"success": False, "draft_id": "", "jump_url": "", "error": str(e)}


def upload_cover_to_wechat(image_path: str) -> dict:
    """Upload cover image to WeChat permanent material. Returns media_id for draft thumb_media_id.

    Returns: {success, media_id, error}
    """
    path = Path(image_path)
    if not path.is_absolute():
        path = VAULT_PATH / path
    if not path.exists():
        return {"success": False, "media_id": "", "error": f"File not found: {path}"}

    app_id = os.getenv("WECHAT_APP_ID", "")
    app_secret = os.getenv("WECHAT_APP_SECRET", "")
    access_token = os.getenv("WECHAT_ACCESS_TOKEN", "")

    if not access_token and (not app_id or not app_secret):
        return {"success": False, "media_id": "", "error": "Set WECHAT credentials in .env"}

    try:
        import requests
        if not access_token:
            r = requests.get(
                f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
            )
            d = r.json()
            if "access_token" not in d:
                return {"success": False, "media_id": "", "error": str(d)}
            access_token = d["access_token"]

        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image"
        mime = "image/jpeg" if path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
        with open(path, "rb") as f:
            r = requests.post(url, files={"media": (path.name, f, mime)})
        d = r.json()
        if "media_id" in d and d.get("errcode", 0) == 0:
            return {"success": True, "media_id": d["media_id"], "error": None}
        return {"success": False, "media_id": "", "error": d.get("errmsg", str(d))}
    except Exception as e:
        return {"success": False, "media_id": "", "error": str(e)}


def upload_image_to_wechat(image_path: str) -> dict:
    """Upload image to WeChat media library. Returns WeChat asset URL or media_id.

    Returns: {success, url, media_id, error}
    """
    path = Path(image_path)
    if not path.is_absolute():
        path = VAULT_PATH / path
    if not path.exists():
        return {"success": False, "url": "", "media_id": "", "error": f"File not found: {path}"}

    app_id = os.getenv("WECHAT_APP_ID", "")
    app_secret = os.getenv("WECHAT_APP_SECRET", "")
    access_token = os.getenv("WECHAT_ACCESS_TOKEN", "")

    if not access_token and (not app_id or not app_secret):
        return {"success": False, "url": "", "media_id": "", "error": "Set WECHAT credentials in .env"}

    try:
        import requests
        if not access_token:
            r = requests.get(
                f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
            )
            d = r.json()
            if "access_token" not in d:
                return {"success": False, "url": "", "media_id": "", "error": str(d)}
            access_token = d["access_token"]

        # Upload to get URL for article body images (uploadimg API)
        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={access_token}"
        mime = "image/jpeg" if path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
        with open(path, "rb") as f:
            r = requests.post(url, files={"media": (path.name, f, mime)})
        d = r.json()
        if "url" in d and d.get("errcode", 0) == 0:
            return {"success": True, "url": d["url"], "media_id": "", "error": None}
        return {"success": False, "url": "", "media_id": "", "error": d.get("errmsg", str(d))}
    except Exception as e:
        return {"success": False, "url": "", "media_id": "", "error": str(e)}


def generate_digest_from_html(html: str, max_len: int = 120) -> str:
    """Extract plain text from HTML and truncate to max_len chars (WeChat limit). No trailing '...'."""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_len:
        return text
    return text[:max_len]


def parse_note(filepath: Path) -> dict:
    """Read note and extract frontmatter + body."""
    content = filepath.read_text(encoding="utf-8")
    frontmatter = {}
    body = content
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if fm_match:
        for line in fm_match.group(1).splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                frontmatter[key.strip()] = val.strip().strip('"').strip("'")
        body = content[fm_match.end():]

    title = frontmatter.get("title", "")
    if not title:
        m = re.match(r"^#\s+(.+)$", body, re.MULTILINE)
        if m:
            title = m.group(1).strip()
            body = body[m.end():].lstrip("\n")

    body = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"[\2](\1)", body)
    body = re.sub(r"\[\[([^\]]+)\]\]", r"[\1](\1)", body)
    body = re.sub(r"> \[!(\w+)\][+-]?\s*", "> ", body)

    return {
        "title": title or filepath.stem,
        "author": frontmatter.get("author", ""),
        "digest": frontmatter.get("digest", ""),
        "body": body.strip(),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Markdown → WeChat Official Account HTML — write and format 公众号 articles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/md2wechat_skill.py note.md                    # Convert, copy to clipboard
  python3 _scripts/md2wechat_skill.py note.md --theme bytedance   # Use theme
  python3 _scripts/md2wechat_skill.py note.md --save              # Save HTML
  python3 _scripts/md2wechat_skill.py note.md --api --thumb ID   # Create draft via API
  python3 _scripts/md2wechat_skill.py upload-image path/to.png    # Upload image, get URL
  python3 _scripts/md2wechat_skill.py --theme chinese              # Read markdown from stdin
""",
    )
    parser.add_argument("note", nargs="?", help="Path to note (or omit to read from stdin)")
    parser.add_argument("--theme", type=str, default="default", choices=THEMES, help="Visual theme")
    parser.add_argument("--save", action="store_true", help="Save HTML to Sources/")
    parser.add_argument("--no-copy", action="store_true", help="Do not copy to clipboard")
    parser.add_argument("--api", action="store_true", help="Create draft via WeChat API")
    parser.add_argument("--thumb", type=str, default="", help="Cover image thumb_media_id (for --api, Python fallback)")
    parser.add_argument("--cover", type=str, default="", help="Cover image file path (for --api when using binary)")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    # Subcommand: install
    if args.note and args.note.lower() == "install":
        script = Path(__file__).parent / "install_md2wechat.sh"
        bin_dir = Path.home() / ".local" / "bin"
        result = subprocess.run(["bash", str(script), str(bin_dir)], cwd=str(Path(__file__).parent))
        if result.returncode == 0:
            print(f"\n✓ Add to PATH: export PATH=\"{bin_dir}:$PATH\"")
            print("  Or add to ~/.zshrc / ~/.bashrc")
        sys.exit(result.returncode)

    # Subcommand: upload-image IMAGE_PATH
    if args.note and args.note.lower() == "upload-image":
        if len(sys.argv) < 3:
            sys.exit("Usage: md2wechat_skill.py upload-image IMAGE_PATH")
        img_path = sys.argv[2]
        result = upload_image_to_wechat(img_path)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif result["success"]:
            print(f"✓ URL: {result['url']}")
        else:
            print(f"Error: {result['error']}")
        return

    if args.note:
        note_path = Path(args.note)
        if not note_path.is_absolute():
            note_path = VAULT_PATH / note_path
        if not note_path.exists():
            sys.exit(f"Error: Note not found: {note_path}")
        note = parse_note(note_path)
        markdown = note["body"]
        title = note["title"]
        author = note.get("author", "")
        digest = note.get("digest", "")
        md_path = note_path  # Full note path for binary (binary needs full markdown file)
        # Binary needs the raw file; we use body for Python. For binary, pass the note file.
    else:
        markdown = sys.stdin.read()
        note = {"title": "Untitled", "author": "", "digest": ""}
        title = note["title"]
        author = note["author"]
        digest = note["digest"]
        md_path = None

    # Prefer binary when available
    binary = find_md2wechat_binary()
    if binary and md_path is None and markdown:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(markdown)
            md_path = Path(f.name)
        _cleanup_tmp = md_path
    else:
        _cleanup_tmp = None

    use_binary = binary is not None and md_path is not None
    use_binary_draft = use_binary and args.api and args.cover and Path(args.cover).exists()

    try:
        if use_binary_draft:
            # Use binary for convert only; Python for draft (avoids md2wechat digest 120-char bug)
            # Pass body-only (no frontmatter) so YAML doesn't render in article
            with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tmp_md:
                tmp_md.write(note["body"])
                tmp_md_path = Path(tmp_md.name)
            with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
                tmp_path = Path(tmp.name)
            theme = resolve_theme_for_api(args.theme)
            if theme != args.theme:
                print(f"使用主题: {theme} ({args.theme} → {theme})")
            try:
                ok, html, err = run_binary_convert(tmp_md_path, theme, output_path=tmp_path, draft=False)
            finally:
                tmp_md_path.unlink(missing_ok=True)
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
            if not ok or not html:
                print(f"Error: {err or 'Conversion failed'}")
                return
            if "<body" in html:
                body_match = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
                if body_match:
                    html = body_match.group(1).strip()
            cover_result = upload_cover_to_wechat(args.cover)
            if not cover_result["success"]:
                print(f"Error: {cover_result['error']}")
                return
            digest_val = (digest or "").strip()
            if len(digest_val) > 120:
                digest_val = digest_val[:120]
            elif not digest_val:
                digest_val = generate_digest_from_html(html)
            draft = upload_wechat_draft(title, html, author, digest_val, cover_result["media_id"])
            if args.json:
                print(json.dumps(draft, ensure_ascii=False, indent=2))
            elif draft["success"]:
                print("✓ Draft created. Publish via mp.weixin.qq.com 草稿箱.")
            else:
                print(f"Error: {draft['error']}")
            return

        if use_binary and md_path:
            # Binary convert only
            ok, html, err = run_binary_convert(md_path, args.theme)
            if ok and html:
                # Extract body from full HTML if needed (binary may output full doc)
                if "<body" in html:
                    body_match = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
                    if body_match:
                        html = body_match.group(1).strip()
                result = {"success": True, "html": html, "word_count": len(html), "estimated_read_time_min": 1, "theme": args.theme, "error": None}
            else:
                result = None
        else:
            result = None
    finally:
        if _cleanup_tmp and _cleanup_tmp.exists():
            _cleanup_tmp.unlink(missing_ok=True)

    if result is None:
        result = convert_markdown_to_wechat(markdown, args.theme)

    if not result["success"] and not result.get("html"):
        sys.exit(f"Error: {result.get('error', 'Conversion failed')}")

    html = result["html"]
    if result.get("error"):
        print(f"Note: {result['error']}")

    if args.api:
        draft = upload_wechat_draft(title, html, author, digest, args.thumb)
        if args.json:
            print(json.dumps(draft, ensure_ascii=False, indent=2))
        elif draft["success"]:
            print(f"✓ Draft created: {draft['draft_id']}. Publish via mp.weixin.qq.com 草稿箱.")
        else:
            print(f"Error: {draft['error']}")
        return

    if not args.no_copy:
        if copy_to_clipboard(html):
            print("✓ Copied to clipboard. Paste into mp.weixin.qq.com → 新建图文消息")
        else:
            print("Could not copy. Use --save to save HTML.")

    if args.save:
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_title = re.sub(r"[^\w\s\u4e00-\u9fff-]", "", title)[:40].strip() or "article"
        path = f"Sources/WeChat Article - {safe_title} - {date_str}.html"
        full = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{title}</title></head>
<body>
{html}
</body>
</html>"""
        save_note(path, full)
        print(f"Saved: {path}")

    if args.json:
        out = {
            "success": result["success"],
            "html": html,
            "word_count": result["word_count"],
            "estimated_read_time_min": result["estimated_read_time_min"],
            "theme": result["theme"],
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
    elif args.no_copy and not args.save:
        print("\n--- HTML Content ---\n")
        print(html)


if __name__ == "__main__":
    main()
