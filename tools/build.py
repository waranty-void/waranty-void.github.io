"""Build the public catalogue or its standalone Count23 field guide. Python 3.9+."""
import argparse
from html import escape
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
ORG = "https://github.com/waranty-void"
HUB = "https://wvoid.coal.marketing/"
CHAT = "https://discord.gg/CPjRJzZYpf"
BOARD = "https://client.coal.marketing/warranty-void/kanban"
DEMO = "https://perlytiara.github.io/Count23/"
SOURCE = "https://github.com/perlytiara/Count23/tree/605a29b4d150bc3d6837b5eee94eaa14a25b9581"
BLOB = SOURCE.replace("/tree/", "/blob/")
FORK = ORG + "/count23"
LINKED = "https://support.discord.com/hc/en-us/articles/8063233404823-Connections-Linked-Roles-Community-Members"
ALT = "Count23 running a sample countdown, with its timer ring and sharing controls."

def link(url, label, cls=""):
    return f'<a href="{escape(url, quote=True)}" class="{cls}">{label}</a>'

def template(title, desc, section, content, assets, home):
    nav = [("Projects", home + "#projects"), ("Engineering", home + "engineering/"), ("Community", home + "community/")]
    menu = "".join(f'<a href="{u}"' + (' aria-current="page"' if s == section else '') + f'>{s}</a>' for s, u in nav)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title><meta name="description" content="{escape(desc, quote=True)}"><meta name="theme-color" content="#102c2e">
<link rel="icon" href="{assets}warranty-void.webp"><link rel="stylesheet" href="{assets}site.css"><script defer src="{assets}demo.js"></script></head>
<body><a href="#main" class="skip">Skip to content</a><header class="top"><div class="wrap bar"><a class="brand" href="{home}"><img src="{assets}warranty-void.webp" width="38" height="38" alt="">Warranty Void</a>
<nav class="nav" aria-label="Main navigation">{menu}<a class="join" href="{CHAT}">Join Discord</a></nav></div></header>
<main id="main">{content}</main><footer class="foot"><div class="wrap"><p>Warranty Void is an independent project collective. Coal Marketing provides the web address and hosts the Kanban.</p>
<nav aria-label="Footer">{link(ORG,"GitHub")}{link(CHAT,"Discord")}{link(BOARD,"Member Kanban")}</nav></div></footer></body></html>'''

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
        for name in ["site.css","demo.js","warranty-void.webp","count23-wide.webp","count23-setup.webp"]:
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
    feature = f'''<section class="intro"><div class="wrap intro-inner"><div><h1>Warranty <span>Void</span></h1><p>An independent workshop for people who take things apart, build prototypes, and share what worked.</p></div><div class="logo-plate"><img src="assets/warranty-void.webp" width="512" height="512" alt="The Warranty Void orange folded-metal spark"></div></div></section>
<section class="wrap block" id="projects"><div class="section-top"><h2>Published projects</h2></div><article class="feature">
<a class="feature-img" href="projects/count23/" aria-label="Open the Count23 demonstration"><img src="assets/count23-screen.webp" width="1740" height="1050" alt="{ALT}"></a>
<div class="feature-copy"><p class="eyebrow">Browser app</p><h3>Count23</h3><p>A countdown you can send to someone. Pick a time, share it, and let them suggest a better one.</p>
<div class="links">{link("projects/count23/","Try Count23","button")}{link("engineering/count23/","Engineering notes","textlink")}</div></div></article></section>
<div class="wrap actions"><section><h2>Bring an idea</h2><p>Start with a sketch or a problem in the Discord. Keep prototype photos and test results together in a build log.</p>{link("community/","How to join the workshop","textlink")}</section>
<section><h2>Build on a release</h2><p>Engineering notes link to the source, the tested build, and the work still open for contributors.</p>{link("engineering/","Browse engineering docs","textlink")}</section></div>'''
    write("index.html","Warranty Void · Projects","Independent inventions, working demos and engineering notes.","Projects",feature,"assets/","./")
    write("projects/count23/index.html","Count23 · Warranty Void","Run Count23 and share a proposed time.","Projects",product("./","../../engineering/count23/","../../assets/","../../"),"../../assets/","../../")
    write("engineering/count23/index.html","Count23 engineering · Warranty Void","Build and understand Count23.","Engineering",engineering("../../projects/count23/","./","../../assets/","../../"),"../../assets/","../../")
    docs=head(link("../","Warranty Void")+" / Engineering","Engineering docs","Source, build instructions, and verified behaviour for each published project.") + '<div class="wrap docs-index"><a class="row" href="count23/"><div><strong>Count23</strong><span>Static React app, countdown timing and shareable proposal state.</span></div><span class="action">Read the guide</span></a></div>'
    write("engineering/index.html","Engineering · Warranty Void","Technical documentation for published projects.","Engineering",docs,"../assets/","../")
    community=head(link("../","Warranty Void")+" / Community","Join the workshop","Bring an idea, document an experiment, or help someone test a release.") + f'''<div class="wrap"><div class="reading"><p>{link(CHAT,"Join Warranty Void on Discord","button")}</p><h2>From the first sketch</h2><p>Use <strong>idea-drop</strong> for a question or sketch. Start one thread per prototype in <strong>build-logs</strong>. When others can try it, post the version, source or build files, licence, and instructions in <strong>releases</strong>.</p>
<h2>Connect GitHub in Discord</h2><ol><li>Open Discord’s <strong>User Settings → Connections</strong>.</li><li>Select <strong>GitHub</strong> and authorize your own account on GitHub.</li><li>Return to Warranty Void. Open the server menu and choose <strong>Linked Roles → GitHub Connected</strong> to claim the optional badge. Discord checks that you connected a GitHub account.</li><li>To work on a private project, share your GitHub username with an organizer in <strong>bench-chat</strong>. The organizer sends a separate invitation on GitHub.</li></ol><p>{link(LINKED,"Discord’s account-connection guide")} · {link(ORG,"Warranty Void on GitHub")}</p>
<h2>Contribute or publish</h2><p>Anyone can explore a public demo. Check the project’s licence before reusing its code or assets. You can open an issue or propose a change on GitHub. An organizer can invite collaborators to a private project individually.</p>
<h2>Member Kanban</h2><p>Invited collaborators use the signed-in board to track work. Releases appear in the public gallery when their project pages are published.</p>{link(BOARD,"Open the member Kanban","button light")}</div></div>'''
    write("community/index.html","Community · Warranty Void","Join the Discord, connect a GitHub account and contribute.","Community",community,"../assets/","../")

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--companion",type=Path,help="write the standalone Count23 Pages site to this directory")
    args=parser.parse_args()
    build(args.companion or ROOT, bool(args.companion))
