"""Compliance Oracle MCP Server.

Main entry point for the MCP server that provides compliance framework tools.
"""

from fastmcp import FastMCP

from compliance_oracle.tools.lookup import register_lookup_tools
from compliance_oracle.tools.search import register_search_tools
from compliance_oracle.tools.documentation import register_documentation_tools
from compliance_oracle.tools.framework_mgmt import register_framework_tools

# Create the MCP server
mcp = FastMCP(
    name="compliance-oracle",
    instructions="MCP server for evaluating designs and code against compliance frameworks (NIST CSF 2.0, 800-53)",
)

# Register all tools
register_lookup_tools(mcp)
register_search_tools(mcp)
register_documentation_tools(mcp)
register_framework_tools(mcp)


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
