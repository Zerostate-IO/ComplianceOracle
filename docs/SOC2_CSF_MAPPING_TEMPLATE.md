# SOC 2 ↔ NIST CSF 2.0 Mapping Template

## Overview

This document provides a mapping template between SOC 2 Trust Services Criteria (TSC) and NIST Cybersecurity Framework 2.0 (CSF 2.0). The mappings establish relationships between controls in both frameworks to support:

- Cross-framework gap analysis
- Hypothetical coverage projection
- Compliance posture assessment across frameworks

## Mapping Relationship Types

| Relationship | Definition | Example |
|--------------|-----------|---------|
| **Equivalent** | Controls address the same objective with similar scope | CSF PR.AC-01 ↔ SOC2 CC6.1 (both address authentication/authorization) |
| **Broader** | Source control covers more than target | CSF PR.DS-01 (all data protection) → SOC2 C1.1 (confidentiality only) |
| **Narrower** | Source control covers part of target | SOC2 CC1.1 (governance) ← CSF GV.RO-01 (broader governance) |
| **Related** | Controls overlap but don't directly map | CSF DE.AE-01 (anomaly detection) ↔ SOC2 CC5.1 (monitoring) |

## Mapping Structure

### JSON Format

```json
{
  "mappings": [
    {
      "source_framework": "nist-csf-2.0",
      "source_control_id": "PR.AC-01",
      "source_control_name": "Processes and procedures are managed to ensure that access to assets is authorized, authenticated and enforced",
      "target_framework": "soc2-tsc-2017",
      "target_control_id": "CC6.1",
      "target_control_name": "Logical Access Controls",
      "relationship": "equivalent",
      "confidence": 0.95,
      "notes": "Both controls require authentication and authorization mechanisms for system access",
      "mapping_rationale": "CSF PR.AC-01 directly addresses access control processes that align with SOC2 CC6.1 requirements for logical access security"
    }
  ]
}
```

### Mapping Fields

- **source_framework**: Source framework ID (e.g., "nist-csf-2.0")
- **source_control_id**: Control ID in source framework
- **source_control_name**: Control name/description
- **target_framework**: Target framework ID (e.g., "soc2-tsc-2017")
- **target_control_id**: Control ID in target framework
- **target_control_name**: Control name/description
- **relationship**: Type of relationship (equivalent, broader, narrower, related)
- **confidence**: Confidence level (0.0-1.0) for the mapping accuracy
- **notes**: Brief explanation of the mapping
- **mapping_rationale**: Detailed rationale for the relationship

## Comprehensive Mapping Matrix

### Security (Common Criteria - CC) Mappings

#### CC1: Organization and Management

| SOC2 Control | CSF 2.0 Equivalent | Relationship | Notes |
|--------------|-------------------|--------------|-------|
| CC1.1 - Governance Structure | GV.RO-01 | Equivalent | Board oversight and governance structure |
| CC1.2 - Organizational Structure | GV.RO-02 | Equivalent | Organizational roles and responsibilities |
| CC1.3 - Responsibility for Controls | GV.RO-03 | Equivalent | Assignment of control responsibilities |
| CC1.4 - Competence | GV.HR-01 | Related | Personnel competence and training |
| CC1.5 - Accountability | GV.RO-04 | Equivalent | Accountability for control performance |

#### CC2: Communications and Information

| SOC2 Control | CSF 2.0 Equivalent | Relationship | Notes |
|--------------|-------------------|--------------|-------|
| CC2.1 - Information and Communication | GV.OC-01 | Equivalent | Communication of policies and procedures |
| CC2.2 - Internal Communication | GV.OC-02 | Related | Internal communication mechanisms |
| CC2.3 - External Communication | GV.OC-03 | Related | External stakeholder communication |
| CC2.4 - Roles and Responsibilities | GV.RO-02 | Equivalent | Clear communication of roles |

#### CC3: System and Communications Protection

| SOC2 Control | CSF 2.0 Equivalent | Relationship | Notes |
|--------------|-------------------|--------------|-------|
| CC3.1 - Logical Access Controls | PR.AC-01 | Equivalent | Access control mechanisms |
| CC3.2 - Encryption | PR.DS-01, PR.DS-02 | Equivalent | Data protection in transit and at rest |
| CC3.3 - Network Segmentation | PR.AC-03 | Related | Network isolation and segmentation |
| CC3.4 - Malware Protection | PR.PT-01 | Related | Malware detection and prevention |

#### CC4: Logical and Physical Access Controls

| SOC2 Control | CSF 2.0 Equivalent | Relationship | Notes |
|--------------|-------------------|--------------|-------|
| CC4.1 - Physical Access | PR.AC-02 | Equivalent | Physical access controls |
| CC4.2 - Logical Access | PR.AC-01 | Equivalent | Logical access controls |
| CC4.3 - Access Revocation | PR.AC-01 | Related | Timely removal of access |

#### CC5: System Monitoring and Maintenance

| SOC2 Control | CSF 2.0 Equivalent | Relationship | Notes |
|--------------|-------------------|--------------|-------|
| CC5.1 - Monitoring | DE.AE-01 | Equivalent | System monitoring and logging |
| CC5.2 - System Maintenance | PR.MA-01 | Equivalent | Maintenance and patching |
| CC5.3 - Vulnerability Management | PR.PT-01 | Related | Vulnerability identification and remediation |

#### CC6: Logical Access Security

| SOC2 Control | CSF 2.0 Equivalent | Relationship | Notes |
|--------------|-------------------|--------------|-------|
| CC6.1 - Authentication | PR.AC-01 | Equivalent | User authentication mechanisms |
| CC6.2 - Authorization | PR.AC-01 | Equivalent | Access authorization controls |
| CC6.3 - Privileged Access | PR.AC-04 | Equivalent | Privileged access management |
| CC6.4 - Access Logging | DE.AE-01 | Related | Logging of access events |

#### CC7: System Software, Data, and Configuration Management

| SOC2 Control | CSF 2.0 Equivalent | Relationship | Notes |
|--------------|-------------------|--------------|-------|
| CC7.1 - Configuration Management | PR.PS-01 | Equivalent | System configuration control |
| CC7.2 - Change Management | PR.PS-02 | Equivalent | Change control procedures |
| CC7.3 - Data Backup | RC.RP-01 | Related | Data backup and recovery |

#### CC8: Change Management

| SOC2 Control | CSF 2.0 Equivalent | Relationship | Notes |
|--------------|-------------------|--------------|-------|
| CC8.1 - Change Authorization | PR.PS-02 | Equivalent | Change approval and authorization |
| CC8.2 - Change Testing | PR.PS-02 | Related | Testing of changes |
| CC8.3 - Change Documentation | PR.PS-02 | Related | Documentation of changes |

#### CC9: Risk Mitigation

| SOC2 Control | CSF 2.0 Equivalent | Relationship | Notes |
|--------------|-------------------|--------------|-------|
| CC9.1 - Risk Assessment | RM.RA-01 | Equivalent | Risk identification and assessment |
| CC9.2 - Risk Response | RM.RA-02 | Equivalent | Risk response planning |
| CC9.3 - Incident Response | RS.RP-01 | Equivalent | Incident response procedures |

### Availability (A) Mappings

| SOC2 Control | CSF 2.0 Equivalent | Relationship | Notes |
|--------------|-------------------|--------------|-------|
| A1.1 - Availability Objectives | GV.RO-01 | Related | Definition of availability requirements |
| A1.2 - Recovery Planning | RC.RP-01 | Equivalent | Disaster recovery and business continuity |
| A1.3 - Infrastructure Resilience | RC.RP-02 | Related | System redundancy and resilience |
| A2.1 - Capacity Planning | PR.PS-01 | Related | Capacity and performance management |
| A2.2 - Performance Monitoring | DE.AE-01 | Related | System performance monitoring |

### Processing Integrity (PI) Mappings

| SOC2 Control | CSF 2.0 Equivalent | Relationship | Notes |
|--------------|-------------------|--------------|-------|
| PI1.1 - Input Validation | PR.PT-01 | Related | Input validation and error handling |
| PI1.2 - Processing Accuracy | PR.PT-01 | Related | Accurate processing of transactions |
| PI1.3 - Output Validation | PR.PT-01 | Related | Output validation and completeness |
| PI1.4 - Timeliness | DE.AE-01 | Related | Timely processing of transactions |
| PI2.1 - Authorization | PR.AC-01 | Related | Authorization of transactions |
| PI2.2 - Logging | DE.AE-01 | Related | Transaction logging and audit trails |

### Confidentiality (C) Mappings

| SOC2 Control | CSF 2.0 Equivalent | Relationship | Notes |
|--------------|-------------------|--------------|-------|
| C1.1 - Confidentiality Classification | PR.DS-01 | Related | Data classification and handling |
| C1.2 - Access Restrictions | PR.AC-01 | Equivalent | Restricting access to confidential data |
| C1.3 - Encryption | PR.DS-01, PR.DS-02 | Equivalent | Encryption of confidential data |
| C1.4 - Secure Disposal | PR.DS-03 | Equivalent | Secure data disposal |
| C2.1 - Third-Party Agreements | GV.RO-01 | Related | Confidentiality agreements with vendors |

### Privacy (P) Mappings

| SOC2 Control | CSF 2.0 Equivalent | Relationship | Notes |
|--------------|-------------------|--------------|-------|
| P1.1 - Privacy Notice | GV.OC-01 | Related | Privacy policy and transparency |
| P1.2 - Consent | GV.RO-01 | Related | Obtaining consent for data collection |
| P2.1 - Data Collection | PR.DS-01 | Related | Authorized data collection |
| P2.2 - Data Use | PR.DS-01 | Related | Authorized use of personal data |
| P3.1 - Data Retention | PR.DS-03 | Related | Data retention policies |
| P3.2 - Data Disposal | PR.DS-03 | Equivalent | Secure disposal of personal data |
| P4.1 - Individual Rights | GV.RO-01 | Related | Fulfilling individual data subject rights |
| P5.1 - Third-Party Management | GV.RO-01 | Related | Managing third-party access to personal data |

## Mapping JSON Template

```json
{
  "source_framework": "nist-csf-2.0",
  "target_framework": "soc2-tsc-2017",
  "version": "1.0",
  "created_date": "2026-02-28",
  "description": "Mapping between NIST CSF 2.0 and SOC 2 Trust Services Criteria",
  "mappings": [
    {
      "source_control_id": "GV.RO-01",
      "source_control_name": "Organizational context and objectives are established and communicated",
      "target_control_id": "CC1.1",
      "target_control_name": "Governance Structure",
      "relationship": "equivalent",
      "confidence": 0.95,
      "notes": "Both controls address governance structure and organizational objectives",
      "mapping_rationale": "GV.RO-01 requires establishment of organizational context and objectives, which directly aligns with CC1.1's requirement for governance structure demonstrating board oversight"
    },
    {
      "source_control_id": "PR.AC-01",
      "source_control_name": "Processes and procedures are managed to ensure that access to assets is authorized, authenticated and enforced",
      "target_control_id": "CC6.1",
      "target_control_name": "Logical Access Controls",
      "relationship": "equivalent",
      "confidence": 0.95,
      "notes": "Both controls require authentication and authorization mechanisms",
      "mapping_rationale": "PR.AC-01 directly addresses access control processes that align with CC6.1 requirements for logical access security"
    },
    {
      "source_control_id": "PR.DS-01",
      "source_control_name": "Data-at-rest is protected",
      "target_control_id": "C1.3",
      "target_control_name": "Encryption of Confidential Data",
      "relationship": "equivalent",
      "confidence": 0.90,
      "notes": "Both controls address encryption of data at rest",
      "mapping_rationale": "PR.DS-01 requires protection of data at rest, which aligns with C1.3's requirement for encryption of confidential data"
    },
    {
      "source_control_id": "RC.RP-01",
      "source_control_name": "Recovery plan is executed during or after an event",
      "target_control_id": "A1.2",
      "target_control_name": "Recovery Planning",
      "relationship": "equivalent",
      "confidence": 0.90,
      "notes": "Both controls address disaster recovery and business continuity",
      "mapping_rationale": "RC.RP-01 requires execution of recovery plans, which aligns with A1.2's requirement for recovery planning and business continuity"
    }
  ]
}
```

## Implementation Notes

### Mapping Confidence Levels

- **0.95-1.0**: High confidence - controls are nearly equivalent
- **0.85-0.94**: Good confidence - controls address similar objectives
- **0.75-0.84**: Moderate confidence - controls overlap significantly
- **0.65-0.74**: Fair confidence - controls are related but not directly equivalent
- **< 0.65**: Low confidence - controls have limited relationship

### Bidirectional Mappings

The template above shows CSF 2.0 → SOC 2 mappings. For bidirectional analysis:

1. Create reverse mappings (SOC 2 → CSF 2.0)
2. Use the same relationship types but in reverse
3. Maintain consistency in confidence levels

### Gap Analysis Interpretation

When using these mappings for gap analysis:

1. **Equivalent mappings**: Assume coverage transfers directly
2. **Broader mappings**: Source control may exceed target requirements
3. **Narrower mappings**: Source control may not fully cover target
4. **Related mappings**: Partial coverage; manual review recommended

## File Location

When implementing SOC 2 support, store the mapping file at:

```
data/mappings/nist-csf-2.0_to_soc2-tsc-2017.json
```

This follows the existing naming convention for framework mappings.

## References

- NIST CSF 2.0: https://www.nist.gov/cyberframework
- SOC 2 TSC: https://www.aicpa.org/soc2
- AICPA Trust Services Criteria: https://www.aicpa.org/
