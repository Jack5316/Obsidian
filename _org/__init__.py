"""
AI Vault Automation - Atomic Design System
===========================================

A modular automation system using atomic design principles.

Structure:
- atoms: Core utilities (config, logger, script runner)
- molecules: Composite components (registry, execution engine)
- organisms: Complete modules (digesters, analyzers)
- templates: Workflow orchestrators (daily, weekly)
- pages: CLI interfaces
"""

__version__ = "1.0.0"
__author__ = "AI Vault System"

from .atoms import VaultConfig, ExecutionLogger, ScriptRunner
from .molecules import ScriptRegistry, ExecutionEngine
from .organisms import ContentDigester, AnalysisTools, EnhancementTools
from .templates import DailyWorkflow, WeeklyWorkflow, CustomWorkflow

__all__ = [
    "VaultConfig",
    "ExecutionLogger",
    "ScriptRunner",
    "ScriptRegistry",
    "ExecutionEngine",
    "ContentDigester",
    "AnalysisTools",
    "EnhancementTools",
    "DailyWorkflow",
    "WeeklyWorkflow",
    "CustomWorkflow",
]
