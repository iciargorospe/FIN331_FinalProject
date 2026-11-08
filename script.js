const DATA_URL = "outputs/explorer_data.json";
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
    if (!response.ok) throw new Error("Could not load the saved explorer data.");
    return response.json();
  })
  .then((data) => {
    window.explorerData = data;
    document.querySelector("#data-release").textContent = data.data_release;
    document.querySelector("#data-release-footer").textContent = data.data_release;
    data.anomalies.forEach((anomaly, index) => {
      const option = document.createElement("option");
      option.value = anomaly.signal;
      option.textContent = anomaly.label;
      select.append(option);
      if (index === 0) select.value = anomaly.signal;
    });
    status.textContent = "";
    content.hidden = false;
    renderSelected();
  })
  .catch((error) => {
    status.textContent = `${error.message} Run python3 prepare_data.py, then preview with a local web server.`;
  });

select.addEventListener("change", renderSelected);
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
  document.querySelector("#anomaly-description").textContent = anomaly.description;
  renderChart(anomaly);
  renderSummary(anomaly);
}

function formatNumber(value) {
  return value == null ? "—" : `${value.toFixed(2)}%`;
}

function renderSummary(anomaly) {
  const table = document.querySelector("#summary-table");
  table.replaceChildren();
  PERIOD_ORDER.forEach((period) => {
    const result = anomaly.summary[period];
    const row = document.createElement("tr");
    const dotClass = period === "gap" ? "gap-dot" : period === "post_publication" ? "post-dot" : "";
    const label = document.createElement("td");
    const periodCell = document.createElement("span");
    periodCell.className = "period-cell";
    const dot = document.createElement("i");
    dot.className = `period-dot ${dotClass}`;
    periodCell.append(dot, document.createTextNode(result.label));
    label.append(periodCell);
    row.append(label);
    [
      formatNumber(result.mean_monthly_pct),
      formatNumber(result.median_monthly_pct),
      formatNumber(result.std_monthly_pct),
      result.observations.toLocaleString(),
    ].forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    table.append(row);
  });
  document.querySelector("#range-note").textContent =
    `Sample ${anomaly.sample_start_year}–${anomaly.sample_end_year} · Published ${anomaly.publication_year}`;
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