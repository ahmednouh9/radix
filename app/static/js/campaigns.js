let deleteTargetId = null;

async function loadCampaigns() {
  const tbody = document.getElementById("campaigns-tbody");
  const empty = document.getElementById("campaigns-empty");
  try {
    const data = await apiFetch("/api/v1/campaigns");
    tbody.innerHTML = "";
    if (data.length === 0) {
      empty.style.display = "block";
      return;
    }
    empty.style.display = "none";
    data.forEach(c => {
      const tr = document.createElement("tr");
      tr.dataset.id = c.id;
      const keywords = c.keywords.split(",").map(k => `<span class="keyword-chip">${k.trim()}</span>`).join(" ");
      const platformBadge = c.platform === "instagram"
        ? '<span class="badge badge-instagram">📱 Instagram</span>'
        : '<span class="badge badge-facebook">📘 Facebook</span>';
      tr.innerHTML = `
        <td><strong>${c.name}</strong></td>
        <td>${platformBadge}</td>
        <td><div class="keyword-chips">${keywords}</div></td>
        <td><span class="badge badge-amber">${c.match_type}</span></td>
        <td>${c.reply_text ? (c.reply_text.length > 50 ? c.reply_text.slice(0, 50) + '...' : c.reply_text) : '—'}</td>
        <td>
          <label class="toggle">
            <input type="checkbox" ${c.is_active ? 'checked' : ''} onchange="toggleCampaign(${c.id})">
            <span class="toggle-slider"></span>
          </label>
        </td>
        <td>${c.stats_total_matched}</td>
        <td>
          <div class="action-group">
            <button class="btn btn-ghost btn-sm" onclick="editCampaign(${c.id})">✏️</button>
            <button class="btn btn-ghost btn-sm btn-danger" onclick="confirmDelete(${c.id})">🗑️</button>
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error("Failed to load campaigns:", e);
  }
}

function openAddModal() {
  document.getElementById("modal-title").textContent = t("campaign.add", currentLang);
  document.getElementById("campaign-id").value = "";
  document.getElementById("campaign-form").reset();
  document.getElementById("campaign-modal").classList.add("open");
}

function closeModal() {
  document.getElementById("campaign-modal").classList.remove("open");
  document.getElementById("delete-modal").classList.remove("open");
}

async function editCampaign(id) {
  try {
    const c = await apiFetch(`/api/v1/campaigns/${id}`);
    document.getElementById("modal-title").textContent = t("campaign.edit", currentLang);
    document.getElementById("campaign-id").value = c.id;
    document.getElementById("campaign-name").value = c.name;
    document.getElementById("campaign-platform").value = c.platform;
    document.getElementById("campaign-keywords").value = c.keywords;
    document.getElementById("campaign-match-type").value = c.match_type;
    document.getElementById("campaign-reply-text").value = c.reply_text || "";
    document.getElementById("campaign-dm-text").value = c.dm_text || "";
    document.getElementById("campaign-modal").classList.add("open");
  } catch (e) {}
}

async function saveCampaign(event) {
  event.preventDefault();
  const id = document.getElementById("campaign-id").value;
  const data = {
    name: document.getElementById("campaign-name").value,
    platform: document.getElementById("campaign-platform").value,
    keywords: document.getElementById("campaign-keywords").value,
    match_type: document.getElementById("campaign-match-type").value,
    reply_text: document.getElementById("campaign-reply-text").value || null,
    dm_text: document.getElementById("campaign-dm-text").value || null,
  };
  try {
    if (id) {
      await apiFetch(`/api/v1/campaigns/${id}`, { method: "PUT", body: data });
    } else {
      await apiFetch("/api/v1/campaigns", { method: "POST", body: data });
    }
    closeModal();
    loadCampaigns();
    showToast("Campaign saved!", "success");
  } catch (e) {}
}

function confirmDelete(id) {
  deleteTargetId = id;
  document.getElementById("confirm-delete-btn").onclick = async () => {
    try {
      await apiFetch(`/api/v1/campaigns/${deleteTargetId}`, { method: "DELETE" });
      document.getElementById("delete-modal").classList.remove("open");
      loadCampaigns();
      showToast("Campaign deleted", "success");
    } catch (e) {}
  };
  document.getElementById("delete-modal").classList.add("open");
}

async function deleteCampaign(id) {
  confirmDelete(id);
}

async function toggleCampaign(id) {
  try {
    const result = await apiFetch(`/api/v1/campaigns/${id}/toggle`, { method: "PATCH" });
    loadCampaigns();
  } catch (e) {}
}

document.addEventListener("DOMContentLoaded", loadCampaigns);

document.addEventListener("click", (e) => {
  if (e.target.classList.contains("modal-overlay")) {
    e.target.classList.remove("open");
  }
});
