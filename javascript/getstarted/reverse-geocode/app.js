const MAPSET_URL = "../../../datasets/jp-admin-n03-2024/N03-20240101-grid-4096-1000.remap.wgsmapset.glc";
const WORDBOOK_URL = "../../../datasets/jp-admin-n03-2024/N03-20240101.giswordbook";

const form = document.getElementById("query-form");
const lonInput = document.getElementById("lon");
const latInput = document.getElementById("lat");
const submitButton = document.getElementById("submit");
const nameOutput = document.getElementById("name");
const detailsOutput = document.getElementById("details");

let geocoder = null;
let mapset = null;
let wordbook = null;

main().catch(showFatalError);

async function main() {
  const [mapsetBytes, wordbookBytes] = await Promise.all([
    fetchBinary(MAPSET_URL),
    fetchBinary(WORDBOOK_URL),
  ]);

  mapset = Galuchat.GaluchatWGSMapSet3Reader.fromUint8Array(mapsetBytes);
  wordbook = Galuchat.GaluchatGisWordBookReader.fromUint8Array(wordbookBytes);
  geocoder = new Galuchat.ReverseGeocoder(mapset, wordbook);

  submitButton.disabled = false;
  submitButton.textContent = "地名を調べる";
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    renderResult();
  });

  for (const button of document.querySelectorAll(".sample")) {
    button.addEventListener("click", () => {
      lonInput.value = button.dataset.lon;
      latInput.value = button.dataset.lat;
      renderResult();
    });
  }

  renderResult();
}

function renderResult() {
  try {
    const lon = Number(lonInput.value);
    const lat = Number(latInput.value);
    const result = geocoder.reverseGeocode(lon, lat);

    nameOutput.classList.remove("error");
    nameOutput.textContent = result.name ?? "地名が見つかりません";
    detailsOutput.textContent = JSON.stringify(
      {
        query: { lon, lat },
        result,
        mapset: {
          unitInvX: mapset.unitInvX,
          unitInvY: mapset.unitInvY,
          areaOfWgs: mapset.areaOfWgs,
        },
        wordbook: {
          source: "N03-20240101.giswordbook",
          recordCount: wordbook.recordCount,
          depth: wordbook.depth,
          componentCount: wordbook.componentCount,
        },
      },
      null,
      2,
    );
  } catch (error) {
    nameOutput.classList.add("error");
    nameOutput.textContent = "入力を確認してください";
    detailsOutput.textContent = error instanceof Error ? error.message : String(error);
  }
}

async function fetchBinary(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to fetch ${url}: ${response.status} ${response.statusText}`);
  }
  return new Uint8Array(await response.arrayBuffer());
}

function showFatalError(error) {
  submitButton.disabled = true;
  submitButton.textContent = "初期化失敗";
  nameOutput.classList.add("error");
  nameOutput.textContent = "初期化に失敗しました";
  detailsOutput.textContent = error instanceof Error ? error.stack : String(error);
}
