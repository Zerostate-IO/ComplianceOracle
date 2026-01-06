# Compliance Oracle MCP Server — Design Document

**Version:** 1.0 Draft  
**Date:** January 4, 2026  
**Author:** Derp / N2con Inc.

---

## 1. Executive Summary

The Compliance Oracle is an MCP (Model Context Protocol) server designed to evaluate design documents and code against compliance frameworks (starting with NIST CSF 2.0). Unlike existing NIST tools focused on organizational maturity assessment, this agent serves as a **code review auditor** — identifying non-compliance without providing fixes.

### Core Principle
> "Identify what isn't compliant and why. Never suggest fixes."

---

## 2. Use Cases

### Operating Modes

The Compliance Oracle supports **three distinct operating modes**:

| Mode | Consumer | Purpose |
|------|----------|---------|
| **Agent Mode** | Coding agents, design agents, automated pipelines | Evaluate designs/code for compliance violations |
| **Interactive Mode** | Human + LLM chat | Q&A, guidance, self-assessments, framework exploration |
| **Documentation Mode** | Human + LLM chat, CI/CD | Record compliance, link evidence, export for audits |

This multi-mode design creates a complete compliance lifecycle: **evaluate → document → export**.

---

### Agent Mode Use Cases

**Primary:** A developer or architect submits a design document describing a new feature. The Compliance Oracle:
1. Receives the design document text
2. Identifies relevant compliance controls via RAG
3. Evaluates the design against those controls
4. Returns a list of findings: what's non-compliant and why

**Secondary:**
- Evaluate code files for a specific module
- Batch evaluation of related files (all files in a feature branch)
- Manual invocation via `/compliance-check` command
- Called programmatically by other agents (coding agents, design agents)

---

### Interactive Mode Use Cases

**Framework Exploration:**
- "What controls are in the PROTECT function?"
- "Explain PR.AC-01 in plain English"
- "What's the difference between CSF and 800-53?"

**Implementation Guidance:**
- "How do I implement multi-factor authentication to satisfy PR.AC-03?"
- "What are best practices for DE.CM-01 network monitoring?"
- "Give me a checklist for the Data Security category"

**Self-Assessment:**
- "Help me assess our compliance with the IDENTIFY function"
- "Am I compliant with PR.DS-01 if I use AES-256 for disk encryption?"
- "What questions should I ask to evaluate our incident response?"

**Research & Planning:**
- "Which controls should a small business prioritize?"
- "Map our current security tools to CSF controls"
- "What controls address ransomware protection?"

---

### Documentation Mode Use Cases

**Recording Compliance:**
- "Document that we satisfy PR.DS-02 with TLS 1.3 on all API connections"
- "Mark PR.AC-03 as implemented — we have MFA everywhere"
- "Link our Terraform config as evidence for infrastructure controls"

**Evidence Collection:**
- "Attach this screenshot showing our Azure MFA settings"
- "Point to nginx.conf lines 42-58 as evidence for TLS configuration"
- "Add our penetration test report as evidence for ID.RA-01"

**Guided Interviews:**
- "Walk me through the access control questions"
- "Let's document our incident response posture"
- "Interview me about our data protection controls"

**Reporting & Export:**
- "Generate a compliance status report"
- "Export our documentation for the SOC2 auditor"
- "What's our current compliance percentage for CSF?"

**Cross-Framework Analysis:**
- "We're CSF compliant — what more do we need for SOC2?"
- "Map our CSF documentation to ISO 27001"
- "Show me the gap between our current state and 800-171"

---

## 3. Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CONSUMERS                                    │
├───────────────────┬───────────────────┬─────────────────────────────┤
│    AGENT MODE     │  INTERACTIVE MODE │    DOCUMENTATION MODE       │
│                   │                   │                             │
│ • OpenCode Agents │ • Claude.ai + MCP │ • Claude.ai + MCP           │
│ • Design Agents   │ • ChatGPT + MCP   │ • CI/CD pipelines           │
│ • CI/CD Pipelines │ • Local LLM + MCP │ • Audit prep workflows      │
│ • Manual command  │ • Any MCP client  │ • GRC portal replacement    │
└───────────────────┴───────────────────┴─────────────────────────────┘
                                 │
                                 │ MCP Protocol (stdio or SSE)
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   COMPLIANCE ORACLE MCP SERVER                       │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                         MCP TOOLS                               │ │
│  ├──────────────┬──────────────┬──────────────┬───────────────────┤ │
│  │ AGENT MODE   │ INTERACTIVE  │ DOCUMENTATION│  FRAMEWORK MGMT   │ │
│  │              │    MODE      │     MODE     │                   │ │
│  │ • evaluate_  │ • search_    │ • document_  │ • manage_         │ │
│  │   compliance │   controls   │   compliance │   framework       │ │
│  │              │ • get_       │ • link_      │ • import_         │ │
│  │              │   guidance   │   evidence   │   framework       │ │
│  │              │ • assess_    │ • interview_ │ • get_framework_  │ │
│  │              │   control    │   control    │   gap             │ │
│  │              │ • compare_   │ • get_       │                   │ │
│  │              │   frameworks │   documentation                  │ │
│  │              │ • get_       │ • export_    │                   │ │
│  │              │   control_   │   documentation                  │ │
│  │              │   context    │              │                   │ │
│  ├──────────────┴──────────────┴──────────────┴───────────────────┤ │
│  │                        SHARED TOOLS                             │ │
│  │  • get_control_details  • list_controls  • list_frameworks     │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                 │                                    │
│                                 ▼                                    │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      CORE ENGINE                                │ │
│  │                                                                 │ │
│  │  • RAG search for controls                                     │ │
│  │  • LLM client for evaluation/assessment                        │ │
│  │  • Documentation state management                              │ │
│  │  • Cross-framework mapping engine                              │ │
│  │  • Framework import/validation                                 │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                 │                                    │
│       ┌─────────────┬──────────┴────────┬─────────────┐            │
│       ▼             ▼                   ▼             ▼            │
│  ┌─────────┐  ┌───────────┐  ┌────────────────┐  ┌─────────┐      │
│  │ChromaDB │  │ Framework │  │  Compliance    │  │  LLM    │      │
│  │(Vectors)│  │   Data    │  │  State (JSON)  │  │ Client  │      │
│  │         │  │           │  │                │  │         │      │
│  │• CSF 2.0│  │• Schemas  │  │• Documented    │  │• Claude │      │
│  │• 800-53 │  │• Mappings │  │  controls      │  │• OpenAI │      │
│  │• 800-171│  │• Metadata │  │• Evidence links│  │• Ollama │      │
│  │• SOC2   │  │           │  │• Status        │  │         │      │
│  │• ISO    │  │           │  │                │  │         │      │
│  └─────────┘  └───────────┘  └────────────────┘  └─────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Design Principles

**1. LLM-Optional Tools**
Some tools require LLM reasoning (like `evaluate_compliance`), while others are pure data retrieval (like `search_controls`). This maximizes flexibility.

**2. Git-Native Documentation**
Compliance state is stored in JSON files that live alongside your code. Version control your compliance posture.

**3. Framework Extensibility**
New frameworks can be added via structured import. LLM-assisted parsing for unstructured sources (PDFs, docs).

**4. Cross-Framework Intelligence**
Built-in mappings between frameworks enable "what more do I need?" analysis.

---

## 4. MCP Tool Specifications

### 4.1 `evaluate_compliance`

**Purpose:** Primary tool for compliance evaluation

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "content": {
      "type": "string",
      "description": "Design document text or code to evaluate"
    },
    "content_type": {
      "type": "string",
      "enum": ["design_doc", "code", "architecture"],
      "default": "design_doc"
    },
    "framework": {
      "type": "string",
      "enum": ["nist-csf-2.0", "nist-800-53", "nist-800-171"],
      "default": "nist-csf-2.0"
    },
    "focus_areas": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Optional: Limit evaluation to specific functions/categories (e.g., ['PR', 'DE'])"
    }
  },
  "required": ["content"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "framework": {"type": "string"},
    "findings_count": {"type": "integer"},
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "control_id": {"type": "string"},
          "control_name": {"type": "string"},
          "function": {"type": "string"},
          "category": {"type": "string"},
          "finding": {"type": "string"},
          "rationale": {"type": "string"},
          "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
        }
      }
    },
    "evaluated_controls": {"type": "integer"},
    "compliant_areas": {"type": "array", "items": {"type": "string"}}
  }
}
```

**Example Output:**
```json
{
  "framework": "nist-csf-2.0",
  "findings_count": 2,
  "findings": [
    {
      "control_id": "PR.AC-01",
      "control_name": "Identity Management, Authentication, and Access Control",
      "function": "PROTECT",
      "category": "Identity Management, Authentication, and Access Control",
      "finding": "Design does not specify identity verification for privileged access",
      "rationale": "CSF PR.AC-01 requires that identities and credentials for authorized users, services, and hardware are managed. The design describes an admin interface but lacks specification for how admin identities are verified or managed.",
      "severity": "high"
    },
    {
      "control_id": "DE.CM-01",
      "control_name": "Continuous Monitoring",
      "function": "DETECT",
      "category": "Continuous Monitoring",
      "finding": "No monitoring or logging strategy defined",
      "rationale": "CSF DE.CM-01 requires networks and network services to be monitored for potential cybersecurity events. The design omits logging, alerting, or monitoring considerations.",
      "severity": "medium"
    }
  ],
  "evaluated_controls": 15,
  "compliant_areas": ["Data security encryption at rest", "Backup strategy mentioned"]
}
```

### 4.2 `get_control_details`

**Purpose:** Retrieve full details for a specific control

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "control_id": {
      "type": "string",
      "description": "Control identifier (e.g., 'PR.AC-01', 'GV.OC-01')"
    },
    "framework": {
      "type": "string",
      "default": "nist-csf-2.0"
    }
  },
  "required": ["control_id"]
}
```

**Output:** Full control text, implementation examples, related controls

### 4.3 `list_controls`

**Purpose:** Browse the framework hierarchy

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "framework": {"type": "string", "default": "nist-csf-2.0"},
    "function": {"type": "string", "description": "Filter by function (GV, ID, PR, DE, RS, RC)"},
    "category": {"type": "string", "description": "Filter by category ID"}
  }
}
```

### 4.4 `list_frameworks`

**Purpose:** Show available compliance frameworks

**Output:**
```json
{
  "frameworks": [
    {"id": "nist-csf-2.0", "name": "NIST Cybersecurity Framework 2.0", "status": "active"},
    {"id": "nist-800-53", "name": "NIST SP 800-53 Rev 5", "status": "planned"},
    {"id": "nist-800-171", "name": "NIST SP 800-171 Rev 2", "status": "planned"}
  ]
}
```

---

## 5. Interactive Mode Tools

These tools are designed for human-LLM chat sessions where users want to explore frameworks, get guidance, and perform self-assessments.

### 5.1 `search_controls`

**Purpose:** Semantic search across all framework controls — the RAG capability exposed directly

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Natural language search query"
    },
    "framework": {
      "type": "string",
      "description": "Limit search to specific framework (optional)"
    },
    "limit": {
      "type": "integer",
      "default": 10,
      "description": "Maximum results to return"
    }
  },
  "required": ["query"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {"type": "string"},
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "control_id": {"type": "string"},
          "control_name": {"type": "string"},
          "description": {"type": "string"},
          "framework": {"type": "string"},
          "relevance_score": {"type": "number"}
        }
      }
    }
  }
}
```

**Example:**
```
User: "Find controls about encryption"

Results:
- PR.DS-01: Data-at-rest confidentiality (0.92)
- PR.DS-02: Data-in-transit confidentiality (0.89)
- PR.DS-10: Data-in-use confidentiality (0.85)
```

### 5.2 `get_guidance`

**Purpose:** Detailed implementation guidance for a specific control

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "control_id": {
      "type": "string",
      "description": "Control identifier (e.g., 'PR.AC-03')"
    },
    "context": {
      "type": "string",
      "description": "Optional context about the organization or environment"
    },
    "detail_level": {
      "type": "string",
      "enum": ["summary", "detailed", "checklist"],
      "default": "detailed"
    }
  },
  "required": ["control_id"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "control_id": {"type": "string"},
    "control_name": {"type": "string"},
    "description": {"type": "string"},
    "implementation_guidance": {
      "type": "object",
      "properties": {
        "overview": {"type": "string"},
        "key_activities": {"type": "array", "items": {"type": "string"}},
        "common_technologies": {"type": "array", "items": {"type": "string"}},
        "considerations": {"type": "array", "items": {"type": "string"}},
        "checklist": {"type": "array", "items": {"type": "string"}}
      }
    },
    "related_controls": {"type": "array", "items": {"type": "string"}},
    "informative_references": {"type": "array", "items": {"type": "string"}}
  }
}
```

### 5.3 `assess_control`

**Purpose:** Interactive self-assessment for a single control — returns assessment questions and evaluates responses

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "control_id": {
      "type": "string",
      "description": "Control to assess"
    },
    "mode": {
      "type": "string",
      "enum": ["get_questions", "evaluate_response"],
      "description": "Get assessment questions or evaluate a response"
    },
    "response": {
      "type": "string",
      "description": "User's response describing their implementation (for evaluate_response mode)"
    }
  },
  "required": ["control_id", "mode"]
}
```

**Output (get_questions mode):**
```json
{
  "control_id": "PR.AC-03",
  "control_name": "Authentication",
  "assessment_questions": [
    "What authentication methods are used for user access?",
    "Is multi-factor authentication implemented? For which user types?",
    "How are service accounts authenticated?",
    "What authentication protocols are in use (SAML, OAuth, etc.)?",
    "How are failed authentication attempts handled?"
  ],
  "maturity_indicators": {
    "basic": "Single-factor authentication with password policies",
    "intermediate": "MFA for privileged users, SSO implemented",
    "advanced": "MFA for all users, adaptive authentication, passwordless options"
  }
}
```

**Output (evaluate_response mode):**
```json
{
  "control_id": "PR.AC-03",
  "assessment_result": {
    "status": "partial",
    "maturity_level": "intermediate",
    "strengths": [
      "MFA implemented for admin accounts",
      "SSO in place for major applications"
    ],
    "gaps": [
      "MFA not required for standard users",
      "Service account authentication relies on static credentials"
    ],
    "recommendations": [
      "Extend MFA to all user accounts",
      "Implement managed identities or certificate-based auth for service accounts"
    ]
  }
}
```

### 5.4 `compare_frameworks`

**Purpose:** Compare controls across frameworks or show mappings

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "control_id": {
      "type": "string",
      "description": "Control to find mappings for"
    },
    "source_framework": {
      "type": "string",
      "description": "Framework of the source control"
    },
    "target_framework": {
      "type": "string",
      "description": "Framework to map to (optional - if omitted, shows all mappings)"
    }
  },
  "required": ["control_id"]
}
```

**Output:**
```json
{
  "source": {
    "framework": "nist-csf-2.0",
    "control_id": "PR.AC-03",
    "description": "Users, services, and hardware are authenticated"
  },
  "mappings": [
    {
      "framework": "nist-800-53",
      "controls": ["IA-2", "IA-3", "IA-8"],
      "relationship": "equivalent"
    },
    {
      "framework": "nist-800-171",
      "controls": ["3.5.1", "3.5.2"],
      "relationship": "subset"
    },
    {
      "framework": "iso-27001",
      "controls": ["A.9.2.1", "A.9.4.2"],
      "relationship": "related"
    }
  ]
}
```

### 5.5 `get_control_context`

**Purpose:** Get full context for a control including related controls, parent/child relationships, and cross-references

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "control_id": {"type": "string"},
    "include_siblings": {"type": "boolean", "default": true},
    "include_related": {"type": "boolean", "default": true}
  },
  "required": ["control_id"]
}
```

**Output:**
```json
{
  "control": {
    "id": "PR.DS-01",
    "description": "The confidentiality, integrity, and availability of data-at-rest are protected"
  },
  "hierarchy": {
    "function": {"id": "PR", "name": "PROTECT"},
    "category": {"id": "PR.DS", "name": "Data Security"}
  },
  "siblings": [
    {"id": "PR.DS-02", "description": "Data-in-transit protection"},
    {"id": "PR.DS-10", "description": "Data-in-use protection"},
    {"id": "PR.DS-11", "description": "Backups"}
  ],
  "related_controls": [
    {"id": "ID.AM-05", "relationship": "depends_on", "reason": "Must know critical data to protect it"},
    {"id": "PR.AC-05", "relationship": "supports", "reason": "Access control protects data confidentiality"},
    {"id": "RC.RP-03", "relationship": "supported_by", "reason": "Backup verification ensures recoverability"}
  ]
}

---

## 6. Documentation Mode Tools

These tools enable recording compliance state, linking evidence, and exporting for audits.

### 6.1 `document_compliance`

**Purpose:** Record that a control is satisfied (or partially satisfied) by your implementation

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "control_id": {
      "type": "string",
      "description": "Control identifier (e.g., 'PR.DS-02')"
    },
    "framework": {
      "type": "string",
      "default": "nist-csf-2.0"
    },
    "status": {
      "type": "string",
      "enum": ["implemented", "partial", "planned", "not_applicable", "not_addressed"],
      "description": "Implementation status"
    },
    "implementation_summary": {
      "type": "string",
      "description": "Brief description of how the control is satisfied"
    },
    "evidence": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {"type": "string", "enum": ["config", "code", "screenshot", "document", "url", "other"]},
          "path": {"type": "string", "description": "File path or URL"},
          "line_range": {"type": "array", "items": {"type": "integer"}, "description": "Optional: [start, end] lines"},
          "description": {"type": "string"}
        }
      }
    },
    "owner": {
      "type": "string",
      "description": "Team or person responsible"
    },
    "notes": {
      "type": "string",
      "description": "Additional notes or context"
    }
  },
  "required": ["control_id", "status"]
}
```

**Example:**
```json
{
  "control_id": "PR.DS-02",
  "status": "implemented",
  "implementation_summary": "All API traffic uses TLS 1.3 with mutual authentication between services",
  "evidence": [
    {
      "type": "config",
      "path": "infrastructure/nginx.conf",
      "line_range": [42, 58],
      "description": "TLS 1.3 configuration with strong cipher suites"
    },
    {
      "type": "code",
      "path": "src/api/client.py",
      "line_range": [15, 25],
      "description": "Certificate pinning implementation"
    }
  ],
  "owner": "platform-team"
}
```

### 6.2 `link_evidence`

**Purpose:** Add evidence to an already-documented control

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "control_id": {"type": "string"},
    "framework": {"type": "string", "default": "nist-csf-2.0"},
    "evidence": {
      "type": "object",
      "properties": {
        "type": {"type": "string"},
        "path": {"type": "string"},
        "line_range": {"type": "array"},
        "description": {"type": "string"}
      },
      "required": ["type", "path", "description"]
    }
  },
  "required": ["control_id", "evidence"]
}
```

### 6.3 `interview_control`

**Purpose:** Guided Q&A to document a control — like a GRC portal questionnaire but conversational

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "control_id": {
      "type": "string",
      "description": "Control to interview about (or category like 'PR.AC' for multiple)"
    },
    "framework": {"type": "string", "default": "nist-csf-2.0"},
    "mode": {
      "type": "string",
      "enum": ["start", "submit", "skip"],
      "description": "Start interview, submit answers, or skip control"
    },
    "answers": {
      "type": "object",
      "description": "For submit mode: answers keyed by question ID"
    }
  },
  "required": ["control_id", "mode"]
}
```

**Output (start mode):**
```json
{
  "control_id": "PR.DS-01",
  "control_name": "Data-at-rest protection",
  "description": "The confidentiality, integrity, and availability of data-at-rest are protected",
  "questions": [
    {
      "id": "q1",
      "question": "What encryption is used for data at rest?",
      "type": "text",
      "examples": ["AES-256", "BitLocker", "LUKS", "Cloud-managed keys"]
    },
    {
      "id": "q2",
      "question": "Where is encryption applied?",
      "type": "multi_select",
      "options": ["Databases", "File storage", "Backups", "Laptops/endpoints", "Cloud storage"]
    },
    {
      "id": "q3",
      "question": "How are encryption keys managed?",
      "type": "text",
      "examples": ["HSM", "Cloud KMS", "Manual key management"]
    },
    {
      "id": "q4",
      "question": "Can you point to evidence of this configuration?",
      "type": "evidence_link"
    }
  ],
  "maturity_indicators": {
    "basic": "Some encryption in place, manual key management",
    "intermediate": "Encryption across most systems, centralized key management",
    "advanced": "Full encryption coverage, HSM-backed keys, automated rotation"
  }
}
```

**Output (submit mode):**
```json
{
  "control_id": "PR.DS-01",
  "status": "documented",
  "recorded": {
    "implementation_summary": "AES-256-GCM encryption on databases and cloud storage via Azure SSE",
    "coverage": ["Databases", "Cloud storage", "Backups"],
    "key_management": "Azure Key Vault with customer-managed keys"
  },
  "evidence_linked": 2,
  "assessed_maturity": "intermediate",
  "follow_up_recommendations": [
    "Consider extending encryption to endpoint devices",
    "Document key rotation procedures"
  ]
}
```

### 6.4 `get_documentation`

**Purpose:** Retrieve current compliance documentation state

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "framework": {"type": "string"},
    "function": {"type": "string", "description": "Filter by function (e.g., 'PR')"},
    "category": {"type": "string", "description": "Filter by category (e.g., 'PR.DS')"},
    "status": {"type": "string", "description": "Filter by status"},
    "include_evidence": {"type": "boolean", "default": false}
  }
}
```

**Output:**
```json
{
  "framework": "nist-csf-2.0",
  "generated_at": "2026-01-04T15:30:00Z",
  "summary": {
    "total_controls": 106,
    "implemented": 45,
    "partial": 23,
    "planned": 15,
    "not_applicable": 8,
    "not_addressed": 15,
    "completion_percentage": 64
  },
  "by_function": {
    "GV": {"total": 17, "implemented": 8, "partial": 5},
    "ID": {"total": 17, "implemented": 10, "partial": 4},
    "PR": {"total": 14, "implemented": 12, "partial": 2},
    "DE": {"total": 8, "implemented": 5, "partial": 3},
    "RS": {"total": 7, "implemented": 4, "partial": 2},
    "RC": {"total": 6, "implemented": 6, "partial": 0}
  },
  "controls": [
    {
      "control_id": "PR.DS-01",
      "status": "implemented",
      "summary": "AES-256 encryption on all storage",
      "evidence_count": 3,
      "owner": "platform-team",
      "last_updated": "2026-01-04"
    }
  ]
}
```

### 6.5 `export_documentation`

**Purpose:** Export compliance documentation in various formats

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "format": {
      "type": "string",
      "enum": ["markdown", "json", "csv", "html", "pdf"],
      "default": "markdown"
    },
    "framework": {"type": "string", "default": "nist-csf-2.0"},
    "include_evidence": {"type": "boolean", "default": true},
    "include_gaps": {"type": "boolean", "default": true},
    "output_path": {"type": "string", "description": "Where to write the file"}
  },
  "required": ["format"]
}
```

**Example Markdown Output (COMPLIANCE_DOC.md):**
```markdown
# Compliance Documentation
**Framework:** NIST Cybersecurity Framework 2.0  
**Generated:** 2026-01-04  
**Overall Status:** 64% Complete (68/106 controls addressed)

## Executive Summary
| Function | Implemented | Partial | Planned | Gaps |
|----------|-------------|---------|---------|------|
| GOVERN   | 8           | 5       | 2       | 2    |
| IDENTIFY | 10          | 4       | 2       | 1    |
| PROTECT  | 12          | 2       | 0       | 0    |
| DETECT   | 5           | 3       | 0       | 0    |
| RESPOND  | 4           | 2       | 1       | 0    |
| RECOVER  | 6           | 0       | 0       | 0    |

---

## PR: PROTECT

### PR.DS-01: Data-at-Rest Protection
**Status:** ✅ Implemented  
**Owner:** Platform Team  
**Last Updated:** 2026-01-04

**Implementation:**  
All data at rest uses AES-256-GCM encryption via Azure Storage Service Encryption.
Customer databases use TDE with customer-managed keys in Azure Key Vault.

**Evidence:**
| Type | Location | Description |
|------|----------|-------------|
| Config | `terraform/storage.tf:25-40` | Storage encryption settings |
| Config | `terraform/keyvault.tf:12-30` | Key Vault CMK configuration |
| Screenshot | `evidence/azure-encryption.png` | Azure portal encryption view |

---

### PR.DS-02: Data-in-Transit Protection
**Status:** ✅ Implemented  
...
```

---

## 7. Framework Management Tools

These tools handle downloading, adding, updating, and mapping compliance frameworks.

### 7.1 `manage_framework`

**Purpose:** Download, update, or remove compliance frameworks

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": ["list", "download", "update", "remove", "validate"],
      "description": "Action to perform"
    },
    "framework_id": {
      "type": "string",
      "description": "Framework identifier (for download/update/remove)"
    },
    "source": {
      "type": "string",
      "description": "For download: URL or 'official' for built-in sources"
    }
  },
  "required": ["action"]
}
```

**Available Official Sources:**
```json
{
  "official_sources": {
    "nist-csf-2.0": "https://csrc.nist.gov/extensions/nudp/services/json/csf/download",
    "nist-800-53-r5": "https://csrc.nist.gov/extensions/nudp/services/json/sp800-53/download",
    "nist-800-171-r2": "https://csrc.nist.gov/extensions/nudp/services/json/sp800-171/download",
    "cis-controls-v8": "requires-license",
    "iso-27001-2022": "requires-purchase",
    "soc2-trust-principles": "community-maintained"
  }
}
```

**Output (list action):**
```json
{
  "installed_frameworks": [
    {
      "id": "nist-csf-2.0",
      "name": "NIST Cybersecurity Framework 2.0",
      "version": "2.0",
      "controls": 106,
      "installed": "2026-01-01",
      "last_updated": "2026-01-04",
      "status": "current"
    }
  ],
  "available_frameworks": [
    {
      "id": "nist-800-53-r5",
      "name": "NIST SP 800-53 Rev 5",
      "source": "official",
      "controls": 1189
    },
    {
      "id": "soc2-trust-principles",
      "name": "SOC 2 Trust Service Principles",
      "source": "community",
      "controls": 64
    }
  ]
}
```

### 7.2 `import_framework`

**Purpose:** Import a custom framework from structured data or use LLM to parse unstructured documents

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Name for the framework"
    },
    "source_type": {
      "type": "string",
      "enum": ["json", "csv", "pdf", "url", "text"],
      "description": "Type of source material"
    },
    "source_path": {
      "type": "string",
      "description": "Path or URL to source material"
    },
    "use_llm_parsing": {
      "type": "boolean",
      "default": false,
      "description": "Use LLM to extract structure from unstructured docs"
    },
    "parent_framework": {
      "type": "string",
      "description": "Optional: base framework this extends (for company-specific additions)"
    }
  },
  "required": ["name", "source_type", "source_path"]
}
```

**Expected JSON Schema for Direct Import:**
```json
{
  "framework": {
    "id": "custom-framework-id",
    "name": "Custom Framework Name",
    "version": "1.0"
  },
  "controls": [
    {
      "id": "CF-01",
      "name": "Control Name",
      "description": "What this control requires",
      "category": "Category Name",
      "keywords": ["keyword1", "keyword2"],
      "implementation_guidance": "How to implement this",
      "mappings": {
        "nist-csf-2.0": ["PR.AC-01", "PR.AC-02"],
        "nist-800-53": ["AC-2", "AC-3"]
      }
    }
  ]
}
```

**LLM-Assisted Import Flow:**
```
1. User provides PDF/document
2. System extracts text
3. LLM identifies control structure (hierarchy, IDs, descriptions)
4. LLM generates structured JSON
5. User reviews/confirms
6. Framework is ingested into ChromaDB
```

### 7.3 `get_framework_gap`

**Purpose:** Analyze what's needed to achieve compliance with a target framework given your current compliance state

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "current_framework": {
      "type": "string",
      "description": "Framework you're currently compliant with"
    },
    "target_framework": {
      "type": "string",
      "description": "Framework you want to achieve"
    },
    "use_documented_state": {
      "type": "boolean",
      "default": true,
      "description": "Use your documented compliance state (vs assuming full compliance)"
    }
  },
  "required": ["current_framework", "target_framework"]
}
```

**Output:**
```json
{
  "analysis": {
    "current_framework": "nist-csf-2.0",
    "target_framework": "soc2-trust-principles",
    "your_compliance_level": "64%",
    "mapping_coverage": "78%"
  },
  "summary": {
    "already_covered": 50,
    "partially_covered": 8,
    "gaps": 6,
    "total_target_controls": 64
  },
  "already_covered": [
    {
      "target_control": "CC6.1",
      "target_name": "Logical and Physical Access Controls",
      "covered_by": ["PR.AC-01", "PR.AC-03", "PR.AC-05"],
      "your_status": "implemented"
    }
  ],
  "partially_covered": [
    {
      "target_control": "CC7.2",
      "target_name": "System Monitoring",
      "covered_by": ["DE.CM-01", "DE.CM-03"],
      "your_status": "partial",
      "gap_description": "Network monitoring implemented, but endpoint monitoring incomplete"
    }
  ],
  "gaps": [
    {
      "target_control": "CC4.1",
      "target_name": "COSO Principle 16: Internal Communication",
      "no_mapping_from": "nist-csf-2.0",
      "recommendation": "Requires new documentation around internal security communication processes",
      "effort_estimate": "medium"
    }
  ],
  "effort_summary": {
    "low_effort_items": 3,
    "medium_effort_items": 2,
    "high_effort_items": 1,
    "estimated_completion": "4-6 weeks with current resources"
  }
}
```

**Example Conversation:**
```
User: "We're CSF 2.0 compliant. What do we need for SOC2?"

Claude: [calls get_framework_gap with current="nist-csf-2.0", target="soc2-trust-principles"]

        "Good news — your CSF 2.0 work covers about 78% of SOC2 requirements.
        
        ✅ Already Covered (50 controls):
        Your access control, encryption, and monitoring work maps directly.
        
        ⚠️ Partially Covered (8 controls):
        A few areas need enhancement, mainly around...
        
        ❌ Gaps (6 controls):
        SOC2 has some unique requirements around:
        - CC4.1: Internal communication processes
        - CC5.3: Change management board documentation
        ...
        
        Estimated effort: 4-6 weeks to close the gaps.
        
        Want me to detail any specific gap?"
```

### 7.4 `build_mapping`

**Purpose:** Create or update mappings between frameworks (can be LLM-assisted)

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "source_framework": {"type": "string"},
    "target_framework": {"type": "string"},
    "use_llm": {
      "type": "boolean",
      "default": true,
      "description": "Use LLM to suggest mappings"
    },
    "review_mode": {
      "type": "boolean",
      "default": true,
      "description": "Require human review before saving"
    }
  },
  "required": ["source_framework", "target_framework"]
}
```

---

## Tool Summary

### All Tools by Mode

| Tool | Mode | LLM Required | Purpose |
|------|------|--------------|---------|
| **Agent Mode** ||||
| `evaluate_compliance` | Agent | Yes | Evaluate design/code for violations |
| **Interactive Mode** ||||
| `search_controls` | Interactive | No | Semantic search across frameworks |
| `get_guidance` | Interactive | No* | Implementation guidance for a control |
| `assess_control` | Interactive | Yes | Self-assessment with evaluation |
| `compare_frameworks` | Interactive | No | Cross-framework mappings |
| `get_control_context` | Interactive | No | Related controls and hierarchy |
| **Documentation Mode** ||||
| `document_compliance` | Documentation | No | Record control implementation |
| `link_evidence` | Documentation | No | Attach evidence to controls |
| `interview_control` | Documentation | Yes | Guided Q&A collection |
| `get_documentation` | Documentation | No | View current compliance state |
| `export_documentation` | Documentation | No | Export for auditors/GRC |
| **Framework Management** ||||
| `manage_framework` | Management | No | Download/update/remove frameworks |
| `import_framework` | Management | Yes* | Import custom frameworks |
| `get_framework_gap` | Management | No | Cross-framework gap analysis |
| `build_mapping` | Management | Yes | Create framework mappings |
| **Shared Tools** ||||
| `get_control_details` | Shared | No | Lookup specific control details |
| `list_controls` | Shared | No | Browse framework hierarchy |
| `list_frameworks` | Shared | No | Show available frameworks |

*LLM optional or only needed for enhanced features

---

## 8. Framework Data Structure

### 8.1 NIST CSF 2.0 Hierarchy

```
Framework: NIST CSF 2.0
├── Function: GOVERN (GV)
│   ├── Category: Organizational Context (GV.OC)
│   │   ├── GV.OC-01: Organizational mission understood
│   │   ├── GV.OC-02: Internal/external stakeholders understood
│   │   ├── GV.OC-03: Legal/regulatory requirements understood
│   │   ├── GV.OC-04: Critical objectives determined
│   │   └── GV.OC-05: Outcomes/dependencies determined
│   ├── Category: Risk Management Strategy (GV.RM)
│   ├── Category: Roles, Responsibilities & Authorities (GV.RR)
│   ├── Category: Policy (GV.PO)
│   ├── Category: Oversight (GV.OV)
│   └── Category: Cybersecurity Supply Chain Risk Management (GV.SC)
│
├── Function: IDENTIFY (ID)
│   ├── Category: Asset Management (ID.AM)
│   ├── Category: Risk Assessment (ID.RA)
│   └── Category: Improvement (ID.IM)
│
├── Function: PROTECT (PR)
│   ├── Category: Identity Management, Auth & Access Control (PR.AC)
│   ├── Category: Awareness and Training (PR.AT)
│   ├── Category: Data Security (PR.DS)
│   ├── Category: Platform Security (PR.PS)
│   └── Category: Technology Infrastructure Resilience (PR.IR)
│
├── Function: DETECT (DE)
│   ├── Category: Continuous Monitoring (DE.CM)
│   └── Category: Adverse Event Analysis (DE.AE)
│
├── Function: RESPOND (RS)
│   ├── Category: Incident Management (RS.MA)
│   ├── Category: Incident Analysis (RS.AN)
│   ├── Category: Incident Response Reporting & Communication (RS.CO)
│   └── Category: Incident Mitigation (RS.MI)
│
└── Function: RECOVER (RC)
    ├── Category: Incident Recovery Plan Execution (RC.RP)
    └── Category: Incident Recovery Communication (RC.CO)
```

### 8.2 Data Schema (JSON)

Each control is stored as:

```json
{
  "id": "PR.AC-01",
  "framework": "nist-csf-2.0",
  "function": {
    "id": "PR",
    "name": "PROTECT",
    "description": "Safeguards to manage the organization's cybersecurity risks are used"
  },
  "category": {
    "id": "PR.AC",
    "name": "Identity Management, Authentication, and Access Control",
    "description": "Access to physical and logical assets is limited to authorized users..."
  },
  "subcategory": {
    "id": "PR.AC-01",
    "description": "Identities and credentials for authorized users, services, and hardware are managed by the organization"
  },
  "implementation_examples": [
    "Use multi-factor authentication for privileged accounts",
    "Implement centralized identity management",
    "Review access rights periodically"
  ],
  "informative_references": [
    "NIST SP 800-53 AC-2",
    "NIST SP 800-53 IA-4",
    "CIS CSC 5.1"
  ],
  "keywords": ["identity", "authentication", "credentials", "access", "MFA", "IAM", "users", "privileges"]
}
```

---

## 9. RAG Implementation

### 9.1 Vector Database: ChromaDB

**Why ChromaDB:**
- File-based, zero configuration
- Pure Python, easy deployment
- Handles thousands of chunks efficiently
- Backup = copy folder

### 9.2 Chunking Strategy

Each **subcategory** becomes one chunk with rich metadata:

```python
{
    "id": "PR.AC-01",
    "text": "Identities and credentials for authorized users, services, and hardware are managed by the organization. Implementation examples include: Use multi-factor authentication...",
    "metadata": {
        "framework": "nist-csf-2.0",
        "function_id": "PR",
        "function_name": "PROTECT",
        "category_id": "PR.AC",
        "category_name": "Identity Management, Authentication, and Access Control",
        "control_id": "PR.AC-01"
    }
}
```

### 9.3 Embedding Model

**Recommendation:** `all-MiniLM-L6-v2` via sentence-transformers
- Fast, efficient
- Good semantic understanding for compliance text
- Works offline

### 9.4 Search Strategy

1. **Semantic search** on design document content
2. **Retrieve top-k** relevant controls (k=10-20)
3. **Re-rank** based on keyword overlap
4. **Filter** by focus_areas if specified

---

## 10. Evaluation Engine

### 10.1 System Prompt (Auditor Persona)

```markdown
You are a compliance auditor evaluating technical designs against the {framework_name} framework.

## Your Role
- Identify design decisions that may violate compliance requirements
- Cite specific controls being potentially violated
- Explain WHY something is a compliance concern
- Assess severity based on risk impact

## You Must NOT
- Suggest fixes or remediation steps
- Rewrite code or designs
- Provide implementation guidance
- Make assumptions about what "should" be done

## Output Requirements
For each finding:
1. Control ID and name
2. Clear description of what's missing or non-compliant
3. Rationale explaining why this matters for compliance
4. Severity assessment (critical/high/medium/low)

## Context
You have been provided with relevant controls from {framework_name}.
Evaluate the following content against these controls.

Only report genuine compliance gaps. Do not manufacture findings where none exist.
```

### 10.2 Evaluation Flow

```
┌─────────────────┐
│  Input Content  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  RAG Search     │ ──── Retrieve relevant controls
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Build Prompt   │ ──── System prompt + controls + content
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Evaluation │ ──── Claude/GPT-4/etc.
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parse & Return │ ──── Structured findings JSON
└─────────────────┘
```

---

## 11. LLM Configuration

### 11.1 Model Selection

| Tier | Model | Use Case | Notes |
|------|-------|----------|-------|
| **Primary** | Claude Sonnet 4 | Standard evaluations | Best reasoning/cost balance |
| **Deep Analysis** | Claude Opus 4 | Critical reviews | Maximum reasoning depth |
| **Quick Scan** | Claude Haiku 4 | Rapid checks | Fast, lower cost |
| **Fallback** | GPT-4o | If Claude unavailable | Good alternative |
| **Local** | Llama 3.1 70B | Air-gapped environments | Requires beefy hardware |

### 11.2 Configuration File

```yaml
# config.yaml
compliance_oracle:
  default_framework: nist-csf-2.0
  
  llm:
    provider: anthropic  # anthropic | openai | ollama | openrouter
    model: claude-sonnet-4-20250514
    temperature: 0.1  # Low for consistency
    max_tokens: 4096
  
  quick_scan:
    provider: anthropic
    model: claude-haiku-4-20250414
  
  rag:
    embedding_model: all-MiniLM-L6-v2
    top_k: 15
    similarity_threshold: 0.5
  
  data_path: ./data/frameworks
  chroma_path: ./data/chroma
```

---

## 12. Integration with Oh-My-Opencode

### 12.1 Manual Command

Add command `/compliance-check`:

```bash
/compliance-check [framework] <content>
```

Examples:
```bash
/compliance-check                           # Check current file
/compliance-check nist-csf-2.0             # Specify framework
/compliance-check --design design.md       # Check specific file
```

### 12.2 Agent Integration

Other agents call the MCP tool:

```python
# From another agent
result = await mcp_client.call_tool(
    "compliance_oracle",
    "evaluate_compliance",
    {
        "content": design_document_text,
        "framework": "nist-csf-2.0",
        "content_type": "design_doc"
    }
)

if result["findings_count"] > 0:
    # Present findings to user
    for finding in result["findings"]:
        print(f"⚠️ {finding['control_id']}: {finding['finding']}")
```

---

## 13. Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Set up MCP server skeleton (FastMCP or TypeScript SDK)
- [ ] Download and parse NIST CSF 2.0 data
- [ ] Create JSON data structure with keywords for RAG
- [ ] Ingest into ChromaDB
- [ ] Implement shared tools: `get_control_details`, `list_controls`, `list_frameworks`
- [ ] Basic testing

### Phase 2: Interactive Mode Tools (Week 3)
- [ ] Implement `search_controls` (RAG search exposed)
- [ ] Implement `get_control_context` (hierarchy/relationships)
- [ ] Implement `get_guidance` (implementation guidance)
- [ ] Test interactive mode with Claude/ChatGPT + MCP

### Phase 3: Evaluation Engine (Week 4-5)
- [ ] Implement RAG search pipeline for evaluation
- [ ] Create evaluation system prompt (auditor persona)
- [ ] Wire up LLM client abstraction (Claude, OpenAI, Ollama)
- [ ] Implement `evaluate_compliance` tool
- [ ] Implement `assess_control` tool
- [ ] Output formatting and structured responses
- [ ] Test against sample design docs

### Phase 4: Documentation Mode (Week 6-7)
- [ ] Design compliance state JSON schema
- [ ] Implement `document_compliance` tool
- [ ] Implement `link_evidence` tool
- [ ] Implement `interview_control` with question generation
- [ ] Implement `get_documentation` tool
- [ ] Implement `export_documentation` (Markdown, JSON, CSV)
- [ ] Test documentation workflow end-to-end

### Phase 5: Framework Management (Week 8-9)
- [ ] Implement `manage_framework` (download, update, validate)
- [ ] Implement `import_framework` with JSON/CSV support
- [ ] Add LLM-assisted parsing for unstructured imports
- [ ] Build initial cross-framework mappings (CSF ↔ 800-53)
- [ ] Implement `get_framework_gap` analysis
- [ ] Implement `build_mapping` tool
- [ ] Implement `compare_frameworks` tool

### Phase 6: Integration & Polish (Week 10)
- [ ] Oh-My-Opencode command integration
- [ ] Configuration file support (LLM selection, etc.)
- [ ] Documentation for agent integration
- [ ] Error handling and edge cases
- [ ] Performance optimization

### Phase 7: Expand Frameworks (Ongoing)
- [ ] Ingest NIST 800-53 Rev 5
- [ ] Ingest NIST 800-171 Rev 2
- [ ] Add SOC 2 Trust Service Principles
- [ ] Add ISO 27001:2022 (if licensing allows)
- [ ] Build comprehensive cross-framework mappings
- [ ] Community framework contributions

---

## 14. File Structure

```
compliance-oracle/
├── README.md
├── config.yaml
├── pyproject.toml / package.json
│
├── src/
│   ├── server.py              # MCP server entry point
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   │
│   │   │  # Agent Mode Tools
│   │   ├── evaluate.py        # evaluate_compliance
│   │   │
│   │   │  # Interactive Mode Tools
│   │   ├── search.py          # search_controls
│   │   ├── guidance.py        # get_guidance
│   │   ├── assess.py          # assess_control
│   │   ├── compare.py         # compare_frameworks
│   │   ├── context.py         # get_control_context
│   │   │
│   │   │  # Documentation Mode Tools
│   │   ├── document.py        # document_compliance, link_evidence
│   │   ├── interview.py       # interview_control
│   │   ├── export.py          # get_documentation, export_documentation
│   │   │
│   │   │  # Framework Management Tools
│   │   ├── framework_mgmt.py  # manage_framework, import_framework
│   │   ├── gap_analysis.py    # get_framework_gap
│   │   ├── mapping.py         # build_mapping
│   │   │
│   │   │  # Shared Tools
│   │   ├── lookup.py          # get_control_details, list_controls
│   │   └── frameworks.py      # list_frameworks
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── embeddings.py      # Embedding generation
│   │   ├── search.py          # ChromaDB search
│   │   └── ingest.py          # Framework data ingestion
│   │
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── engine.py          # Evaluation orchestration
│   │   ├── prompts.py         # System prompts (auditor, assessor, interviewer)
│   │   └── llm_client.py      # LLM abstraction layer
│   │
│   ├── documentation/
│   │   ├── __init__.py
│   │   ├── state.py           # Compliance state management
│   │   ├── evidence.py        # Evidence linking and validation
│   │   ├── export_formats.py  # Markdown, CSV, HTML, PDF exporters
│   │   └── interview_flows.py # Interview question generation
│   │
│   ├── frameworks/
│   │   ├── __init__.py
│   │   ├── manager.py         # Framework download/update/validation
│   │   ├── importer.py        # Custom framework import (JSON, CSV, LLM-parsed)
│   │   ├── mapper.py          # Cross-framework mapping engine
│   │   └── gap_analyzer.py    # Gap analysis calculations
│   │
│   └── models/
│       ├── __init__.py
│       ├── schemas.py         # Pydantic/dataclass schemas
│       ├── framework.py       # Framework data models
│       ├── compliance.py      # Compliance state models
│       └── evidence.py        # Evidence models
│
├── data/
│   ├── frameworks/
│   │   ├── nist-csf-2.0.json
│   │   ├── nist-800-53.json
│   │   ├── nist-800-171.json
│   │   ├── soc2-trust-principles.json
│   │   └── custom/            # User-imported frameworks
│   │
│   ├── mappings/              # Cross-framework mappings
│   │   ├── csf-to-800-53.json
│   │   ├── csf-to-800-171.json
│   │   ├── csf-to-soc2.json
│   │   └── csf-to-iso27001.json
│   │
│   ├── compliance/            # Your compliance documentation (git-tracked)
│   │   ├── state.json         # Current compliance state
│   │   └── history/           # State snapshots for audit trail
│   │
│   ├── evidence/              # Evidence files
│   │   ├── screenshots/
│   │   ├── configs/           # Exported config snippets
│   │   └── documents/
│   │
│   ├── exports/               # Generated reports
│   │   ├── COMPLIANCE_DOC.md
│   │   └── reports/
│   │
│   └── chroma/                # Vector DB storage
│
├── scripts/
│   ├── ingest_csf.py          # Initial data ingestion
│   ├── ingest_800_53.py       # 800-53 ingestion
│   ├── build_mappings.py      # Generate cross-framework mappings
│   ├── download_frameworks.py # Fetch framework data from official sources
│   └── migrate_state.py       # Migrate compliance state between versions
│
└── tests/
    ├── test_evaluate.py
    ├── test_search.py
    ├── test_assess.py
    ├── test_document.py
    ├── test_interview.py
    ├── test_gap_analysis.py
    ├── test_rag.py
    └── fixtures/
        ├── sample_designs/
        │   ├── compliant_design.md
        │   └── non_compliant_design.md
        └── sample_state/
            └── test_compliance_state.json
```

---

## 15. Data Sources

### NIST CSF 2.0
- **Source:** https://csrc.nist.gov/projects/cybersecurity-framework
- **Format:** JSON/Excel available via NIST CPRT
- **License:** Public domain (US Government work)
- **Alternative:** https://csf.tools/framework/csf-v2-0/ (structured reference)

### NIST 800-53 Rev 5
- **Source:** https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final
- **Format:** JSON, XML, Excel available
- **License:** Public domain

### NIST 800-171 Rev 2/3
- **Source:** https://csrc.nist.gov/publications/detail/sp/800-171/rev-2/final
- **Format:** PDF, Excel
- **License:** Public domain

---

## 16. Prior Art / Related Projects

### Existing NIST CSF MCP Server
- **Repo:** https://github.com/rocklambros/nist-csf-2-mcp-server
- **Purpose:** Organizational maturity assessment (740 questions, scoring, dashboards)
- **Difference from this project:** 
  - That tool: "How mature is our organization?"
  - This tool: "Is this specific design/code compliant?"

### Nisify
- **Repo:** https://github.com/clay-good/nisify
- **Purpose:** Evidence aggregation from cloud platforms
- **Difference:** Automated evidence collection vs. design review

---

## 17. Open Questions

### Technical
1. **Caching:** Should we cache evaluation results for repeated content?
2. **Incremental evaluation:** Support diff-based evaluation (what changed since last check)?
3. **Confidence scoring:** Should findings include confidence levels?
4. **Conflict resolution:** How to handle conflicts between framework requirements?

### Documentation Mode
5. **State versioning:** How to handle compliance state migrations when schema changes?
6. **Evidence validation:** Should we verify evidence files still exist/haven't changed?
7. **Multi-tenant:** Support multiple clients/projects in one installation?
8. **Audit trail:** How much history to retain for compliance state changes?

### Framework Management
9. **Mapping confidence:** How to indicate mapping quality (exact match vs. similar)?
10. **Community frameworks:** Accept community-contributed framework definitions?
11. **Framework licensing:** How to handle frameworks that require purchase (ISO)?
12. **Update notifications:** Alert users when official frameworks are updated?

### Integration
13. **CI/CD integration:** GitHub Actions / GitLab CI examples?
14. **GRC export formats:** Which GRC portals to prioritize for export compatibility?
15. **Evidence auto-discovery:** Can we auto-link evidence from code analysis?

---

## 18. Success Criteria

The Compliance Oracle is successful when:

### Agent Mode
1. ✅ Correctly identifies obvious compliance gaps in test designs
2. ✅ Does NOT suggest fixes (maintains auditor role)
3. ✅ Returns structured, actionable findings
4. ✅ Responds within 10 seconds for typical design documents
5. ✅ Can be called programmatically by other agents

### Interactive Mode
6. ✅ Users can explore frameworks conversationally
7. ✅ Guidance is practical and actionable
8. ✅ Self-assessments produce useful maturity insights

### Documentation Mode
9. ✅ Compliance state survives across sessions (persistence works)
10. ✅ Evidence linking is intuitive
11. ✅ Exports are auditor-ready (no manual cleanup needed)
12. ✅ Interview mode captures complete control documentation

### Framework Management
13. ✅ New frameworks can be added without code changes
14. ✅ Cross-framework gap analysis is accurate
15. ✅ Mappings are transparent and auditable

### MSP Use Case
16. ✅ Can baseline a new client's compliance in <2 hours
17. ✅ Ongoing documentation takes <5 minutes per change
18. ✅ Audit prep reduced from days to hours

---

## Appendix A: NIST CSF 2.0 Complete Control List

### GOVERN (GV) — 17 subcategories
- GV.OC-01 through GV.OC-05 (Organizational Context)
- GV.RM-01 through GV.RM-07 (Risk Management Strategy)
- GV.RR-01 through GV.RR-04 (Roles, Responsibilities, Authorities)
- GV.PO-01 through GV.PO-02 (Policy)
- GV.OV-01 through GV.OV-03 (Oversight)
- GV.SC-01 through GV.SC-10 (Supply Chain Risk Management)

### IDENTIFY (ID) — 17 subcategories
- ID.AM-01 through ID.AM-08 (Asset Management)
- ID.RA-01 through ID.RA-10 (Risk Assessment)
- ID.IM-01 through ID.IM-04 (Improvement)

### PROTECT (PR) — 14 subcategories
- PR.AC-01 through PR.AC-06 (Access Control)
- PR.AT-01 through PR.AT-02 (Awareness & Training)
- PR.DS-01 through PR.DS-11 (Data Security)
- PR.PS-01 through PR.PS-06 (Platform Security)
- PR.IR-01 through PR.IR-04 (Infrastructure Resilience)

### DETECT (DE) — 8 subcategories
- DE.CM-01 through DE.CM-09 (Continuous Monitoring)
- DE.AE-01 through DE.AE-08 (Adverse Event Analysis)

### RESPOND (RS) — 7 subcategories
- RS.MA-01 through RS.MA-05 (Incident Management)
- RS.AN-01 through RS.AN-08 (Incident Analysis)
- RS.CO-01 through RS.CO-03 (Reporting & Communication)
- RS.MI-01 through RS.MI-02 (Mitigation)

### RECOVER (RC) — 6 subcategories
- RC.RP-01 through RC.RP-06 (Recovery Plan Execution)
- RC.CO-01 through RC.CO-04 (Recovery Communication)

**Total: 106 subcategories across 6 functions and 22 categories**

---

*Document generated for Compliance Oracle MCP Server project planning*
