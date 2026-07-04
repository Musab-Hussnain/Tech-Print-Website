# T&P — Interior Fit-Out & Contracting Website

A modern, fully responsive 4-page marketing website for an interior fit-out / contracting
business. Built with clean HTML, CSS and vanilla JavaScript — **no build step, no backend,
no database**. Just open or upload the files.

---

## 📁 Structure

```
.
├── index.html            ← Home (hero slider, services, 9 project showcase, stats, CTA)
├── about.html            ← About (story, values, stats, why choose us)
├── services.html         ← Services (6 trades in detail + 4-step process)
├── contact.html          ← Contact (info, WhatsApp block, WhatsApp form, map)
│
├── css/styles.css        ← All styling (design tokens, responsive, animations)
├── js/script.js          ← Slider, menu, scroll reveal, counters, WhatsApp + social config
│
├── sitemap.xml           ← SEO: sitemap for Google Search Console
├── robots.txt            ← SEO: crawler directives
├── site.webmanifest      ← PWA manifest (app name, theme colour, icon)
├── netlify.toml          ← One-click deploy + security headers
├── favicon (linked)      ← images/favicon.png
│
├── images/               ← 11 photos + logo + favicon
└── deliverables/
    ├── business-card.html ← Print-ready business card (85×55 mm) → Save as PDF
    └── letterhead.html    ← Print-ready A4 letterhead → Save as PDF
```

---

## 🚀 Deploy (Free Hosting)

The site is 100% static, so hosting is **free**:

1. **Netlify:** drag the whole folder into [Netlify Drop](https://app.netlify.com/drop),
   or connect the repo (the included `netlify.toml` configures publishing + HTTPS).
2. **GitHub Pages:** push to a repo → Settings → Pages → deploy from branch.
3. **Any host:** upload all files via FTP/cPanel to `public_html`.
4. **Local preview:** run `python3 -m http.server` in the folder, then open `localhost:8000`.

> **SSL / HTTPS** is auto-provisioned by Netlify, GitHub Pages, Vercel, etc. — no setup needed.
> **3D Secure** only matters if you sell online; this is a lead-gen site, so it isn't required.

---

## ✏️ Customize (the important edits)

All in **`js/script.js`** near the top — one config block:

```js
var WHATSAPP_NUMBER = "971501234567";      // country code + number, digits only
var WHATSAPP_MSG    = "Hi T&P, I'd like..."; // pre-filled message
var SOCIAL_LINKS = {
  Instagram: "https://instagram.com/tp.fitout",
  Linkedin:  "https://www.linkedin.com/company/tp-fitout",
  Facebook:  "https://facebook.com/tpfitout"
};
```

These drive **every** WhatsApp button and social icon across all 4 pages automatically.

### Other details — search & replace across the `.html` files
- `+971 50 123 4567` → your phone (display + `tel:` links)
- `hello@tpfitout.com` → your email
- `Business Bay, Dubai, UAE` → your location
- `www.tpfitout.com` → your domain. **Also update it in** `sitemap.xml`, `robots.txt`,
  and the Open Graph / canonical / schema tags in each `<head>`.
- `Your Name` / `Founder & Director` in the deliverables.

> **Business email accounts** (e.g. info@yourdomain.com) are created at your domain/hosting
> provider's control panel — not part of the website code.

---

## ✨ Features

- Auto-playing **hero slider** with Ken Burns zoom + clickable dots
- Sticky compaction header, animated **mobile menu**
- **Scroll-reveal** animations + animated stat counters
- Hover-reveal **project grid** (9 projects) + 6 service cards + alternating service rows
- **Floating WhatsApp button** on every page (with pulse ring)
- Contact form that composes a pre-filled **WhatsApp message** (no backend)
- Fully **responsive** (desktop → mobile), `prefers-reduced-motion` aware
- **Complete SEO:** meta keywords, per-page titles/descriptions, Open Graph + Twitter cards,
  canonical URLs, JSON-LD `LocalBusiness` schema, `sitemap.xml`, `robots.txt`
- **Social media** icons wired to your profiles via one config point

## 🖨️ Print deliverables
Open `deliverables/business-card.html` and `deliverables/letterhead.html` in a browser,
edit the name/details, then **File → Print → Save as PDF** (set margins to "None").
