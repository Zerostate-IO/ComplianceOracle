# LaTeX Reporting Specification (Deferred)

> **STATUS: DEFERRED** - This specification defines a future epic. No implementation
> should occur in the current 90-day execution backlog. This document serves as a
> planning artifact for a future enhancement cycle.

## 1. Scope

LaTeX reporting would enable generation of professional, publication-ready compliance
reports suitable for:

- Executive summaries and board presentations
- Auditor-ready documentation packages
- Formal compliance attestation packages
- Client deliverables requiring branded formatting

The LaTeX renderer would consume the same data sources as existing JSON and Markdown
exports, ensuring feature parity while adding typesetting capabilities.

### In Scope

| Feature | Description |
|---------|-------------|
| Cover page generation | Framework name, organization, date, version |
| Table of contents | Auto-generated from section hierarchy |
| Control summary tables | Status counts, completion percentage |
| Detailed control entries | Full control text, implementation status, evidence |
| Evidence appendices | Linked evidence items with source references |
| Gap analysis section | Unaddressed controls with remediation priority |
| Hybrid intelligence metadata | LLM enrichment fields when present (analysis_mode, llm_used, degrade_reason) |
| Cross-framework mappings | Related controls from other frameworks |
| PDF compilation | Optional pdflatex/xelatex invocation |

### Report Variants

1. **Executive Summary** - High-level posture overview, no detailed control text
2. **Full Assessment** - Complete control documentation with evidence
3. **Gap-Focused** - Only unaddressed and partial controls
4. **Audit Package** - Full assessment plus evidence appendices

## 2. Data Contract

The LaTeX renderer must consume data from the existing export pipeline. No new data
structures are required, but certain fields become mandatory for LaTeX output.

### Required Export Fields

The `export_documentation()` tool already produces the following structure:

```python
{
    "export_date": str,           # ISO 8601 timestamp
    "framework_id": str,          # e.g., "nist-csf-2.0"
    "summary": {
        "total_controls": int,
        "implemented": int,
        "partial": int,
        "planned": int,
        "not_applicable": int,
        "not_addressed": int,
        "completion_percentage": float,
    },
    "controls": [
        {
            "control_id": str,
            "status": str,           # ControlStatus enum value
            "implementation_summary": str | None,
            "owner": str | None,
            "last_updated": str | None,
            "evidence": [
                {
                    "type": str,
                    "source": str,
                    "description": str,
                    "line_start": int | None,
                    "line_end": int | None,
                }
            ] | None,
            "intelligence_metadata": {  # Optional, when hybrid mode used
                "analysis_mode": str,   # "deterministic" | "hybrid"
                "llm_used": bool,
                "degrade_reason": str | None,
                "llm_rationale": str | None,
                "llm_context": str | None,
                "policy_violations": list[str] | None,
                "latency_ms": int | None,
            } | None,
        }
    ],
    "gaps": [  # Only when include_gaps=True
        {
            "control_id": str,
            "control_name": str,
            "description": str,
            "priority": str,  # "high" | "medium" | "low"
        }
    ]
}
```

### Data Source Reference

| Data Element | Source File | Function |
|-------------|-------------|----------|
| Control documentation | `state.py:204` | `export()` |
| Export options | `documentation.py:171` | `export_documentation()` |
| Control status enum | `schemas.py` | `ControlStatus` |
| Intelligence metadata | `assessment/contracts.py` | `IntelligenceMetadata` |

### Extension Points

For LaTeX-specific needs, the following optional fields may be added later:

```python
# Optional fields for LaTeX customization (future)
{
    "latex_config": {
        "template": str,           # Template name or path
        "document_class": str,     # article, report, book
        "geometry": str,           # margins, paper size
        "font_family": str,        # Latin Modern, Times, etc.
        "logo_path": str | None,   # Organization logo
        "color_scheme": dict,      # Primary/secondary colors
    }
}
```

These are NOT required for the initial implementation and should be added via
configuration rather than state mutation.

## 3. Template Contract

LaTeX templates must follow a structured contract to ensure consistent output
and maintainability.

### Template Structure

```
templates/latex/
├── base.tex                    # Base document class and packages
├── sections/
│   ├── cover.tex              # Title page template
│   ├── toc.tex                # Table of contents
│   ├── summary.tex            # Executive summary table
│   ├── controls.tex           # Control documentation loop
│   ├── gaps.tex               # Gap analysis section
│   ├── evidence.tex           # Evidence appendix template
│   └── mappings.tex           # Cross-framework mapping table
└── variants/
    ├── executive.tex          # Executive summary only
    ├── full.tex               # Complete documentation
    ├── gaps.tex               # Gap-focused report
    └── audit.tex              # Audit package with appendices
```

### Template Variables

Templates must accept the following Jinja2-style variables:

| Variable | Type | Description |
|----------|------|-------------|
| `{{ export_date }}` | str | ISO 8601 export timestamp |
| `{{ framework_id }}` | str | Framework identifier |
| `{{ framework_name }}` | str | Human-readable framework name |
| `{{ organization }}` | str | Organization name (config) |
| `{{ summary }}` | dict | ComplianceSummary fields |
| `{{ controls }}` | list | List of ControlDocumentation |
| `{{ gaps }}` | list | Gap analysis results |
| `{{ metadata }}` | dict | Hybrid intelligence metadata |

### LaTeX Package Requirements

The base template should declare these packages:

```latex
\documentclass[11pt,a4paper]{report}

% Required packages
\usepackage{geometry}        % Page layout
\usepackage{graphicx}        % Images/logos
\usepackage{booktabs}        % Professional tables
\usepackage{longtable}       % Multi-page tables
\usepackage{hyperref}        % Cross-references
\usepackage{xcolor}          % Status coloring
\usepackage{enumitem}        % List customization
\usepackage{tcolorbox}       % Highlighted boxes for gaps
\usepackage{fontspec}        % Font selection (XeLaTeX)
```

### Status Color Mapping

| Status | LaTeX Color | Hex Code |
|--------|-------------|----------|
| implemented | ForestGreen | #228B22 |
| partial | Goldenrod | #DAA520 |
| planned | SteelBlue | #4682B4 |
| not_applicable | Gray | #808080 |
| not_addressed | Crimson | #DC143C |

## 4. Non-Goals

The following are explicitly out of scope for the LaTeX reporting epic:

### Technical Non-Goals

- **No real-time rendering**: LaTeX compilation is a batch operation
- **No browser-based preview**: PDF is the output format
- **No WYSIWYG editor**: Templates are text-based
- **No pandoc dependency**: Direct LaTeX generation only
- **No custom LaTeX commands**: Use standard packages only
- **No Windows-specific paths**: POSIX path handling only

### Feature Non-Goals

- **No automated distribution**: Reports are generated on demand
- **No digital signatures**: PDF signing is a separate concern
- **No version comparison**: Diff views are out of scope
- **No internationalization**: English-only templates initially
- **No custom branding designer**: Use configuration files
- **No report scheduling**: CLI/programmatic invocation only

### Data Non-Goals

- **No new data collection**: Use existing export data only
- **No assessment modifications**: LaTeX does not change control status
- **No evidence embedding**: Evidence is referenced, not embedded
- **No external data sources**: Only compliance state data

## 5. Acceptance Gates

The LaTeX reporting epic is considered complete when all gates pass:

### G1: Core Generation

- [ ] `export_documentation(format="latex")` produces valid `.tex` file
- [ ] Generated LaTeX compiles without errors using pdflatex
- [ ] Generated LaTeX compiles without errors using xelatex
- [ ] All four report variants generate successfully

### G2: Content Accuracy

- [ ] Cover page includes framework name, organization, date
- [ ] Table of contents matches section hierarchy
- [ ] Summary statistics match JSON export exactly
- [ ] Control entries include all documentation fields
- [ ] Evidence references link correctly to appendix
- [ ] Gap analysis section includes priority ordering

### G3: Hybrid Intelligence Integration

- [ ] Reports include `analysis_mode` field when present
- [ ] Reports indicate `llm_used` status appropriately
- [ ] Reports display `degrade_reason` when degradation occurred
- [ ] LLM rationale/context rendered in designated section
- [ ] Policy violations flagged in output when present

### G4: Quality Assurance

- [ ] Generated PDFs pass accessibility checks (PDF/A)
- [ ] Table formatting survives multi-page breaks
- [ ] Long control descriptions wrap correctly
- [ ] Evidence references remain readable after compilation
- [ ] Unicode characters render correctly (XeLaTeX)

### G5: Performance

- [ ] Report generation completes in <5 seconds for 100 controls
- [ ] LaTeX compilation completes in <30 seconds for full audit package
- [ ] Memory usage stays under 500MB during generation
- [ ] No temporary files left after compilation

### G6: Documentation

- [ ] User documentation for LaTeX export added to README
- [ ] Template customization guide created
- [ ] Troubleshooting section for common LaTeX errors
- [ ] Example outputs committed to repository

## 6. Implementation Notes

### Entry Criteria

Before starting this epic:

1. R-001 through R-008 complete (stabilization)
2. Coverage ≥60% on documentation module
3. Export metadata parity (T9) complete
4. No open P1 bugs

### Estimated Effort

| Component | Effort | Dependencies |
|-----------|--------|--------------|
| Template structure | M | None |
| Data mapping layer | S | Export API stable |
| Variant implementations | M | Templates |
| PDF compilation integration | M | Templates |
| Testing suite | M | All components |
| Documentation | S | All components |

**Total: L (Large)** - Estimated 3-4 weeks with dedicated focus.

### Risk Factors

1. **LaTeX distribution dependency**: Users must have texlive/mactex installed
2. **Template maintenance**: LaTeX syntax errors are cryptic
3. **Cross-platform paths**: Windows vs POSIX handling in templates
4. **Unicode edge cases**: Some characters may require font fallbacks

### Alternative Considered: Pandoc

Pandoc was considered as an intermediate format but rejected because:

- Adds runtime dependency on pandoc binary
- Less control over precise formatting
- Markdown-to-LaTeX conversion loses semantic structure
- Debugging requires understanding two transformation layers

Direct LaTeX generation provides better control and simpler debugging.

---

## Appendix A: Example LaTeX Output Fragment

```latex
\section{Compliance Summary}

\begin{tabular}{lr}
\toprule
\textbf{Metric} & \textbf{Value} \\
\midrule
Total Controls & 108 \\
Implemented & 45 \\
Partial & 23 \\
Planned & 12 \\
Not Applicable & 8 \\
Not Addressed & 20 \\
\midrule
Completion & 64.8\% \\
\bottomrule
\end{tabular}

\section{Documented Controls}

\subsection{Implemented}

\subsubsection{PR.AC-01: Identity and Access Control}

\textbf{Status:} \textcolor{ForestGreen}{Implemented}

\textbf{Owner:} Security Team

\textbf{Implementation Summary:}

Multi-factor authentication is enforced for all administrative access
to production systems. Service accounts use hardware security keys...

\textbf{Evidence:}
\begin{itemize}
\item \texttt{config/auth.yml} (lines 10-45): MFA configuration
\item \texttt{policies/access.md}: Access control policy document
\end{itemize}

\textbf{Analysis Metadata:}

\begin{tabular}{ll}
Analysis Mode & Hybrid \\
LLM Used & Yes \\
Model & llama3.2 \\
\end{tabular}
```

---

## Appendix B: Configuration Schema

```yaml
# .compliance-oracle/latex-config.yaml
organization: "Acme Corporation"
template: "audit"
output:
  format: "pdf"  # latex | pdf
  compiler: "xelatex"  # pdflatex | xelatex | lualatex
  output_dir: "./reports"
branding:
  logo_path: "./assets/logo.png"
  primary_color: "#1E3A5F"
  secondary_color: "#4A90A4"
sections:
  cover: true
  toc: true
  summary: true
  controls: true
  gaps: true
  evidence_appendix: true
  mappings: false
```

---

*Document Version: 1.0*
*Created: 2026-03-01*
*Status: Deferred - No implementation in current epic*
