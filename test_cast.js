const { JSDOM } = require("jsdom");
(async () => {
  const dom = await JSDOM.fromURL("http://127.0.0.1:8977/index.html", {
    runScripts: "dangerously", resources: "usable", pretendToBeVisual: true,
  });
  await new Promise(r => setTimeout(r, 1500));
  const d = dom.window.document;
  console.log("cards:", d.querySelectorAll(".card").length);
  console.log("card cast EN spans:", d.querySelectorAll(".cast .cen").length);
  console.log("sample card cast:", d.querySelector(".card .cast")?.textContent.trim());
  // open 復仇者 detail
  const q = d.querySelector("#q");
  q.value = "復仇者"; q.dispatchEvent(new dom.window.Event("input", { bubbles: true }));
  await new Promise(r => setTimeout(r, 200));
  const c = d.querySelector(".card");
  console.log("found:", c?.querySelector(".ttl")?.textContent);
  c.dispatchEvent(new dom.window.MouseEvent("click", { bubbles: true }));
  await new Promise(r => setTimeout(r, 200));
  const p = d.querySelector("#panel");
  console.log("panel open:", p.classList.contains("on"));
  console.log("panel 主演 block:", p.querySelector(".plist")?.textContent.trim().replace(/\s+/g, " "));
  console.log("OK");
  process.exit(0);
})().catch(e => { console.error("FAIL", e); process.exit(1); });
