# State

## Current Focus

Design phase complete. Ready for implementation planning.

## Status

- [x] Business model selected (Content + Merch)
- [x] Agent architecture designed (LangGraph + MCP tools)
- [x] Budget allocated ($1,000-1,500 of $2,000, rest in reserve)
- [x] Design document written and approved
- [ ] Implementation plan created
- [ ] Infrastructure provisioned
- [ ] Site built and deployed
- [ ] Hobson agent built and running
- [ ] Obsidian vault section created
- [ ] Substack launched

## Known Issues

- Overseerr Cloudflare tunnel currently on buildscharacter.com -- needs to move to a subdomain before site goes live
- Freya rpool is tight (472GB) -- Hobson's container should go on Loki if possible
- Claude API cost for Hobson needs monitoring -- may supplement with Ollama for low-stakes tasks

## Next Steps

1. Create implementation plan (break design into atomic, committable tasks)
2. Provision Hobson's LXC container
3. Build the site
4. Build the agent
5. Launch
