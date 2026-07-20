const CYTOSCAPE_URL = "https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js";

export const GROUP_PALETTE = [
  "#8b4a1e",
  "#3d7a52",
  "#2f6fa8",
  "#a3341f",
  "#7a5b8c",
  "#b57140"
];

let cyLoader = null;

export function loadCytoscape() {
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

function formatNodeInfo(d) {
  const parts = [`Elev ${d.id}`];
  if (d.group !== undefined && d.group !== "" && d.group !== "exemplu") {
    parts.push(`clasa ${d.group}`);
  }
  return parts.join(" — ");
}

function buildGroupColors(groups) {
  const map = new Map();
  groups.forEach((g, i) => map.set(g, GROUP_PALETTE[i % GROUP_PALETTE.length]));
  return map;
}

function baseStyle(showLabels, edgeWidth) {
  return [
    {
      selector: "node",
      style: {
        "background-color": "data(color)",
        "label": showLabels ? "data(label)" : "",
        "color": "#2a1f16",
        "font-family": "Georgia, serif",
        "font-size": 13,
        "text-valign": "bottom",
        "text-margin-y": 6,
        "width": 24,
        "height": 24,
        "border-width": 1,
        "border-color": "#5a4a3a",
        "transition-property": "width, height, border-width, border-color, background-color",
        "transition-duration": 150
      }
    },
    {
      selector: "edge",
      style: {
        "line-color": "#b57140",
        "width": typeof edgeWidth === "number" ? edgeWidth : "data(w)",
        "curve-style": "bezier",
        "opacity": 0.6,
        "transition-property": "opacity, line-color, width",
        "transition-duration": 150
      }
    },
    {
      selector: ".highlighted",
      style: {
        "border-color": "#2a1f16",
        "border-width": 3,
        "width": 30,
        "height": 30
      }
    },
    {
      selector: ".neighbor-edge",
      style: {
        "line-color": "#2a1f16",
        "opacity": 0.95
      }
    },
    {
      selector: ".dimmed",
      style: { "opacity": 0.12 }
    }
  ];
}

function createShell(container, block, buttonText, buttonVariant) {
  container.classList.add("viz");
  container.innerHTML = "";

  const stage = document.createElement("div");
  stage.className = "viz__stage";
  stage.setAttribute("role", "img");
  stage.setAttribute("aria-label", block.title || "Rețea");
  stage.tabIndex = 0;
  container.appendChild(stage);

  const legend = document.createElement("div");
  legend.className = "viz__legend";
  container.appendChild(legend);

  const footer = document.createElement("div");
  footer.className = "viz__footer";
  const button = document.createElement("button");
  button.type = "button";
  button.className = `btn ${buttonVariant === "primary" ? "btn--primary" : "btn--ghost"}`;
  button.textContent = buttonText;
  const info = document.createElement("div");
  info.className = "viz__info";
  info.textContent = "";
  footer.appendChild(button);
  footer.appendChild(info);
  container.appendChild(footer);

  return { stage, legend, footer, button, info };
}

function renderLegend(legendEl, groups, colorMap) {
  const visible = groups.filter((g) => g && g !== "exemplu");
  if (visible.length < 2) {
    legendEl.remove();
    return;
  }
  legendEl.innerHTML = "";
  for (const g of visible) {
    const chip = document.createElement("span");
    chip.className = "viz__legend-chip";
    const dot = document.createElement("span");
    dot.className = "viz__legend-dot";
    dot.style.background = colorMap.get(g);
    chip.appendChild(dot);
    chip.appendChild(document.createTextNode(g));
    legendEl.appendChild(chip);
  }
}

function normalizeAndBuild(data) {
  const nodes = data.nodes.map((n) => ({
    id: String(n.id),
    label: n.label != null ? String(n.label) : String(n.id),
    group: n.group != null ? String(n.group) : (n.clasa != null ? String(n.clasa) : "")
  }));
  const edges = data.edges.map((e, i) => ({
    id: `e${i}`,
    source: String(e.source),
    target: String(e.target),
    weight: typeof e.weight === "number" ? e.weight : 1
  }));
  const groups = [...new Set(nodes.map((n) => n.group).filter(Boolean))];
  const colorMap = buildGroupColors(groups);
  const weights = edges.map((e) => e.weight);
  const wMin = weights.length ? Math.min(...weights) : 1;
  const wMax = weights.length ? Math.max(...weights) : 1;
  const scaleWidth = (w) => (wMax === wMin ? 2 : 1.2 + ((w - wMin) / (wMax - wMin)) * 4.8);

  const elements = [
    ...nodes.map((n) => ({
      data: {
        id: n.id,
        label: n.label,
        group: n.group,
        color: colorMap.get(n.group) || GROUP_PALETTE[0]
      }
    })),
    ...edges.map((e) => ({
      data: {
        id: e.id,
        source: e.source,
        target: e.target,
        weight: e.weight,
        w: scaleWidth(e.weight)
      }
    }))
  ];

  return { elements, nodes, edges, groups, colorMap };
}

function attachTapHighlight(cy, info, defaultText) {
  function clear() {
    cy.elements().removeClass("highlighted neighbor-edge dimmed");
    info.textContent = defaultText;
  }
  function highlight(node) {
    cy.elements().addClass("dimmed");
    node.closedNeighborhood().removeClass("dimmed");
    node.addClass("highlighted");
    node.connectedEdges().addClass("neighbor-edge");
    info.textContent = formatNodeInfo(node.data());
  }
  cy.on("tap", "node", (e) => highlight(e.target));
  cy.on("tap", (e) => { if (e.target === cy) clear(); });
  return { clear, highlight };
}

function attachResize(cy, stage) {
  const refit = () => {
    try {
      cy.resize();
      if (cy.elements().length > 0) cy.fit(undefined, 30);
    } catch { /* ignore */ }
  };
  const onWin = () => refit();
  window.addEventListener("resize", onWin);
  const ro = new ResizeObserver(refit);
  ro.observe(stage);
  return {
    refit,
    destroy() {
      window.removeEventListener("resize", onWin);
      ro.disconnect();
    }
  };
}

function errorHandle(container, message) {
  container.innerHTML = "";
  const errEl = document.createElement("div");
  errEl.className = "code-runner__unsupported";
  errEl.textContent = message;
  container.appendChild(errEl);
  return { refit() {}, destroy() {} };
}

export async function renderNetwork(container, block) {
  const defaultInfo = "Atinge un nod pentru detalii.";
  const shell = createShell(container, block, "Resetează", "ghost");
  shell.info.textContent = defaultInfo;

  let cytoscape, data;
  try {
    [cytoscape, data] = await Promise.all([loadCytoscape(), loadJSON(block.data)]);
  } catch (err) {
    return errorHandle(container, err.message);
  }

  const { elements, nodes, groups, colorMap } = normalizeAndBuild(data);
  const showLabels = nodes.length <= 12;

  const cy = cytoscape({
    container: shell.stage,
    elements,
    style: baseStyle(showLabels),
    layout: {
      name: "cose",
      animate: false,
      padding: 24,
      idealEdgeLength: 60,
      nodeRepulsion: 5000,
      componentSpacing: 40
    },
    minZoom: 0.3,
    maxZoom: 2.5,
    wheelSensitivity: 0.2
  });
  cy.style().update();

  renderLegend(shell.legend, groups, colorMap);
  const hl = attachTapHighlight(cy, shell.info, defaultInfo);

  shell.button.addEventListener("click", () => {
    hl.clear();
    cy.resize();
    cy.fit(undefined, 30);
  });

  shell.stage.addEventListener("keydown", (e) => {
    if (e.key === "Escape") hl.clear();
  });

  const resizer = attachResize(cy, shell.stage);
  requestAnimationFrame(resizer.refit);

  return {
    refit: resizer.refit,
    destroy() { resizer.destroy(); cy.destroy(); }
  };
}

export async function renderInteractive(container, block) {
  const mode = block.mode;
  const primaryColor = GROUP_PALETTE[0];

  let cytoscape;
  try {
    cytoscape = await loadCytoscape();
  } catch (err) {
    return errorHandle(container, err.message);
  }

  if (mode === "mini-network") {
    let data;
    try { data = await loadJSON(block.data); }
    catch (err) { return errorHandle(container, err.message); }

    const defaultInfo = block.hint || "Atinge un nod pentru detalii.";
    const shell = createShell(container, block, "Resetează", "ghost");
    shell.info.textContent = defaultInfo;

    const { elements } = normalizeAndBuild(data);
    const cy = cytoscape({
      container: shell.stage,
      elements,
      style: baseStyle(false),
      layout: { name: "cose", animate: false, padding: 24, idealEdgeLength: 70 },
      minZoom: 0.4,
      maxZoom: 2.5
    });
    cy.style().update();
    shell.legend.remove();

    const hl = attachTapHighlight(cy, shell.info, defaultInfo);
    shell.button.addEventListener("click", () => {
      hl.clear();
      cy.resize();
      cy.fit(undefined, 30);
    });

    const resizer = attachResize(cy, shell.stage);
    requestAnimationFrame(resizer.refit);

    return {
      refit: resizer.refit,
      destroy() { resizer.destroy(); cy.destroy(); }
    };
  }

  if (mode === "add-node") {
    const shell = createShell(container, block, block.buttonLabel || "Adaugă un elev", "primary");
    const startHint = "Apasă butonul pentru a adăuga primul elev.";
    shell.info.textContent = block.hint || startHint;

    const cy = cytoscape({
      container: shell.stage,
      elements: [],
      style: baseStyle(true, 2.5),
      layout: { name: "preset" },
      minZoom: 0.5,
      maxZoom: 2
    });
    cy.style().update();
    shell.legend.remove();

    const names = ["Ana", "Bogdan", "Carla", "Doru", "Elena", "Florin"];
    let count = 0;
    shell.button.addEventListener("click", () => {
      if (count >= names.length) return;
      const id = String(count + 1);
      cy.add({ data: { id, label: names[count], group: "exemplu", color: primaryColor } });
      count++;
      cy.layout({ name: "circle", animate: false, padding: 30, radius: 60 }).run();
      cy.resize();
      cy.fit(undefined, 30);
      shell.info.textContent = block.successText || "Ai creat un nod.";
      if (count >= names.length) {
        shell.button.disabled = true;
        shell.button.textContent = "Suficient";
      } else if (count >= 1) {
        shell.button.textContent = "Încă un elev";
      }
    });

    const resizer = attachResize(cy, shell.stage);
    requestAnimationFrame(resizer.refit);

    return {
      refit: resizer.refit,
      destroy() { resizer.destroy(); cy.destroy(); }
    };
  }

  if (mode === "add-edge") {
    const shell = createShell(container, block, block.buttonLabel || "Conectează-i", "primary");
    const startHint = "Doi elevi, încă neconectați. Apasă butonul.";
    shell.info.textContent = block.hint || startHint;

    const cy = cytoscape({
      container: shell.stage,
      elements: [
        { data: { id: "1", label: "Ana", group: "exemplu", color: primaryColor }, position: { x: 120, y: 120 } },
        { data: { id: "2", label: "Bogdan", group: "exemplu", color: primaryColor }, position: { x: 260, y: 120 } }
      ],
      style: baseStyle(true, 3),
      layout: { name: "preset" },
      minZoom: 0.5,
      maxZoom: 2
    });
    cy.style().update();
    shell.legend.remove();

    let connected = false;
    shell.button.addEventListener("click", () => {
      if (connected) return;
      cy.add({ data: { id: "e12", source: "1", target: "2", weight: 1, w: 3 } });
      connected = true;
      shell.button.disabled = true;
      shell.button.textContent = "Conectați";
      cy.resize();
      cy.fit(undefined, 30);
      shell.info.textContent =
        block.successText ||
        "O muchie este o relație. Cât de groasă va fi arată cât timp au petrecut împreună.";
    });

    const resizer = attachResize(cy, shell.stage);
    requestAnimationFrame(resizer.refit);

    return {
      refit: resizer.refit,
      destroy() { resizer.destroy(); cy.destroy(); }
    };
  }

  return errorHandle(container, `Mod interactiv necunoscut: ${mode}`);
}
