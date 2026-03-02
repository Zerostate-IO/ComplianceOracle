# SOC 2 Trust Services Criteria (TSC) Framework Structure

## Overview

SOC 2 (Service Organization Control 2) is a compliance framework developed by the American Institute of Certified Public Accountants (AICPA) for evaluating controls at service organizations. It is based on the **2017 Trust Services Criteria (TSC)** with revised points of focus (2022).

**Key Characteristics:**
- **Licensed Framework**: SOC 2 is proprietary to AICPA and requires a license to access the full criteria document
- **Service Organization Focus**: Designed for organizations providing services to other entities
- **Five Trust Service Principles**: Security, Availability, Processing Integrity, Confidentiality, Privacy
- **~100+ Criteria**: Approximately 100+ detailed control criteria across all principles
- **Type I & Type II Audits**: Evaluates both design effectiveness and operational effectiveness

## Trust Services Criteria (TSC) Structure

### 1. Security (Common Criteria - CC)

**Objective**: Protect information and systems against unauthorized access, unauthorized disclosure, and unauthorized modification.

**Structure**: 9 control categories (CC1-CC9)

| Category | Focus Area |
|----------|-----------|
| CC1 | Organization and Management |
| CC2 | Communications and Information |
| CC3 | System and Communications Protection |
| CC4 | Logical and Physical Access Controls |
| CC5 | System Monitoring and Maintenance |
| CC6 | Logical Access Security |
| CC7 | System Software, Data, and Configuration Management |
| CC8 | Change Management |
| CC9 | Risk Mitigation |

**Key Points of Focus** (2022 Revised):
- Entity governance and risk management
- Information security policies and procedures
- Access control mechanisms (authentication, authorization)
- Encryption and data protection
- Incident response and management
- Vulnerability management
- Third-party risk management
- Monitoring and logging

### 2. Availability (A)

**Objective**: Information and systems are available for operation and use as committed or agreed upon.

**Structure**: Multiple criteria addressing:
- System availability and performance
- Capacity planning
- Disaster recovery and business continuity
- Infrastructure resilience
- Monitoring and alerting

**Key Points of Focus**:
- Availability commitments and SLAs
- Infrastructure redundancy
- Backup and recovery procedures
- Disaster recovery testing
- Performance monitoring

### 3. Processing Integrity (PI)

**Objective**: System processing is complete, accurate, timely, and authorized.

**Structure**: Multiple criteria addressing:
- Data validation and completeness
- Processing accuracy
- Timeliness of processing
- Authorization of transactions
- Error handling and correction

**Key Points of Focus**:
- Input validation and error handling
- Processing logic verification
- Output validation and completeness
- Transaction logging and audit trails
- Data reconciliation procedures

### 4. Confidentiality (C)

**Objective**: Information designated as confidential is protected against unauthorized disclosure.

**Structure**: Multiple criteria addressing:
- Confidentiality classification
- Access restrictions
- Encryption and protection mechanisms
- Secure disposal
- Third-party confidentiality agreements

**Key Points of Focus**:
- Data classification schemes
- Encryption standards (in transit and at rest)
- Access control enforcement
- Secure data disposal
- Confidentiality agreements with third parties

### 5. Privacy (P)

**Objective**: Personal information is collected, used, retained, disclosed, and disposed of to meet the entity's objectives related to privacy.

**Structure**: Multiple criteria addressing:
- Privacy policies and procedures
- Consent and choice
- Data collection and use
- Data retention and disposal
- Individual rights (access, correction, deletion)
- Third-party management

**Key Points of Focus**:
- Privacy notice and transparency
- Consent mechanisms
- Data subject rights fulfillment
- Privacy impact assessments
- Data retention policies
- Third-party privacy agreements

## Data Structure Template

### Framework JSON Structure

```json
{
  "framework_id": "soc2-tsc-2017",
  "name": "SOC 2 Trust Services Criteria (2017)",
  "version": "2017",
  "status": "active",
  "description": "AICPA Trust Services Criteria for evaluating controls at service organizations",
  "source_url": "https://www.aicpa.org/",
  "license_note": "SOC 2 is a proprietary framework. Users must obtain the official criteria from AICPA.",
  "functions": [
    {
      "id": "CC",
      "name": "Security (Common Criteria)",
      "description": "Protection against unauthorized access, disclosure, and modification",
      "required": true,
      "categories": [
        {
          "id": "CC1",
          "name": "Organization and Management",
          "description": "The entity demonstrates a commitment to competence and enforces responsibility for the performance of internal control over the system.",
          "controls": [
            {
              "id": "CC1.1",
              "name": "Governance Structure",
              "description": "The board of directors demonstrates independence from management and exercises oversight of the development, performance, and reporting of internal control over the system.",
              "implementation_examples": [
                "Board charter defining roles and responsibilities",
                "Board meeting minutes documenting oversight activities",
                "Board committees with defined charters"
              ],
              "informative_references": [
                "COSO Internal Control Framework",
                "NIST CSF: GV (Governance)"
              ]
            }
          ]
        }
      ]
    },
    {
      "id": "A",
      "name": "Availability",
      "description": "Information and systems are available for operation and use as committed or agreed upon",
      "required": false,
      "categories": []
    },
    {
      "id": "PI",
      "name": "Processing Integrity",
      "description": "System processing is complete, accurate, timely, and authorized",
      "required": false,
      "categories": []
    },
    {
      "id": "C",
      "name": "Confidentiality",
      "description": "Information designated as confidential is protected against unauthorized disclosure",
      "required": false,
      "categories": []
    },
    {
      "id": "P",
      "name": "Privacy",
      "description": "Personal information is collected, used, retained, disclosed, and disposed of to meet the entity's objectives related to privacy",
      "required": false,
      "categories": []
    }
  ]
}
```

### Control Model

Each control in SOC 2 should include:

```python
class SOC2Control(BaseModel):
    """SOC 2 Trust Services Criteria control."""
    
    id: str  # e.g., "CC1.1", "A1.2"
    name: str
    description: str
    principle_id: str  # CC, A, PI, C, or P
    principle_name: str
    category_id: str | None  # e.g., "CC1" for Security
    category_name: str | None
    
    # Points of focus (2022 revised)
    points_of_focus: list[str]
    
    # Implementation guidance
    implementation_examples: list[str]
    informative_references: list[str]
    
    # Audit considerations
    audit_considerations: str | None
    type_i_considerations: str | None  # Design effectiveness
    type_ii_considerations: str | None  # Operating effectiveness
```

## Mapping Approach: CSF 2.0 to SOC 2

### Mapping Strategy

SOC 2 and NIST CSF 2.0 address overlapping but distinct concerns:

| Aspect | NIST CSF 2.0 | SOC 2 |
|--------|-------------|-------|
| **Scope** | All organizations | Service organizations |
| **Focus** | Cybersecurity risk management | Control evaluation for attestation |
| **Principles** | 6 Functions (GV, RM, PR, DE, RS, RC) | 5 Trust Principles (CC, A, PI, C, P) |
| **Audience** | Internal risk management | External audits/attestation |
| **Maturity** | Capability levels | Type I/II effectiveness |

### Mapping Relationships

**Security (CC) ↔ CSF Functions**:
- CC1-CC9 map broadly to **GV (Govern)** and **PR (Protect)** functions
- Strong overlap with access control, risk management, and system protection

**Availability (A) ↔ CSF Functions**:
- Maps to **RC (Recover)** and **DE (Detect)** functions
- Addresses business continuity and disaster recovery

**Processing Integrity (PI) ↔ CSF Functions**:
- Maps to **PR (Protect)** and **DE (Detect)** functions
- Addresses data accuracy and transaction validation

**Confidentiality (C) ↔ CSF Functions**:
- Maps to **PR (Protect)** function
- Addresses encryption and access controls for sensitive data

**Privacy (P) ↔ CSF Functions**:
- Maps to **GV (Govern)** and **PR (Protect)** functions
- Addresses personal data handling and individual rights

### Example Mappings

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
      "notes": "Both controls address authentication and authorization of system access"
    },
    {
      "source_framework": "nist-csf-2.0",
      "source_control_id": "PR.DS-02",
      "source_control_name": "Data-in-transit is protected",
      "target_framework": "soc2-tsc-2017",
      "target_control_id": "CC3.1",
      "target_control_name": "System and Communications Protection",
      "relationship": "equivalent",
      "notes": "Both controls address encryption of data in transit"
    },
    {
      "source_framework": "nist-csf-2.0",
      "source_control_id": "RC.RP-01",
      "source_control_name": "Recovery plan is executed during or after an event",
      "target_framework": "soc2-tsc-2017",
      "target_control_id": "A1.2",
      "target_control_name": "Availability - Recovery Planning",
      "relationship": "equivalent",
      "notes": "Both controls address disaster recovery and business continuity"
    }
  ]
}
```

## Implementation Considerations

### Data Availability Challenge

**Problem**: SOC 2 is a proprietary framework owned by AICPA. The full criteria document is not freely available via public APIs like NIST CPRT.

**Solutions**:

1. **Community-Maintained Data** (Recommended)
   - Create a community-maintained JSON file with publicly available SOC 2 TSC summaries
   - Include only information from public sources (AICPA summaries, audit guidance, etc.)
   - Do NOT copy licensed content from the official AICPA document

2. **User-Provided Data**
   - Allow users to import their own SOC 2 data if they have a license
   - Provide a data import template and validation schema
   - Document the expected JSON structure

3. **Hybrid Approach**
   - Provide a basic framework structure with publicly available information
   - Allow users to enhance with their own licensed data
   - Support merging of community and proprietary data

### Recommended Implementation Path

1. **Phase 1: Framework Structure**
   - Define SOC2 framework metadata and control schema
   - Create a template JSON file with publicly available TSC summaries
   - Document the data structure and mapping approach

2. **Phase 2: Mapping Integration**
   - Create CSF 2.0 → SOC 2 mapping file
   - Integrate with existing FrameworkManager
   - Add SOC 2 to framework listing and search

3. **Phase 3: User Data Import**
   - Implement data import tool for users with AICPA licenses
   - Validate imported data against schema
   - Support merging with community data

4. **Phase 4: Documentation & Guidance**
   - Create user guide for SOC 2 assessment
   - Document mapping relationships
   - Provide implementation examples

## References

- **AICPA Trust Services Criteria**: https://www.aicpa.org/
- **2017 TSC with 2022 Revised Points of Focus**: Available from AICPA (requires license)
- **SOC 2 Overview**: https://www.aicpa.org/soc2
- **NIST CSF 2.0**: https://www.nist.gov/cyberframework

## License Note

This documentation describes the structure and approach for SOC 2 support in Compliance Oracle. The actual SOC 2 Trust Services Criteria are proprietary to AICPA and require a license to access the full document. Users implementing SOC 2 support should:

1. Obtain the official 2017 TSC document from AICPA
2. Respect AICPA's intellectual property rights
3. Use only publicly available information in community-maintained data
4. Provide their own licensed data for complete SOC 2 assessment
