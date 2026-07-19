const CYTOSCAPE_URL = "https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js";

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

export async function renderNetwork(container, block) {
  container.classList.add("viz");

  const stage = document.createElement("div");
  stage.className = "viz__stage";
  stage.setAttribute("role", "img");
  stage.setAttribute("aria-label", block.title || "Rețea socială demonstrativă");
  stage.tabIndex = 0;
  container.appendChild(stage);

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
    footer.remove();
    const errEl = document.createElement("div");
    errEl.className = "code-runner__unsupported";
    errEl.textContent = err.message;
    container.appendChild(errEl);
    return;
  }

  const elements = [
    ...data.nodes.map((n) => ({
      data: { id: n.id, label: n.label, clasa: n.clasa, interes: n.interes }
    })),
    ...data.edges.map((e, i) => ({
      data: { id: `e${i}`, source: e.source, target: e.target }
    }))
  ];

  const cy = cytoscape({
    container: stage,
    elements,
    style: [
      {
        selector: "node",
        style: {
          "background-color": "#8b4a1e",
          "label": "data(label)",
          "color": "#2a1f16",
          "font-family": "Georgia, serif",
          "font-size": 13,
          "text-valign": "bottom",
          "text-margin-y": 6,
          "width": 22,
          "height": 22,
          "border-width": 1,
          "border-color": "#5a4a3a",
          "transition-property": "opacity, background-color, border-color",
          "transition-duration": 150
        }
      },
      {
        selector: "edge",
        style: {
          "line-color": "#b57140",
          "width": 1.5,
          "curve-style": "bezier",
          "opacity": 0.7,
          "transition-property": "opacity, line-color",
          "transition-duration": 150
        }
      },
      {
        selector: ".highlighted",
        style: {
          "background-color": "#a3341f",
          "border-color": "#2a1f16",
          "border-width": 2
        }
      },
      {
        selector: ".neighbor",
        style: {
          "background-color": "#b57140"
        }
      },
      {
        selector: ".dimmed",
        style: { "opacity": 0.15 }
      }
    ],
    layout: { name: "cose", animate: false, padding: 30 },
    minZoom: 0.5,
    maxZoom: 2.5,
    wheelSensitivity: 0.2
  });

  function clearHighlight() {
    cy.elements().removeClass("highlighted neighbor dimmed");
    info.textContent = "Atinge un nod pentru detalii.";
  }

  function highlightNode(node) {
    const neighborhood = node.closedNeighborhood();
    cy.elements().addClass("dimmed");
    neighborhood.removeClass("dimmed");
    node.addClass("highlighted");
    node.neighborhood("node").addClass("neighbor");
    const d = node.data();
    info.textContent = `${d.label} — clasa ${d.clasa}, interes: ${d.interes}`;
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
