(() => {
  "use strict";

  document.addEventListener("DOMContentLoaded", async () => {
    const form = document.getElementById("archive-filters");
    const categoryInput = document.getElementById("category-filter");
    const dateInput = document.getElementById("date-filter");
    const status = document.getElementById("archive-status");
    const list = document.getElementById("archive-list");
    if (!form || !categoryInput || !dateInput || !status || !list) return;

    let reports = [];

    function updateUrl() {
      const params = new URLSearchParams();
      if (categoryInput.value !== "all") params.set("category", categoryInput.value);
      if (dateInput.value) params.set("date", dateInput.value);
      const query = params.toString();
      history.replaceState(null, "", query ? `?${query}` : "archive.html");
    }

    function render() {
      const category = categoryInput.value;
      const selectedDate = dateInput.value;
      const filtered = reports.filter(
        (report) =>
          (category === "all" || report.category === category) &&
          (!selectedDate || report.date === selectedDate)
      );
      list.replaceChildren();
      for (const report of filtered) {
        const row = MacroReports.element("article", "archive-item");
        const meta = MacroReports.element("div", "archive-meta");
        meta.append(
          MacroReports.element(
            "span",
            `category-pill category-${report.category}`,
            MacroReports.categoryLabels[report.category] || report.category
          ),
          MacroReports.element("time", "report-date", MacroReports.formatDate(report.date))
        );
        const title = MacroReports.element("h2", "archive-title", report.title);
        const link = MacroReports.element("a", "text-link", "閱讀報告 →");
        link.href = MacroReports.reportUrl(report);
        row.append(meta, title, link);
        list.append(row);
      }
      if (!filtered.length) {
        list.append(
          MacroReports.element("p", "empty-state", "目前沒有符合條件的報告。")
        );
      }
      status.textContent = `顯示 ${filtered.length} / ${reports.length} 份報告`;
      updateUrl();
    }

    const initial = new URLSearchParams(location.search);
    let initialCategory = initial.get("category");
    if (initialCategory === "morning") initialCategory = "daily";
    if (["early-warning", "daily", "weekly"].includes(initialCategory)) {
      categoryInput.value = initialCategory;
    }
    dateInput.value = initial.get("date") || "";

    form.addEventListener("change", render);
    form.addEventListener("reset", () => setTimeout(render, 0));

    try {
      const data = await MacroReports.loadReports();
      reports = data.reports;
      render();
    } catch (error) {
      status.textContent = error.message;
      status.classList.add("status-error");
    }
  });
})();
