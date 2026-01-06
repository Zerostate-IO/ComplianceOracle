```typescript
// AGENTS.md - Compliance Oracle Agent (add to your project)

export const complianceOracleAgent: AgentConfig = {
  name: "compliance-oracle",
  description: "NIST CSF 2.0 & 800-53 compliance auditing, gap analysis, documentation",
  mcp: "complianceoracle",
  tools: true,  // Auto-discover 12+ compliance tools
  icon: "🔒",
  trigger: [/compliance/i, /nist/i, /csf|800-53/i, /audit/i],
};
```","filePath">/Users/legend/projects/ComplianceOracle/AGENTS.md