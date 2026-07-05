#!/usr/bin/env python3
"""Generate gallery.html + per-category detail pages, and add Gallery to the nav."""
import os, re, html, json
from urllib.parse import quote as urlquote

ROOT = "/home/user"
CAT_DIR = os.path.join(ROOT, "categories")
os.makedirs(CAT_DIR, exist_ok=True)

# ---- icon SVGs (inner content; wrapped in a parent <svg viewBox="0 0 24 24">) ----
ICONS = {
  "signage":   '<path d="M3 7l9-4 9 4-9 4-9-4zM3 7v10l9 4 9-4V7" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 11v10" stroke-linecap="round"/>',
  "print":     '<path d="M6 9V3h12v6M6 18H4a2 2 0 01-2-2v-3a2 2 0 012-2h16a2 2 0 012 2v3a2 2 0 01-2 2h-2M6 14h12v7H6z" stroke-linecap="round" stroke-linejoin="round"/>',
  "uv":        '<path d="M6 9V3h12v6M6 18H4a2 2 0 01-2-2v-3a2 2 0 012-2h16a2 2 0 012 2v3a2 2 0 01-2 2h-2M6 14h12v7H6z" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 17l2 2 4-4" stroke-linecap="round" stroke-linejoin="round"/>',
  "gift":      '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M5 12v9h14v-9M12 8v13" stroke-linecap="round"/><path d="M12 8S10.5 3 8 3a2 2 0 000 4h4zM12 8s1.5-5 4-5a2 2 0 010 4h-4z" stroke-linecap="round" stroke-linejoin="round"/>',
  "sticker":   '<path d="M20.6 13.4L13.4 20.6a2 2 0 01-2.8 0l-7-7V4h9.6l7 7a2 2 0 010 2.8z" stroke-linecap="round" stroke-linejoin="round"/><circle cx="7.5" cy="7.5" r="1.2"/>',
  "vehicle":   '<path d="M3 13l2-5a2 2 0 012-1.5h10A2 2 0 0119 8l2 5v5a1 1 0 01-1 1h-1a1 1 0 01-1-1v-1H6v1a1 1 0 01-1 1H4a1 1 0 01-1-1v-5z" stroke-linecap="round" stroke-linejoin="round"/><path d="M3 13h18M7 16h.01M17 16h.01" stroke-linecap="round"/>',
  "offset":    '<rect x="3" y="8" width="18" height="12" rx="1"/><path d="M3 12h18M7 8V4h10v4" stroke-linecap="round" stroke-linejoin="round"/>',
  "cnc":       '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M20 4L8.12 15.88M14.47 14.48L20 20M8.12 8.12L12 12" stroke-linecap="round" stroke-linejoin="round"/>',
  "smart":     '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4" stroke-linecap="round"/><path d="M9 9l2 2 4-4" stroke-linecap="round" stroke-linejoin="round"/>',
  "mep":       '<path d="M13 2L3 14h7l-1 8 11-13h-7l0-7z" stroke-linecap="round" stroke-linejoin="round"/>',
  "carpentry": '<path d="M14.7 6.3a4 4 0 00-5.4 5.4L3 18v3h3l6.3-6.3a4 4 0 005.4-5.4l-2.3 2.3-2-2 2.3-2.3z" stroke-linecap="round" stroke-linejoin="round"/>',
  "decor":     '<path d="M12 3l2.39 4.84L20 8.6l-4 3.9.94 5.5L12 15.5 7.06 18l.94-5.5-4-3.9 5.61-.76L12 3z" stroke-linecap="round" stroke-linejoin="round"/>',
  "security":  '<path d="M12 2l8 4v5c0 4.5-3.2 8.5-8 9-4.8-.5-8-4.5-8-9V6l8-4z" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 12l2 2 4-4" stroke-linecap="round" stroke-linejoin="round"/>',
  "shift":     '<path d="M1 12h13M12 6l6 6-6 6" stroke-linecap="round" stroke-linejoin="round"/><rect x="18" y="3" width="4" height="18" rx="1"/>',
}

# ---- category data ----
CATS = [
  # Printing & Branding
  dict(slug="3d-signage", name="3D Signage", group="Printing & Branding", icon="signage",
       short="Eye-catching illuminated and dimensional lettering & logos for shopfronts.",
       long="Stand out day and night with bespoke 3D signage. We design, fabricate and install illuminated channel letters, fabricated logos, acrylic and metal 3D lettering, and backlit halo signs engineered for both indoor and outdoor use — built to endure the UAE climate and built to be noticed.",
       hero="hero3.jpg", imgs=["hero3.jpg","about.jpg","hero1.jpg","project1.jpg","project3.jpg","hero2.jpg"]),
  dict(slug="digital-print", name="Digital Print", group="Printing & Branding", icon="print",
       short="High-resolution large-format digital printing for any surface.",
       long="From posters and banners to backlit films and exhibition graphics, our large-format digital printing delivers sharp, vibrant output on a huge range of media. Fast turnaround, accurate colour, and finishes up to archival quality.",
       hero="hero3.jpg", imgs=["hero3.jpg","about.jpg","project4.jpg","hero1.jpg","hero2.jpg","project1.jpg"]),
  dict(slug="uv-printing", name="UV Printing", group="Printing & Branding", icon="uv",
       short="Direct-to-substrate UV printing on wood, glass, acrylic & more.",
       long="Print directly onto rigid and flexible materials — wood, glass, acrylic, metal, foam board and more — with our flatbed UV printers. Vivid, durable, scratch-resistant prints that open up endless branding and decor possibilities.",
       hero="project4.jpg", imgs=["project4.jpg","hero3.jpg","hero1.jpg","about.jpg","project1.jpg","hero2.jpg"]),
  dict(slug="gift-items", name="Gift Items", group="Printing & Branding", icon="gift",
       short="Personalised corporate gifts, mugs, pens, diaries & premium sets.",
       long="Memorable branded gifts that keep your business top-of-mind. We customise mugs, pens, notebooks, USBs, trophies, glassware and premium corporate gift sets with your logo — perfect for events, clients and staff.",
       hero="hero3.jpg", imgs=["hero3.jpg","project4.jpg","hero2.jpg","project1.jpg","hero1.jpg","about.jpg"]),
  dict(slug="indoor-outdoor-sticker", name="Indoor / Outdoor Sticker", group="Printing & Branding", icon="sticker",
       short="Frosted, vinyl, cut and one-way vision stickers & decals.",
       long="Custom stickers and decals for every application — glass manifestation, frosted privacy film, vinyl cut lettering, floor graphics, vehicle-grade vinyl and one-way vision. Precision-cut and weatherproof for lasting results.",
       hero="hero3.jpg", imgs=["hero3.jpg","hero1.jpg","about.jpg","project3.jpg","hero2.jpg","project4.jpg"]),
  dict(slug="vehicle-branding", name="Vehicle Branding", group="Printing & Branding", icon="vehicle",
       short="Full & partial vehicle wraps that turn your fleet into moving ads.",
       long="Transform your car, van or fleet into a moving billboard. We handle design, printing and professional installation of full wraps, partial wraps and cut-vinyl graphics using premium cast vinyl and protective laminate.",
       hero="about.jpg", imgs=["about.jpg","hero3.jpg","hero1.jpg","project4.jpg","project2.jpg","hero2.jpg"]),
  dict(slug="screen-offset-printing", name="Screen & Offset Printing", group="Printing & Branding", icon="offset",
       short="Volume printing — brochures, cards, letterheads & stationery.",
       long="Cost-effective volume printing for business stationery and marketing collateral. Brochures, business cards, letterheads, envelopes, invoices, flyers and booklets — produced on screen and offset presses for consistent quality at scale.",
       hero="about.jpg", imgs=["about.jpg","hero3.jpg","project4.jpg","hero1.jpg","project2.jpg","hero2.jpg"]),
  dict(slug="cnc-laser-cutting", name="CNC & Laser Cutting", group="Printing & Branding", icon="cnc",
       short="Precision-cut signage, letters, panels & decorative grids.",
       long="Intricate, repeatable cutting and engraving on acrylic, wood, MDF, metal and more. Ideal for custom signage, 3D letters, decorative wall panels, display stands and architectural detailing that needs exact tolerances.",
       hero="about.jpg", imgs=["about.jpg","project3.jpg","hero1.jpg","hero3.jpg","project4.jpg","project2.jpg"]),
  # Technical & Fit-Out
  dict(slug="smart-home-paints", name="Smart Home & Paints Works", group="Technical & Fit-Out", icon="smart",
       short="Smart automation plus premium painting & decorative finishes.",
       long="Bring your walls to life and your home online. Our team delivers premium painting, texture and decorative wall finishes alongside smart-home automation — lighting, climate, blinds and security controlled from your phone or voice.",
       hero="project1.jpg", imgs=["project1.jpg","hero2.jpg","project4.jpg","hero1.jpg","project3.jpg","project5.jpg"]),
  dict(slug="maintenance-mep", name="Maintenance (MEP)", group="Technical & Fit-Out", icon="mep",
       short="Electrical, plumbing, HVAC & general property maintenance.",
       long="A single point of contact for all your mechanical, electrical and plumbing needs. From fault-finding and repairs to full installations and preventative maintenance contracts, our licensed technicians keep your property running smoothly.",
       hero="project3.jpg", imgs=["project3.jpg","hero1.jpg","project1.jpg","project4.jpg","project5.jpg","about.jpg"]),
  dict(slug="carpenter-work", name="Carpenter Work", group="Technical & Fit-Out", icon="carpentry",
       short="Custom cabinetry, wardrobes, doors & bespoke woodwork.",
       long="Skilled carpentry tailored to your space — built-in wardrobes, kitchens, vanity units, doors, shelving and custom furniture. Crafted from quality timber and boards, finished to a furniture-grade standard and fitted on-site.",
       hero="project2.jpg", imgs=["project2.jpg","about.jpg","project4.jpg","hero2.jpg","project1.jpg","project3.jpg"]),
  dict(slug="decor", name="Decor", group="Technical & Fit-Out", icon="decor",
       short="Gypsum, false ceilings, panelling & complete interior decor.",
       long="Turnkey interior decor that elevates any space. False ceilings and gypsum work, feature walls, wood panelling, lighting design and complete room makeovers — coordinated end-to-end for a polished, cohesive result.",
       hero="hero2.jpg", imgs=["hero2.jpg","project4.jpg","project5.jpg","project1.jpg","hero1.jpg","hero3.jpg"]),
  dict(slug="home-security", name="Home Security", group="Technical & Fit-Out", icon="security",
       short="CCTV, access control, alarms & smart surveillance systems.",
       long="Protect what matters with reliable security systems. We supply and install HD CCTV, video doorbells, access control, intercoms and alarm systems — with remote monitoring so you can check in from anywhere, anytime.",
       hero="hero1.jpg", imgs=["hero1.jpg","project3.jpg","about.jpg","hero3.jpg","project1.jpg","hero2.jpg"]),
  dict(slug="packing-shifting", name="Packing & Shifting", group="Technical & Fit-Out", icon="shift",
       short="Safe, insured home & office moving and packing services.",
       long="Stress-free relocation for homes and offices. Professional packing with quality materials, careful handling of furniture and fragile items, transport and reassembly at your new location — fully coordinated from start to finish.",
       hero="about.jpg", imgs=["about.jpg","hero1.jpg","hero3.jpg","project4.jpg","hero2.jpg","project3.jpg"]),
]

GROUPS = ["Printing & Branding", "Technical & Fit-Out"]
IMG_POOL = ["hero1.jpg","hero2.jpg","hero3.jpg","project1.jpg","project2.jpg","project3.jpg","project4.jpg","project5.jpg","about.jpg"]

def icon_svg(name, sw="1.5", extra=""):
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="%s"%s>%s</svg>' % (sw, extra, ICONS[name])

# ---------------- shared head ----------------
def head(prefix, title, desc, og_image):
    domain = "https://www.tpfitout.com"
    keywords = ("printing, signage, advertising, branding, digital print, UV printing, 3D signage, "
                "vehicle branding, stickers, CNC laser cutting, screen printing, gift items, "
                "smart home, MEP maintenance, carpentry, decor, home security, packing and shifting")
    schema = {"@context":"https://schema.org","@type":"LocalBusiness",
              "name":"T&P / TechandPrint","description":desc}
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{html.escape(desc)}" />
  <meta name="keywords" content="{keywords}" />
  <meta name="theme-color" content="#0a1622" />
  <link rel="canonical" href="{domain}/{('gallery.html' if 'Gallery' in title else 'categories/')}" />
  <link rel="manifest" href="{prefix}site.webmanifest" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{html.escape(desc)}" />
  <meta property="og:image" content="{domain}/{og_image}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:image" content="{domain}/{og_image}" />
  <script type="application/ld+json">{json.dumps(schema)}</script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500;1,600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{prefix}css/styles.css" />
  <link rel="icon" type="image/png" href="{prefix}images/favicon.png" />
</head>'''

# ---------------- shared header / footer ----------------
def header(prefix, active):
    nav_items = [("index.html","Home"), ("gallery.html","Gallery"), ("about.html","About"), ("services.html","Services"), ("contact.html","Contact")]
    nav = ""
    for href,label in nav_items:
        cls = ' class="active"' if label==active else ""
        nav += f'<a href="{prefix}{href}"{cls}>{label}</a>\n        '
    mobile = "".join(f'<a href="{prefix}{href}">{label}</a>' for href,label in nav_items)
    return f'''<header class="header" id="header">
    <div class="container">
      <a href="{prefix}index.html" class="logo" aria-label="T&amp;P home"><img src="{prefix}images/logo.png" alt="T&amp;P logo" class="logo-img" width="699" height="444" /></a>
      <nav class="nav" aria-label="Primary">
        {nav}<a href="{prefix}contact.html" class="btn btn-gold nav-cta">Get a Quote</a>
      </nav>
      <button class="hamburger" id="hamburger" aria-label="Open menu" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </header>
  <div class="mobile-menu" id="mobileMenu">
    {mobile}
    <a href="{prefix}contact.html" class="btn btn-gold">Get a Quote</a>
  </div>'''

WA_SVG = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M.057 24l1.687-6.163a11.867 11.867 0 01-1.587-5.946C.16 5.335 5.495 0 12.05 0a11.817 11.817 0 018.413 3.488 11.824 11.824 0 013.48 8.414c-.003 6.557-5.338 11.892-11.893 11.892a11.9 11.9 0 01-5.688-1.448L.057 24zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/></svg>'

def footer(prefix):
    return f'''<footer class="footer">
    <div class="container">
      <div class="footer-top">
        <div class="footer-about">
          <a href="{prefix}index.html" class="logo"><img src="{prefix}images/logo.png" alt="T&amp;P logo" class="logo-img" width="699" height="444" /></a>
          <p>Print | Brand | Promote. One-stop solution for all your advertising, printing, signage and technical fit-out needs.</p>
          <div class="social-row">
            <a href="#" aria-label="Instagram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg></a>
            <a href="#" aria-label="LinkedIn"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M4.98 3.5C4.98 4.88 3.87 6 2.5 6S0 4.88 0 3.5 1.12 1 2.5 1s2.48 1.12 2.48 2.5zM.22 8h4.56v15H.22V8zm7.5 0h4.37v2.05h.06c.61-1.15 2.1-2.36 4.32-2.36 4.62 0 5.47 3.04 5.47 6.99V23h-4.56v-6.62c0-1.58-.03-3.62-2.2-3.62-2.2 0-2.54 1.72-2.54 3.5V23H7.72V8z"/></svg></a>
            <a href="#" aria-label="Facebook"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M22 12a10 10 0 10-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.5 1.49-3.89 3.78-3.89 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56V12h2.78l-.44 2.89h-2.34v6.99A10 10 0 0022 12z"/></svg></a>
          </div>
        </div>
        <div>
          <h5>Pages</h5>
          <div class="footer-links"><a href="{prefix}index.html">Home</a><a href="{prefix}gallery.html">Gallery</a><a href="{prefix}about.html">About Us</a><a href="{prefix}services.html">Services</a><a href="{prefix}contact.html">Contact</a></div>
        </div>
        <div>
          <h5>Popular Categories</h5>
          <div class="footer-links"><a href="{prefix}categories/3d-signage.html">3D Signage</a><a href="{prefix}categories/digital-print.html">Digital Print</a><a href="{prefix}categories/vehicle-branding.html">Vehicle Branding</a><a href="{prefix}categories/decor.html">Decor</a></div>
        </div>
        <div>
          <h5>Get in Touch</h5>
          <ul class="footer-contact">
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M21 10c0 7-9 12-9 12s-9-5-9-12a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg> Abu Bakar Al Sadique Rd, Dubai, UAE</li>
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.13.96.36 1.9.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0122 16.92z" stroke-linecap="round" stroke-linejoin="round"/></svg> <a href="tel:+971562799398">+971 56 279 9398</a></li>
            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6" stroke-linecap="round" stroke-linejoin="round"/></svg> <a href="mailto:techandprint360@gmail.com">techandprint360@gmail.com</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <span>&copy; <span id="year"></span> TechandPrint (T&amp;P). All rights reserved.</span>
        <span>Print &middot; Brand &middot; Promote</span>
      </div>
    </div>
  </footer>

  <a href="https://api.whatsapp.com/send?phone=971562799398" class="wa-float wa-link" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">{WA_SVG}</a>
  <script src="{prefix}js/script.js"></script>'''

# ============================================================
# 1) GALLERY PAGE  (root)
# ============================================================
def build_gallery():
    cards_html = ""
    for gi, group in enumerate(GROUPS):
        cards_html += f'<div class="gallery-group-label reveal"><h3>{group}</h3><span class="gline"></span></div>\n      <div class="gallery-grid">\n'
        for c in [c for c in CATS if c["group"]==group]:
            cards_html += f'''        <a class="gallery-card reveal" href="categories/{c["slug"]}.html">
          <img src="images/{c["hero"]}" alt="{c["name"]} work by T&amp;P" loading="lazy" />
          <div class="gc-body">
            <span class="gc-cat">{c["group"]}</span>
            <span class="gc-title">{c["name"]}</span>
            <span class="gc-desc">{c["short"]}</span>
          </div>
          <span class="gc-arrow">{icon_svg("signage", "2")}</span>
        </a>
'''
        cards_html += "      </div>\n      "

    page = f'''{head("", "Gallery — T&P / TechandPrint Services", "Browse our work across printing, signage, branding and technical services. Click any category to view a full gallery of that service.", "images/hero3.jpg")}
<body>
  {header("", "Gallery")}

  <section class="page-hero">
    <div class="container">
      <div class="breadcrumb"><a href="index.html">Home</a> <span>/</span> <span>Gallery</span></div>
      <span class="eyebrow">Our Work</span>
      <h1>Service Gallery</h1>
      <p>Explore what we do. Each tile below represents one of our service categories — click any image to open its full gallery and see more detail.</p>
    </div>
  </section>

  <section class="section">
    <div class="container">
      {cards_html}
    </div>
  </section>

  <section class="cta-band section">
    <div class="container">
      <span class="eyebrow center" style="color:var(--gold); justify-content:center;">Ready to Start?</span>
      <h2>Need Any of These Services?</h2>
      <p>From a single sign to a full fit-out, we've got you covered. Message us on WhatsApp for a quick quote.</p>
      <div class="cta-actions">
        <a href="contact.html" class="btn btn-gold">Get a Quote</a>
        <a href="https://api.whatsapp.com/send?phone=971562799398" class="btn btn-whatsapp wa-link" target="_blank" rel="noopener">{WA_SVG} Chat on WhatsApp</a>
      </div>
    </div>
  </section>

  {footer("")}
</body>
</html>
'''
    open(os.path.join(ROOT,"gallery.html"),"w",encoding="utf-8").write(page)
    print("✓ gallery.html")

# ============================================================
# 2) CATEGORY DETAIL PAGES  (categories/<slug>.html)
# ============================================================
def build_category(c):
    # gallery items
    items = ""
    for im in c["imgs"]:
        items += f'''        <a class="cg-item" data-lightbox="{c["slug"]}" data-full="images/{im}" href="images/{im}">
          <img src="../images/{im}" alt="{c["name"]} sample" loading="lazy" />
          <span class="zoom"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4M11 8v6M8 11h6" stroke-linecap="round"/></svg></span>
        </a>
'''
    # related (other categories in same group, fallback to all)
    related = [x for x in CATS if x["slug"]!=c["slug"]]
    rel_html = "".join(f'<a href="../categories/{x["slug"]}.html">{x["name"]}</a>' for x in related[:8])

    page = f'''{head("../", c["name"]+" — T&P / TechandPrint", c["short"]+" "+c["long"][:120], "images/"+c["hero"])}
<body>
  {header("../", "Gallery")}

  <section class="page-hero">
    <div class="container">
      <div class="breadcrumb"><a href="../index.html">Home</a> <span>/</span> <a href="../gallery.html">Gallery</a> <span>/</span> <span>{c["name"]}</span></div>
      <span class="eyebrow">{c["group"]}</span>
      <h1>{c["name"]}</h1>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <a href="../gallery.html" class="cat-back"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M11 18l-6-6 6-6" stroke-linecap="round" stroke-linejoin="round"/></svg> Back to Gallery</a>

      <div class="cat-intro">
        <div class="reveal">
          <div class="cat-ic">{icon_svg(c["icon"])}</div>
          <span class="eyebrow">{c["group"]}</span>
          <h2>{c["name"]}</h2>
          <p class="lead">{c["long"]}</p>
          <div style="margin-top:26px;">
            <a href="../contact.html" class="btn btn-gold">Enquire Now</a>
            <a href="https://api.whatsapp.com/send?phone=971562799398&text={urlquote('Hi T&P, I am interested in your '+c['name']+' service.')}" class="btn btn-outline wa-link" target="_blank" rel="noopener" style="margin-left:8px;">WhatsApp Us</a>
          </div>
        </div>
        <div class="cat-intro-media reveal d1">
          <img src="../images/{c["hero"]}" alt="{c["name"]} featured work" loading="lazy" />
        </div>
      </div>

      <div class="section-head reveal" style="margin-bottom:24px;">
        <span class="eyebrow">Project Gallery</span>
        <h2>{c["name"]} — Our Work</h2>
        <p>Click any image to enlarge.</p>
      </div>

      <div class="cat-gallery reveal">
{items}      </div>

      <div class="cat-related reveal">
        <span style="align-self:center; font-size:0.8rem; letter-spacing:0.1em; text-transform:uppercase; color:var(--text-soft); margin-right:6px;">More services:</span>
        {rel_html}
      </div>
    </div>
  </section>

  {footer("../")}
</body>
</html>
'''
    open(os.path.join(CAT_DIR, c["slug"]+".html"),"w",encoding="utf-8").write(page)
    print(f"✓ categories/{c['slug']}.html")

# ============================================================
# 3) ADD GALLERY TO NAV ON EXISTING PAGES
# ============================================================
def update_existing_nav():
    nav_re = re.compile(r'(<a href="index\.html"(?:[^>]*)>Home</a>)')
    for f in ["index.html","about.html","services.html","contact.html"]:
        p = os.path.join(ROOT,f)
        c = open(p,encoding="utf-8").read()
        new = nav_re.sub(lambda m: m.group(1)+'\n        <a href="gallery.html">Gallery</a>', c)
        if new != c:
            open(p,"w",encoding="utf-8").write(new)
            print(f"✓ nav updated: {f}")
        else:
            print(f"  (nav already has gallery or no match): {f}")

if __name__ == "__main__":
    build_gallery()
    for c in CATS:
        build_category(c)
    update_existing_nav()
    print("\nDone. %d categories." % len(CATS))
