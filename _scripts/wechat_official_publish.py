"""Official WeChat Publisher - Publish articles to WeChat Official Account (微信公众号) quickly.

Converts Obsidian notes to WeChat-compatible format and either:
1. Copies formatted HTML to clipboard for quick paste into mp.weixin.qq.com
2. Saves HTML file for manual upload
3. (Optional) Creates draft via WeChat API if credentials are configured
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import VAULT_PATH

# WeChat Official Account format constants
WECHAT_STYLE = """
/* WeChat 公众号典型排版 - 简洁、易读 */
/* 使用语义化标签，避免过度样式（微信可能过滤部分 inline style） */
"""


def parse_note(filepath: Path) -> dict:
    """Read an Obsidian note and extract frontmatter + body."""
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
        heading_match = re.match(r"^#\s+(.+)$", body, re.MULTILINE)
        if heading_match:
            title = heading_match.group(1).strip()
            # Remove H1 from body (WeChat uses separate title field)
            body = body[heading_match.end():].lstrip("\n")

    author = frontmatter.get("author", "")
    digest = frontmatter.get("digest", "")

    # Convert Obsidian wikilinks to standard markdown
    body = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"[\2](\1)", body)
    body = re.sub(r"\[\[([^\]]+)\]\]", r"[\1](\1)", body)

    # Strip Obsidian callouts to blockquotes
    body = re.sub(r"> \[!(\w+)\][+-]?\s*", "> ", body)

    return {
        "title": title or filepath.stem,
        "author": author,
        "digest": digest,
        "body": body.strip(),
        "frontmatter": frontmatter,
    }


def markdown_to_wechat_html(md: str) -> str:
    """Convert markdown to WeChat-compatible HTML.

    Uses semantic tags and minimal styling. WeChat may filter complex CSS.
    Supported: headings, paragraphs, bold, italic, lists, links, blockquotes, code.
    """
    html_parts = []
    lines = md.split("\n")
    i = 0
    in_list = False
    list_tag = None
    in_blockquote = False
    blockquote_lines = []

    def flush_blockquote():
        nonlocal blockquote_lines
        if blockquote_lines:
            content = "\n".join(blockquote_lines)
            inner = markdown_to_wechat_html(content)  # Recursive for nested
            html_parts.append(f"<blockquote>\n{inner}\n</blockquote>")
            blockquote_lines = []

    def flush_list():
        nonlocal in_list, list_tag
        if in_list:
            html_parts.append(f"</{list_tag}>")
            in_list = False
            list_tag = None

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Blockquote
        if line.startswith(">"):
            if not in_blockquote:
                flush_list()
            in_blockquote = True
            blockquote_lines.append(line[1:].strip())
            i += 1
            continue
        else:
            if in_blockquote:
                flush_blockquote()
                in_blockquote = False

        # Empty line
        if not stripped:
            flush_list()
            html_parts.append("<p><br/></p>")
            i += 1
            continue

        # Headings
        if stripped.startswith("#"):
            flush_list()
            level = 0
            while level < len(stripped) and stripped[level] == "#":
                level += 1
            level = min(level, 6)
            text = stripped[level:].strip()
            text = _inline_md_to_html(text)
            html_parts.append(f"<h{level}>{text}</h{level}>")
            i += 1
            continue

        # Unordered list
        if re.match(r"^[\-\*]\s+", stripped) or re.match(r"^\d+\.\s+", stripped):
            is_ordered = bool(re.match(r"^\d+\.\s+", stripped))
            tag = "ol" if is_ordered else "ul"
            if not in_list or list_tag != tag:
                flush_list()
                in_list = True
                list_tag = tag
                html_parts.append(f"<{tag}>")
            item = re.sub(r"^[\-\*]\s+", "", stripped)
            item = re.sub(r"^\d+\.\s+", "", item)
            item = _inline_md_to_html(item)
            html_parts.append(f"<li>{item}</li>")
            i += 1
            continue

        # Horizontal rule
        if stripped in ("---", "***", "___"):
            flush_list()
            html_parts.append("<hr/>")
            i += 1
            continue

        # Code block
        if stripped.startswith("```"):
            flush_list()
            lang = stripped[3:].strip()
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            code = "\n".join(code_lines)
            code = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html_parts.append(f'<pre><code>{code}</code></pre>')
            continue

        # Paragraph
        flush_list()
        html_parts.append(f"<p>{_inline_md_to_html(stripped)}</p>")
        i += 1

    flush_list()
    flush_blockquote()

    return "\n".join(html_parts)


def _escape_html(s: str) -> str:
    """Escape HTML special characters in text content."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _inline_md_to_html(text: str) -> str:
    """Convert inline markdown (bold, italic, links, code) to HTML."""
    # Code - wrap only (escape at end)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # Links - URL may contain parens e.g. [Text](URL (with parens)); use greedy match
    text = re.sub(
        r"\[([^\]]+)\]\(((?:[^()]*|\([^()]*\))*)\)",
        lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>',
        text,
    )
    # Bold ** or __
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", text)
    # Italic * or _
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    text = re.sub(r"_([^_]+)_", r"<em>\1</em>", text)
    # Escape entire text (handles content inside our tags; we restore tags after)
    text = _escape_html(text)
    # Restore our tags (they got escaped)
    for tag in ("strong", "em", "code"):
        text = text.replace(f"&lt;{tag}&gt;", f"<{tag}>")
        text = text.replace(f"&lt;/{tag}&gt;", f"</{tag}>")
    # Restore links: &lt;a href=&quot;URL&quot;&gt; -> <a href="URL">
    text = re.sub(r"&lt;a href=&quot;(.*?)&quot;&gt;", r'<a href="\1">', text)
    text = text.replace("&lt;/a&gt;", "</a>")
    return text


def build_wechat_html(note: dict) -> str:
    """Build full WeChat-style HTML document."""
    body_html = markdown_to_wechat_html(note["body"])

    # WeChat 公众号常见排版：正文 16px，行高 1.8，段落间距
    # 使用 section 包裹，便于粘贴后微信识别结构
    html = f"""<section style="font-size:16px;line-height:1.8;color:#333;max-width:750px;">
{body_html}
</section>"""
    return html


def copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard. Returns True on success."""
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
                    proc = subprocess.Popen(
                        cmd,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.PIPE,
                    )
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


def create_draft_via_api(note: dict, html_content: str, thumb_media_id: str) -> str:
    """Create draft via WeChat API. Returns media_id or error message."""
    app_id = os.getenv("WECHAT_APP_ID", "")
    app_secret = os.getenv("WECHAT_APP_SECRET", "")
    access_token = os.getenv("WECHAT_ACCESS_TOKEN", "")

    if not access_token and (not app_id or not app_secret):
        return "Error: Set WECHAT_ACCESS_TOKEN or (WECHAT_APP_ID + WECHAT_APP_SECRET) in .env"

    if not thumb_media_id:
        return "Error: Cover image required. Upload image via WeChat API first to get thumb_media_id."

    # Get access_token if not set
    if not access_token:
        import requests
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
        r = requests.get(url)
        data = r.json()
        if "access_token" not in data:
            return f"Error: Failed to get access_token: {data}"
        access_token = data["access_token"]

    import requests
    api_url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
    payload = {
        "articles": [
            {
                "title": note["title"][:32],
                "author": (note.get("author") or "")[:16],
                "digest": (note.get("digest") or "")[:128],
                "content": html_content,
                "thumb_media_id": thumb_media_id,
                "need_open_comment": 0,
                "only_fans_can_comment": 0,
            }
        ]
    }
    r = requests.post(api_url, json=payload)
    data = r.json()
    if "media_id" in data:
        return f"Success! Draft media_id: {data['media_id']}. Publish via mp.weixin.qq.com 草稿箱."
    return f"Error: {data.get('errcode', '')} {data.get('errmsg', str(data))}"


def main():
    parser = argparse.ArgumentParser(
        description="Official WeChat Publisher - Publish to 微信公众号 quickly",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /skill official-wechat-publisher note.md           # Convert and copy to clipboard
  /skill official-wechat-publisher note.md --save     # Also save HTML file
  /skill official-wechat-publisher note.md --no-copy  # Only save, don't copy
  /skill official-wechat-publisher note.md --api --thumb MEDIA_ID  # Create draft via API
""",
    )
    parser.add_argument(
        "note",
        help="Path to Obsidian note (relative to vault or absolute)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save HTML to Sources/WeChat Official - TITLE - DATE.html",
    )
    parser.add_argument(
        "--no-copy",
        action="store_true",
        help="Do not copy to clipboard",
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Create draft via WeChat API (requires .env credentials + --thumb)",
    )
    parser.add_argument(
        "--thumb",
        type=str,
        default="",
        help="Cover image thumb_media_id (required for --api)",
    )
    args = parser.parse_args()

    note_path = Path(args.note)
    if not note_path.is_absolute():
        note_path = VAULT_PATH / note_path
    if not note_path.exists():
        sys.exit(f"Error: Note not found: {note_path}")

    note = parse_note(note_path)
    html = build_wechat_html(note)

    print(f"Title: {note['title']}")
    print(f"Author: {note.get('author', '(none)')}")
    print(f"Body length: {len(html)} chars")

    if args.api:
        result = create_draft_via_api(note, html, args.thumb)
        print(result)
        return

    if not args.no_copy:
        if copy_to_clipboard(html):
            print("✓ Copied to clipboard. Paste into mp.weixin.qq.com → 新建图文消息")
        else:
            print("Could not copy to clipboard. Use --save to save HTML file.")

    if args.save:
        from config import save_note
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_title = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', note["title"])[:40].strip() or "article"
        path = f"Sources/WeChat Official - {safe_title} - {date_str}.html"
        full_html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{note['title']}</title></head>
<body>
{html}
</body>
</html>"""
        save_note(path, full_html)
        print(f"Saved: {path}")

    if args.no_copy and not args.save:
        print("\n--- HTML Content ---\n")
        print(html)


if __name__ == "__main__":
    main()
