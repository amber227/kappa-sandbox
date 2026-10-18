# Protein Digest Generation Workflow

## Current Status

**Coverage**: 18/97 proteins (18.6%)
- Generated: 18 protein digests
- Missing: 79 proteins
- Total interactions: 133 (previously 137, updated database)
- Interactions blocked by missing proteins: 93

**Completed Batches**:
- Batch 1: AXIN2, CSNK1A1, BTRC, DVL2 (≥3 interactions)
- Batch 2: DVL3, BCL9, EP300, CREBBP, LRP5 (2 interactions)

**Remaining High-Priority Proteins** (2 interactions each):
- Batch 3: FZD5, FZD8, DKK1, WNT3, HIPK2
- Batch 4: TP53, ZNRF3, RNF43, RSPO1

## Workflow Steps

### 1. Identify Missing Proteins

```bash
.venv/bin/python find_missing_digests.py
```

This generates `missing_digests.json` with prioritized list.

### 2. Generate Agent Commands

```bash
.venv/bin/python generate_missing_digests.py --min-interactions 2 --max-concurrent 5
```

This outputs Task invocations for Claude Code to execute in parallel batches.

### 3. Execute Digest Generation

Copy the Task commands and send them in a single message to spawn agents in parallel.

Example for Batch 3:
```
Task(subagent_type="protein-info-digest",
     description="Generate FZD5 digest",
     prompt="Generate a comprehensive protein information digest for human FZD5 (Frizzled-5) following the standardized schema. Create both FZD5_digest.json and update interactions.json with all discovered interactions. Keep your final summary brief (max 500 words).")
Task(subagent_type="protein-info-digest",
     description="Generate FZD8 digest",
     prompt="Generate a comprehensive protein information digest for human FZD8 (Frizzled-8) following the standardized schema. Create both FZD8_digest.json and update interactions.json with all discovered interactions. Keep your final summary brief (max 500 words).")
Task(subagent_type="protein-info-digest",
     description="Generate DKK1 digest",
     prompt="Generate a comprehensive protein information digest for human DKK1 (Dickkopf-related protein 1) following the standardized schema. Create both DKK1_digest.json and update interactions.json with all discovered interactions. Keep your final summary brief (max 500 words).")
Task(subagent_type="protein-info-digest",
     description="Generate WNT3 digest",
     prompt="Generate a comprehensive protein information digest for human WNT3 (Proto-oncogene Wnt-3) following the standardized schema. Create both WNT3_digest.json and update interactions.json with all discovered interactions. Keep your final summary brief (max 500 words).")
Task(subagent_type="protein-info-digest",
     description="Generate HIPK2 digest",
     prompt="Generate a comprehensive protein information digest for human HIPK2 (Homeodomain-interacting protein kinase 2) following the standardized schema. Create both HIPK2_digest.json and update interactions.json with all discovered interactions. Keep your final summary brief (max 500 words).")
```

### 4. Commit Results

After each batch completes:
```bash
git add *_digest.json interactions.json missing_digests.json
git commit -m "Add N protein digests (Batch X/Y)"
```

### 5. Compile Kappa Model

After adding digests, regenerate the Kappa model:
```bash
.venv/bin/python compile_kappa.py
```

This produces:
- `wnt_compiled.ka` - Updated Kappa model
- `wnt_compiled_provenance.json` - Provenance tracking

### 6. Iterate

Repeat steps 1-5 to expand coverage progressively.

## Priority Guidelines

**High Priority** (≥2 interactions):
- Core pathway components
- Proteins involved in multiple interactions
- Rate-limiting components

**Medium Priority** (1 interaction):
- Pathway-specific regulators
- Tissue-specific factors
- Disease-associated variants

**Low Priority**:
- Peripheral interactors
- Context-specific modulators

## Notes

- Agent rate limits may require waiting between batches
- Keep batches to ≤5 proteins to avoid timeouts
- Use `--min-interactions` flag to filter by priority
- DVL3 previously timed out but succeeded on retry
- Interactions.json is automatically merged; no manual consolidation needed
