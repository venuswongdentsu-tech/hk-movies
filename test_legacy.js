const { JSDOM } = require("jsdom");
(async () => {
  const dom = await JSDOM.fromURL("http://127.0.0.1:8977/index.html", {
    runScripts: "dangerously", resources: "usable", pretendToBeVisual: true,
  });
  const w = dom.window;
  await new Promise(r => { if (w.APP_DATA) return r(); w.addEventListener("load", r); });
  await new Promise(r => setTimeout(r, 1500));
  // 模擬「舊版快取」：cast 係純中文字串陣列（會令舊碼出 undefined）
  w.APP_DATA.movies[0].cast = ["羅拔唐尼", "貝兒娜森", "基斯咸士禾夫"];
  w.open(0);
  await new Promise(r => setTimeout(r, 400));
  const p = w.document.querySelector("#panel").textContent;
  const rows = w.document.querySelectorAll("#panel .plist .prow");
  console.log("panel has 'undefined'? ->", p.includes("undefined"));
  console.log("rows:", rows.length);
  rows.forEach(r => console.log("   row:", r.textContent.trim()));
  // 再測 card 渲染
  const cardHtml = w.card(w.APP_DATA.movies[0]);
  console.log("card has 'undefined'? ->", cardHtml.includes("undefined"));
  console.log("card cast text:", cardHtml.match(/主演：([^<]*)/) ? cardHtml.match(/主演：([^<]*)/)[1] : "n/a");
})();
