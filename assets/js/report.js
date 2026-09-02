(() => {
  "use strict";

  function safeReportPath(value) {
    if (!value || value.includes("\\")) return null;
    const parts = value.split("/");
    if (
      parts.length < 3 ||
      parts[0] !== "reports" ||
      !["early-warning", "daily", "morning", "weekly"].includes(parts[1]) ||
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

    const newerBtn = document.getElementById("nav-newer-btn");
    const olderBtn = document.getElementById("nav-older-btn");
    const mobileNewerBtn = document.getElementById("mobile-nav-newer-btn");
    const mobileOlderBtn = document.getElementById("mobile-nav-older-btn");

    const mobileCategory = document.getElementById("mobile-report-category");
    const mobileDate = document.getElementById("mobile-report-date");

    let reportsData = null;
    let currentReport = null;
    let newerReport = null;
    let olderReport = null;

    function fail(message) {
      title.textContent = "無法開啟報告";
      status.textContent = message;
      status.classList.add("status-error");
      frame.hidden = true;
    }

    function setNavButtonState(btn, report, directionLabel) {
      if (!btn) return;
      if (report) {
        btn.classList.remove("is-disabled");
        btn.removeAttribute("aria-disabled");
        btn.href = MacroReports.reportUrl(report);
        btn.title = `${directionLabel}：${report.title} (${MacroReports.formatDate(report.date)})`;
      } else {
        btn.classList.add("is-disabled");
        btn.setAttribute("aria-disabled", "true");
        btn.href = "#";
        btn.title = `已是${directionLabel}`;
      }
    }

    function renderReport(targetFile, updateHistory = false) {
      if (!reportsData || !Array.isArray(reportsData.reports)) return;

      const safePath = safeReportPath(targetFile);
      if (!safePath) {
        fail("報告路徑無效。請從首頁或歸檔重新選擇報告。");
        return;
      }

      const reportIndex = reportsData.reports.findIndex((item) => item.file === targetFile);
      if (reportIndex === -1) {
        fail("此報告不在目前的 reports.json 索引中。");
        return;
      }

      currentReport = reportsData.reports[reportIndex];
      // Index 0 is newest, index N is oldest
      newerReport = reportIndex > 0 ? reportsData.reports[reportIndex - 1] : null;
      olderReport = reportIndex < reportsData.reports.length - 1 ? reportsData.reports[reportIndex + 1] : null;

      const localUrl = safePath;
      const catLabel = MacroReports.categoryLabels[currentReport.category] || currentReport.category;
      const dateFormatted = MacroReports.formatDate(currentReport.date);

      title.textContent = currentReport.title;
      category.textContent = catLabel;
      category.className = `category-pill category-${currentReport.category}`;
      date.textContent = dateFormatted;

      if (mobileCategory) {
        mobileCategory.textContent = catLabel;
        mobileCategory.className = `category-pill category-${currentReport.category}`;
      }
      if (mobileDate) {
        mobileDate.textContent = dateFormatted;
      }

      document.title = `${currentReport.title} · Global Macro Signal Report`;

      // Update Navigation Buttons
      setNavButtonState(newerBtn, newerReport, "較新一份");
      setNavButtonState(olderBtn, olderReport, "較舊一份");
      setNavButtonState(mobileNewerBtn, newerReport, "較新一份");
      setNavButtonState(mobileOlderBtn, olderReport, "較舊一份");

      const cacheBust = currentReport.sha256 ? `?v=${encodeURIComponent(currentReport.sha256.slice(0, 16))}` : "";
      frame.src = `${localUrl}${cacheBust}`;
      frame.title = currentReport.title;
      frame.hidden = false;
      status.textContent = "報告已載入。";
      status.classList.remove("status-error");

      frame.addEventListener(
        "load",
        () => {
          status.textContent = "";
        },
        { once: true }
      );

      if (updateHistory) {
        const newUrl = `report.html?file=${encodeURIComponent(currentReport.file)}`;
        history.pushState({ file: currentReport.file }, "", newUrl);
      }
    }

    function setupNavEvents(desktopBtn, mobileBtn, getTarget) {
      const handler = (event) => {
        const target = getTarget();
        if (target) {
          event.preventDefault();
          renderReport(target.file, true);
        }
      };
      if (desktopBtn) desktopBtn.addEventListener("click", handler);
      if (mobileBtn) mobileBtn.addEventListener("click", handler);
    }

    setupNavEvents(newerBtn, mobileNewerBtn, () => newerReport);
    setupNavEvents(olderBtn, mobileOlderBtn, () => olderReport);

    // Keyboard Shortcuts: ArrowLeft (Newer), ArrowRight (Older)
    window.addEventListener("keydown", (event) => {
      if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)) {
        return;
      }
      if (event.key === "ArrowLeft" && newerReport) {
        renderReport(newerReport.file, true);
      } else if (event.key === "ArrowRight" && olderReport) {
        renderReport(olderReport.file, true);
      }
    });

    // Browser Back / Forward buttons
    window.addEventListener("popstate", (event) => {
      const fileFromUrl = new URLSearchParams(location.search).get("file");
      if (fileFromUrl) {
        renderReport(fileFromUrl, false);
      }
    });

    try {
      reportsData = await MacroReports.loadReports();
      const requested = new URLSearchParams(location.search).get("file");
      let targetFile = requested;
      if (!targetFile && Array.isArray(reportsData.reports) && reportsData.reports.length > 0) {
        targetFile = reportsData.reports[0].file;
      }
      renderReport(targetFile, false);
    } catch (error) {
      fail(error.message);
    }
  });
})();
