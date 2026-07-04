/* ===========================================================
   CADPOINT — Education Management Portal — Core Logic
   Data is persisted in localStorage so the demo behaves like a
   real CRM across page reloads (no backend required).
   =========================================================== */

const CAD = (() => {

  const LS = {
    students: "cad_students",
    enquiries: "cad_enquiries",
    session: "cad_session",
    activity: "cad_activity",
    theme: "cad_theme"
  };

  /* ---------------- Seed data (first run only) ---------------- */
  function seed() {
    if (!localStorage.getItem(LS.students)) {
      const demo = [
        { id: "STU001", name: "Arun Kumar", course: "AutoCAD 2D & 3D", duration: "3 Months", join: "2026-01-12", mobile: "9876543210", email: "arun.k@example.com", attendance: 92, progress: 100, status: "Finished", photo: "" },
        { id: "STU002", name: "Priya Sharma", course: "Revit Architecture", duration: "4 Months", join: "2026-02-03", mobile: "9876511220", email: "priya.s@example.com", attendance: 88, progress: 65, status: "Ongoing", photo: "" },
        { id: "STU003", name: "Mohammed Faisal", course: "SolidWorks", duration: "3 Months", join: "2026-03-10", mobile: "9988776655", email: "faisal.m@example.com", attendance: 76, progress: 40, status: "Ongoing", photo: "" },
        { id: "STU004", name: "Divya Ranganathan", course: "Python Programming", duration: "2 Months", join: "2025-12-01", mobile: "9090909090", email: "divya.r@example.com", attendance: 95, progress: 100, status: "Finished", photo: "" },
        { id: "STU005", name: "Karthik Raja", course: "Data Science & AI", duration: "6 Months", join: "2026-04-18", mobile: "9123456780", email: "karthik.r@example.com", attendance: 81, progress: 22, status: "Ongoing", photo: "" }
      ];
      localStorage.setItem(LS.students, JSON.stringify(demo));
    }
    if (!localStorage.getItem(LS.enquiries)) {
      const enq = [
        { name: "Sneha Patel", course: "UI/UX Design", phone: "9876001122", stage: "Follow-up", date: "2026-06-10" },
        { name: "Rahul Verma", course: "Civil 3D", phone: "9876334455", stage: "New", date: "2026-06-15" },
        { name: "Anita Joseph", course: "Java Development", phone: "9876778899", stage: "Admitted", date: "2026-05-28" }
      ];
      localStorage.setItem(LS.enquiries, JSON.stringify(enq));
    }
    if (!localStorage.getItem(LS.activity)) {
      logActivity("System", "Education Management Portal initialised.", true);
    }
  }

  function students() { return JSON.parse(localStorage.getItem(LS.students) || "[]"); }
  function saveStudents(arr) { localStorage.setItem(LS.students, JSON.stringify(arr)); }
  function enquiries() { return JSON.parse(localStorage.getItem(LS.enquiries) || "[]"); }
  function saveEnquiries(arr) { localStorage.setItem(LS.enquiries, JSON.stringify(arr)); }

  function logActivity(actor, text, silent) {
    const arr = JSON.parse(localStorage.getItem(LS.activity) || "[]");
    arr.unshift({ actor, text, time: new Date().toISOString() });
    localStorage.setItem(LS.activity, JSON.stringify(arr.slice(0, 40)));
    if (!silent) refreshActivityWidgets();
  }
  function activity() { return JSON.parse(localStorage.getItem(LS.activity) || "[]"); }
  function refreshActivityWidgets() {
    document.dispatchEvent(new CustomEvent("cad:activity-updated"));
  }

  /* ---------------- Auth ---------------- */
  // Demo credentials — Admin only. Change freely.
  const ADMIN_CREDENTIALS = { username: "admin", password: "Cadpoint@123" };

  function login(username, password) {
    if (username === ADMIN_CREDENTIALS.username && password === ADMIN_CREDENTIALS.password) {
      const session = { role: "admin", name: "Administrator", loggedAt: Date.now() };
      localStorage.setItem(LS.session, JSON.stringify(session));
      logActivity("Admin", "Logged in to the Management Dashboard.");
      return { ok: true };
    }
    return { ok: false, message: "Invalid username or password." };
  }

  function loginAsStudent() {
    const session = { role: "student", name: "Student User", loggedAt: Date.now() };
    localStorage.setItem(LS.session, JSON.stringify(session));
    return { ok: true };
  }

  function session() { return JSON.parse(localStorage.getItem(LS.session) || "null"); }
  function isAdmin() { const s = session(); return !!s && s.role === "admin"; }
  function logout() {
    const s = session();
    if (s) logActivity(s.role === "admin" ? "Admin" : "Student", "Logged out.");
    localStorage.removeItem(LS.session);
  }
  function requireRole(role, redirectTo) {
    const s = session();
    if (!s || (role && s.role !== role)) {
      window.location.href = redirectTo || "login-select.html";
      return false;
    }
    return true;
  }

  /* ---------------- Theme ---------------- */
  function initTheme() {
    const saved = localStorage.getItem(LS.theme) || "light";
    document.documentElement.setAttribute("data-theme", saved);
    updateThemeIcon(saved);
  }
  function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem(LS.theme, next);
    updateThemeIcon(next);
  }
  function updateThemeIcon(theme) {
    document.querySelectorAll(".theme-toggle i").forEach(i => {
      i.className = theme === "dark" ? "fas fa-sun" : "fas fa-moon";
    });
  }

  /* ---------------- Toast ---------------- */
  function toast(message, icon = "fa-circle-check") {
    document.querySelectorAll(".cad-toast").forEach(t => t.remove());
    const div = document.createElement("div");
    div.className = "cad-toast";
    div.innerHTML = `<i class="fas ${icon}" style="color:var(--primary)"></i><span>${message}</span>`;
    document.body.appendChild(div);
    setTimeout(() => div.remove(), 3200);
  }

  /* ---------------- Utilities ---------------- */
  function initials(name) {
    return name.split(" ").map(n => n[0]).slice(0, 2).join("").toUpperCase();
  }
  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }
  function timeAgo(iso) {
    const diff = (Date.now() - new Date(iso).getTime()) / 1000;
    if (diff < 60) return "just now";
    if (diff < 3600) return Math.floor(diff / 60) + "m ago";
    if (diff < 86400) return Math.floor(diff / 3600) + "h ago";
    return Math.floor(diff / 86400) + "d ago";
  }

  /* ---------------- Export helpers ---------------- */
  function exportToCSV(rows, headers, filename) {
    const csv = [headers.join(",")]
      .concat(rows.map(r => headers.map(h => `"${String(r[h] ?? "").replace(/"/g, '""')}"`).join(",")))
      .join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
  }
  function exportToPDF(title, rows, headers) {
    const w = window.open("", "_blank");
    const style = `body{font-family:Arial,sans-serif;padding:24px;color:#222}
      h2{color:#8B0000} table{width:100%;border-collapse:collapse;margin-top:14px}
      th,td{border:1px solid #ddd;padding:8px 10px;font-size:13px;text-align:left}
      th{background:#8B0000;color:#fff}`;
    const head = `<tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr>`;
    const body = rows.map(r => `<tr>${headers.map(h => `<td>${r[h] ?? ""}</td>`).join("")}</tr>`).join("");
    w.document.write(`<html><head><title>${title}</title><style>${style}</style></head>
      <body><h2>${title}</h2><table>${head}${body}</table></body></html>`);
    w.document.close();
    setTimeout(() => w.print(), 300);
  }

  seed();

  return {
    students, saveStudents, enquiries, saveEnquiries,
    logActivity, activity,
    login, loginAsStudent, session, isAdmin, logout, requireRole,
    initTheme, toggleTheme, toast,
    initials, escapeHtml, timeAgo,
    exportToCSV, exportToPDF
  };
})();

document.addEventListener("DOMContentLoaded", () => CAD.initTheme());