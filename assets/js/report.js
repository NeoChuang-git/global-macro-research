(() => {
  "use strict";

  function safeReportPath(value) {
    if (!value || value.includes("\\")) return null;
    const parts = value.split("/");
    if (
      parts.length < 3 ||
      parts[0] !== "reports" ||
      !["early-warning", "morning", "weekly"].includes(parts[1]) ||
      parts.some((part) => !part || part === "." || part === "..") ||
      !parts[parts.length - 1].toLowerCase().endsWith(".html")
    ) {
      return null;
    }
    return parts.map(encodeURIComponent).join("/");
  }

  document.addEventListener("DOMContentLoaded", async () => {
    const title = document.getElementById("report-title");
    const category = document.getElementById("report-category");
    const date = document.getElementById("report-date");
    const status = document.getElementById("report-status");
    const frame = document.getElementById("report-frame");
    const requested = new URLSearchParams(location.search).get("file");
    const safePath = safeReportPath(requested);

    function fail(message) {
      title.textContent = "無法開啟報告";
      status.textContent = message;
      status.classList.add("status-error");
    }

    if (!safePath) {
      fail("報告路徑無效。請從首頁或歸檔重新選擇報告。");
      return;
    }

    try {
      const data = await MacroReports.loadReports();
      const report = data.reports.find((item) => item.file === requested);
      if (!report) {
        fail("此報告不在目前的 reports.json 索引中。");
        return;
      }
      const localUrl = safePath;
      const catLabel = MacroReports.categoryLabels[report.category] || report.category;
      const dateFormatted = MacroReports.formatDate(report.date);

      title.textContent = report.title;
      category.textContent = catLabel;
      category.className = `category-pill category-${report.category}`;
      date.textContent = dateFormatted;

      const mobileCategory = document.getElementById("mobile-report-category");
      const mobileDate = document.getElementById("mobile-report-date");
      if (mobileCategory) {
        mobileCategory.textContent = catLabel;
        mobileCategory.className = `category-pill category-${report.category}`;
      }
      if (mobileDate) {
        mobileDate.textContent = dateFormatted;
      }

      document.title = `${report.title} · Global Macro Signal Report`;
      const cacheBust = report.sha256 ? `?v=${encodeURIComponent(report.sha256.slice(0, 16))}` : "";
      frame.src = `${localUrl}${cacheBust}`;
      frame.title = report.title;
      frame.hidden = false;
      status.textContent = "報告已載入。";
      frame.addEventListener("load", () => {
        status.textContent = "";
      });
    } catch (error) {
      fail(error.message);
    }
  });
})();
