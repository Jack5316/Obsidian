"""Obsidian CLI Integration Module - Wrapper for the Obsidian CLI tool.

This module provides Python functions to interact with Obsidian via its CLI,
allowing seamless integration with your existing skills and automation workflows.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import VAULT_PATH


class ObsidianCLI:
    """Wrapper class for Obsidian CLI commands."""
    
    def __init__(self, vault_name: Optional[str] = None):
        self.vault_name = vault_name
        self.base_cmd = ["obsidian"]
        if vault_name:
            self.base_cmd.append(f"vault={vault_name}")
    
    def _run_command(self, command: List[str]) -> Tuple[str, str, int]:
        """Execute an Obsidian CLI command and return results."""
        cmd = self.base_cmd + command
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(VAULT_PATH)
            )
            return (result.stdout, result.stderr, result.returncode)
        except Exception as e:
            return ("", str(e), 1)
    
    # File Operations
    def create_file(self, name: Optional[str] = None, path: Optional[str] = None, 
                   content: str = "", template: Optional[str] = None,
                   overwrite: bool = False, silent: bool = False,
                   newtab: bool = False) -> bool:
        """Create a new file in the vault."""
        cmd = ["create"]
        if name:
            cmd.append(f"name={name}")
        if path:
            cmd.append(f"path={path}")
        if content:
            cmd.append(f"content={content}")
        if template:
            cmd.append(f"template={template}")
        if overwrite:
            cmd.append("overwrite")
        if silent:
            cmd.append("silent")
        if newtab:
            cmd.append("newtab")
        
        stdout, stderr, code = self._run_command(cmd)
        return code == 0
    
    def read_file(self, name: Optional[str] = None, path: Optional[str] = None) -> Optional[str]:
        """Read contents of a file."""
        cmd = ["read"]
        if name:
            cmd.append(f"file={name}")
        if path:
            cmd.append(f"path={path}")
        
        stdout, stderr, code = self._run_command(cmd)
        return stdout if code == 0 else None
    
    def append_content(self, name: Optional[str] = None, path: Optional[str] = None,
                      content: str = "", inline: bool = False) -> bool:
        """Append content to a file."""
        cmd = ["append"]
        if name:
            cmd.append(f"file={name}")
        if path:
            cmd.append(f"path={path}")
        cmd.append(f"content={content}")
        if inline:
            cmd.append("inline")
        
        stdout, stderr, code = self._run_command(cmd)
        return code == 0
    
    def prepend_content(self, name: Optional[str] = None, path: Optional[str] = None,
                       content: str = "", inline: bool = False) -> bool:
        """Prepend content to a file."""
        cmd = ["prepend"]
        if name:
            cmd.append(f"file={name}")
        if path:
            cmd.append(f"path={path}")
        cmd.append(f"content={content}")
        if inline:
            cmd.append("inline")
        
        stdout, stderr, code = self._run_command(cmd)
        return code == 0
    
    def delete_file(self, name: Optional[str] = None, path: Optional[str] = None,
                   permanent: bool = False) -> bool:
        """Delete a file."""
        cmd = ["delete"]
        if name:
            cmd.append(f"file={name}")
        if path:
            cmd.append(f"path={path}")
        if permanent:
            cmd.append("permanent")
        
        stdout, stderr, code = self._run_command(cmd)
        return code == 0
    
    def move_file(self, name: Optional[str] = None, path: Optional[str] = None,
                 to: str = "") -> bool:
        """Move or rename a file."""
        cmd = ["move"]
        if name:
            cmd.append(f"file={name}")
        if path:
            cmd.append(f"path={path}")
        cmd.append(f"to={to}")
        
        stdout, stderr, code = self._run_command(cmd)
        return code == 0
    
    def open_file(self, name: Optional[str] = None, path: Optional[str] = None,
                 newtab: bool = False) -> bool:
        """Open a file in Obsidian."""
        cmd = ["open"]
        if name:
            cmd.append(f"file={name}")
        if path:
            cmd.append(f"path={path}")
        if newtab:
            cmd.append("newtab")
        
        stdout, stderr, code = self._run_command(cmd)
        return code == 0
    
    # Vault Information
    def list_files(self, folder: Optional[str] = None, ext: Optional[str] = None,
                  total: bool = False) -> List[str]:
        """List files in the vault."""
        cmd = ["files"]
        if folder:
            cmd.append(f"folder={folder}")
        if ext:
            cmd.append(f"ext={ext}")
        if total:
            cmd.append("total")
        
        stdout, stderr, code = self._run_command(cmd)
        if code == 0 and stdout:
            return [f.strip() for f in stdout.strip().split("\n") if f.strip()]
        return []
    
    def list_folders(self, folder: Optional[str] = None, total: bool = False) -> List[str]:
        """List folders in the vault."""
        cmd = ["folders"]
        if folder:
            cmd.append(f"folder={folder}")
        if total:
            cmd.append("total")
        
        stdout, stderr, code = self._run_command(cmd)
        if code == 0 and stdout:
            return [f.strip() for f in stdout.strip().split("\n") if f.strip()]
        return []
    
    def get_vault_info(self, info: str = "path") -> Optional[str]:
        """Get vault information."""
        cmd = ["vault", f"info={info}"]
        stdout, stderr, code = self._run_command(cmd)
        return stdout.strip() if code == 0 else None
    
    # Search & Query
    def search(self, query: str, path: Optional[str] = None, limit: Optional[int] = None,
              total: bool = False, matches: bool = False, case: bool = False,
              format: str = "text") -> str:
        """Search the vault."""
        cmd = ["search", f"query={query}"]
        if path:
            cmd.append(f"path={path}")
        if limit:
            cmd.append(f"limit={limit}")
        if total:
            cmd.append("total")
        if matches:
            cmd.append("matches")
        if case:
            cmd.append("case")
        cmd.append(f"format={format}")
        
        stdout, stderr, code = self._run_command(cmd)
        return stdout if code == 0 else ""
    
    # Links & Relationships
    def get_backlinks(self, name: Optional[str] = None, path: Optional[str] = None,
                     counts: bool = False, total: bool = False) -> List[str]:
        """Get backlinks to a file."""
        cmd = ["backlinks"]
        if name:
            cmd.append(f"file={name}")
        if path:
            cmd.append(f"path={path}")
        if counts:
            cmd.append("counts")
        if total:
            cmd.append("total")
        
        stdout, stderr, code = self._run_command(cmd)
        if code == 0 and stdout:
            return [f.strip() for f in stdout.strip().split("\n") if f.strip()]
        return []
    
    def get_outgoing_links(self, name: Optional[str] = None, path: Optional[str] = None,
                          total: bool = False) -> List[str]:
        """Get outgoing links from a file."""
        cmd = ["links"]
        if name:
            cmd.append(f"file={name}")
        if path:
            cmd.append(f"path={path}")
        if total:
            cmd.append("total")
        
        stdout, stderr, code = self._run_command(cmd)
        if code == 0 and stdout:
            return [f.strip() for f in stdout.strip().split("\n") if f.strip()]
        return []
    
    def get_orphans(self, total: bool = False, all: bool = False) -> List[str]:
        """Get files with no incoming links."""
        cmd = ["orphans"]
        if total:
            cmd.append("total")
        if all:
            cmd.append("all")
        
        stdout, stderr, code = self._run_command(cmd)
        if code == 0 and stdout:
            return [f.strip() for f in stdout.strip().split("\n") if f.strip()]
        return []
    
    def get_deadends(self, total: bool = False, all: bool = False) -> List[str]:
        """Get files with no outgoing links."""
        cmd = ["deadends"]
        if total:
            cmd.append("total")
        if all:
            cmd.append("all")
        
        stdout, stderr, code = self._run_command(cmd)
        if code == 0 and stdout:
            return [f.strip() for f in stdout.strip().split("\n") if f.strip()]
        return []
    
    def get_unresolved_links(self, total: bool = False, counts: bool = False,
                            verbose: bool = False) -> List[str]:
        """Get unresolved links in the vault."""
        cmd = ["unresolved"]
        if total:
            cmd.append("total")
        if counts:
            cmd.append("counts")
        if verbose:
            cmd.append("verbose")
        
        stdout, stderr, code = self._run_command(cmd)
        if code == 0 and stdout:
            return [f.strip() for f in stdout.strip().split("\n") if f.strip()]
        return []
    
    # Tags
    def list_tags(self, all: bool = False, name: Optional[str] = None,
                 path: Optional[str] = None, total: bool = False,
                 counts: bool = False, sort: str = "count") -> List[str]:
        """List tags in the vault."""
        cmd = ["tags"]
        if all:
            cmd.append("all")
        if name:
            cmd.append(f"file={name}")
        if path:
            cmd.append(f"path={path}")
        if total:
            cmd.append("total")
        if counts:
            cmd.append("counts")
        cmd.append(f"sort={sort}")
        
        stdout, stderr, code = self._run_command(cmd)
        if code == 0 and stdout:
            return [f.strip() for f in stdout.strip().split("\n") if f.strip()]
        return []
    
    # Tasks
    def list_tasks(self, all: bool = False, daily: bool = False,
                  name: Optional[str] = None, path: Optional[str] = None,
                  total: bool = False, done: bool = False, todo: bool = False,
                  status: Optional[str] = None, verbose: bool = False) -> List[str]:
        """List tasks in the vault."""
        cmd = ["tasks"]
        if all:
            cmd.append("all")
        if daily:
            cmd.append("daily")
        if name:
            cmd.append(f"file={name}")
        if path:
            cmd.append(f"path={path}")
        if total:
            cmd.append("total")
        if done:
            cmd.append("done")
        if todo:
            cmd.append("todo")
        if status:
            cmd.append(f'status="{status}"')
        if verbose:
            cmd.append("verbose")
        
        stdout, stderr, code = self._run_command(cmd)
        if code == 0 and stdout:
            return [f.strip() for f in stdout.strip().split("\n") if f.strip()]
        return []
    
    # Daily Notes
    def open_daily_note(self, pane_type: str = "tab", silent: bool = False) -> bool:
        """Open daily note."""
        cmd = ["daily", f"paneType={pane_type}"]
        if silent:
            cmd.append("silent")
        
        stdout, stderr, code = self._run_command(cmd)
        return code == 0
    
    def append_to_daily(self, content: str, inline: bool = False,
                       silent: bool = False, pane_type: str = "tab") -> bool:
        """Append content to daily note."""
        cmd = ["daily:append", f"content={content}"]
        if inline:
            cmd.append("inline")
        if silent:
            cmd.append("silent")
        cmd.append(f"paneType={pane_type}")
        
        stdout, stderr, code = self._run_command(cmd)
        return code == 0
    
    def prepend_to_daily(self, content: str, inline: bool = False,
                        silent: bool = False, pane_type: str = "tab") -> bool:
        """Prepend content to daily note."""
        cmd = ["daily:prepend", f"content={content}"]
        if inline:
            cmd.append("inline")
        if silent:
            cmd.append("silent")
        cmd.append(f"paneType={pane_type}")
        
        stdout, stderr, code = self._run_command(cmd)
        return code == 0
    
    def read_daily_note(self) -> Optional[str]:
        """Read daily note contents."""
        cmd = ["daily:read"]
        stdout, stderr, code = self._run_command(cmd)
        return stdout if code == 0 else None
    
    # Properties
    def list_properties(self, all: bool = False, name: Optional[str] = None,
                       path: Optional[str] = None, prop_name: Optional[str] = None,
                       total: bool = False, sort: str = "count", counts: bool = False,
                       format: str = "yaml") -> List[str]:
        """List properties in the vault."""
        cmd = ["properties"]
        if all:
            cmd.append("all")
        if name:
            cmd.append(f"file={name}")
        if path:
            cmd.append(f"path={path}")
        if prop_name:
            cmd.append(f"name={prop_name}")
        if total:
            cmd.append("total")
        cmd.append(f"sort={sort}")
        if counts:
            cmd.append("counts")
        cmd.append(f"format={format}")
        
        stdout, stderr, code = self._run_command(cmd)
        if code == 0 and stdout:
            return [f.strip() for f in stdout.strip().split("\n") if f.strip()]
        return []
    
    def set_property(self, name: str, value: str, prop_type: str = "text",
                    file_name: Optional[str] = None, path: Optional[str] = None) -> bool:
        """Set a property on a file."""
        cmd = ["property:set", f"name={name}", f"value={value}", f"type={prop_type}"]
        if file_name:
            cmd.append(f"file={file_name}")
        if path:
            cmd.append(f"path={path}")
        
        stdout, stderr, code = self._run_command(cmd)
        return code == 0
    
    def get_property(self, name: str, file_name: Optional[str] = None,
                    path: Optional[str] = None) -> Optional[str]:
        """Read a property value from a file."""
        cmd = ["property:read", f"name={name}"]
        if file_name:
            cmd.append(f"file={file_name}")
        if path:
            cmd.append(f"path={path}")
        
        stdout, stderr, code = self._run_command(cmd)
        return stdout.strip() if code == 0 else None
    
    def remove_property(self, name: str, file_name: Optional[str] = None,
                       path: Optional[str] = None) -> bool:
        """Remove a property from a file."""
        cmd = ["property:remove", f"name={name}"]
        if file_name:
            cmd.append(f"file={file_name}")
        if path:
            cmd.append(f"path={path}")
        
        stdout, stderr, code = self._run_command(cmd)
        return code == 0
    
    # Aliases
    def list_aliases(self, all: bool = False, name: Optional[str] = None,
                    path: Optional[str] = None, total: bool = False,
                    verbose: bool = False) -> List[str]:
        """List aliases in the vault or file."""
        cmd = ["aliases"]
        if all:
            cmd.append("all")
        if name:
            cmd.append(f"file={name}")
        if path:
            cmd.append(f"path={path}")
        if total:
            cmd.append("total")
        if verbose:
            cmd.append("verbose")
        
        stdout, stderr, code = self._run_command(cmd)
        if code == 0 and stdout:
            return [f.strip() for f in stdout.strip().split("\n") if f.strip()]
        return []
    
    # Recent Files
    def get_recents(self, total: bool = False) -> List[str]:
        """List recently opened files."""
        cmd = ["recents"]
        if total:
            cmd.append("total")
        
        stdout, stderr, code = self._run_command(cmd)
        if code == 0 and stdout:
            return [f.strip() for f in stdout.strip().split("\n") if f.strip()]
        return []
    
    # Outline/Headings
    def get_outline(self, name: Optional[str] = None, path: Optional[str] = None,
                   format: str = "tree", total: bool = False) -> str:
        """Get headings/outline for a file."""
        cmd = ["outline"]
        if name:
            cmd.append(f"file={name}")
        if path:
            cmd.append(f"path={path}")
        cmd.append(f"format={format}")
        if total:
            cmd.append("total")
        
        stdout, stderr, code = self._run_command(cmd)
        return stdout if code == 0 else ""
    
    # Word Count
    def get_wordcount(self, name: Optional[str] = None, path: Optional[str] = None,
                     words: bool = False, characters: bool = False) -> Optional[str]:
        """Get word and character count."""
        cmd = ["wordcount"]
        if name:
            cmd.append(f"file={name}")
        if path:
            cmd.append(f"path={path}")
        if words:
            cmd.append("words")
        if characters:
            cmd.append("characters")
        
        stdout, stderr, code = self._run_command(cmd)
        return stdout.strip() if code == 0 else None
    
    # Bookmarks
    def list_bookmarks(self, total: bool = False, verbose: bool = False) -> List[str]:
        """List bookmarks."""
        cmd = ["bookmarks"]
        if total:
            cmd.append("total")
        if verbose:
            cmd.append("verbose")
        
        stdout, stderr, code = self._run_command(cmd)
        if code == 0 and stdout:
            return [f.strip() for f in stdout.strip().split("\n") if f.strip()]
        return []
    
    def add_bookmark(self, file: Optional[str] = None, subpath: Optional[str] = None,
                    folder: Optional[str] = None, search: Optional[str] = None,
                    url: Optional[str] = None, title: Optional[str] = None) -> bool:
        """Add a bookmark."""
        cmd = ["bookmark"]
        if file:
            cmd.append(f"file={file}")
        if subpath:
            cmd.append(f"subpath={subpath}")
        if folder:
            cmd.append(f"folder={folder}")
        if search:
            cmd.append(f"search={search}")
        if url:
            cmd.append(f"url={url}")
        if title:
            cmd.append(f"title={title}")
        
        stdout, stderr, code = self._run_command(cmd)
        return code == 0
    
    # Plugins
    def list_plugins(self, filter: Optional[str] = None, versions: bool = False) -> List[str]:
        """List installed plugins."""
        cmd = ["plugins"]
        if filter:
            cmd.append(f"filter={filter}")
        if versions:
            cmd.append("versions")
        
        stdout, stderr, code = self._run_command(cmd)
        if code == 0 and stdout:
            return [f.strip() for f in stdout.strip().split("\n") if f.strip()]
        return []
    
    def enable_plugin(self, plugin_id: str, filter: Optional[str] = None) -> bool:
        """Enable a plugin."""
        cmd = ["plugin:enable", f"id={plugin_id}"]
        if filter:
            cmd.append(f"filter={filter}")
        
        stdout, stderr, code = self._run_command(cmd)
        return code == 0
    
    def disable_plugin(self, plugin_id: str, filter: Optional[str] = None) -> bool:
        """Disable a plugin."""
        cmd = ["plugin:disable", f"id={plugin_id}"]
        if filter:
            cmd.append(f"filter={filter}")
        
        stdout, stderr, code = self._run_command(cmd)
        return code == 0
    
    # Templates
    def list_templates(self, total: bool = False) -> List[str]:
        """List templates."""
        cmd = ["templates"]
        if total:
            cmd.append("total")
        
        stdout, stderr, code = self._run_command(cmd)
        if code == 0 and stdout:
            return [f.strip() for f in stdout.strip().split("\n") if f.strip()]
        return []
    
    def read_template(self, name: str, resolve: bool = False,
                     title: Optional[str] = None) -> Optional[str]:
        """Read template content."""
        cmd = ["template:read", f"name={name}"]
        if resolve:
            cmd.append("resolve")
        if title:
            cmd.append(f"title={title}")
        
        stdout, stderr, code = self._run_command(cmd)
        return stdout if code == 0 else None
    
    # Commands
    def list_commands(self, filter: Optional[str] = None) -> List[str]:
        """List available command IDs."""
        cmd = ["commands"]
        if filter:
            cmd.append(f"filter={filter}")
        
        stdout, stderr, code = self._run_command(cmd)
        if code == 0 and stdout:
            return [f.strip() for f in stdout.strip().split("\n") if f.strip()]
        return []
    
    def execute_command(self, command_id: str) -> bool:
        """Execute an Obsidian command."""
        cmd = ["command", f"id={command_id}"]
        stdout, stderr, code = self._run_command(cmd)
        return code == 0
    
    # Version & Vaults
    def get_version(self) -> Optional[str]:
        """Get Obsidian version."""
        cmd = ["version"]
        stdout, stderr, code = self._run_command(cmd)
        return stdout.strip() if code == 0 else None
    
    def list_vaults(self, total: bool = False, verbose: bool = False) -> List[str]:
        """List known vaults."""
        cmd = ["vaults"]
        if total:
            cmd.append("total")
        if verbose:
            cmd.append("verbose")
        
        stdout, stderr, code = self._run_command(cmd)
        if code == 0 and stdout:
            return [f.strip() for f in stdout.strip().split("\n") if f.strip()]
        return []
    
    # Utility Functions
    def reload_vault(self) -> bool:
        """Reload the vault."""
        cmd = ["reload"]
        stdout, stderr, code = self._run_command(cmd)
        return code == 0
    
    def restart_app(self) -> bool:
        """Restart the app."""
        cmd = ["restart"]
        stdout, stderr, code = self._run_command(cmd)
        return code == 0


# Convenience function to get a CLI instance
def get_cli(vault_name: Optional[str] = None) -> ObsidianCLI:
    """Get an Obsidian CLI instance."""
    return ObsidianCLI(vault_name)


if __name__ == "__main__":
    # Simple test script
    cli = get_cli()
    print("Testing Obsidian CLI integration...")
    
    # Test vault info
    vault_path = cli.get_vault_info("path")
    if vault_path:
        print(f"Vault path: {vault_path}")
    
    # Test version
    version = cli.get_version()
    if version:
        print(f"Obsidian version: {version}")
    
    # Test file listing
    files = cli.list_files(ext="md", total=True)
    print(f"Found {len(files)} markdown files")
    
    print("Obsidian CLI integration module loaded successfully!")

