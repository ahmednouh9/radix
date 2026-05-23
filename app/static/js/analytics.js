let chart = null;

async function loadAnalytics() {
  try {
    const overview = await apiFetch("/api/v1/analytics/overview");
    document.getElementById("ana-replies").textContent = overview.total_replies;
    document.getElementById("ana-dms").textContent = overview.total_dms;
    document.getElementById("ana-success").textContent = overview.success_rate + "%";
    document.getElementById("ana-matched").textContent = overview.total_replies + overview.total_dms;
  } catch (e) {}

  try {
    const timeline = await apiFetch("/api/v1/analytics/timeline?days=7");
    const labels = timeline.map(d => {
      const parts = d.date.split("-");
      return parts[2] + "/" + parts[1];
    });
    const replies = timeline.map(d => d.replies);
    const dms = timeline.map(d => d.dms);

    if (chart) chart.destroy();

    const ctx = document.getElementById("analytics-chart").getContext("2d");
    chart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Replies",
            data: replies,
            backgroundColor: "rgba(124, 93, 249, 0.6)",
            borderColor: "#7c5df9",
            borderWidth: 1,
            borderRadius: 4,
          },
          {
            label: "DMs",
            data: dms,
            backgroundColor: "rgba(34, 211, 165, 0.6)",
            borderColor: "#22d3a5",
            borderWidth: 1,
            borderRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: "#8892a4",
              font: { size: 12 },
            },
          },
        },
        scales: {
          x: {
            ticks: { color: "#8892a4", font: { size: 11 } },
            grid: { color: "rgba(255,255,255,0.04)" },
          },
          y: {
            beginAtZero: true,
            ticks: { color: "#8892a4", font: { size: 11 } },
            grid: { color: "rgba(255,255,255,0.04)" },
          },
        },
      },
    });
  } catch (e) {}
}

document.addEventListener("DOMContentLoaded", loadAnalytics);
