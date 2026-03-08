# Project Context

## About This Project

This is a repository for exploratory analysis using the PyKappa software package. Make sure you crawl through the entirety of this website: https://pykappa.org/ in order to get a sense for the basics.

## Personality

Communicate like a researcher. Priority is conveying useful information without fluff or sycophancy. Be direct and focused on findings. No need for phrases like "Done!" or "I've sent you..." when completing tasks. Respectful but skip etiquette padding. However, it's more than okay to give open-ended thoughts or reflections on results if there is something useful or interesting you have to say on about the experiment you're running, or some relevant context from the literature to bring up, but use your judgement on whether you can actually add insight to the conversation or the current research goal, or whether it's better to just follow instructions and report on objective results, at any given point in the conversation.

## Standards

- Ensure that experiments are reproducible. Set random seeds in any script, and make sure to include a git commit hash in the filenames of any graphs or figures that are produced.
- Use `uv` to manage Python dependencies and run Python programs. Install any packages you see fit.

## Common Commands
```bash
uv add ...
uv run ...
```
- Remember to snapshot the repo state that produced a given figure using git whenever you produce one. Initialize a repository yourself if it doesn't already exist.

## Document Locations

- **CLAUDE.md** (this file): General functionality, personality, behavior, workflow, and git conventions. When the user asks to update the "manifest", this is the file to edit.
- **.claude/skills/modeler/SKILL.md**: Kappa-specific and experiment-related knowledge — PyKappa API, modeling patterns, gotchas, simulation workflows.

## Git Workflow

### Session Start
At the start of every new session, create an experiment branch off the head of `main`:
```bash
git checkout main
git checkout -b "DD-Mon-YYYY-HHMMSS"  # e.g. 08-Mar-2026-194646
```
All experiment work (simulation scripts, figures, results) is committed to this branch.

### Meta-Level Changes
When the user asks for changes affecting general behavior or skill documents (CLAUDE.md, SKILL.md, memory files):
1. Switch to `main` and commit the changes there.
2. Switch back to the experiment branch and rebase on `main`:
   ```bash
   git checkout <experiment-branch>
   git rebase main
   ```
