(() => {
  "use strict";

  const categoryLabels = {
    "early-warning": "Early Warning",
    morning: "Morning",
    weekly: "Weekly",
  };

  async function loadReports() {
    const response = await fetch("data/reports.json", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`索引讀取失敗（HTTP ${response.status}）`);
    }
    const data = await response.json();
    if (data.schema_version !== 1 || !Array.isArray(data.reports) || !data.latest) {
      throw new Error("reports.json 格式不相容");
    }
    return data;
  }

  function formatDate(value) {
    if (!value) return "日期未標示";
    const [year, month, day] = value.split("-").map(Number);
    if (!year || !month || !day) return value;
    return new Intl.DateTimeFormat("zh-TW", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).format(new Date(Date.UTC(year, month - 1, day)));
  }

  function reportUrl(report) {
    return `report.html?file=${encodeURIComponent(report.file)}`;
  }

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function reportCard(category, report) {
    const article = element("article", `report-card category-${category}`);
    const badge = element("p", "report-badge", categoryLabels[category]);
    article.append(badge);
    if (!report) {
      article.append(
        element("h3", "report-card-title", "尚無報告"),
        element("p", "report-card-copy", "此分類尚未同步任何 HTML。")
      );
      return article;
    }
    const title = element("h3", "report-card-title", report.title);
    const date = element("p", "report-date", formatDate(report.date));
    const link = element("a", "text-link", "閱讀報告 →");
    link.href = reportUrl(report);
    article.append(title, date, link);
    return article;
  }

  async function renderHome() {
    const grid = document.getElementById("latest-grid");
    const status = document.getElementById("latest-status");
    const heroBtn = document.getElementById("hero-latest-btn");
    if (!grid || !status) return;
    try {
      const data = await loadReports();
      if (heroBtn && Array.isArray(data.reports) && data.reports.length > 0) {
        heroBtn.href = reportUrl(data.reports[0]);
      }
      grid.replaceChildren(
        ...Object.keys(categoryLabels).map((category) =>
          reportCard(category, data.latest[category] || null)
        )
      );
      status.textContent = `索引共 ${data.reports.length} 份報告`;
    } catch (error) {
      status.textContent = error.message;
      status.classList.add("status-error");
    }
  }

  window.MacroReports = {
    categoryLabels,
    element,
    formatDate,
    loadReports,
    reportUrl,
  };

  document.addEventListener("DOMContentLoaded", renderHome);
})();
