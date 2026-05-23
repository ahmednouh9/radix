// ===== Language =====
let currentLang = localStorage.getItem("lang") || "en";

function setLanguage(lang) {
  currentLang = lang;
  localStorage.setItem("lang", lang);
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.dataset.i18n;
    el.textContent = t(key, lang);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    const key = el.dataset.i18nPlaceholder;
    el.placeholder = t(key, lang);
  });
  fetch("/?lang=" + lang).catch(() => {});
}

document.addEventListener("DOMContentLoaded", () => {
  setLanguage(currentLang);
});

// ===== Theme =====
function toggleTheme() {
  // Dark mode is default and only mode
  // This is kept as a stub for potential future light mode
}

// ===== Sidebar =====
function toggleSidebar() {
  document.querySelector(".sidebar").classList.toggle("open");
}

document.addEventListener("click", (e) => {
  const sidebar = document.querySelector(".sidebar");
  const hamburger = document.querySelector(".hamburger");
  if (sidebar && sidebar.classList.contains("open")) {
    if (!sidebar.contains(e.target) && !hamburger?.contains(e.target)) {
      sidebar.classList.remove("open");
    }
  }
});

// ===== SSE Connection =====
function connectSSE() {
  const url = "/api/sse";
  let eventSource = null;
  let reconnectTimer = null;

  function connect() {
    if (eventSource) {
      eventSource.close();
    }

    eventSource = new EventSource(url);

    eventSource.onopen = () => {
      // connected
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.event === "notification") {
          window.dispatchEvent(new CustomEvent("sse-notification", { detail: data.data }));
        }
      } catch (e) {
        // ignore parse errors
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      reconnectTimer = setTimeout(connect, 5000);
    };
  }

  connect();

  return {
    close: () => {
      if (eventSource) eventSource.close();
      if (reconnectTimer) clearTimeout(reconnectTimer);
    }
  };
}

// ===== Toast Notifications =====
function showToast(message, type = "info") {
  const container = document.querySelector(".toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.3s";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ===== Copy to Clipboard =====
function copyToClipboard(text, btn) {
  navigator.clipboard.writeText(text).then(() => {
    btn.textContent = t("share.copied", currentLang);
    btn.classList.add("copied");
    setTimeout(() => {
      btn.textContent = t("share.copy", currentLang);
      btn.classList.remove("copied");
    }, 2000);
  }).catch(() => {
    // fallback
    const textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
    btn.textContent = t("share.copied", currentLang);
    btn.classList.add("copied");
    setTimeout(() => {
      btn.textContent = t("share.copy", currentLang);
      btn.classList.remove("copied");
    }, 2000);
  });
}

// ===== Format Date =====
function formatDate(dateStr) {
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now - date;
  const mins = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (mins < 1) return currentLang === "ar" ? "الآن" : "just now";
  if (mins < 60) return mins + (currentLang === "ar" ? " دقيقة" : "m");
  if (hours < 24) return hours + (currentLang === "ar" ? " ساعة" : "h");
  if (days < 7) return days + (currentLang === "ar" ? " يوم" : "d");
  return date.toLocaleDateString(currentLang === "ar" ? "ar-SA" : "en-US");
}

// ===== Fetch API wrapper =====
async function apiFetch(url, options = {}) {
  const config = {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  };
  if (config.body && typeof config.body === "object") {
    config.body = JSON.stringify(config.body);
  }
  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(err.detail || `HTTP ${response.status}`);
    }
    if (response.status === 204) return null;
    return await response.json();
  } catch (e) {
    showToast(e.message || t("common.error", currentLang), "error");
    throw e;
  }
}

// ===== Initialize =====
document.addEventListener("DOMContentLoaded", () => {
  const sse = connectSSE();
  window.__sse = sse;
});
