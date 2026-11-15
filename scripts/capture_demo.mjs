/* Capture real frames from the deployed GigBid interface for the demo video. */
import { chromium } from "../tmp/demo-recorder/node_modules/playwright-core/index.mjs";
import { mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const output = new URL("../artifacts/demo-frames/", import.meta.url);
const outputPath = fileURLToPath(output);
const chrome = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const appUrl = "https://gigbid-api-pn5q.onrender.com/";

await mkdir(outputPath, { recursive: true });
const browser = await chromium.launch({ executablePath: chrome, headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });

await page.goto(appUrl, { waitUntil: "networkidle" });
await page.screenshot({ path: `${outputPath}01-inbox.png`, fullPage: false });

await page.getByRole("button", { name: "Run safe analysis" }).click();
await page.getByText("Draft paused for your approval.").waitFor({ state: "visible" });
await page.screenshot({ path: `${outputPath}02-analysis.png`, fullPage: false });

await page.locator("#studio").scrollIntoViewIfNeeded();
await page.screenshot({ path: `${outputPath}03-approval.png`, fullPage: false });

await page.getByRole("button", { name: /Urgent dashboard help/ }).click();
await page.getByRole("button", { name: "Run safe analysis" }).click();
await page.getByText("This job was safely skipped. Review the risk report.").waitFor({ state: "visible" });
await page.screenshot({ path: `${outputPath}04-safety.png`, fullPage: false });

await browser.close();
console.log(outputPath);
