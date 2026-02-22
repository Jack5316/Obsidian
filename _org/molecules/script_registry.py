"""Script registry molecule - Manages available scripts and metadata."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional
from enum import Enum


class ScriptCategory(Enum):
    """Categories for organizing scripts."""

    CONTENT_DIGEST = "content_digest"
    ANALYSIS = "analysis"
    PUBLISHING = "publishing"
    ENHANCEMENT = "enhancement"
    SYSTEM = "system"
    SKILL_WRAPPER = "skill_wrapper"


@dataclass
class ScriptInfo:
    """Information about a script."""

    name: str
    description: str
    category: ScriptCategory
    requires_args: bool = False
    recommended: bool = True
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ScriptRegistry:
    """Registry of all available automation scripts."""

    def __init__(self, scripts_dir: Path):
        self.scripts_dir = scripts_dir
        self._scripts: Dict[str, ScriptInfo] = {}
        self._load_default_scripts()

    def _load_default_scripts(self):
        """Load the default script definitions."""
        default_scripts = [
            # Content Digestion
            ScriptInfo(
                name="arxiv_digest.py",
                description="ArXiv paper curation and summarization",
                category=ScriptCategory.CONTENT_DIGEST,
                tags=["research", "papers", "ai"],
            ),
            ScriptInfo(
                name="hn_newsletter.py",
                description="Hacker News newsletter creation",
                category=ScriptCategory.CONTENT_DIGEST,
                tags=["news", "tech", "hackernews"],
            ),
            ScriptInfo(
                name="reddit_digest.py",
                description="Reddit content digestion and summarization",
                category=ScriptCategory.CONTENT_DIGEST,
                tags=["reddit", "social", "discussion"],
            ),
            ScriptInfo(
                name="tophub_news_simple.py",
                description="Simple TopHub news scraping",
                category=ScriptCategory.CONTENT_DIGEST,
                tags=["news", "china", "tophub"],
            ),
            ScriptInfo(
                name="twitter_capture.py",
                description="Twitter content capture and summarization",
                category=ScriptCategory.CONTENT_DIGEST,
                tags=["twitter", "social", "tweets"],
            ),
            # Analysis
            ScriptInfo(
                name="self_evolution.py",
                description="System self-improvement and analysis",
                category=ScriptCategory.ANALYSIS,
                tags=["system", "improvement", "evolution"],
            ),
            ScriptInfo(
                name="self_reflection.py",
                description="Self-reflection prompt generation",
                category=ScriptCategory.ANALYSIS,
                tags=["reflection", "introspection"],
            ),
            ScriptInfo(
                name="weekly_synthesis.py",
                description="Weekly content synthesis",
                category=ScriptCategory.ANALYSIS,
                tags=["weekly", "synthesis", "summary"],
            ),
            # Enhancement
            ScriptInfo(
                name="book_notes.py",
                description="Book notes management and generation",
                category=ScriptCategory.ENHANCEMENT,
                tags=["books", "notes", "reading"],
                requires_args=True,
            ),
            ScriptInfo(
                name="insight_enhancement.py",
                description="AI insight generation for notes",
                category=ScriptCategory.ENHANCEMENT,
                tags=["insights", "ai", "enhancement"],
            ),
            # Publishing (requires args)
            ScriptInfo(
                name="youtube_summary.py",
                description="YouTube video summarization",
                category=ScriptCategory.CONTENT_DIGEST,
                requires_args=True,
                recommended=False,
                tags=["video", "youtube"],
            ),
            ScriptInfo(
                name="bilibili_summary.py",
                description="Bilibili video summarization",
                category=ScriptCategory.CONTENT_DIGEST,
                requires_args=True,
                recommended=False,
                tags=["video", "bilibili", "china"],
            ),
            ScriptInfo(
                name="pdf_summarize.py",
                description="PDF document summarization",
                category=ScriptCategory.ENHANCEMENT,
                requires_args=True,
                recommended=False,
                tags=["pdf", "documents"],
            ),
            ScriptInfo(
                name="bearblog_publish.py",
                description="BearBlog publishing tool",
                category=ScriptCategory.PUBLISHING,
                requires_args=True,
                recommended=False,
                tags=["blog", "publishing"],
            ),
            # Skill Wrappers (for Claude Code /skill commands)
            ScriptInfo(
                name="org_skill.py",
                description="Organization skill - Run all scripts",
                category=ScriptCategory.SKILL_WRAPPER,
                tags=["skill", "organization", "automation"],
            ),
            ScriptInfo(
                name="tophub_skill.py",
                description="TopHub news scraper skill",
                category=ScriptCategory.SKILL_WRAPPER,
                tags=["skill", "tophub", "news"],
            ),
            ScriptInfo(
                name="tophub_news_simple_skill.py",
                description="Simple TopHub news skill with AI summaries",
                category=ScriptCategory.SKILL_WRAPPER,
                tags=["skill", "tophub", "news", "ai"],
            ),
            ScriptInfo(
                name="tophub_news_detailed_skill.py",
                description="Detailed TopHub news skill",
                category=ScriptCategory.SKILL_WRAPPER,
                recommended=False,
                tags=["skill", "tophub", "news", "detailed"],
            ),
            # Atomic Design System Skills (new)
            ScriptInfo(
                name="atomic_org_skill.py",
                description="Atomic design organization skill",
                category=ScriptCategory.SKILL_WRAPPER,
                tags=["skill", "atomic", "organization", "workflow"],
            ),
            ScriptInfo(
                name="daily_skill.py",
                description="Daily workflow skill (atomic design)",
                category=ScriptCategory.SKILL_WRAPPER,
                tags=["skill", "atomic", "daily", "workflow"],
            ),
            ScriptInfo(
                name="weekly_skill.py",
                description="Weekly workflow skill (atomic design)",
                category=ScriptCategory.SKILL_WRAPPER,
                tags=["skill", "atomic", "weekly", "workflow"],
            ),
            # Skill Package Analysis
            ScriptInfo(
                name="skill_package_analysis.py",
                description="Analyze skill status, health, completeness, and pipelines",
                category=ScriptCategory.ANALYSIS,
                tags=["analysis", "skills", "health", "maintenance"],
            ),
            ScriptInfo(
                name="package_skill.py",
                description="Package analysis skill - /package",
                category=ScriptCategory.SKILL_WRAPPER,
                tags=["skill", "package", "analysis", "skills", "health"],
            ),
            ScriptInfo(
                name="skill_package_analysis_skill.py",
                description="Skill package analysis skill wrapper (legacy)",
                category=ScriptCategory.SKILL_WRAPPER,
                recommended=False,
                tags=["skill", "analysis", "skills", "health"],
            ),
            # Raw TopHub scripts (non-skill versions)
            ScriptInfo(
                name="tophub_news.py",
                description="TopHub news scraper (raw)",
                category=ScriptCategory.CONTENT_DIGEST,
                recommended=False,
                tags=["tophub", "news"],
            ),
            ScriptInfo(
                name="tophub_news_detailed.py",
                description="Detailed TopHub news scraper (raw)",
                category=ScriptCategory.CONTENT_DIGEST,
                recommended=False,
                tags=["tophub", "news", "detailed"],
            ),
            ScriptInfo(
                name="flomo_send.py",
                description="Send notes to flomo floating notes via webhook",
                category=ScriptCategory.ENHANCEMENT,
                requires_args=True,
                tags=["flomo", "notes", "capture", "webhook"],
            ),
        ]

        for script in default_scripts:
            self._scripts[script.name] = script

    def get_script(self, name: str) -> Optional[ScriptInfo]:
        """Get a script by name."""
        return self._scripts.get(name)

    def list_scripts(
        self,
        category: Optional[ScriptCategory] = None,
        recommended_only: bool = False,
    ) -> List[ScriptInfo]:
        """List all scripts, optionally filtered."""
        scripts = list(self._scripts.values())

        if category:
            scripts = [s for s in scripts if s.category == category]

        if recommended_only:
            scripts = [s for s in scripts if s.recommended]

        return scripts

    def get_by_category(self) -> Dict[ScriptCategory, List[ScriptInfo]]:
        """Get scripts organized by category."""
        categorized: Dict[ScriptCategory, List[ScriptInfo]] = {}
        for script in self._scripts.values():
            if script.category not in categorized:
                categorized[script.category] = []
            categorized[script.category].append(script)
        return categorized

    def register_script(self, script_info: ScriptInfo) -> None:
        """Register a new script."""
        self._scripts[script_info.name] = script_info
