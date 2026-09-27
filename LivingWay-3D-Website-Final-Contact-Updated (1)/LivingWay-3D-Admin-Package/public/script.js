const header = document.getElementById("siteHeader");
const menuToggle = document.querySelector(".menu-toggle");
const nav = document.querySelector(".nav");

function handleScroll() {
  header.classList.toggle("scrolled", window.scrollY > 18);
}
window.addEventListener("scroll", handleScroll, { passive: true });
handleScroll();

menuToggle?.addEventListener("click", () => {
  const open = nav.classList.toggle("open");
  menuToggle.setAttribute("aria-expanded", String(open));
});

document.querySelectorAll(".nav a").forEach(link => {
  link.addEventListener("click", () => {
    nav.classList.remove("open");
    menuToggle?.setAttribute("aria-expanded", "false");
  });
});

const sections = [...document.querySelectorAll("main section[id]")];
const navLinks = [...document.querySelectorAll('.nav a[href^="#"]')];
const sectionObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    navLinks.forEach(a => a.classList.toggle("active", a.getAttribute("href") === `#${entry.target.id}`));
  });
}, { rootMargin: "-40% 0px -50% 0px", threshold: 0 });
sections.forEach(s => sectionObserver.observe(s));

const revealObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add("visible");
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });
document.querySelectorAll(".reveal").forEach(el => revealObserver.observe(el));

const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();

const form = document.getElementById("designForm");
const statusBox = form?.querySelector(".form-status");
const submitButton = form?.querySelector(".submit-btn");

function setStatus(message, type) {
  if (!statusBox) return;
  statusBox.textContent = message;
  statusBox.className = `form-status show ${type}`;
}

form?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const required = form.querySelectorAll("[required]");
  let valid = true;

  required.forEach(field => {
    const wrapper = field.closest(".field");
    const empty = !field.value.trim();
    wrapper?.classList.toggle("invalid", empty);
    if (empty) valid = false;
  });

  const email = form.querySelector('input[type="email"]');
  if (email && email.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    email.closest(".field")?.classList.add("invalid");
    valid = false;
  }

  // Honeypot: silently stop obvious bots.
  if (form.querySelector('input[name="_honey"]').value) {
    event.preventDefault();
    return;
  }

  if (!valid) {
    event.preventDefault();
    setStatus("Please complete the required fields and check your email address.", "error");
    return;
  }

  // Save the enquiry to the secured LivingWay 3D API / D1 database.
  // The Worker can also send an admin notification when Resend is configured.
  submitButton.disabled = true;
  submitButton.innerHTML = "Sending request…";
  try {
    const payload = Object.fromEntries(new FormData(form).entries());
    const response = await fetch("/api/request", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.error || "Could not submit your request.");
    setStatus("Thank you! Your design request has been received. Our team will contact you soon.", "success");
    form.reset();
  } catch (error) {
    setStatus(error.message || "Something went wrong. Please try again or contact us directly.", "error");
  } finally {
    submitButton.disabled = false;
    submitButton.innerHTML = 'Send Design Request <span>→</span>';
  }
});

form?.querySelectorAll("input, select, textarea").forEach(field => {
  field.addEventListener("input", () => field.closest(".field")?.classList.remove("invalid"));
  field.addEventListener("change", () => field.closest(".field")?.classList.remove("invalid"));
});
