import { expect, test } from "@playwright/test";
type Page=import("@playwright/test").Page;

async function setInput(page:Page,value:string){
  const field=page.locator("math-field").first();
  await field.waitFor({state:"visible"});
  await field.evaluate((el,v)=>{
    const mf=el as HTMLElement&{setValue?:(x:string)=>void;value?:string};
    if(typeof mf.setValue==="function")mf.setValue(String(v));else mf.value=String(v);
    el.dispatchEvent(new InputEvent("input",{bubbles:true,inputType:"insertText",data:String(v)}));
  },value);
  await page.waitForTimeout(100);
}

async function readOutcome(page: Page): Promise<{kind:"result"|"error"; value:string}> {
  const alert=page.locator('[role="alert"]').last();
  const live=page.locator('[aria-live="polite"]').last();
  await expect.poll(async()=>{
    if(await alert.count()){const t=((await alert.textContent().catch(()=>""))??"").trim();if(t)return "error";}
    if(await live.count()){const t=((await live.textContent().catch(()=>""))??"").trim();if(t&&!/calculando/i.test(t)&&!/introduce una expresión/i.test(t))return "result";}
    return "pending";
  },{timeout:15000}).not.toBe("pending");
  if(await alert.count()){const t=((await alert.textContent().catch(()=>""))??"").trim();if(t)return{kind:"error",value:t};}
  const annotation=live.locator('annotation[encoding="application/x-tex"]').first();
  if(await annotation.count()){const t=((await annotation.textContent())??"").trim();if(t)return{kind:"result",value:t};}
  const rows=live.locator("table tbody tr");
  if(await rows.count()){
    const out:string[]=[];
    for(let i=0;i<await rows.count();i++){const cells=rows.nth(i).locator("td");const vals:string[]=[];for(let j=0;j<await cells.count();j++)vals.push(((await cells.nth(j).textContent())??"").trim());out.push(vals.join("&"));}
    return{kind:"result",value:"\\begin{pmatrix}"+out.join("\\\\")+"\\end{pmatrix}"};
  }
  const primary=live.locator(".a11y-scale-result-lg").first();
  if(await primary.count()){const t=((await primary.textContent())??"").trim();if(t)return{kind:"result",value:t};}
  return{kind:"result",value:((await live.textContent())??"").trim()};
}
async function submit(page:Page){
  await page.evaluate(()=>window.mathVirtualKeyboard?.hide());
  const button=page.getByRole("button",{name:"Evaluar",exact:true});
  await expect(button).toBeEnabled();
  await button.click();
  return readOutcome(page);
}
function canonical(v:string){
  return v.replace(/\\left|\\right|\\,/g,"").replace(/\\cdot/g,"").replace(/\s+/g,"").replace(/\{\}/g,"");
}
async function evaluateOnce(page:Page,input:string){
  await setInput(page,input);
  const out=await submit(page);
  expect(out.kind,input+" -> "+out.value).toBe("result");
  expect(out.value.trim()).not.toBe("");
  return out.value;
}

const TRIPLE_INPUTS=[
  "2+3",
  "\\frac{1}{2}+\\frac{1}{3}",
  "2^{10}",
  "\\sqrt{8}",
  "\\sin\\left(\\frac{\\pi}{6}\\right)",
  "\\cos\\left(\\frac{\\pi}{3}\\right)",
  "\\tan\\left(\\frac{\\pi}{4}\\right)",
  "e^{x}",
  "\\ln\\left(x\\right)",
  "x^{2}+2x+1",
  "(x+1)^{3}",
  "3x+2x",
  "\\sqrt{2}/2",
  "\\frac{3}{4}",
  "10^{-3}",
  "\\operatorname{sen}\\left(\\frac{\\pi}{6}\\right)",
  "C+1",
  "C_{1}+1",
  "1.267650600\\times10^{30}",
  "1\\,234\\,567",
];

test.describe("IN625 H1d reentrada avanzada",()=>{
  test("EN-RE-24 idempotencia triple sobre 20 entradas",async({page})=>{
    test.setTimeout(120000);
    await page.goto("./");
    for(const input of TRIPLE_INPUTS){
      const s1=await evaluateOnce(page,input);
      const s2=await evaluateOnce(page,s1);
      const s3=await evaluateOnce(page,s2);
      expect(canonical(s2),"S1="+s1+" S2="+s2+" input="+input).toBe(canonical(s1));
      expect(canonical(s3),"S2="+s2+" S3="+s3+" input="+input).toBe(canonical(s2));
      expect(s3).not.toMatch(/1\\cdot1\\cdot|\+0(?:$|[^0-9])/);
    }
  });

  test("EN-RE-25 equivalencia semántica en muestra de 20",async({page})=>{
    test.setTimeout(120000);
    await page.goto("./");
    for(const input of TRIPLE_INPUTS){
      const s1=await evaluateOnce(page,input);
      const s2=await evaluateOnce(page,s1);
      expect(s2.trim(),"reentrada vacía para "+input).not.toBe("");
      expect(canonical(s2),"reentrada estable para "+input).toBe(canonical(s1));
      // Comprobar puntos de referencia independientes para resultados numéricos.
      // No declarar equivalencia semántica universal basándose solo en salida no vacía.
      const anchors:Record<string,RegExp>={
        "2+3":/^5(?:\.0+)?$/,
        "\\frac{1}{2}+\\frac{1}{3}":/^(?:\\frac\{5\}\{6\}|0\.83{1,2}3*)$/i,
        "2^{10}":/^1024(?:\.0+)?$/,
        "\\frac{3}{4}":/^(?:\\frac\{3\}\{4\}|0\.75)$/,
        "10^{-3}":/^(?:\\frac\{1\}\{1000\}|0\.001)$/,
      };
      const expected=anchors[input];
      if(expected){
        expect(canonical(s1),"referencia inicial "+input).toMatch(expected);
        expect(canonical(s2),"referencia tras reentrada "+input).toMatch(expected);
      }
    }
  });

  test("EN-RE-26 formatos cruzados Lite/Plus son aceptados",async({page})=>{
    await page.goto("./");
    const foreign=[
      "\\ln\\left(x\\right)",
      "2\\sqrt{2}",
      "\\operatorname{asin}{\\left(\\frac{1}{2}\\right)}",
      "\\operatorname{atan}{\\left(1\\right)}",
      "\\begin{pmatrix}-2&1\\\\\\frac{3}{2}&-\\frac{1}{2}\\end{pmatrix}",
      "\\left(-\\infty,-2\\right)\\cup\\left(2,\\infty\\right)"
    ];
    for(const input of foreign){
      const out=await evaluateOnce(page,input);
      expect(out.trim()).not.toBe("");
    }
  });

  test("EN-RE-27 operatorname asin/atan reingresan",async({page})=>{
    await page.goto("./");
    const a=await evaluateOnce(page,"\\operatorname{asin}{\\left(\\frac{1}{2}\\right)}");
    expect(a.toLowerCase()).toMatch(/pi|asin|arcsin|0\.523|frac/);
    const a2=await evaluateOnce(page,a);
    const b=await evaluateOnce(page,"\\operatorname{atan}{\\left(1\\right)}");
    expect(b.toLowerCase()).toMatch(/pi|atan|arctan|0\.785|frac/);
    const b2=await evaluateOnce(page,b);
    expect(canonical(a2),"asin: salida inicial y reentrada").toBe(canonical(a));
    expect(canonical(b2),"atan: salida inicial y reentrada").toBe(canonical(b));
  });

  test("EN-RE-28 piecewise reingresa y preserva casos",async({page})=>{
    await page.goto("./");
    const input="\\begin{cases}x^{2}&x<0\\\\x&x\\geq0\\end{cases}";
    const s1=await evaluateOnce(page,input);
    expect(s1).toMatch(/cases|x/);
    const s2=await evaluateOnce(page,s1);
    expect(s2).toMatch(/cases|x/);
  });
});

// Syntax309 SY-P-23: UI must disclose the ambiguous ungrouped input, not silently assign b*c.
test("SY-P-23 muestra advertencia accesible sin modificar expresiones seguras", async ({ page }) => {
  await page.goto("./");
  const warning = page.getByRole("status", { name: "Convención de división ambigua" });
  await setInput(page, String.raw`\\frac{a}{bc}`);
  await expect(warning).toBeVisible();
  await expect(warning).toContainText("(a/b)*c");
  await expect(warning).toContainText("a/(b*c)");
  await setInput(page, "2+3");
  await expect(warning).toHaveCount(0);
});

// SY-P-23: show guidance only for ambiguous bare division, never for explicit grouping.
test("SY-P-23 no advierte en agrupaciones explícitas ni expresiones no relacionadas", async ({ page }) => {
  await page.goto("./");
  const warning = page.getByRole("status", { name: "Convención de división ambigua" });
  for (const input of ["(a/b)*c", "a/(b*c)", "2+3"]) {
    await setInput(page, input);
    await expect(warning, input).toHaveCount(0);
  }
  await setInput(page, "a/bc");
  await expect(warning).toBeVisible();
});

// SY-P-23: the advisory is informational; it must never rewrite the user's MathLive value.
test("SY-P-23 preserva la entrada original al mostrar la advertencia", async ({ page }) => {
  await page.goto("./");
  const value = String.raw`\frac{a}{bc}`;
  await setInput(page, value);
  await expect(page.getByRole("status", { name: "Convención de división ambigua" })).toBeVisible();
  const actual = await page.locator("math-field").first().evaluate(el => (el as HTMLElement & { value?: string }).value ?? "");
  expect(actual.replace(/\s+/g, ""), "La advertencia no debe reescribir a/bc como a/(b*c)").toBe(value);
});

// SY-P-23: MathLive editing must dismiss and restore the advisory without changing bc into b*c.
test("SY-P-23 transición de entrada ambigua a agrupación explícita y vuelta", async ({ page }) => {
  await page.goto("./");
  const warning = page.getByRole("status", { name: "Convención de división ambigua" });
  await setInput(page, "a/bc");
  await expect(warning).toBeVisible();
  await setInput(page, "a/(b*c)");
  await expect(warning).toHaveCount(0);
  await setInput(page, String.raw`\frac{a}{bc}`);
  await expect(warning).toBeVisible();
  await setInput(page, "(a/b)*c");
  await expect(warning).toHaveCount(0);
});

test("SY-P-23 advierte explícitamente sobre identificador compuesto bc sin reescribirlo", async ({ page }) => {
  await page.goto("./");
  await setInput(page, "a/bc");
  const warning = page.getByRole("status", { name: "Convención de división ambigua" });
  await expect(warning).toContainText("bc es una única variable");
  const input = page.locator("math-field").first();
  await expect.poll(async () => input.evaluate(el => (el as HTMLElement & {value?: string}).value ?? "")).toBe("a/bc");
  await setInput(page, "a/(b*c)");
  await expect(warning).toHaveCount(0);
});

test("SY-P-23 canal UI a resultado: agrupaciones explícitas no se confunden", async ({ page }) => {
  await page.goto("./");
  const warning = page.getByRole("status", { name: "Convención de división ambigua" });
  for (const [expression, expected] of [["(12/3)*2", "8"], ["12/(3*2)", "2"]] as const) {
    await setInput(page, expression);
    await expect(warning).toHaveCount(0);
    const actual = await submit(page);
    expect(actual.kind, expression).toBe("result");
    expect(canonical(actual.value), expression + " => " + actual.value).toContain(expected);
  }
});

test("SY-P-23 UI: bc compuesto preservado hasta endpoint", async ({ page }) => {
  await page.goto("./");
  const substitutions = page.locator("details").filter({ hasText: "Sustituciones" });
  await substitutions.locator("summary").click();
  for (const [name, value] of [["a", "12"], ["bc", "6"], ["b", "3"], ["c", "2"]] as const) {
    await page.getByRole("button", { name: "Añadir sustitución" }).click();
    const rowIndex = await page.getByRole("textbox", { name: /^Nombre de la variable/ }).count();
    await page.getByRole("textbox", { name: `Nombre de la variable ${rowIndex}` }).fill(name);
    await page.getByRole("textbox", { name: `Valor de la variable ${rowIndex}` }).fill(value);
  }
  const warning = page.getByRole("status", { name: "Convención de división ambigua" });
  await setInput(page, "a/bc");
  await expect(warning).toBeVisible();
  const requestPromise = page.waitForRequest(request => request.url().includes("/evaluate") && request.method() === "POST");
  const namedPromise = submit(page);
  const outbound = await requestPromise;
  const payload = outbound.postDataJSON() as { expression?: string; substitutions?: Record<string, string> };
  console.log("SY_P_23_OUTBOUND", JSON.stringify({
    mathliveValue: await page.locator("math-field").first().evaluate(el => (el as HTMLElement & { value?: string }).value ?? ""),
    expression: payload.expression,
    substitutions: payload.substitutions,
  }));
  expect(payload.substitutions, "UI must transmit both bc and separate b,c").toMatchObject({a: "12", bc: "6", b: "3", c: "2"});
  const named = await namedPromise;
  expect(named.kind).toBe("result");
  expect(canonical(named.value)).toMatch(/^2(?:\\.0+)?$/);
});

test("SY-P-23 UI: agrupación (a/b)*c sigue dando 8 con sustituciones", async ({ page }) => {
  await page.goto("./");
  const advanced = page.locator("details").filter({ hasText: "Sustituciones" });
  await advanced.locator("summary").click();
  for (const [name, value] of [["a", "12"], ["b", "3"], ["c", "2"], ["bc", "6"]] as const) {
    await page.getByRole("button", { name: "Añadir sustitución" }).click();
    const count = await page.getByRole("textbox", { name: /^Nombre de la variable/ }).count();
    await page.getByRole("textbox", { name: `Nombre de la variable ${count}` }).fill(name);
    await page.getByRole("textbox", { name: `Valor de la variable ${count}` }).fill(value);
  }
  await setInput(page, "(a/b)*c");
  await expect(page.getByRole("status", { name: "Convención de división ambigua" })).toHaveCount(0);
  const result = await submit(page);
  expect(result.kind).toBe("result");
  expect(canonical(result.value)).toMatch(/^8(?:\\.0+)?$/);
});

test("SY-P-23: bc definida conserva lectura con b y c simultáneos", async ({ page }) => {
  await page.goto("./");
  const substitutions = page.locator("details").filter({ hasText: "Sustituciones" });
  await substitutions.locator("summary").click();
  for (const [name, value] of [["a", "12"], ["bc", "6"], ["b", "3"], ["c", "2"]] as const) {
    await page.getByRole("button", { name: "Añadir sustitución" }).click();
    const index = await page.getByRole("textbox", { name: /^Nombre de la variable/ }).count();
    await page.getByRole("textbox", { name: `Nombre de la variable ${index}` }).fill(name);
    await page.getByRole("textbox", { name: `Valor de la variable ${index}` }).fill(value);
  }
  await setInput(page, "a/bc");
  const requestPromise = page.waitForRequest(req => req.url().includes("/evaluate") && req.method() === "POST");
  const resultPromise = submit(page);
  const request = await requestPromise;
  const payload = request.postDataJSON() as { expression: string; substitutions: Record<string, string> };
  expect(payload.expression).toBe("a/bc");
  expect(payload.substitutions).toMatchObject({ a: "12", bc: "6", b: "3", c: "2" });
  const result = await resultPromise;
  expect(result.kind).toBe("result");
  expect(canonical(result.value)).toMatch(/^2(?:\\.0+)?$/);
});

test("SY-P-23 LaTeX fraction: el payload conserva denominador bc definido", async ({ page }) => {
  await page.goto("./");
  const substitutions = page.locator("details").filter({ hasText: "Sustituciones" });
  await substitutions.locator("summary").click();
  for (const [name, value] of [["a", "12"], ["bc", "6"], ["b", "3"], ["c", "2"]] as const) {
    await page.getByRole("button", { name: "Añadir sustitución" }).click();
    const index = await page.getByRole("textbox", { name: /^Nombre de la variable/ }).count();
    await page.getByRole("textbox", { name: `Nombre de la variable ${index}` }).fill(name);
    await page.getByRole("textbox", { name: `Valor de la variable ${index}` }).fill(value);
  }
  await setInput(page, String.raw`\frac{a}{bc}`);
  await expect(page.getByRole("status", { name: "Convención de división ambigua" })).toBeVisible();
  const pending = page.waitForRequest(req => req.url().includes("/evaluate") && req.method() === "POST");
  const evaluation = submit(page);
  const request = await pending;
  const payload = request.postDataJSON() as { expression: string; substitutions: Record<string, string> };
  expect(payload.expression, "LaTeX denominator bc must retain compound variable").toBe("a/bc");
  expect(payload.substitutions).toMatchObject({ a: "12", bc: "6", b: "3", c: "2" });
  const result = await evaluation;
  expect(result.kind).toBe("result");
  expect(canonical(result.value)).toMatch(/^2(?:\\.0+)?$/);
});


test("SY-P-23 UI: agrupaciones decimales explícitas preservan resultados", async ({ page }) => {
  await page.goto("./");
  const warning = page.getByRole("status", { name: "Convención de división ambigua" });
  for (const [expression, decimal, exactLatex] of [
    ["(9/3)*2.5", "7.5", String.raw`\frac{15}{2}`],
    ["9/(3*2.5)", "1.2", String.raw`\frac{6}{5}`],
  ] as const) {
    await setInput(page, expression);
    await expect(warning).toHaveCount(0);
    const result = await submit(page);
    expect(result.kind, expression).toBe("result");
    const actual = canonical(result.value);
    const decimalPattern = new RegExp("^" + decimal.replace(".", "\\.") + "(?:\\.0+)?$");
    expect(decimalPattern.test(actual) || actual === exactLatex,
      expression + " => " + result.value + " must equal " + decimal).toBe(true);
  }
});

test("SY-P-23 UI: agrupaciones decimales con paréntesis redundantes", async ({ page }) => {
  await page.goto("./");
  const warning = page.getByRole("status", { name: "Convención de división ambigua" });
  for (const [expression, decimal, exact] of [
    ["((9)/(3*2.5))", "1.2", String.raw`\frac{6}{5}`],
    ["(((9)/(3)))*2.5", "7.5", String.raw`\frac{15}{2}`],
  ] as const) {
    await setInput(page, expression);
    await expect(warning).toHaveCount(0);
    const result = await submit(page);
    expect(result.kind, expression).toBe("result");
    const value = canonical(result.value);
    const pattern = new RegExp("^" + decimal.replace(".", "\\.") + "(?:\\.0+)?$");
    expect(pattern.test(value) || value === exact, expression + " => " + result.value).toBe(true);
  }
});

test("SY-P-23 UI: entrada ambigua sin bc definida exige desambiguación", async ({ page }) => {
  await page.goto("./");
  for (const input of ["a/bc", String.raw`\frac{a}{bc}`]) {
    await setInput(page, input);
    await expect(page.getByRole("status", { name: "Convención de división ambigua" })).toBeVisible();
    let requests = 0;
    const onRequest = (req: import("@playwright/test").Request) => {
      if (req.method() === "POST" && req.url().includes("/evaluate")) requests++;
    };
    page.on("request", onRequest);
    await page.getByRole("button", { name: "Evaluar", exact: true }).click();
    await expect(page.getByText("SY-P-23: define la variable bc o escribe (a/b)*c o a/(b*c) antes de calcular.")).toBeVisible();
    expect(requests, input).toBe(0);
    page.off("request", onRequest);
  }
});

test("SY-P-23 UI: después del bloqueo se puede calcular una agrupación explícita", async ({ page }) => {
  await page.goto("./");
  await setInput(page, "a/bc");
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  await expect(page.getByText("SY-P-23: define la variable bc o escribe (a/b)*c o a/(b*c) antes de calcular.")).toBeVisible();
  await setInput(page, "(12/3)*2");
  await expect(page.getByRole("status", { name: "Convención de división ambigua" })).toHaveCount(0);
  const result = await submit(page);
  expect(result.kind).toBe("result");
  expect(canonical(result.value)).toMatch(/^8(?:\.0+)?$/);
});

test("SY-P-23 UI: a/bc entre paréntesis también requiere desambiguación", async ({ page }) => {
  await page.goto("./");
  await setInput(page, "(a/bc)");
  let requests = 0;
  const track = (req: import("@playwright/test").Request) => {
    if (req.method() === "POST" && req.url().includes("/evaluate")) requests++;
  };
  page.on("request", track);
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  await expect(page.getByText("SY-P-23: define la variable bc o escribe (a/b)*c o a/(b*c) antes de calcular.")).toBeVisible();
  expect(requests).toBe(0);
  page.off("request", track);
});

test("SY-P-23 UI: paréntesis exteriores permiten bc explícitamente definida", async ({ page }) => {
  await page.goto("./");
  const details = page.locator("details").filter({ hasText: "Sustituciones" });
  await details.locator("summary").click();
  for (const [name, value] of [["a", "12"], ["bc", "6"], ["b", "3"], ["c", "2"]] as const) {
    await page.getByRole("button", { name: "Añadir sustitución" }).click();
    const index = await page.getByRole("textbox", { name: /^Nombre de la variable/ }).count();
    await page.getByRole("textbox", { name: `Nombre de la variable ${index}` }).fill(name);
    await page.getByRole("textbox", { name: `Valor de la variable ${index}` }).fill(value);
  }
  await setInput(page, "(a/bc)");
  const outgoing = page.waitForRequest(req => req.url().includes("/evaluate") && req.method() === "POST");
  const pending = submit(page);
  const request = await outgoing;
  const payload = request.postDataJSON() as { expression: string; substitutions: Record<string, string> };
  expect(payload.expression, "La agrupación externa debe preservar bc como identificador compuesto").toBe("a/bc");
  expect(payload.substitutions).toMatchObject({ a: "12", bc: "6", b: "3", c: "2" });
  const outcome = await pending;
  expect(outcome.kind).toBe("result");
  expect(canonical(outcome.value)).toMatch(/^2(?:\.0+)?$/);
});


test("SY-P-23: paréntesis redundantes sin bc definida bloquean envío", async ({ page }) => {
  await page.goto("./");
  for (const expression of ["((a/bc))", "(((a/bc)))"]) {
    await setInput(page, expression);
    let requests = 0;
    const track = (req: import("@playwright/test").Request) => {
      if (req.method() === "POST" && req.url().includes("/evaluate")) requests++;
    };
    page.on("request", track);
    await page.getByRole("button", { name: "Evaluar", exact: true }).click();
    await expect(page.getByText("SY-P-23: define la variable bc o escribe (a/b)*c o a/(b*c) antes de calcular.")).toBeVisible();
    expect(requests, expression).toBe(0);
    page.off("request", track);
  }
});

test("SY-P-23: paréntesis redundantes conservan bc definida", async ({ page }) => {
  await page.goto("./");
  const details = page.locator("details").filter({ hasText: "Sustituciones" });
  await details.locator("summary").click();
  for (const [name, value] of [["a", "12"], ["bc", "6"], ["b", "3"], ["c", "2"]] as const) {
    await page.getByRole("button", { name: "Añadir sustitución" }).click();
    const index = await page.getByRole("textbox", { name: /^Nombre de la variable/ }).count();
    await page.getByRole("textbox", { name: "Nombre de la variable " + index }).fill(name);
    await page.getByRole("textbox", { name: "Valor de la variable " + index }).fill(value);
  }
  for (const expression of ["((a/bc))", "(((a/bc)))"]) {
    await setInput(page, expression);
    const outgoing = page.waitForRequest(req => req.url().includes("/evaluate") && req.method() === "POST");
    const pending = submit(page);
    const payload = (await outgoing).postDataJSON() as { expression: string; substitutions: Record<string, string> };
    expect(payload.expression, expression).toBe("a/bc");
    expect(payload.substitutions).toMatchObject({ a: "12", bc: "6", b: "3", c: "2" });
    const outcome = await pending;
    expect(outcome.kind).toBe("result");
    expect(canonical(outcome.value)).toMatch(/^2(?:\.0+)?$/);
  }
});


test("SY-P-23: fracción LaTeX con paréntesis exteriores requiere bc definida", async ({ page }) => {
  await page.goto("./");
  const expression = String.raw`(\frac{a}{bc})`;
  await setInput(page, expression);
  let requests = 0;
  const track = (req: import("@playwright/test").Request) => {
    if (req.method() === "POST" && req.url().includes("/evaluate")) requests++;
  };
  page.on("request", track);
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  await expect(page.getByText("SY-P-23: define la variable bc o escribe (a/b)*c o a/(b*c) antes de calcular.")).toBeVisible();
  expect(requests).toBe(0);
  page.off("request", track);
});

test("SY-P-23: fracción LaTeX parentetizada preserva bc compuesta definida", async ({ page }) => {
  await page.goto("./");
  const details = page.locator("details").filter({ hasText: "Sustituciones" });
  await details.locator("summary").click();
  for (const [name, value] of [["a", "12"], ["bc", "6"], ["b", "3"], ["c", "2"]] as const) {
    await page.getByRole("button", { name: "Añadir sustitución" }).click();
    const index = await page.getByRole("textbox", { name: /^Nombre de la variable/ }).count();
    await page.getByRole("textbox", { name: "Nombre de la variable " + index }).fill(name);
    await page.getByRole("textbox", { name: "Valor de la variable " + index }).fill(value);
  }
  await setInput(page, String.raw`(\frac{a}{bc})`);
  const outgoing = page.waitForRequest(req => req.url().includes("/evaluate") && req.method() === "POST");
  const pending = submit(page);
  const payload = (await outgoing).postDataJSON() as { expression: string; substitutions: Record<string, string> };
  expect(payload.expression).toBe("a/bc");
  expect(payload.substitutions).toMatchObject({ a: "12", bc: "6", b: "3", c: "2" });
  const outcome = await pending;
  expect(outcome.kind).toBe("result");
  expect(canonical(outcome.value)).toMatch(/^2(?:\.0+)?$/);
});


test("SY-P-23: fracción LaTeX con paréntesis redundantes bloquea o conserva bc", async ({ page }) => {
  await page.goto("./");
  const expressions = [String.raw`((\frac{a}{bc}))`, String.raw`(((\frac{a}{bc})))`];
  for (const expression of expressions) {
    await setInput(page, expression);
    const requests: string[] = [];
    const track = (req: import("@playwright/test").Request) => {
      if (req.url().includes("/evaluate") && req.method() === "POST") requests.push(req.url());
    };
    page.on("request", track);
    await page.getByRole("button", { name: "Evaluar", exact: true }).click();
    await expect(page.getByText("SY-P-23: define la variable bc o escribe (a/b)*c o a/(b*c) antes de calcular.")).toBeVisible();
    expect(requests, expression).toHaveLength(0);
    page.off("request", track);
  }

  const details = page.locator("details").filter({ hasText: "Sustituciones" });
  await details.locator("summary").click();
  for (const [name, value] of [["a", "12"], ["bc", "6"], ["b", "3"], ["c", "2"]] as const) {
    await page.getByRole("button", { name: "Añadir sustitución" }).click();
    const index = await page.getByRole("textbox", { name: /^Nombre de la variable/ }).count();
    await page.getByRole("textbox", { name: "Nombre de la variable " + index }).fill(name);
    await page.getByRole("textbox", { name: "Valor de la variable " + index }).fill(value);
  }
  for (const expression of expressions) {
    await setInput(page, expression);
    const outbound = page.waitForRequest(req => req.url().includes("/evaluate") && req.method() === "POST");
    const pending = submit(page);
    const body = (await outbound).postDataJSON() as { expression: string; substitutions: Record<string, string> };
    expect(body.expression, expression).toBe("a/bc");
    expect(body.substitutions).toMatchObject({ a: "12", bc: "6", b: "3", c: "2" });
    const outcome = await pending;
    expect(outcome.kind).toBe("result");
    expect(canonical(outcome.value), expression).toMatch(/^2(?:\.0+)?$/);
  }
});


test("SY-P-23: agrupación explícita no se confunde con bc definida", async ({ page }) => {
  await page.goto("./");
  const details = page.locator("details").filter({ hasText: "Sustituciones" });
  await details.locator("summary").click();
  for (const [name, value] of [["a", "12"], ["bc", "6"], ["b", "3"], ["c", "2"]] as const) {
    await page.getByRole("button", { name: "Añadir sustitución" }).click();
    const index = await page.getByRole("textbox", { name: /^Nombre de la variable/ }).count();
    await page.getByRole("textbox", { name: "Nombre de la variable " + index }).fill(name);
    await page.getByRole("textbox", { name: "Valor de la variable " + index }).fill(value);
  }
  for (const [expression, expected] of [["((a/b)*c)", "8"], ["((a/(b*c)))", "2"]] as const) {
    await setInput(page, expression);
    await expect(page.getByRole("status", { name: "Convención de división ambigua" })).toHaveCount(0);
    const outbound = page.waitForRequest(req => req.url().includes("/evaluate") && req.method() === "POST");
    const pending = submit(page);
    const payload = (await outbound).postDataJSON() as { expression: string; substitutions: Record<string, string> };
    expect(payload.expression, expression).not.toBe("a/bc");
    expect(payload.substitutions).toMatchObject({ a: "12", bc: "6", b: "3", c: "2" });
    const outcome = await pending;
    expect(outcome.kind).toBe("result");
    expect(canonical(outcome.value), expression).toBe(expected);
  }
});


test("SY-P-23: paréntesis exteriores no ocultan multiplicación explícita", async ({ page }) => {
  await page.goto("./");
  const cases = [
    ["(12/3)*2", "8"],
    ["((12/3))*2", "8"],
    ["12/((3*2))", "2"],
    ["((12/(3*2)))", "2"],
  ] as const;
  for (const [expression, expected] of cases) {
    await setInput(page, expression);
    await expect(page.getByRole("status", { name: "Convención de división ambigua" })).toHaveCount(0);
    const output = await submit(page);
    expect(output.kind, expression).toBe("result");
    expect(Number(canonical(output.value)), expression).toBe(Number(expected));
  }
});


test("SY-P-23: las fracciones numéricas LaTeX con paréntesis no activan ambigüedad", async ({ page }) => {
  await page.goto("./");
  for (const [expression, expected] of [
    [String.raw`(\frac{12}{3})*2`, 8],
    [String.raw`(\frac{12}{3*2})`, 2],
  ] as const) {
    await setInput(page, expression);
    await expect(page.getByRole("status", { name: "Convención de división ambigua" })).toHaveCount(0);
    const outcome = await submit(page);
    expect(outcome.kind, expression).toBe("result");
    expect(Number(canonical(outcome.value)), expression).toBe(expected);
  }
});


test("SY-P-23 Plus: aviso con paréntesis preserva entrada y se elimina al desambiguar", async ({ page }) => {
  await page.goto("./");
  const warning = page.getByRole("status", { name: "Convención de división ambigua" });
  const field = page.locator("math-field").first();
  for (const expression of ["(a/bc)", "((a/bc))", String.raw`(\frac{a}{bc})`]) {
    await setInput(page, expression);
    await expect(warning, expression).toBeVisible();
    await expect(warning).toContainText("(a/b)*c");
    await expect(warning).toContainText("a/(b*c)");
    expect(await field.evaluate(el => (el as HTMLElement & {value?: string}).value), expression).toBe(expression);
  }
  for (const expression of ["(a/b)*c", "a/(b*c)", "((a/(b*c)))"]) {
    await setInput(page, expression);
    await expect(warning, expression).toHaveCount(0);
  }
});


test("SY-P-23: el aviso detecta a/bc dentro de expresiones mayores sin alterar MathLive", async ({ page }) => {
  await page.goto("./");
  const warning = page.getByRole("status", { name: "Convención de división ambigua" });
  const field = page.locator("math-field").first();
  for (const expression of ["1+a/bc", "2*(a/bc)", "a/bc+3"]) {
    await setInput(page, expression);
    await expect(warning, expression).toBeVisible();
    await expect(warning).toContainText("(a/b)*c");
    await expect(warning).toContainText("a/(b*c)");
    expect(await field.evaluate(el => (el as HTMLElement & { value?: string }).value), expression).toBe(expression);
  }
  for (const expression of ["1+(a/b)*c", "2*(a/(b*c))", "a/(b*c)+3"]) {
    await setInput(page, expression);
    await expect(warning, expression).toHaveCount(0);
  }
});


test("SY-P-23 Plus: entradas extendidas sin bc definida nunca envían POST", async ({ page }) => {
  await page.goto("./");
  for (const expression of ["1+a/bc", "2*(a/bc)", "a/bc+3"]) {
    await setInput(page, expression);
    const requests: string[] = [];
    const track = (req: import("@playwright/test").Request) => {
      if (req.method() === "POST" && req.url().includes("/evaluate")) requests.push(req.url());
    };
    page.on("request", track);
    await page.getByRole("button", { name: "Evaluar", exact: true }).click();
    await expect(page.getByText("SY-P-23: define la variable bc o escribe (a/b)*c o a/(b*c) antes de calcular.")).toBeVisible();
    expect(requests, expression).toHaveLength(0);
    page.off("request", track);
  }
});


test("SY-P-23 Plus: identificadores vecinos no disparan bloqueo específico de a/bc", async ({ page }) => {
  await page.goto("./");
  const warning = page.getByRole("status", { name: "Convención de división ambigua" });
  for (const expression of ["aa/bc", "a/bcd", "xa/bc", "a/bcx"]) {
    await setInput(page, expression);
    await expect(warning, expression).toHaveCount(0);
    await page.getByRole("button", { name: "Evaluar", exact: true }).click();
    await expect(page.getByText("SY-P-23: define la variable bc o escribe (a/b)*c o a/(b*c) antes de calcular.")).toHaveCount(0);
  }
});

 
// SY-P-23: a/bc is a whole-token policy, including inside LaTeX fractions and larger expressions.
// Neighboring identifiers must never be rewritten or rejected by the bc-specific guard.
test("SY-P-23 Plus: límites de identificador dentro de fracciones LaTeX y subexpresiones", async ({ page }) => {
  await page.goto("./");
  const warning = page.getByRole("status", { name: "Convención de división ambigua" });
  const blocked = page.getByText("SY-P-23: define la variable bc o escribe (a/b)*c o a/(b*c) antes de calcular.");
  const field = page.locator("math-field").first();
  for (const expression of [
    String.raw`\\frac{aa}{bc}`,
    String.raw`\\frac{a}{bcd}`,
    String.raw`\\frac{xa}{bc}`,
    String.raw`\\frac{a}{bcx}`,
    "1+aa/bc",
    "2*(a/bcd)",
    "xa/bc+3",
    "3*(a/bcx)",
  ]) {
    await setInput(page, expression);
    await expect(warning, expression).toHaveCount(0);
    expect(await field.evaluate(el => (el as HTMLElement & { value?: string }).value), expression).toBe(expression);
    await page.getByRole("button", { name: "Evaluar", exact: true }).click();
    await expect(blocked, expression).toHaveCount(0);
  }
});


test("SY-P-23 Plus: fracciones LaTeX numéricas compuestas conservan evaluación explícita", async ({ page }) => {
  await page.goto("./");
  const warning = page.getByRole("status", { name: "Convención de división ambigua" });
  for (const [expression, expected] of [
    [String.raw`1+\frac{12}{3*2}`, 3],
    [String.raw`2*(\frac{12}{3})`, 8],
    [String.raw`\frac{12}{3*2}+3`, 5],
    [String.raw`(\frac{12}{3})*2+1`, 9],
  ] as const) {
    await setInput(page, expression);
    await expect(warning, expression).toHaveCount(0);
    const output = await submit(page);
    expect(output.kind, expression).toBe("result");
    const normalized = canonical(output.value);
    const fraction = normalized.match(/^\\\\(?:d?frac)\\{(-?\\d+)\\}\\{(-?\\d+)\\}$/);
    const actual = fraction ? Number(fraction[1]) / Number(fraction[2]) : Number(normalized);
    expect(actual, `${expression} produced ${JSON.stringify(output.value)} (canonical ${JSON.stringify(normalized)})`).toBe(expected);
  }
});

test("SY-P-23 Plus: fracciones compuestas numéricas rechazan falsa ambigüedad y permiten repetir evaluación", async ({ page }) => {
  await page.goto("./");
  const warning = page.getByRole("status", { name: "Convención de división ambigua" });
  for (const expression of [
    String.raw`\\frac{12}{3*2}+3`,
    String.raw`2*(\\frac{12}{3})`,
  ]) {
    await setInput(page, expression);
    await expect(warning, expression).toHaveCount(0);
    const first = await submit(page);
    expect(first.kind, expression).toBe("result");
    const second = await submit(page);
    expect(second.kind, expression).toBe("result");
    expect(canonical(second.value), expression).toBe(canonical(first.value));
  }
});

// SY-P-24/25: these original fixture inputs are products, not SY-P-23 division.
// This UI check verifies guard scope and MathLive preservation, not numeric parser semantics.
test("SY-P-24/25: xy y xyz no activan bloqueo de división", async ({ page }) => {
  await page.goto("./");
  const warning = page.getByRole("status", { name: "Convención de división ambigua" });
  const field = page.locator("math-field").first();
  for (const expression of ["xy", "xyz"]) {
    await setInput(page, expression);
    await expect(warning, expression).toHaveCount(0);
    const stored = await field.evaluate(el => (el as HTMLElement & { value?: string }).value ?? "");
    expect(stored, expression + " must retain original MathLive text").toBe(expression);
  }
  await setInput(page, "a/bc");
  await expect(warning).toBeVisible();
});

// Fixture provenance: SY-P-24/25 must retain the official product interpretation.
// The UI guard test above is deliberately not counted as numeric substitution proof.
test("SY-P-24/25: los casos originales exigen productos de variables", async () => {
  const fs = await import("node:fs/promises");
  const path = await import("node:path");
  const source = await fs.readFile(path.resolve(process.cwd(), "../qa/certification/syntax309_sy_p_cases.jsonl"), "utf8");
  const rows = source.trim().split(/\r?\n/).map(line => JSON.parse(line) as {id:string; entrada:string; operacion:string; esperado:string});
  for (const [id, input, expected] of [
    ["SY-P-24", "xy", String.raw`x\cdot y`],
    ["SY-P-25", "xyz", String.raw`x\cdot y\cdot z`],
  ]) {
    const matches = rows.filter(row => row.id === id);
    expect(matches, id + " must have exactly one original fixture row").toHaveLength(1);
    expect(matches[0].entrada).toBe(input);
    expect(matches[0].operacion).toBe("interpretacion");
    expect(matches[0].esperado).toBe(expected);
  }
});
