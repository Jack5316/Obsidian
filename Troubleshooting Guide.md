# Troubleshooting Guide

## Overview

This guide provides solutions to common problems you may encounter when using your AI-powered Obsidian vault.

## Table of Contents

1. [Script Execution Issues](#script-execution-issues)
2. [API and Authentication Problems](#api-and-authentication-problems)
3. [Obsidian Plugin Issues](#obsidian-plugin-issues)
4. [System Performance Problems](#system-performance-problems)
5. [Content Acquisition Errors](#content-acquisition-errors)
6. [AI Processing Errors](#ai-processing-errors)
7. [File and Directory Issues](#file-and-directory-issues)
8. [Ralph Loop Plugin Problems](#ralph-loop-plugin-problems)
9. [Logs and Debugging](#logs-and-debugging)
10. [Advanced Troubleshooting](#advanced-troubleshooting)

---

## Script Execution Issues

### Problem: Script won't run (Permission Denied)

**Solution**:
```bash
chmod +x _scripts/*.py
```

### Problem: ModuleNotFoundError

**Solution**:
```bash
pip install -r _scripts/requirements.txt
```

### Problem: Command not found (python3 not recognized)

**Solution**:
- Verify Python installation: `python3 --version`
- If not found, install Python from https://www.python.org

### Problem: Script hangs or takes too long

**Solution**:
- Check internet connection
- Reduce parameters: `--days 7 --max 5`
- Check source API status (e.g., ArXiv downtime)

---

## API and Authentication Problems

### Problem: ARK_API_KEY error

**Solution**:
1. Check `.env` file:
   ```
   ARK_API_KEY=your-api-key-here
   ```
2. Verify API key is correct
3. Check API key permissions

### Problem: BearBlog authentication fails

**Solution**:
1. Verify credentials in `.env`:
   ```
   BEARBLOG_USER=your-email@example.com
   BEARBLOG_PASSWORD=your-password
   ```
2. Check BearBlog login page
3. Reset BearBlog password if needed

---

## Obsidian Plugin Issues

### Problem: Dataview queries not working

**Solution**:
1. Enable Dataview in Obsidian settings
2. Check query syntax
3. Refresh view with `Cmd/Ctrl + P` → "Dataview: Refresh all views"
4. Verify notes have frontmatter metadata

### Problem: Templater not working

**Solution**:
1. Enable Templater in Obsidian settings
2. Check template folder location
3. Verify template syntax
4. Check for conflicting plugins

---

## System Performance Problems

### Problem: Obsidian runs slowly

**Solution**:
1. Disable unused plugins
2. Reduce number of open tabs
3. Optimize Dataview queries
4. Rebuild Obsidian's search index

### Problem: Script execution is slow

**Solution**:
- Reduce `--days` and `--max` parameters
- Close unnecessary applications
- Run scripts during off-peak hours
- Consider increasing system resources

---

## Content Acquisition Errors

### Problem: No papers found (arxiv_digest.py)

**Solution**:
- Increase days parameter: `--days 30`
- Check arxiv_topics.txt for relevant keywords
- Verify ArXiv API is responsive
- Try different topic keywords

### Problem: YouTube video not summarized

**Solution**:
1. Check video URL is valid
2. Verify video has English subtitles
3. Check internet connection
4. Try again later (YouTube API rate limits)

### Problem: PDF not summarizing

**Solution**:
1. Check PDF file is not corrupted
2. Verify file has readable text
3. Reduce PDF file size if too large
4. Try converting to text first

---

## AI Processing Errors

### Problem: Summarization fails

**Solution**:
1. Check ARK_API_KEY is valid
2. Verify internet connection
3. Reduce input text length
4. Try again later (API rate limits)

### Problem: AI output is poor quality

**Solution**:
1. Try different prompt
2. Increase text context
3. Adjust model parameters in config.py
4. Verify input data quality

---

## File and Directory Issues

### Problem: File not found errors

**Solution**:
1. Check relative paths
2. Verify directory structure
3. Check file permissions
4. Restart Obsidian

### Problem: Notes not saving

**Solution**:
1. Check disk space
2. Verify vault location permissions
3. Check iCloud sync status (if using iCloud)
4. Try saving to different location

### Problem: Duplicate notes

**Solution**:
1. Check script deduplication logic
2. Clean up existing duplicates
3. Adjust script parameters
4. Verify source content uniqueness

---

## Ralph Loop Plugin Problems

### Problem: Loop won't start

**Solution**:
1. Check if another loop is active
2. Restart Obsidian
3. Disable and re-enable Ralph Loop plugin
4. Check plugin settings

### Problem: Loop execution fails

**Solution**:
1. View log file: `_logs/ralph-loop.log`
2. Check loop parameters
3. Verify script dependencies
4. Try simpler loop configuration

---

## Logs and Debugging

### Viewing Script Logs

```bash
# Check for errors in log files
grep -r "ERROR" _logs/

# View specific script log
cat _logs/arxiv_digest.log

# Check evolution system
cat _logs/evolution_log.json
```

### Common Log Messages

**Info Messages**: Normal operation
**Warning**: Potential issues, but operation continues
**Error**: Script failed to complete
**Critical**: System failure

### Debugging Scripts

```bash
# Run script with debugging
python3 -m traceback _scripts/arxiv_digest.py --days 1 --max 1

# Print verbose output
python3 _scripts/arxiv_digest.py --verbose
```

---

## Advanced Troubleshooting

### Problem: Script works sometimes but not always

**Solution**:
- Check for intermittent API issues
- Verify internet connection stability
- Check rate limiting on external APIs
- Monitor system resource usage

### Problem: System not evolving

**Solution**:
1. Check evolution log:
   ```bash
   cat _logs/evolution_log.json
   ```
2. Verify LEARNING_RATE in config.py
3. Check if TRACKER is initialized in config.py
4. Run self_evolution.py manually

### Problem: No insights being generated

**Solution**:
1. Check insights_repo.json:
   ```bash
   cat _logs/insights_repo.json
   ```
2. Verify insight_enhancement.py is working
3. Check note frontmatter tags
4. Run insight_enhancement.py on specific notes

---

## Contact Support

If you've tried all the solutions above and still have problems:

1. Collect all relevant error messages
2. Gather log files from `_logs/` directory
3. Note the steps to reproduce the issue
4. Include system information (OS, Python version, Obsidian version)

---

## Preventive Maintenance

### Daily Checks

```bash
# Verify dependencies are up to date
pip list --outdated | grep -E "(openai|youtube|requests)"

# Check log file sizes
ls -lh _logs/

# Verify vault structure
find . -name "*.md" | wc -l
```

### Weekly Maintenance

```bash
# Clean up old log files
find _logs/ -name "*.log" -mtime +7 -delete

# Optimize vault
python3 _scripts/self_evolution.py

# Create backup
zip -r AI_Vault_Backup_$(date +%Y%m%d).zip . -x "*.git/*"
```

---

*Last updated: 2026-02-16*
