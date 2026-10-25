# Reflection 
 
## Designing my tool schemas

I ended up using "z.enum(['open', 'in_progress', 'completed'])" for "status" instead of the free-text "z.string()" used in the Drill 2 handout. This is because the enum rejects bad values like "done" before the database is touched, and Claude then sees the allowed values in the schema, so it rarely guesses wrong. The trade-off is flexibility. Adding a new status means updating the enum, the database CHECK constraint and restarting the server. For a small, fixed set of values, that safety is worth it.

## MCP compared to calling a REST API 

With MCP, Claude discovers typed tools automatically, inputs are validated before my code runs, and permissions can be set per tool. The limitations for this are setup work and fragility. My server is a local process, and when it crashed on Node v19 the tools disappeared and /mcp showed the server as failed until I reconnected. Calling my Flask "/api" routes with "curl" through Bash needs no extra server, but Claude has to know the endpoints and build commands by hand, nothing validates its input, and allowing Bash grants far broader access than one tool.  

## A third MCP tool

I would add a "tasks_by_assignee" tool to answer questions like "How many open tasks right now are assigned to Alice?" Its schema would be "{ name: z.string().min(1), status: z.enum([...]).optional() }". The handler would open the database read-only, run a parameterized "SELECT ... WHERE assigned_to = ?" with an optional status filter, and return the same table format, or a "No tasks found for: <name>" message for when nothing matches. 
