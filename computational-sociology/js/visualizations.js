const CYTOSCAPE_URL = "https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js";

const GROUP_PALETTE = [
  "#8b4a1e",
  "#3d7a52",
  "#2f6fa8",
  "#a3341f",
  "#7a5b8c",
  "#b57140"
];

let cyLoader = null;

function loadCytoscape() {
  if (window.cytoscape) return Promise.resolve(window.cytoscape);
  if (cyLoader) return cyLoader;
  cyLoader = new Promise((resolve, reject) => {
    const s = document.createElement("script");
    s.src = CYTOSCAPE_URL;
    s.async = true;
    s.onload = () => resolve(window.cytoscape);
    s.onerror = () => reject(new Error("Nu am putut încărca Cytoscape.js"));
    document.head.appendChild(s);
  });
  return cyLoader;
}

async function loadJSON(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Nu am putut încărca ${path}`);
  return res.json();
}

function normalizeNode(n) {
  return {
    id: String(n.id),
    label: n.label != null ? String(n.label) : String(n.id),
    group: n.group != null ? String(n.group) : (n.clasa != null ? String(n.clasa) : ""),
    interes: n.interes != null ? String(n.interes) : ""
  };
}

function normalizeEdge(e, i) {
  return {
    id: `e${i}`,
    source: String(e.source),
    target: String(e.target),
    weight: typeof e.weight === "number" ? e.weight : 1
  };
}

function buildGroupColors(nodes) {
  const groups = [...new Set(nodes.map((n) => n.group).filter(Boolean))];
  const map = new Map();
  groups.forEach((g, i) => map.set(g, GROUP_PALETTE[i % GROUP_PALETTE.length]));
  return { groups, map };
}

export async function renderNetwork(container, block) {
  container.classList.add("viz");

  const stage = document.createElement("div");
  stage.className = "viz__stage";
  stage.setAttribute("role", "img");
  stage.setAttribute("aria-label", block.title || "Rețea socială");
  stage.tabIndex = 0;
  container.appendChild(stage);

  const legend = document.createElement("div");
  legend.className = "viz__legend";
  container.appendChild(legend);

  const footer = document.createElement("div");
  footer.className = "viz__footer";
  const resetBtn = document.createElement("button");
  resetBtn.type = "button";
  resetBtn.className = "btn btn--ghost";
  resetBtn.textContent = "Resetează";
  const info = document.createElement("div");
  info.className = "viz__info";
  info.textContent = "Atinge un nod pentru detalii.";
  footer.appendChild(resetBtn);
  footer.appendChild(info);
  container.appendChild(footer);

  let cytoscape, data;
  try {
    [cytoscape, data] = await Promise.all([loadCytoscape(), loadJSON(block.data)]);
  } catch (err) {
    stage.remove();
    legend.remove();
    footer.remove();
    const errEl = document.createElement("div");
    errEl.className = "code-runner__unsupported";
    errEl.textContent = err.message;
    container.appendChild(errEl);
    return;
  }

  const nodes = data.nodes.map(normalizeNode);
  const edges = data.edges.map(normalizeEdge);
  const { groups, map: colorMap } = buildGroupColors(nodes);

  const weights = edges.map((e) => e.weight);
  const wMin = Math.min(...weights, 1);
  const wMax = Math.max(...weights, 1);
  const scaleWidth = (w) => {
    if (wMax === wMin) return 1.6;
    const t = (w - wMin) / (wMax - wMin);
    return 1.2 + t * 4.4;
  };

  const elements = [
    ...nodes.map((n) => ({
      data: {
        id: n.id,
        label: n.label,
        group: n.group,
        interes: n.interes,
        color: colorMap.get(n.group) || GROUP_PALETTE[0]
      }
    })),
    ...edges.map((e) => ({
      data: { id: e.id, source: e.source, target: e.target, weight: e.weight, w: scaleWidth(e.weight) }
    }))
  ];

  const showLabels = nodes.length <= 12;

  const cy = cytoscape({
    container: stage,
    elements,
    style: [
      {
        selector: "node",
        style: {
          "background-color": "data(color)",
          "label": showLabels ? "data(label)" : "",
          "color": "#2a1f16",
          "font-family": "Georgia, serif",
          "font-size": 12,
          "text-valign": "bottom",
          "text-margin-y": 6,
          "width": 20,
          "height": 20,
          "border-width": 1,
          "border-color": "#5a4a3a",
          "transition-property": "opacity, background-color, border-color, width, height",
          "transition-duration": 150
        }
      },
      {
        selector: "edge",
        style: {
          "line-color": "#b57140",
          "width": "data(w)",
          "curve-style": "bezier",
          "opacity": 0.55,
          "transition-property": "opacity, line-color",
          "transition-duration": 150
        }
      },
      {
        selector: ".highlighted",
        style: {
          "border-color": "#2a1f16",
          "border-width": 3,
          "width": 26,
          "height": 26
        }
      },
      {
        selector: ".neighbor-edge",
        style: {
          "line-color": "#2a1f16",
          "opacity": 0.9
        }
      },
      {
        selector: ".dimmed",
        style: { "opacity": 0.12 }
      }
    ],
    layout: {
      name: "cose",
      animate: false,
      padding: 24,
      idealEdgeLength: 60,
      nodeRepulsion: 5000,
      componentSpacing: 40
    },
    minZoom: 0.4,
    maxZoom: 2.5,
    wheelSensitivity: 0.2
  });

  if (groups.length > 1) {
    legend.innerHTML = "";
    for (const g of groups) {
      const chip = document.createElement("span");
      chip.className = "viz__legend-chip";
      const dot = document.createElement("span");
      dot.className = "viz__legend-dot";
      dot.style.background = colorMap.get(g);
      chip.appendChild(dot);
      chip.appendChild(document.createTextNode(g));
      legend.appendChild(chip);
    }
  } else {
    legend.remove();
  }

  function clearHighlight() {
    cy.elements().removeClass("highlighted neighbor-edge dimmed");
    info.textContent = "Atinge un nod pentru detalii.";
  }

  function highlightNode(node) {
    const neighborhood = node.closedNeighborhood();
    cy.elements().addClass("dimmed");
    neighborhood.removeClass("dimmed");
    node.addClass("highlighted");
    node.connectedEdges().addClass("neighbor-edge");
    const d = node.data();
    const parts = [d.label];
    if (d.group) parts.push(`clasa ${d.group}`);
    if (d.interes) parts.push(`interes: ${d.interes}`);
    const degree = node.connectedEdges().length;
    parts.push(`${degree} vecin${degree === 1 ? "" : "i"}`);
    info.textContent = parts.join(" · ");
  }

  cy.on("tap", "node", (e) => highlightNode(e.target));
  cy.on("tap", (e) => { if (e.target === cy) clearHighlight(); });

  resetBtn.addEventListener("click", clearHighlight);

  stage.addEventListener("keydown", (e) => {
    if (e.key === "Escape") clearHighlight();
    if (e.key === "Enter" || e.key === " ") {
      const first = cy.nodes()[0];
      if (first) highlightNode(first);
    }
  });

  const ro = new ResizeObserver(() => cy.resize());
  ro.observe(stage);
}
