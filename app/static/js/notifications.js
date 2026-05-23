let notificationsPage = 1;
let loading = false;
let hasMore = true;

async function loadNotifications(reset = true) {
  if (loading) return;
  if (reset) {
    notificationsPage = 1;
    hasMore = true;
    document.getElementById("notifications-feed").innerHTML = "";
  }
  if (!hasMore) return;

  loading = true;
  document.getElementById("notif-loading").style.display = "block";

  const platform = document.getElementById("filter-platform").value;
  const type = document.getElementById("filter-type").value;
  const readFilter = document.getElementById("filter-read").value;

  let url = `/api/v1/notifications?page=${notificationsPage}&page_size=20`;
  if (platform) url += `&platform=${platform}`;
  if (type) url += `&type=${type}`;
  if (readFilter === "unread") url += `&is_read=false`;

  try {
    const data = await apiFetch(url);
    const feed = document.getElementById("notifications-feed");
    const empty = document.getElementById("notif-empty");

    if (data.items.length === 0 && reset) {
      feed.innerHTML = "";
      const emptyClone = empty.cloneNode(true);
      emptyClone.style.display = "block";
      feed.appendChild(emptyClone);
      hasMore = false;
      loading = false;
      document.getElementById("notif-loading").style.display = "none";
      return;
    }

    if (empty) empty.style.display = "none";

    data.items.forEach(n => {
      const card = document.createElement("div");
      card.className = "notif-card" + (n.is_read ? "" : " unread");
      card.dataset.id = n.id;
      card.onclick = () => markNotifRead(n.id);
      const icon = n.type === "reply_sent" ? "💬" : n.type === "dm_sent" ? "✉️" : n.type === "error" ? "⚠️" : "💭";
      card.innerHTML = `
        <div class="notif-icon">${icon}</div>
        <div class="notif-body">
          <div class="notif-title">${n.title}</div>
          <div class="notif-message">${n.message}</div>
        </div>
        <div class="notif-time">${formatDate(n.created_at)}</div>
      `;
      feed.appendChild(card);
    });

    hasMore = data.items.length === 20;
    notificationsPage++;
  } catch (e) {}

  loading = false;
  document.getElementById("notif-loading").style.display = hasMore ? "block" : "none";
}

async function markNotifRead(id) {
  try {
    await apiFetch(`/api/v1/notifications/${id}/read`, { method: "PATCH" });
    const card = document.querySelector(`.notif-card[data-id="${id}"]`);
    if (card) {
      card.classList.remove("unread");
    }
  } catch (e) {}
}

async function markAllRead() {
  try {
    await apiFetch("/api/v1/notifications/read-all", { method: "POST" });
    document.querySelectorAll(".notif-card.unread").forEach(c => c.classList.remove("unread"));
    showToast("All marked as read", "success");
  } catch (e) {}
}

window.addEventListener("sse-notification", (e) => {
  const data = e.detail;
  const feed = document.getElementById("notifications-feed");
  const empty = document.querySelector("#notif-empty");
  if (empty) empty.style.display = "none";
  const card = document.createElement("div");
  card.className = "notif-card unread";
  card.dataset.id = data.id;
  card.onclick = () => markNotifRead(data.id);
  const icon = data.type === "reply_sent" ? "💬" : data.type === "dm_sent" ? "✉️" : data.type === "error" ? "⚠️" : "💭";
  card.innerHTML = `
    <div class="notif-icon">${icon}</div>
    <div class="notif-body">
      <div class="notif-title">${data.title}</div>
      <div class="notif-message">${data.message}</div>
    </div>
    <div class="notif-time">${formatDate(data.created_at)}</div>
  `;
  feed.insertBefore(card, feed.firstChild);

  const badge = document.getElementById("notif-badge");
  if (badge) {
    const count = parseInt(badge.textContent || "0");
    badge.textContent = count + 1;
    badge.style.display = "inline";
  }
});

document.addEventListener("DOMContentLoaded", () => {
  loadNotifications();

  document.getElementById("notifications-feed").addEventListener("scroll", () => {
    const feed = document.getElementById("notifications-feed");
    if (feed.scrollTop + feed.clientHeight >= feed.scrollHeight - 200) {
      loadNotifications(false);
    }
  });
});
