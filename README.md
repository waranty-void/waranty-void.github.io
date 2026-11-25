# Warranty Void

[Project gallery](https://waranty-void.github.io/) · [Engineering docs](https://waranty-void.github.io/engineering/) · [Join the workshop](https://discord.gg/CPjRJzZYpf)

This is the public site for the independent Warranty Void project collective. The gallery carries individually published projects. Work in progress is managed in the membership-gated Kanban.

## Develop

Run `python3 tools/build.py` to regenerate the static pages, then `python3 -m http.server 8000` to preview the site locally. The standalone Count23 companion site can be generated with `python3 tools/build.py --companion /path/to/output`. Both sites use relative asset URLs.

Each project has a working product view and an engineering guide. New releases should link the real demonstration, authoritative source and revision, tested setup, known gaps, credits and reuse terms. Send changes by pull request. Leave private planning files outside this repository.

## Reuse and credits

The original Warranty Void website code and field-guide text use the MIT licence. The Warranty Void name and logo identify the collective. The Count23 screenshots show the upstream application and its interface. That application's code, dependencies and depicted interface retain their existing terms. The upstream project has no declared application licence at the documented revision.

[Count23 source and history](https://github.com/perlytiara/Count23) · [Organization fork](https://github.com/waranty-void/count23)
