import { expect, test, type Page } from "@playwright/test";

type H2Probe = { hazards: string[]; observedRoots: number };

async function installH2SecurityProbe(page: Page) {
  const dialogs: string[] = [];
  const pageErrors: string[] = [];
  page.on("dialog", async (dialog) => {
    dialogs.push(dialog.type() + ":" + dialog.message());
    await dialog.dismiss();
  });
  page.on("pageerror", (error) => pageErrors.push(error.message));

  await page.addInitScript(() => {
    const roots: Array<Document | ShadowRoot> = [document];
    const hazards = new Set<string>();

    const inspectElement = (element: Element) => {
      const tag = element.localName.toLowerCase();
      if (tag === "script" && /alert\s*\(\s*1\s*\)/i.test(element.textContent ?? "")) {
        hazards.add("script:alert(1)");
      }
      if (tag === "img" && element.hasAttribute("onerror")) {
        hazards.add("img:onerror");
      }
      if (tag === "a") {
        const href = element.getAttribute("href") ?? "";
        if (/^\s*javascript:/i.test(href)) hazards.add("a:javascript");
        if (/example\.com/i.test(href)) hazards.add("a:example.com");
      }
      if (tag === "b" && (element.textContent ?? "").trim() === "hola") {
        hazards.add("b:hola");
      }
      if (/color\s*:\s*red/i.test(element.getAttribute("style") ?? "")) {
        hazards.add("style:color-red");
      }
      if ((element.getAttribute("class") ?? "").split(/\s+/).includes("a")) {
        hazards.add("class:htmlClass-a");
      }
    };

    const inspect = (node: Node) => {
      if (node instanceof Element) inspectElement(node);
      if (node instanceof Element || node instanceof Document || node instanceof DocumentFragment) {
        node.querySelectorAll("*").forEach(inspectElement);
      }
    };
    const observer = new MutationObserver((records) => {
      for (const record of records) {
        for (const node of record.addedNodes) inspect(node);
        if (record.type === "attributes" && record.target instanceof Element) {
          inspectElement(record.target);
        }
        if (record.type === "characterData" && record.target.parentElement) {
          inspectElement(record.target.parentElement);
        }
      }
    });
    observer.observe(document, {
      childList: true, subtree: true, characterData: true, attributes: true,
      attributeFilter: ["href", "src", "onerror", "class", "style"],
    });

    const originalAttachShadow = Element.prototype.attachShadow;
    Element.prototype.attachShadow = function(init: ShadowRootInit) {
      const root = originalAttachShadow.call(this, init);
      roots.push(root);
      inspect(root);
      observer.observe(root, {
        childList: true, subtree: true, characterData: true, attributes: true,
        attributeFilter: ["href", "src", "onerror", "class", "style"],
      });
      return root;
    };

    (window as Window & { __h2SecurityProbe?: () => H2Probe }).__h2SecurityProbe = () => {
      roots.forEach(inspect);
      return { hazards: [...hazards].sort(), observedRoots: roots.length };
    };
  });

  return {
    dialogs,
    pageErrors,
    async snapshot() {
      return page.evaluate(() =>
        (window as Window & { __h2SecurityProbe: () => H2Probe }).__h2SecurityProbe()
      );
    },
  };
}

async function enter(page: Page, source: string) {
  const field = page.locator("math-field").first();
  await field.waitFor({ state: "visible" });
  await field.evaluate((element, value) => {
    const mathfield = element as HTMLElement & { setValue(value: string): void };
    mathfield.setValue(value);
    element.dispatchEvent(new InputEvent("input", {
      bubbles: true, inputType: "insertText", data: value,
    }));
  }, source);
}

async function calculateAndObserve(page: Page, source: string, mustShowError: boolean) {
  await enter(page, source);
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();

  await expect.poll(async () => {
    const error = (await page.getByRole("alert").allInnerTexts()).join(" ").trim();
    const result = (await page.locator(".a11y-scale-result-lg").allInnerTexts()).join(" ").trim();
    return error || result ? "settled" : "pending";
  }, { timeout: 8_000 }).toBe("settled");

  const error = (await page.getByRole("alert").allInnerTexts()).join(" ").trim();
  const result = (await page.locator(".a11y-scale-result-lg").allInnerTexts()).join(" ").trim();
  if (mustShowError) {
    expect(error, "Expected a clear user-facing error for " + source).not.toBe("");
  } else {
    expect(error || result, "Expected a clear error or inert text for " + source).not.toBe("");
  }
}

const cases = [
  { id: "EN-SG-01 raw script", source: "<script>alert(1)</script>", mustShowError: false },
  { id: "EN-SG-02 image onerror", source: "<img src=x onerror=alert(1)>", mustShowError: false },
  { id: "EN-SG-03 bold HTML in math text", source: "x^{2}\\text{<b>hola</b>}", mustShowError: false },
  { id: "EN-SG-04 javascript href", source: "\\href{javascript:alert(1)}{x}", mustShowError: false },
  { id: "EN-SG-05 url macro", source: "\\url{http://example.com}", mustShowError: true },
  { id: "EN-SG-05 includegraphics macro", source: "\\includegraphics{x.png}", mustShowError: true },
  { id: "EN-SG-05 htmlClass macro", source: "\\htmlClass{a}{x}", mustShowError: true },
  { id: "EN-SG-05 htmlStyle macro", source: "\\htmlStyle{color:red}{x}", mustShowError: true },
  { id: "EN-SG-06 recursive def macro", source: "\\def\\a{\\a}\\a", mustShowError: true },
  { id: "EN-SG-07 newcommand macro", source: "\\newcommand{\\a}{\\a}\\a", mustShowError: true },
  { id: "EN-SG-07 let macro", source: "\\let\\a\\b", mustShowError: true },
  { id: "EN-SG-07 catcode macro", source: "\\catcode", mustShowError: true },
] as const;

for (const item of cases) {
  test(item.id + " is inert and does not hang the UI", async ({ page }) => {
    test.setTimeout(15_000);
    const probe = await installH2SecurityProbe(page);
    await page.goto("/");
    await calculateAndObserve(page, item.source, item.mustShowError);
    const snapshot = await probe.snapshot();
    expect(snapshot.observedRoots).toBeGreaterThan(1);
    expect(snapshot.hazards, JSON.stringify(snapshot)).toEqual([]);
    expect(probe.dialogs).toEqual([]);
    expect(probe.pageErrors).toEqual([]);
  });
}
