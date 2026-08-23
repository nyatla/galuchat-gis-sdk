const WORDBOOK_URL = "../../../datasets/jp-admin-n03-2024/N03-20240101.giswordbook";
const DEFAULT_CENTER = Object.freeze({ lon: 140.0267, lat: 35.6810 });
const OFFSCREEN_PADDING = 160;
const RESOLVER_MAPSET_ID = "10000";
const MAPSETS = Object.freeze({
  "10000": "../../../datasets/jp-admin-n03-2024/N03-20240101-grid-8192-10000.remap.wgsmapset.glc",
  "1000": "../../../datasets/jp-admin-n03-2024/N03-20240101-grid-4096-1000.remap.wgsmapset.glc",
  "100": "../../../datasets/jp-admin-n03-2024/N03-20240101-grid-512-100.remap.wgsmapset.glc",
});
const ZOOM_LEVELS = Object.freeze([
  { id: "10000", mapset: "10000", scale: 1 },
  { id: "10000/2", mapset: "10000", scale: 2 },
  { id: "10000/4", mapset: "10000", scale: 4 },
  { id: "1000", mapset: "1000", scale: 1 },
  { id: "1000/2", mapset: "1000", scale: 2 },
  { id: "1000/4", mapset: "1000", scale: 4 },
  { id: "100", mapset: "100", scale: 1 },
  { id: "100/2", mapset: "100", scale: 2 },
  { id: "100/4", mapset: "100", scale: 4 },
]);

const shell = document.getElementById("map-shell");
const placeNameOutput = document.getElementById("place-name");
const zoomOutButton = document.getElementById("zoom-out");
const zoomInButton = document.getElementById("zoom-in");
const homeButton = document.getElementById("home");

let interactiveMap = null;
let source = null;

main().catch(showFatalError);

async function main() {
  const [displayReaders, wordbookBytes] = await Promise.all([
    loadMapsets(MAPSETS),
    fetchBinary(WORDBOOK_URL),
  ]);
  const wordbookReader = Galuchat.GaluchatGisWordBookReader.fromUint8Array(wordbookBytes);
  source = new Galuchat.MultiZoomMapSource({
    displayReaders,
    resolverReader: displayReaders[RESOLVER_MAPSET_ID],
    wordbookReader,
    levels: ZOOM_LEVELS,
    padding: OFFSCREEN_PADDING,
  });

  interactiveMap = new Galuchat.GaluchatInteractiveMap(shell, source, {
    center: DEFAULT_CENTER,
    maxWidth: 640,
    maxHeight: 480,
  });
  interactiveMap.addEventListener("placechange", (event) => {
    placeNameOutput.classList.remove("error");
    placeNameOutput.textContent = event.detail.name;
  });
  interactiveMap.addEventListener("maprender", updateButtons);

  zoomOutButton.addEventListener("click", () => interactiveMap.zoomOut());
  zoomInButton.addEventListener("click", () => interactiveMap.zoomIn());
  homeButton.addEventListener("click", () => {
    source.setZoomLevelIndex(0);
    interactiveMap.setView({
      center: source.snapCenter(DEFAULT_CENTER),
      selectedCode: null,
    });
  });
  interactiveMap.canvas.addEventListener("wheel", (event) => interactiveMap.zoomByWheel(event), { passive: false });
  interactiveMap.canvas.addEventListener("dblclick", (event) => {
    event.preventDefault();
    interactiveMap.zoomIn(interactiveMap.eventToCanvasPoint(event));
  });

  for (const button of [zoomOutButton, zoomInButton, homeButton]) {
    button.disabled = false;
  }
  updateButtons();
  await interactiveMap.render();
}

function updateButtons() {
  if (interactiveMap === null) {
    return;
  }
  zoomInButton.disabled = !interactiveMap.canZoomIn();
  zoomOutButton.disabled = !interactiveMap.canZoomOut();
}

async function loadMapsets(mapsets) {
  const entries = await Promise.all(
    Object.entries(mapsets).map(async ([id, url]) => {
      const bytes = await fetchBinary(url);
      return [id, Galuchat.GaluchatWGSMapSet3Reader.fromUint8Array(bytes)];
    }),
  );
  return Object.fromEntries(entries);
}

async function fetchBinary(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to fetch ${url}: ${response.status} ${response.statusText}`);
  }
  return new Uint8Array(await response.arrayBuffer());
}

function showFatalError(error) {
  placeNameOutput.classList.add("error");
  placeNameOutput.textContent = "初期化に失敗しました";
  console.error(error);
}
