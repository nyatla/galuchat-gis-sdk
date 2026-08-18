const MAPSET_URL = "../../../datasets/jp-admin-n03/N03-20240101-grid-4096-1000.remap.wgsmapset.glc";
const MAX_IMAGE_PIXELS = 2048 * 2048;

const form = document.getElementById("render-form");
const lonInput = document.getElementById("lon");
const latInput = document.getElementById("lat");
const widthInput = document.getElementById("width");
const heightInput = document.getElementById("height");
const scaleInput = document.getElementById("scale");
const edgeInput = document.getElementById("edge");
const renderButton = document.getElementById("render");
const downloadButton = document.getElementById("download");
const canvas = document.getElementById("map");
const context = canvas.getContext("2d");
const detailsOutput = document.getElementById("details");

let mapset = null;
let renderer = null;
let lastRender = null;

main().catch(showFatalError);

async function main() {
  const mapsetBytes = await fetchBinary(MAPSET_URL);
  mapset = Galuchat.GaluchatWGSMapSet3Reader.fromUint8Array(mapsetBytes);
  renderer = new Galuchat.MapImageRenderer();

  renderButton.disabled = false;
  renderButton.textContent = "画像を取得";
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    renderMap();
  });
  downloadButton.addEventListener("click", downloadCanvasPng);

  for (const button of document.querySelectorAll(".sample")) {
    button.addEventListener("click", () => {
      lonInput.value = button.dataset.lon;
      latInput.value = button.dataset.lat;
      renderMap();
    });
  }

  renderMap();
}

function renderMap() {
  try {
    const request = readRenderRequest();
    const selector = new Galuchat.WgsPointRectSelector(
      request.lon,
      request.lat,
      request.width,
      request.height,
    );
    const image = renderer.render(mapset, selector, new Galuchat.MapImageRenderOptions({
      fillOptions: new Galuchat.MapFillRenderOptions({
        defaultColor: new Galuchat.Color(60, 160, 60, 255),
        colors: {
          0: new Galuchat.Color(0, 0, 255, 255),
        },
      }),
      edgeOptions: request.drawEdge
        ? new Galuchat.MapEdgeRenderOptions({
          edgeColor: new Galuchat.Color(64, 64, 64, 255),
          edgeWidth: 1,
          includeZero: true,
        })
        : null,
    }));
    const rect = selector.resolveRect(mapset);

    canvas.width = image.width;
    canvas.height = image.height;
    canvas.style.width = `${Math.round(image.width * request.cssScale)}px`;
    canvas.style.height = `${Math.round(image.height * request.cssScale)}px`;
    context.putImageData(image.toImageData((width, height) => context.createImageData(width, height)), 0, 0);

    lastRender = { ...request, rect };
    downloadButton.disabled = false;
    detailsOutput.classList.remove("error");
    detailsOutput.textContent = JSON.stringify(
      {
        renderRequest: request,
        pixelCenter: selector.resolvePoint(mapset),
        pixelRect: rect,
        lonLatBounds: rectToLonLatBounds(rect),
        mapset: {
          unitInvX: mapset.unitInvX,
          unitInvY: mapset.unitInvY,
          areaOfWgs: mapset.areaOfWgs,
        },
      },
      null,
      2,
    );
  } catch (error) {
    downloadButton.disabled = true;
    detailsOutput.classList.add("error");
    detailsOutput.textContent = error instanceof Error ? error.message : String(error);
  }
}

function readRenderRequest() {
  const lon = Number(lonInput.value);
  const lat = Number(latInput.value);
  const width = readPositiveInteger(widthInput.value, "幅");
  const height = readPositiveInteger(heightInput.value, "高さ");
  const cssScale = Number(scaleInput.value);
  if (!Number.isFinite(lon) || !Number.isFinite(lat)) {
    throw new Error("経度・緯度を数値で入力してください");
  }
  if (!Number.isFinite(cssScale) || cssScale <= 0) {
    throw new Error("CSS表示倍率を正の数値で入力してください");
  }
  if (width * height > MAX_IMAGE_PIXELS) {
    throw new Error(`画像サイズが大きすぎます: ${width}x${height}`);
  }
  return {
    lon,
    lat,
    width,
    height,
    cssScale,
    drawEdge: edgeInput.checked,
  };
}

function rectToLonLatBounds(rect) {
  return {
    west: rect.x / mapset.unitInvX,
    south: rect.y / mapset.unitInvY,
    east: (rect.x + rect.width) / mapset.unitInvX,
    north: (rect.y + rect.height) / mapset.unitInvY,
  };
}

function readPositiveInteger(value, label) {
  const number = Number(value);
  if (!Number.isInteger(number) || number <= 0) {
    throw new Error(`${label}を正の整数で入力してください`);
  }
  return number;
}

async function fetchBinary(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to fetch ${url}: ${response.status} ${response.statusText}`);
  }
  return new Uint8Array(await response.arrayBuffer());
}

function downloadCanvasPng() {
  if (lastRender === null) {
    return;
  }
  const anchor = document.createElement("a");
  anchor.download = `galuchat-${lastRender.lon}-${lastRender.lat}-${lastRender.width}x${lastRender.height}.png`;
  anchor.href = canvas.toDataURL("image/png");
  anchor.click();
}

function showFatalError(error) {
  renderButton.disabled = true;
  renderButton.textContent = "初期化失敗";
  downloadButton.disabled = true;
  detailsOutput.classList.add("error");
  detailsOutput.textContent = error instanceof Error ? error.stack : String(error);
}
