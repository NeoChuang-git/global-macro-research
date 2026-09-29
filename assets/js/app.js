(() => {
  "use strict";

  const categoryLabels = {
    "early-warning": "Early Warning",
    daily: "Daily Brief",
    weekly: "Weekly",
  };

  const categoryMeta = {
    "early-warning": {
      label: "Early Warning",
      shortLabel: "突發預警",
      icon: "⚡",
    },
    daily: {
      label: "Daily Brief",
      shortLabel: "每日全景",
      icon: "☀️",
    },
    weekly: {
      label: "Weekly",
      shortLabel: "中期趨勢",
      icon: "📅",
    },
  };

  const riskLevels = {
    GREEN: {
      key: "GREEN",
      label: "LOW RISK",
      zh: "正常",
      pillClass: "risk-green",
      score: 1,
    },
    YELLOW: {
      key: "YELLOW",
      label: "MODERATE",
      zh: "關注",
      pillClass: "risk-yellow",
      score: 2,
    },
    ORANGE: {
      key: "ORANGE",
      label: "ELEVATED",
      zh: "警戒",
      pillClass: "risk-orange",
      score: 3,
    },
    RED: {
      key: "RED",
      label: "HIGH RISK",
      zh: "高危",
      pillClass: "risk-red",
      score: 4,
    },
  };

  function normalizeRisk(report) {
    if (report && report.risk_light) {
      const raw = String(report.risk_light).toUpperCase();
      for (const key of Object.keys(riskLevels)) {
        if (raw.includes(key)) return riskLevels[key];
      }
    }
    // Fallback for weekly or legacy reports if not explicitly in catalog
    if (report && report.category === "weekly") {
      return riskLevels.ORANGE;
    }
    return riskLevels.YELLOW;
  }

  function cleanHeadline(title) {
    if (!title) return "尚無最新報告";
    const parts = title.split(/[｜|]/);
    if (parts.length > 1) {
      return parts.slice(1).join("｜").trim();
    }
    return title;
  }

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
    const header = element("div", "report-card-header");
    const badge = element("p", "report-badge", categoryLabels[category]);
    header.append(badge);

    if (report) {
      const risk = normalizeRisk(report);
      const riskPill = element("span", `risk-pill ${risk.pillClass}`);
      const dot = element("span", "risk-dot");
      riskPill.append(dot, document.createTextNode(`${risk.key} RISK`));
      header.append(riskPill);
    }
    article.append(header);

    if (!report) {
      const body = element("div", "report-card-body");
      body.append(
        element("h3", "report-card-title", "尚無報告"),
        element("p", "report-card-copy", "此分類尚未同步任何 HTML。")
      );
      article.append(body);
      return article;
    }

    const body = element("div", "report-card-body");
    const title = element("h3", "report-card-title", report.title);
    body.append(title);

    const footer = element("div", "report-card-footer");
    const date = element("p", "report-date", formatDate(report.date));
    const link = element("a", "text-link", "閱讀報告 →");
    link.href = reportUrl(report);
    footer.append(date, link);

    article.append(body, footer);
    return article;
  }

  function renderOverallRisk(data) {
    const pill = document.getElementById("hero-risk-pill");
    const text = document.getElementById("hero-risk-text");
    if (!pill || !text || !data || !data.latest) return;

    const categories = ["early-warning", "daily", "weekly"];
    let highestRisk = riskLevels.GREEN;

    categories.forEach((cat) => {
      const report = data.latest[cat];
      if (report) {
        const risk = normalizeRisk(report);
        if (risk.score > highestRisk.score) {
          highestRisk = risk;
        }
      }
    });

    pill.className = `hero-risk-pill ${highestRisk.pillClass}`;
    text.textContent = `${highestRisk.zh} (${highestRisk.label})`;
  }

  function formatSyncTime(raw) {
    if (!raw) return "";
    const clean = String(raw).replace("T", " ");
    const match = clean.match(/^(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{2}):(\d{2}))?/);
    if (match) {
      const [, y, m, d, hh, mm] = match;
      if (hh !== undefined && mm !== undefined) {
        return `${y}/${m}/${d} ${hh}:${mm}`;
      }
      return `${y}/${m}/${d}`;
    }
    return raw;
  }

  function getLatestSyncTime(data) {
    let latest = "";
    if (data && data.latest) {
      for (const cat of Object.keys(data.latest)) {
        const rep = data.latest[cat];
        if (!rep) continue;
        const t = rep.generated_at_taipei || rep.modified_time || rep.date || "";
        if (t > latest) latest = t;
      }
    }
    if (!latest && data && Array.isArray(data.reports) && data.reports.length > 0) {
      for (let i = 0; i < Math.min(5, data.reports.length); i++) {
        const r = data.reports[i];
        const t = r.generated_at_taipei || r.modified_time || r.date || "";
        if (t > latest) latest = t;
      }
    }
    return formatSyncTime(latest);
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
      renderOverallRisk(data);
      grid.replaceChildren(
        ...Object.keys(categoryLabels).map((category) =>
          reportCard(category, data.latest[category] || null)
        )
      );
      const syncTime = getLatestSyncTime(data);
      const syncText = syncTime ? `最新同步基準：${syncTime}` : "";
      const countText = `索引共 ${data.reports.length} 份報告`;
      status.textContent = syncText ? `${syncText} · ${countText}` : countText;
    } catch (error) {
      status.textContent = error.message;
      status.classList.add("status-error");
    }
  }

  window.MacroReports = {
    categoryLabels,
    categoryMeta,
    element,
    formatDate,
    loadReports,
    normalizeRisk,
    reportUrl,
    riskLevels,
  };

  document.addEventListener("DOMContentLoaded", renderHome);
})();
