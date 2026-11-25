"""Build the public catalogue or its standalone Count23 field guide. Python 3.9+."""
import argparse
from html import escape
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
ORG = "https://github.com/waranty-void"
HUB = "https://wvoid.coal.marketing/"
BOARD = "https://client.coal.marketing/warranty-void/kanban"
DEMO = "https://perlytiara.github.io/Count23/"
SOURCE = "https://github.com/perlytiara/Count23/tree/605a29b4d150bc3d6837b5eee94eaa14a25b9581"
BLOB = SOURCE.replace("/tree/", "/blob/")
FORK = ORG + "/count23"
ROADSTER = "https://libertygrage.github.io/roadster-x/"
TANDEM = "https://libertygrage.github.io/tandem-t6/"
ALT = "Count23 running a sample countdown, with its timer ring and sharing controls."

def link(url, label, cls=""):
    return f'<a href="{escape(url, quote=True)}" class="{cls}">{label}</a>'

def template(title, desc, section, content, assets, home):
    nav = [("Projects", home + "#projects"), ("Engineering", home + "engineering/"), ("Community", home + "community/")]
    menu = "".join(f'<a href="{u}"' + (' aria-current="page"' if s == section else '') + f'>{s}</a>' for s, u in nav)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title><meta name="description" content="{escape(desc, quote=True)}"><meta name="theme-color" content="#102c2e">
<link rel="icon" type="image/svg+xml" href="{assets}warranty-w.svg"><link rel="stylesheet" href="{assets}site.css?v=workshop-2"><script defer src="{assets}demo.js"></script></head>
<body><a href="#main" class="skip">Skip to content</a><header class="top"><div class="wrap bar"><a class="brand" href="{home}"><img src="{assets}warranty-w.svg" width="44" height="44" alt="">Warranty Void</a>
<nav class="nav" aria-label="Main navigation">{menu}</nav></div></header>
<main id="main">{content}</main><footer class="foot"><div class="wrap"><p>Warranty Void is an independent project collective. Coal Marketing provides the web address and hosts the Kanban.</p>
<nav aria-label="Footer">{link(ORG,"GitHub")}{link(BOARD,"Member Kanban")}</nav></div></footer></body></html>'''

def head(crumb, title, lead):
    return f'<div class="wrap interior"><p class="crumb">{crumb}</p><h1>{title}</h1><p class="lede">{lead}</p></div>'

def tabs(view, docs, active):
    return f'<nav class="tabs" aria-label="Count23 views"><a href="{view}"' + (' aria-current="page"' if active == "view" else '') + f'>Live demo</a><a href="{docs}"' + (' aria-current="page"' if active == "docs" else '') + '>Engineering notes</a></nav>'

def product(view, docs, assets, home):
    return head(link(home + "#projects", "Projects") + " / Count23", "Count23", "Pick a time, share the countdown, and send back an alternative if it doesn’t work for you.") + f'''
<div class="wrap">{tabs(view,docs,"view")}
<div class="viewer"><img class="poster" width="1915" height="980" src="{assets}count23-wide.webp" alt="{ALT}"><button data-launch class="button orange load" type="button">Launch Count23</button></div>
<p class="under">The demo runs the original application. {link(DEMO,"Open it in its own tab")} for the full browser controls.</p>
<div class="reading"><h2>Try it with a friend</h2><ol><li>Choose a future time and select <strong>Start Countdown</strong>. The quick buttons add time to the date already in the picker.</li><li>Copy the link and open it in another tab. The link carries the proposal, so the recipient can view the time in their own time zone.</li><li>Select <strong>Suggest edit</strong> or <strong>Confirm this time</strong>. Copy the revised link to send the answer back.</li></ol>
<p>{link(docs,"Read the engineering notes")} · {link(FORK,"Browse the organization’s fork")}</p></div></div>'''

def engineering(view, docs, assets, home):
    return head(link(home+"engineering/","Engineering") + " / Count23", "Inside Count23", "How the timer runs, what a shared link carries, and how to build the app from source.") + f'''
<div class="wrap">{tabs(view,docs,"docs")}<article class="reading">
<h2>What runs where</h2><p>Count23 is a statically exported Next.js 16 app with React 19 and TypeScript. The browser handles the countdown and the proposal history. There is no server-side meeting record to update.</p>
<h2>Time and proposal links</h2><p>The picker takes a local date and time. The proposal stores a UTC timestamp and the interface renders that instant in the viewer’s time zone. A link stores a snapshot in its <code>#s=</code> fragment. An edit or confirmation creates a new snapshot. Send the revised link to share that change.</p>
<p>Anyone holding a proposal link can read its contents. Use sample details when demonstrating the project publicly.</p>
<img class="guide-image" src="{assets}count23-setup.webp" width="1760" height="1000" loading="lazy" alt="The Count23 picker with a sample date, quick time adjustments, and Start Countdown"><h2>Build it</h2><p>Use Node.js 22 and npm. These commands reproduce the inspected source revision and build a static site under <code>/demos/count23</code>.</p>
<pre><code>git clone https://github.com/waranty-void/count23.git
cd count23
git checkout 605a29b4d150bc3d6837b5eee94eaa14a25b9581
npm ci --ignore-scripts
NEXT_PUBLIC_BASE_PATH=/demos/count23 npm run build</code></pre>
<p>Mount the contents of <code>out/</code> at that same URL prefix, or set an empty base path before building for a domain root. Rebuild when the deployment path changes.</p>
<h2>Read the implementation</h2><ul><li>{link(BLOB+"/src/features/countdown/components/TimeInput.tsx","TimeInput.tsx")} handles the picker and time adjustments.</li><li>{link(BLOB+"/src/features/countdown/hooks/useCountdown.ts","useCountdown.ts")} derives the remaining time for the display.</li><li>{link(BLOB+"/src/features/proposal/utils/linkState.ts","linkState.ts")} encodes and reads the proposal in the URL fragment.</li></ul>
<h2>What was checked</h2><p>The public app displayed a running sample countdown in Safari. The pinned source compiled, passed the build’s TypeScript check, and produced an export whose page and twelve referenced assets loaded at the test prefix. Offline use still needs a separate test and a fix for the service worker’s icon paths.</p>
<h2>Source and reuse</h2><p>The organization fork preserves the upstream history and credits. The inspected application revision has no published licence. The new Warranty Void field-guide text and website code carry the MIT licence. The application and its depicted interface retain their existing terms.</p>
<p>{link(SOURCE,"Inspected upstream revision")} · {link(FORK,"Organization fork")} · {link(view,"Open the demo")}</p></article></div>'''

def build(out, companion=False):
    out = out.resolve()
    if companion:
        (out / "assets").mkdir(parents=True,exist_ok=True)
        for name in ["site.css","demo.js","warranty-w.svg","count23-wide.webp","count23-setup.webp"]:
            shutil.copyfile(ROOT / "assets" / name, out / "assets" / name)
    def write(path, name, desc, section, body, assets, home):
        dest=out/path
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(template(name,desc,section,body,assets,home))
    if companion:
        write("index.html","Count23 · Warranty Void","Run Count23 and share a proposed time.","Projects",product("./","engineering/","assets/",HUB),"assets/",HUB)
        write("engineering/index.html","Count23 engineering · Warranty Void","Build and understand Count23.","Engineering",engineering("../","./","../assets/",HUB),"../assets/",HUB)
        (out/".nojekyll").touch()
        return
    feature = f'''<section class="intro"><div class="wrap showcase-hero"><div class="hero-copy"><h1>Warranty <span>Void</span></h1><p>A workshop for prototypes you can try. Pick a project, see how it was built and bring back a test of your own.</p><a class="button orange" href="#projects">Explore the projects <span aria-hidden="true">↓</span></a></div>
<figure class="hero-photo"><a href="{ROADSTER}"><img src="assets/roadster-hover.webp" width="1440" height="810" fetchpriority="high" alt="Roadster X hovering beside the airport control tower in GTA IV."></a><figcaption><a href="{ROADSTER}">Roadster X · Airport hover test <span aria-hidden="true">↗</span></a><span>Liberty Garage / GTA IV</span></figcaption></figure></div></section>
<section class="wrap block" id="projects"><div class="section-top"><h2>Published projects</h2></div><div class="release-grid">
<article class="release-card"><a href="{ROADSTER}"><img src="assets/roadster-apron.webp" width="960" height="540" alt="The Roadster X on the airport apron in GTA IV."></a><div><p class="eyebrow">Liberty Garage · GTA IV</p><h3>Roadster X</h3><p>Take a hover car from the runway to the rooftops. The guide includes flight controls and in-game tests.</p>{link(ROADSTER,"Open the player guide ↗","textlink")}</div></article>
<article class="release-card"><a href="{TANDEM}"><img src="assets/tandem-width.webp" width="960" height="540" alt="The narrow Tandem T6 parked beside a stock Admiral for a width comparison."></a><div><p class="eyebrow">Liberty Garage · GTA IV</p><h3>Tandem T6</h3><p>Two seats in a line and a body under a metre wide. See it beside a stock Admiral and out in city traffic.</p>{link(TANDEM,"Open the player guide ↗","textlink")}</div></article>
<article class="release-card"><a href="projects/count23/"><img src="assets/count23-screen.webp" width="1740" height="1050" alt="{ALT}"></a><div><p class="eyebrow">Browser app</p><h3>Count23</h3><p>Pick a time, send the countdown and let someone suggest a better one.</p><p class="card-links">{link("projects/count23/","Try Count23","textlink")}{link("engineering/count23/","Engineering notes","textlink")}</p></div></article>
</div></section>
<div class="wrap actions"><section><h2>Bring an idea</h2><p>Open an issue on a released project to propose a change or share something you built.</p>{link("community/","How to contribute","textlink")}</section>
<section><h2>Build on a release</h2><p>Engineering notes link to the source, the tested build, and the work still open for contributors.</p>{link("engineering/","Browse engineering docs","textlink")}</section></div>'''
    write("index.html","Warranty Void · Projects","Independent inventions, working demos and engineering notes.","Projects",feature,"assets/","./")
    write("projects/count23/index.html","Count23 · Warranty Void","Run Count23 and share a proposed time.","Projects",product("./","../../engineering/count23/","../../assets/","../../"),"../../assets/","../../")
    write("engineering/count23/index.html","Count23 engineering · Warranty Void","Build and understand Count23.","Engineering",engineering("../../projects/count23/","./","../../assets/","../../"),"../../assets/","../../")
    docs=head(link("../","Warranty Void")+" / Engineering","Engineering docs","Source, build instructions, and verified behaviour for each published project.") + '<div class="wrap docs-index"><a class="row" href="count23/"><div><strong>Count23</strong><span>Static React app, countdown timing and shareable proposal state.</span></div><span class="action">Read the guide</span></a></div>'
    docs += f'<section class="wrap reading"><h2>Liberty Garage player guides</h2><p>{link(ROADSTER,"Roadster X")} covers jump, hover and flight controls. {link(TANDEM,"Tandem T6")} documents the narrow-body car with side-by-side tests. Both guides include original GTA IV screenshots.</p></section>'
    write("engineering/index.html","Engineering · Warranty Void","Technical documentation for published projects.","Engineering",docs,"../assets/","../")
    community=head(link("../","Warranty Void")+" / Community","Build with us","Bring an idea, document an experiment, or help someone test a release.") + f'''<div class="wrap"><div class="reading"><p>The Discord workshop is invite-only. If you already know a member, ask the organizer privately for an invitation. You can contribute to public projects on GitHub.</p><h2>From the first sketch</h2><p>Bring a question or sketch to <strong>Idea Drop</strong>. Start a thread in <strong>Product Showcase</strong> with a photo, a prototype or something another member can test. Organizers choose what goes into <strong>Releases</strong>.</p>
<h2>Connect your GitHub account</h2><ol><li>Invited members can open <strong>My desk</strong> in Discord, or type <code>!desk</code>.</li><li>Choose <strong>Connect GitHub</strong> and authorize your own account on GitHub.</li><li>After an organizer assigns a project, choose <strong>My invitations</strong> and accept its invitation on GitHub. Watch gives read access. Build also lets you contribute.</li><li>Open the project card for <strong>Review changes</strong> and <strong>Release notes</strong>. To find a room, choose <strong>Search projects</strong> and type its name.</li></ol><p>{link(ORG,"Warranty Void on GitHub")}</p>
<h2>Contribute or publish</h2><p>Anyone can explore a public demo. Check the project’s licence before reusing its code or assets. You can open an issue or propose a change on GitHub. An organizer can invite collaborators to a private project individually.</p>
<h2>Member Kanban</h2><p>Invited collaborators use the signed-in board to track work. Releases appear in the public gallery when their project pages are published.</p>{link(BOARD,"Open the member Kanban","button light")}</div></div>'''
    write("community/index.html","Community · Warranty Void","Contribute to public projects and learn how invited members build together.","Community",community,"../assets/","../")

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--companion",type=Path,help="write the standalone Count23 Pages site to this directory")
    args=parser.parse_args()
    build(args.companion or ROOT, bool(args.companion))
