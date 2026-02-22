"""Skill Snapshot - Version control for PAI skills.

Create snapshots of skills with version control. Store backups locally (or push to GitHub).
Inspired by wshuyi/skill-snapshot-skill: https://github.com/wshuyi/skill-snapshot-skill
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import VAULT_PATH

SKILLS_DIR = VAULT_PATH / ".claude" / "skills"
SNAPSHOTS_DIR = VAULT_PATH / "_logs" / "skill-snapshots"
SKIP_NAMES = {"skill-snapshot", "archive"}
MAX_SIZE_MB = 10


def _run(cmd: list, capture: bool = False, cwd: Optional[Path] = None) -> Optional[str]:
    wd = cwd or (SNAPSHOTS_DIR if SNAPSHOTS_DIR.exists() else VAULT_PATH)
    result = subprocess.run(cmd, capture_output=capture, text=True, cwd=wd)
    if capture:
        return result.stdout.strip() if result.returncode == 0 else ""
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return None


def _check_skill(skill_path: Path) -> tuple[str, str, str]:
    """Returns (type, name, info). type is BACKUP or SKIP."""
    name = skill_path.name
    if name in SKIP_NAMES:
        return "SKIP", name, "快照工具本身" if name == "skill-snapshot" else "归档目录"
    if skill_path.is_symlink():
        return "SKIP", name, "符号链接（外部安装）"
    if (skill_path / ".git").exists():
        return "SKIP", name, "自带 Git 版本控制"
    if (skill_path / ".venv").exists() or (skill_path / "node_modules").exists():
        return "SKIP", name, "包含依赖目录 (.venv/node_modules)"
    try:
        size_mb = sum(f.stat().st_size for f in skill_path.rglob("*") if f.is_file()) / (1024 * 1024)
        if size_mb > MAX_SIZE_MB:
            return "SKIP", name, f"体积过大 ({size_mb:.1f}MB > {MAX_SIZE_MB}MB)"
    except OSError:
        pass
    if not (skill_path / "SKILL.md").exists():
        return "SKIP", name, "缺少 SKILL.md"
    files = sum(1 for f in skill_path.rglob("*") if f.is_file() and f.name != ".DS_Store")
    size = sum(f.stat().st_size for f in skill_path.rglob("*") if f.is_file())
    size_str = f"{size / 1024:.0f}K" if size < 1024 * 1024 else f"{size / 1024 / 1024:.1f}M"
    has_snapshot = ""
    if (SNAPSHOTS_DIR / ".git").exists():
        tags = _run(["git", "tag", "-l", f"{name}/v*"], capture=True) or ""
        if tags:
            latest = sorted(tags.split(), key=lambda t: (t.split("/v")[-1] if "/v" in t else "0"))[-1]
            has_snapshot = latest
    return "BACKUP", name, f"{files} files, {size_str}|{has_snapshot}"


def cmd_scan() -> None:
    """Scan skills and identify which need backup."""
    print("=== 技能快照扫描 ===\n")
    backup_list = []
    skip_list = []
    for d in sorted(SKILLS_DIR.iterdir()):
        if not d.is_dir():
            continue
        t, name, info = _check_skill(d)
        if t == "BACKUP":
            backup_list.append((name, info))
        else:
            skip_list.append((name, info))
    print("【需要备份】")
    if not backup_list:
        print("  (无)")
    else:
        for name, info in backup_list:
            parts = info.split("|")
            detail = parts[0]
            snap = parts[1] if len(parts) > 1 else ""
            if snap:
                print(f"  ✓ {name} ({detail}) [已有: {snap}]")
            else:
                print(f"  ○ {name} ({detail}) [未备份]")
    print("\n【跳过】")
    if not skip_list:
        print("  (无)")
    else:
        for name, reason in skip_list:
            print(f"  ✗ {name} - {reason}")
    print("\n----------------------------------------")
    need = sum(1 for _, i in backup_list if "|" in i and not i.split("|")[1])
    print(f"需要备份: {len(backup_list)} 个")
    print(f"跳过: {len(skip_list)} 个")
    if need > 0:
        print(f"\n【待备份】{need} 个技能尚未创建快照:")
        for name, info in backup_list:
            if "|" not in info or not info.split("|")[1]:
                print(f"  - {name}")


def cmd_init() -> None:
    """Initialize snapshot repository."""
    print("=== Skill Snapshot 初始化 ===\n")
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    if (SNAPSHOTS_DIR / ".git").exists():
        print("✓ 本地仓库已存在:", SNAPSHOTS_DIR)
        try:
            _run(["git", "pull", "--quiet", "origin", "main"], capture=False)
        except Exception:
            pass
    else:
        subprocess.run(["git", "init", "--quiet"], cwd=SNAPSHOTS_DIR, check=True)
        readme = SNAPSHOTS_DIR / "README.md"
        if not readme.exists():
            readme.write_text("""# Skill Snapshots

PAI 技能快照备份。

## 结构

每个技能对应一个目录，使用 Git tags 管理版本：

```
├── <skill-name>/
│   ├── SKILL.md
│   └── ...
```

Tags 格式: `<skill>/v<n>`

## 使用

由 `skill_snapshot.py` 自动管理。
""", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=SNAPSHOTS_DIR, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "Initial commit"], cwd=SNAPSHOTS_DIR, capture_output=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=SNAPSHOTS_DIR, capture_output=True)
        print("✓ 本地仓库已初始化")
    print("\n=== 初始化完成 ===")
    print("本地路径:", SNAPSHOTS_DIR)
    print("可选: 添加 GitHub 远程仓库以备份到云端")
    print("  cd _logs/skill-snapshots && git remote add origin https://github.com/<user>/skill-snapshots.git")


def cmd_save(skill_name: str, message: str) -> None:
    """Save a skill snapshot."""
    skill_path = SKILLS_DIR / skill_name
    if not skill_path.exists():
        print(f"错误: 技能不存在: {skill_path}")
        sys.exit(1)
    if skill_path.is_symlink():
        print(f"错误: {skill_name} 是符号链接，不支持快照")
        sys.exit(1)
    if not (SNAPSHOTS_DIR / ".git").exists():
        print("错误: 仓库未初始化，请先执行 init")
        sys.exit(1)
    try:
        subprocess.run(["git", "checkout", "--quiet", "main"], cwd=SNAPSHOTS_DIR, capture_output=True, check=True)
    except subprocess.CalledProcessError:
        pass
    try:
        subprocess.run(["git", "fetch", "--tags", "--quiet"], cwd=SNAPSHOTS_DIR, capture_output=True)
    except Exception:
        pass
    tags_out = _run(["git", "tag", "-l", f"{skill_name}/v*"], capture=True) or ""
    existing = sorted(tags_out.split()) if tags_out else []
    if not existing:
        next_ver = "v1"
    else:
        last = existing[-1]
        num = 1
        if "/v" in last:
            try:
                num = int(last.split("/v")[-1]) + 1
            except ValueError:
                pass
        next_ver = f"v{num}"
    tag_name = f"{skill_name}/{next_ver}"
    msg = message or f"Snapshot at {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}"
    print("=== 保存快照 ===")
    print(f"技能: {skill_name}")
    print(f"版本: {next_ver}")
    print(f"说明: {msg}\n")
    dest = SNAPSHOTS_DIR / skill_name
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    for f in skill_path.rglob("*"):
        if f.is_file() and f.name not in (".DS_Store",) and "__pycache__" not in str(f):
            rel = f.relative_to(skill_path)
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)
    subprocess.run(["git", "add", skill_name], cwd=SNAPSHOTS_DIR, check=True)
    diff_ok = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=SNAPSHOTS_DIR, capture_output=True)
    if diff_ok.returncode != 0:
        subprocess.run(["git", "commit", "--quiet", "-m", f"[{skill_name}] {next_ver}: {msg}"], cwd=SNAPSHOTS_DIR, check=True)
        subprocess.run(["git", "tag", "-a", tag_name, "-m", msg], cwd=SNAPSHOTS_DIR, check=True)
        print(f"✓ 快照已保存: {tag_name}")
    else:
        print("✓ 无变化 - 内容与最新快照相同，无需保存")
        if existing:
            print(f"→ 最新快照: {existing[-1]}")
    print(f"→ 可用 'restore {skill_name} {next_ver}' 恢复")


def cmd_restore(skill_name: str, version: Optional[str]) -> None:
    """Restore a skill to a snapshot version."""
    if not (SNAPSHOTS_DIR / ".git").exists():
        print("错误: 仓库未初始化，请先执行 init")
        sys.exit(1)
    tags_out = _run(["git", "tag", "-l", f"{skill_name}/v*"], capture=True) or ""
    available = sorted(tags_out.split()) if tags_out else []
    if not available:
        print(f"错误: 没有找到 {skill_name} 的快照")
        sys.exit(1)
    if not version:
        print(f"=== {skill_name} 可用版本 ===\n")
        for tag in available:
            ver = tag.split("/")[-1] if "/" in tag else tag
            msg = _run(["git", "tag", "-l", tag, "-n1"], capture=True) or ""
            msg = msg.replace(tag, "").strip()
            date = _run(["git", "log", "-1", "--format=%ci", tag], capture=True) or ""
            date = date.split()[0] if date else ""
            print(f"  {ver} - {date} - {msg}")
        print(f"\n请指定版本: restore {skill_name} v2")
        return
    tag_name = f"{skill_name}/{version}" if "/" not in version else version
    if tag_name not in available:
        tag_name = next((t for t in available if t.endswith(f"/{version}") or t == f"{skill_name}/{version}"), None)
        if not tag_name:
            print(f"错误: 版本不存在: {version}")
            print("可用版本:", ", ".join(t.split("/")[-1] for t in available))
            sys.exit(1)
    skill_path = SKILLS_DIR / skill_name
    if skill_path.is_symlink():
        print(f"错误: {skill_name} 是符号链接，不支持恢复")
        sys.exit(1)
    backup_dir = SKILLS_DIR / ".snapshot-backup"
    if skill_path.exists():
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_name = f"{skill_name}-{__import__('datetime').datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copytree(skill_path, backup_dir / backup_name, dirs_exist_ok=True)
        print(f"→ 当前版本已备份到: .snapshot-backup/{backup_name}")
    subprocess.run(["git", "checkout", "--quiet", tag_name], cwd=SNAPSHOTS_DIR, check=True)
    src = SNAPSHOTS_DIR / skill_name
    if skill_path.exists():
        shutil.rmtree(skill_path)
    shutil.copytree(src, skill_path)
    subprocess.run(["git", "checkout", "--quiet", "main"], cwd=SNAPSHOTS_DIR, check=True)
    print(f"✓ 已恢复到 {tag_name}")


def cmd_list(skill_name: Optional[str]) -> None:
    """List snapshots."""
    if not (SNAPSHOTS_DIR / ".git").exists():
        print("错误: 仓库未初始化，请先执行 init")
        sys.exit(1)
    if not skill_name:
        tags_out = _run(["git", "tag", "-l", "*/v*"], capture=True) or ""
        tags = sorted(set(t.split("/")[0] for t in tags_out.split() if "/" in t))
        print("=== 所有技能快照 ===\n")
        if not tags:
            print("暂无快照")
            return
        for s in tags:
            st = _run(["git", "tag", "-l", f"{s}/v*"], capture=True) or ""
            count = len(st.split()) if st else 0
            latest = st.split()[-1].split("/")[-1] if st else "-"
            print(f"  {s} ({count} 个版本, 最新: {latest})")
        print("\n查看特定技能: list <skill>")
    else:
        tags_out = _run(["git", "tag", "-l", f"{skill_name}/v*"], capture=True) or ""
        available = sorted(tags_out.split()) if tags_out else []
        if not available:
            print(f"没有找到 {skill_name} 的快照")
            return
        print(f"=== {skill_name} 快照历史 ===\n")
        for tag in available:
            ver = tag.split("/")[-1]
            msg = _run(["git", "tag", "-l", tag, "-n1"], capture=True) or ""
            msg = msg.replace(tag, "").strip()
            date = _run(["git", "log", "-1", "--format=%ci", tag], capture=True) or ""
            date = date.split()[0] if date else ""
            print(f"  {ver} - {date} - {msg}")
        print(f"\n最新版本: {available[-1].split('/')[-1]}")


def cmd_diff(skill_name: str, version: Optional[str]) -> None:
    """Diff current skill with snapshot."""
    skill_path = SKILLS_DIR / skill_name
    if not skill_path.exists():
        print(f"错误: 技能不存在: {skill_path}")
        sys.exit(1)
    if not (SNAPSHOTS_DIR / ".git").exists():
        print("错误: 仓库未初始化，请先执行 init")
        sys.exit(1)
    tags_out = _run(["git", "tag", "-l", f"{skill_name}/v*"], capture=True) or ""
    available = sorted(tags_out.split()) if tags_out else []
    if not available:
        print(f"没有找到 {skill_name} 的快照")
        return
    tag_name = available[-1]
    if version:
        cand = f"{skill_name}/{version}"
        if cand in available:
            tag_name = cand
        else:
            cand2 = next((t for t in available if t.endswith(f"/{version}")), None)
            if cand2:
                tag_name = cand2
    ver = tag_name.split("/")[-1]
    print("=== 对比差异 ===")
    print(f"技能: {skill_name}")
    print(f"快照版本: {ver}")
    print("当前版本: (本地)\n")
    import tempfile
    import tarfile
    with tempfile.TemporaryDirectory() as tmp:
        tarpath = Path(tmp) / "snap.tar"
        with open(tarpath, "wb") as f:
            subprocess.run(["git", "archive", tag_name, f"{skill_name}/"], cwd=SNAPSHOTS_DIR, stdout=f, check=True)
        with tarfile.open(tarpath) as tf:
            tf.extractall(tmp)
        snap_dir = Path(tmp) / skill_name
        if not snap_dir.exists():
            snap_dir = Path(tmp)
        result = subprocess.run(
            ["diff", "-ru", str(snap_dir), str(skill_path), "-x", ".DS_Store", "-x", "__pycache__"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            print("✓ 无差异 - 当前版本与快照相同")
        else:
            out = result.stdout.replace(str(snap_dir), "snapshot").replace(str(skill_path), "current")
            print(out)


def main():
    parser = argparse.ArgumentParser(
        description="Skill Snapshot - Version control for PAI skills (wshuyi/skill-snapshot-skill)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 _scripts/skill_snapshot.py init
  python3 _scripts/skill_snapshot.py scan
  python3 _scripts/skill_snapshot.py save deep-research "pre-methodology update"
  python3 _scripts/skill_snapshot.py restore deep-research v1
  python3 _scripts/skill_snapshot.py list deep-research
  python3 _scripts/skill_snapshot.py diff deep-research v1
""",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init", help="Initialize snapshot repository")
    sub.add_parser("scan", help="Scan skills, identify which need backup")
    save_p = sub.add_parser("save", help="Save a skill snapshot")
    save_p.add_argument("skill", help="Skill name")
    save_p.add_argument("message", nargs="?", default="", help="Snapshot message")
    rest_p = sub.add_parser("restore", help="Restore skill to version")
    rest_p.add_argument("skill", help="Skill name")
    rest_p.add_argument("version", nargs="?", help="Version (e.g. v1)")
    list_p = sub.add_parser("list", help="List snapshots")
    list_p.add_argument("skill", nargs="?", help="Skill name (optional)")
    diff_p = sub.add_parser("diff", help="Diff current with snapshot")
    diff_p.add_argument("skill", help="Skill name")
    diff_p.add_argument("version", nargs="?", help="Version (optional, default latest)")
    args = parser.parse_args()

    if args.cmd == "init":
        cmd_init()
    elif args.cmd == "scan":
        cmd_scan()
    elif args.cmd == "save":
        cmd_save(args.skill, args.message)
    elif args.cmd == "restore":
        cmd_restore(args.skill, args.version)
    elif args.cmd == "list":
        cmd_list(args.skill)
    elif args.cmd == "diff":
        cmd_diff(args.skill, args.version)


if __name__ == "__main__":
    main()
