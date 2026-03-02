================================================================================
COMPLIANCE ORACLE - README TOOLS RECONCILIATION
================================================================================
Generated: 2026-02-28
Task: Task 5 - Reconcile README Tool Catalog with Runtime Registration
================================================================================

VERIFICATION: README TOOLS vs RUNTIME REGISTRATION
================================================================================

Runtime Tools (from task-2-contract-baseline.txt):
  1.  list_frameworks
  2.  list_controls
  3.  get_control_details
  4.  search_controls
  5.  get_control_context
  6.  document_compliance
  7.  link_evidence
  8.  get_documentation
  9.  export_documentation
  10. compare_frameworks
  11. get_framework_gap
  12. get_guidance
  13. get_assessment_questions

README Tools (after fix):
  1.  list_frameworks
  2.  list_controls
  3.  search_controls
  4.  get_control_details
  5.  document_compliance
  6.  link_evidence
  7.  get_documentation
  8.  export_documentation
  9.  compare_frameworks
  10. get_guidance
  11. get_control_context
  12. get_framework_gap
  13. get_assessment_questions  <-- ADDED

================================================================================
CHANGE SUMMARY
================================================================================

File Modified: README.md
Location: Lines 135-149 (MCP tools catalog table)

Change Made:
  - Added row for `get_assessment_questions()` tool
  - Purpose: "Generate interview-style questions"
  - Example: `get_assessment_questions(framework="nist-csf-2.0", function="PR")`

Previous State:
  - 12 tools documented
  - Missing: get_assessment_questions

Current State:
  - 13 tools documented
  - All runtime tools now represented

================================================================================
VERIFICATION CHECKSUM
================================================================================

Tool Count:
  - Runtime: 13
  - README:  13
  - Match:   YES

Set Difference (runtime - README):
  - EMPTY (no missing tools)

Set Difference (README - runtime):
  - EMPTY (no phantom tools)

Status: RECONCILED

================================================================================
END OF EVIDENCE
================================================================================
