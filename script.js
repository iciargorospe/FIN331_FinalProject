const DATA_URL = "outputs/website_data.json";
const PERIOD_ORDER = ["original_sample", "gap", "post_publication"];
const PERIOD_COLORS = {
  original_sample: "#167c79",
  gap: "#c9824c",
  post_publication: "#172f43",
};

const select = document.querySelector("#anomaly-select");
const status = document.querySelector("#data-status");
const content = document.querySelector("#explorer-content");

fetch(DATA_URL)
  .then((response) => {
    if (!response.ok) throw new Error("Could not load the saved website data.");
    return response.json();
  })
  .then((data) => {
    window.explorerData = data;
    document.querySelector("#data-release").textContent = data.data_release;
    document.querySelector("#data-release-footer").textContent = data.data_release;
    document.querySelectorAll(".dynamic-count").forEach((node) => {
      node.textContent = data.eligible_anomalies.toLocaleString();
    });
    document.querySelectorAll("#eligible-count, #eligible-count-copy").forEach((node) => {
      node.textContent = data.eligible_anomalies.toLocaleString();
    });

    data.anomalies.forEach((anomaly) => {
      const option = document.createElement("option");
      option.value = anomaly.signal;
      option.textContent = anomaly.label;
      select.append(option);
    });
    select.value = data.anomalies[0].signal;

    renderOverview(data);
    renderTests(data);
    renderRegressions(data);
    renderCategories(data);
    renderRobustness(data);
    status.textContent = "";
    content.hidden = false;
    renderSelected();
  })
  .catch((error) => {
    status.textContent = `${error.message} Run python3 prepare_data.py, then preview with a local web server.`;
  });

select.addEventListener("change", renderSelected);
document.querySelector("#test-filter").addEventListener("change", () => renderTests(window.explorerData));
document.querySelector("#category-filter").addEventListener("change", () => renderCategories(window.explorerData));
window.addEventListener("resize", () => {
  if (window.explorerData) renderChart(findSelected());
});

function findSelected() {
  return window.explorerData.anomalies.find((item) => item.signal === select.value);
}

function renderSelected() {
  if (!window.explorerData) return;
  const anomaly = findSelected();
  document.querySelector("#anomaly-title").textContent = anomaly.label;
  document.querySelector("#anomaly-description").textContent =
    `${anomaly.economic_category} · ${anomaly.data_category} · published ${anomaly.publication_year}`;
  renderChart(anomaly);
  renderSummary(anomaly);
}

function formatPct(value) {
  return value == null ? "—" : `${value.toFixed(2)}%`;
}

function formatP(value) {
  if (value == null) return "—";
  if (value < 0.0001) return "<0.0001";
  return value.toFixed(4);
}

function formatPP(value) {
  if (value == null) return "—";
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)} pp`;
}

function appendRows(tableId, rows) {
  const table = document.querySelector(tableId);
  table.replaceChildren();
  rows.forEach((values) => {
    const row = document.createElement("tr");
    values.forEach((value) => {
      const cell = document.createElement("td");
      if (value instanceof Node) cell.append(value);
      else cell.textContent = value;
      row.append(cell);
    });
    table.append(row);
  });
}

function renderOverview(data) {
  const desc = data.descriptive;
  document.querySelector("#original-average").textContent = formatPct(desc.original_average_pct);
  document.querySelector("#post-average").textContent = formatPct(desc.post_average_pct);
  document.querySelector("#declined-count").textContent =
    `${desc.declined_count.toLocaleString()} / ${data.eligible_anomalies.toLocaleString()}`;

  appendRows("#period-results-table", [
    ["Original research sample", formatPct(desc.original_average_pct), data.period_counts.original_sample.toLocaleString()],
    ["Pre-publication gap", formatPct(desc.gap_average_pct), data.period_counts.gap.toLocaleString()],
    ["Post-publication", formatPct(desc.post_average_pct), data.period_counts.post_publication.toLocaleString()],
  ]);

  document.querySelector("#raw-significant").textContent = data.individual_tests.raw_significant.toLocaleString();
  document.querySelector("#bh-significant").textContent = data.individual_tests.bh_significant.toLocaleString();
  document.querySelector("#bh-declines").textContent = data.individual_tests.bh_declines.toLocaleString();
}

function renderTests(data) {
  const filter = document.querySelector("#test-filter").value;
  const filtered = data.anomalies.filter((anomaly) => {
    const test = anomaly.test;
    if (filter === "bh_decline") return test.significant_decline;
    if (filter === "bh_increase") return test.significant_increase;
    if (filter === "unsignificant") return !test.significant_after_BH;
    return true;
  });
  appendRows("#tests-table", filtered.map((anomaly) => {
    const test = anomaly.test;
    const result = test.significant_decline
      ? "BH-significant decline"
      : test.significant_increase
        ? "BH-significant increase"
        : "Not BH-significant";
    const link = document.createElement("button");
    link.type = "button";
    link.className = "table-link";
    link.textContent = anomaly.label;
    link.addEventListener("click", () => {
      select.value = anomaly.signal;
      renderSelected();
      document.querySelector("#explorer").scrollIntoView({ behavior: "smooth" });
    });
    return [
      link,
      formatPct(test.original_mean),
      formatPct(test.post_mean),
      formatPP(test.difference_pp),
      formatP(test.p_value),
      formatP(test.adjusted_p_value),
      result,
    ];
  }));
}

function renderRegressions(data) {
  const rows = data.regressions.map((item) => [
    item.model,
    `${formatPP(item.post_sample.coefficient)}\np = ${formatP(item.post_sample.p_value)}`,
    `${formatPP(item.post_publication.coefficient)}\np = ${formatP(item.post_publication.p_value)}`,
    `${formatPP(item.total.coefficient)}\np = ${formatP(item.total.p_value)}`,
  ]);
  appendRows("#regression-table", rows);
}

function renderCategories(data) {
  const showAll = document.querySelector("#category-filter").value === "all";
  document.querySelector("#category-count").textContent = data.categories.length.toLocaleString();
  const rows = data.categories
    .filter((category) => showAll || category.at_least_5_anomalies)
    .map((category) => [
      category.economic_category,
      category.n_anomalies.toLocaleString(),
      formatPct(category.original_mean_pct),
      formatPct(category.post_mean_pct),
      formatPP(category.mean_change_pp),
      `${category.n_declined.toLocaleString()} (${category.pct_declined.toFixed(1)}%)`,
      category.n_significant_declines.toLocaleString(),
    ]);
  appendRows("#categories-table", rows);
}

function renderRobustness(data) {
  document.querySelector("#equal-declined").textContent = data.equal_length.declined_count.toLocaleString();
  document.querySelector("#equal-bh").textContent = data.equal_length.bh_significant_declines.toLocaleString();
  document.querySelector("#equal-average-change").textContent = formatPP(data.equal_length.average_change_pp);

  appendRows("#costs-table", data.hypothetical_costs.map((cost) => [
    `${cost.bps} bps / month`,
    formatPct(cost.average_net_pct),
    `${cost.positive_count.toLocaleString()} / ${data.eligible_anomalies.toLocaleString()}`,
  ]));

  appendRows("#wins-table", data.winsorized.map((row) => [
    row.variable,
    formatPP(row.coefficient_original),
    formatPP(row.coefficient_winsorized),
    formatP(row.p_value_winsorized),
  ]));

  appendRows("#cluster-table", data.two_way_clustering.map((row) => [
    row.variable,
    formatP(row.p_month_only),
    formatP(row.p_two_way),
  ]));
}

function renderSummary(anomaly) {
  const table = document.querySelector("#summary-table");
  table.replaceChildren();
  PERIOD_ORDER.forEach((period) => {
    const result = anomaly.summary[period];
    const row = document.createElement("tr");
    const label = document.createElement("td");
    const periodCell = document.createElement("span");
    periodCell.className = "period-cell";
    const dot = document.createElement("i");
    dot.className = `period-dot ${period === "gap" ? "gap-dot" : period === "post_publication" ? "post-dot" : ""}`;
    const labels = {
      original_sample: "Original research sample",
      gap: "Pre-publication gap",
      post_publication: "Post-publication",
    };
    periodCell.append(dot, document.createTextNode(labels[period]));
    label.append(periodCell);
    row.append(label);
    [
      formatPct(result.mean_monthly_pct),
      result.observations.toLocaleString(),
    ].forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    table.append(row);
  });
  document.querySelector("#range-note").textContent = `Published ${anomaly.publication_year}`;
}

function svgElement(tag, attributes = {}, text = "") {
  const element = document.createElementNS("http://www.w3.org/2000/svg", tag);
  Object.entries(attributes).forEach(([name, value]) => element.setAttribute(name, value));
  if (text) element.textContent = text;
  return element;
}

function renderChart(anomaly) {
  const svg = document.querySelector("#return-chart");
  const width = Math.max(320, Math.round(svg.parentElement.clientWidth));
  const height = width < 520 ? 300 : 390;
  const margin = { top: 24, right: 20, bottom: 45, left: 67 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const points = anomaly.annual_means;
  svg.replaceChildren();
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.setAttribute("aria-label", `Annual average monthly long-short return for ${anomaly.label}`);

  if (!points.length) {
    svg.append(svgElement("text", { x: width / 2, y: height / 2, "text-anchor": "middle" }, "No observations in the comparison periods."));
    return;
  }

  const firstYear = Math.min(...points.map((point) => point.year));
  const lastYear = Math.max(...points.map((point) => point.year));
  let low = Math.min(0, ...points.map((point) => point.mean_monthly_pct));
  let high = Math.max(0, ...points.map((point) => point.mean_monthly_pct));
  const padding = Math.max((high - low) * 0.12, 0.25);
  low -= padding;
  high += padding;
  const x = (year) => margin.left + ((year - firstYear) / Math.max(1, lastYear - firstYear)) * plotWidth;
  const y = (value) => margin.top + ((high - value) / (high - low)) * plotHeight;

  for (let tick = 0; tick <= 4; tick += 1) {
    const value = low + ((high - low) * tick) / 4;
    const yPosition = y(value);
    svg.append(svgElement("line", { x1: margin.left, x2: width - margin.right, y1: yPosition, y2: yPosition, class: "grid-line" }));
    svg.append(svgElement("text", { x: margin.left - 10, y: yPosition + 4, "text-anchor": "end" }, `${value.toFixed(1)}%`));
  }

  svg.append(svgElement("line", { x1: margin.left, x2: margin.left, y1: margin.top, y2: height - margin.bottom, class: "axis-line" }));
  svg.append(svgElement("line", { x1: margin.left, x2: width - margin.right, y1: height - margin.bottom, y2: height - margin.bottom, class: "axis-line" }));

  if (anomaly.publication_year >= firstYear && anomaly.publication_year <= lastYear) {
    const publicationX = x(anomaly.publication_year);
    svg.append(svgElement("line", {
      x1: publicationX, x2: publicationX, y1: margin.top, y2: height - margin.bottom,
      class: "publication-line",
    }));
    svg.append(svgElement("text", {
      x: publicationX + (publicationX > width - 150 ? -7 : 7),
      y: margin.top + 13,
      "text-anchor": publicationX > width - 150 ? "end" : "start",
      class: "publication-label",
    }, `Published ${anomaly.publication_year}`));
  }

  const tickCount = Math.min(6, Math.max(2, Math.floor(plotWidth / 115)));
  for (let tick = 0; tick <= tickCount; tick += 1) {
    const year = Math.round(firstYear + ((lastYear - firstYear) * tick) / tickCount);
    svg.append(svgElement("text", { x: x(year), y: height - 15, "text-anchor": "middle" }, String(year)));
  }

  PERIOD_ORDER.forEach((period) => {
    const series = points.filter((point) => point.period === period);
    if (!series.length) return;
    const path = series.map((point, index) => `${index ? "L" : "M"}${x(point.year)},${y(point.mean_monthly_pct)}`).join(" ");
    svg.append(svgElement("path", { d: path, class: "data-line", stroke: PERIOD_COLORS[period] }));
    series.forEach((point) => {
      const marker = svgElement("circle", {
        cx: x(point.year), cy: y(point.mean_monthly_pct), r: 3.4,
        fill: PERIOD_COLORS[period], class: "data-point",
      });
      marker.append(svgElement("title", {}, `${point.year}: ${point.mean_monthly_pct.toFixed(2)}% mean monthly return (${point.observations} months)`));
      svg.append(marker);
    });
  });
}
