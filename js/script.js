/* =========================================================
   T&P — Interior Fit-Out & Contracting
   Core interactions
   ========================================================= */

(function () {
  "use strict";

  /* -------------------------------------------------------
     CONFIG — change your WhatsApp number here (ONE place).
     International format, digits only, no "+" or spaces.
     ------------------------------------------------------- */
  var WHATSAPP_NUMBER = "971567861057"; // <-- REPLACE WITH YOUR NUMBER
  var WHATSAPP_MSG = "Hi T&P, I'd like to discuss an interior fit-out project.";

  /* -------------------------------------------------------
     SOCIAL LINKS — change to your real profile URLs here.
     ------------------------------------------------------- */
  var SOCIAL_LINKS = {
    Instagram: "https://instagram.com/tp.fitout",
    Linkedin: "https://www.linkedin.com/company/tp-fitout",
    Facebook: "https://facebook.com/tpfitout"
  };

  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  /* ---- Apply WhatsApp links everywhere ---- */
  function buildWaHref(msg) {
    var base = "https://api.whatsapp.com/send?phone=" + WHATSAPP_NUMBER;
    return msg ? base + "&text=" + encodeURIComponent(msg) : base;
  }
  function initWhatsAppLinks() {
    var defaultHref = buildWaHref(WHATSAPP_MSG);
    $$(".wa-link").forEach(function (el) {
      // Only set href if it isn't a custom-prefilled link
      if (!el.getAttribute("href") || el.getAttribute("href").indexOf("api.whatsapp.com") === -1) {
        el.setAttribute("href", defaultHref);
      } else if (el.getAttribute("href").indexOf("phone=") > -1 &&
                 el.getAttribute("href").indexOf(WHATSAPP_NUMBER) === -1) {
        // Ensure it always points at the configured number
        el.setAttribute("href", el.getAttribute("href").replace(/phone=\d+/, "phone=" + WHATSAPP_NUMBER));
      }
      el.setAttribute("target", "_blank");
      el.setAttribute("rel", "noopener");
    });
  }

  /* ---- Apply social media links ---- */
  function initSocialLinks() {
    var norm = {};
    Object.keys(SOCIAL_LINKS).forEach(function (k) { norm[k.toLowerCase()] = SOCIAL_LINKS[k]; });
    $$(".social-row a").forEach(function (el) {
      var label = (el.getAttribute("aria-label") || "").trim().toLowerCase();
      var url = norm[label];
      if (url) {
        el.setAttribute("href", url);
        el.setAttribute("target", "_blank");
        el.setAttribute("rel", "noopener");
      }
    });
  }

  /* ---- Header scroll state ---- */
  function initHeader() {
    var header = $("#header");
    if (!header) return;
    var onScroll = function () {
      if (window.scrollY > 40) header.classList.add("scrolled");
      else header.classList.remove("scrolled");
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---- Mobile menu ---- */
  function initMobileMenu() {
    var burger = $("#hamburger");
    var menu = $("#mobileMenu");
    if (!burger || !menu) return;

    var toggle = function (open) {
      var isOpen = typeof open === "boolean" ? open : !menu.classList.contains("open");
      menu.classList.toggle("open", isOpen);
      burger.classList.toggle("active", isOpen);
      burger.setAttribute("aria-expanded", isOpen ? "true" : "false");
      document.body.style.overflow = isOpen ? "hidden" : "";
    };

    burger.addEventListener("click", function () { toggle(); });
    $$("#mobileMenu a").forEach(function (a) {
      a.addEventListener("click", function () { toggle(false); });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.classList.contains("open")) toggle(false);
    });
  }

  /* ---- Hero slider ---- */
  function initHeroSlider() {
    var hero = $("#hero");
    if (!hero) return;
    var slides = $$(".hero-slide", hero);
    var dots = $$("#heroDots button", hero);
    if (slides.length < 2) return;

    var current = 0;
    var timer = null;
    var INTERVAL = 5500;

    function show(idx) {
      slides.forEach(function (s, i) { s.classList.toggle("active", i === idx); });
      dots.forEach(function (d, i) { d.classList.toggle("active", i === idx); });
      current = idx;
    }
    function next() { show((current + 1) % slides.length); }
    function start() { stop(); timer = setInterval(next, INTERVAL); }
    function stop() { if (timer) clearInterval(timer); }

    dots.forEach(function (d, i) {
      d.addEventListener("click", function () { show(i); start(); });
    });

    // Pause when tab hidden / hero out of view
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) stop(); else start();
    });
    start();
  }

  /* ---- Scroll reveal ---- */
  function initReveal() {
    var items = $$(".reveal");
    if (!items.length) return;
    if (!("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("in"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -60px 0px" });
    items.forEach(function (el) { io.observe(el); });
  }

  /* ---- Animated counters ---- */
  function initCounters() {
    var nums = $$("[data-count]");
    if (!nums.length) return;

    var run = function (el) {
      var target = parseInt(el.getAttribute("data-count"), 10) || 0;
      var dur = 1600;
      var start = null;
      function step(ts) {
        if (!start) start = ts;
        var p = Math.min((ts - start) / dur, 1);
        var eased = 1 - Math.pow(1 - p, 3); // easeOutCubic
        el.textContent = Math.floor(eased * target).toLocaleString();
        if (p < 1) requestAnimationFrame(step);
        else el.textContent = target.toLocaleString();
      }
      requestAnimationFrame(step);
    };

    if (!("IntersectionObserver" in window)) {
      nums.forEach(run); return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          run(entry.target);
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });
    nums.forEach(function (el) { io.observe(el); });
  }

  /* ---- Contact form → WhatsApp (no backend) ---- */
  function initContactForm() {
    var form = $("#contactForm");
    if (!form) return;
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      var name = ($("#name", form) || {}).value || "";
      var phone = ($("#phone", form) || {}).value || "";
      var email = ($("#email", form) || {}).value || "";
      var service = ($("#service", form) || {}).value || "";
      var message = ($("#message", form) || {}).value || "";

      // Basic validation
      if (!name.trim() || !phone.trim()) {
        var firstBad = !name.trim() ? $("#name", form) : $("#phone", form);
        if (firstBad) { firstBad.focus(); firstBad.style.borderColor = "#d9836b"; }
        return;
      }

      var lines = [
        "Hello T&P, I'd like a quote for an interior fit-out.",
        "",
        "Name: " + name,
        "Phone: " + phone
      ];
      if (email.trim()) lines.push("Email: " + email);
      if (service) lines.push("Service: " + service);
      if (message.trim()) lines.push("", "Details: " + message);

      var url = buildWaHref(lines.join("\n"));
      window.open(url, "_blank", "noopener");
    });
  }

  /* ---- Footer year ---- */
  function initYear() {
    var y = $("#year");
    if (y) y.textContent = new Date().getFullYear();
  }

  /* ---- Boot ---- */
  function init() {
    initWhatsAppLinks();
    initSocialLinks();
    initHeader();
    initMobileMenu();
    initHeroSlider();
    initReveal();
    initCounters();
    initContactForm();
    initYear();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
