let configCache = {};

function switchTab(tab) {
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
  document.querySelector(`.tab[data-tab="${tab}"]`).classList.add("active");
  document.getElementById(`tab-${tab}`).classList.add("active");
}

function togglePassword(btn) {
  const input = btn.parentElement.querySelector(".form-input");
  if (input.type === "password") {
    input.type = "text";
    btn.textContent = "🙈";
  } else {
    input.type = "password";
    btn.textContent = "👁️";
  }
}

async function loadConfig(platform) {
  try {
    const data = await apiFetch(`/api/v1/configs/${platform}`);
    configCache[platform] = data;
    const prefix = platform === "instagram" ? "ig" : "fb";
    document.getElementById(`${prefix}-app-id`).value = data.app_id || "";
    document.getElementById(`${prefix}-app-secret`).value = data.app_secret || "";
    document.getElementById(`${prefix}-access-token`).value = data.access_token || "";
    if (platform === "instagram") {
      document.getElementById("ig-user-id").value = data.ig_user_id || "";
    } else {
      document.getElementById("fb-page-id").value = data.page_id || "";
    }
    document.getElementById(`${prefix}-webhook-token`).value = data.webhook_verify_token || "";
  } catch (e) {
    // Config not found, leave fields empty
  }
}

async function saveConfig(event, platform) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);
  const data = {
    platform: platform,
    app_id: formData.get("app_id"),
    app_secret: formData.get("app_secret"),
    access_token: formData.get("access_token"),
    webhook_verify_token: formData.get("webhook_verify_token"),
  };
  if (platform === "instagram") {
    data.ig_user_id = formData.querySelector("[name='ig_user_id']").value;
  } else {
    data.page_id = formData.querySelector("[name='page_id']").value;
  }

  try {
    await apiFetch(`/api/v1/configs`, { method: "POST", body: data });
    showToast("Settings saved!", "success");
    // Update platform status indicator
    const statusEl = document.getElementById(platform === "instagram" ? "ig-status" : "fb-status");
    if (statusEl) {
      const dot = statusEl.querySelector(".status-dot");
      dot.className = "status-dot connected";
    }
  } catch (e) {}
}

async function testConnection(platform) {
  const resultDiv = document.getElementById(`${platform === "instagram" ? "ig" : "fb"}-test-result`);
  resultDiv.innerHTML = `<span style="color:var(--text-muted)">Testing...</span>`;

  try {
    const result = await apiFetch(`/api/v1/configs/${platform}/test`, { method: "POST" });
    if (result.success) {
      resultDiv.innerHTML = `<span style="color:var(--accent-green)">✅ ${result.message}</span>`;
    } else {
      resultDiv.innerHTML = `<span style="color:var(--accent-red)">❌ ${result.message}</span>`;
    }
  } catch (e) {
    resultDiv.innerHTML = `<span style="color:var(--accent-red)">❌ Connection failed: ${e.message}</span>`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadConfig("instagram");
  loadConfig("facebook");
});
