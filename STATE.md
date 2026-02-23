# State

## Current Focus

Design and planning complete. Homelab docs written. Ready to begin prerequisites and implementation.

## Status

- [x] Business model selected (Content + Merch)
- [x] Agent architecture designed (LangGraph + MCP tools)
- [x] Budget allocated ($600-1,200 of $2,000, rest in reserve)
- [x] Design document written and approved (revised after Gemini adversarial review)
- [x] Implementation plan created (26 tasks, 10 phases)
- [x] Homelab documentation written and published
- [ ] Prerequisites completed (7 manual tasks)
- [ ] Infrastructure provisioned
- [ ] Site built and deployed
- [ ] Hobson agent built and running
- [ ] Obsidian vault section created
- [ ] Substack launched

## Known Issues

- Overseerr Cloudflare tunnel currently on buildscharacter.com -- needs to move to a subdomain before site goes live
- Freya rpool is tight (472GB) -- Hobson's container should go on Loki if possible
- Claude Max quota shared with Bob and Tim -- monitor for rate limiting
- Substack has no public API -- python-substack (reverse-engineered) is fragile, needs fallback plan

## Next Steps

1. Complete 7 manual prerequisites (accounts, Telegram bot, move Overseerr tunnel)
2. Begin Phase 1: Scaffolding (Python project, brand guidelines, DB schema, LXC container, Obsidian vault)
3. Phase 2: Build the Astro website
4. Phase 3: Build core agent
5. Continue through phases 4-10
