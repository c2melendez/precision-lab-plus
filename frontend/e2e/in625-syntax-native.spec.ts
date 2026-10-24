import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import {installScriptProbe,verifyInsertionControl} from "./scriptInertProbe";
import {installFileProbe,verifyFileProbeControl} from "./fileAccessProbe";
import { expect, test, type Locator, type Page } from "@playwright/test";

// Native integration: real MathLive, React handlers, HTTP API and rendered result.
// No route interception, mocked converter, direct API substitution or silent skip.
const cases = readFileSync(new URL("../../qa/certification/syntax309_cases.jsonl", import.meta.url), "utf8")
  .trim().split("\n").map((line) => JSON.parse(line) as { id: string; entrada: string });
const fixture = (id: string) => {
  const row = cases.find((candidate) => candidate.id === id);
  if (!row) throw new Error(`Missing canonical fixture ${id}`);
  return row.entrada;
};

async function enter(field: Locator, source: string) {
  await field.evaluate((element, value) => {
    const mathfield = element as HTMLElement & { setValue(value: string): void };
    mathfield.setValue(value);
    element.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: value }));
  }, source);
  // Ingestion is evidence: erasing a malformed source must fail this test.
  await expect.poll(() => field.evaluate((element) =>
    (element as HTMLElement & { value: string }).value)).toBe(source);
}

async function evaluate(page: Page, field: Locator, source: string, expected: number, backendExpression = source) {
  await enter(field, source);
  const responsePromise = page.waitForResponse((response) =>
    response.url().endsWith("/api/v1/evaluate") && response.request().method() === "POST");
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  const response = await responsePromise;
  expect(response.status()).toBe(200);
  expect(response.request().postDataJSON().expression).toBe(backendExpression);
  const body = await response.json();
  expect(body.success).toBe(true);
  expect(body.result_approx).toBe(expected);
  expect(body.request_id).toBeTruthy();
  // KaTeX renders the mathematical minus as U+2212; retain the exact value.
  await expect.poll(async () => (await page.locator('[aria-live="polite"] .a11y-scale-result-lg .katex-html').last().textContent())?.replace(/−/g, "-")).toBe(String(expected));
  await expect(page.getByRole("alert")).toHaveCount(0);
  expect(body.result_latex).toBe(String(expected));
  return {requestId: body.request_id as string, reentry: body.result_latex as string};
}

test("SY-R-13 native original cube-root binding, controls and HTTP reentry", async ({ page }, testInfo) => {
  const pageErrors: string[] = [];
  const requests: Array<{ url: string; body: unknown }> = [];
  const evidence: Array<{ source: string; expected: number; requestId: string; reentry: string }> = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("request", (request) => {
    if (request.url().includes("/api/v1/") && request.method() === "POST") {
      requests.push({ url: request.url(), body: request.postDataJSON() });
    }
  });
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const canonical = fixture("SY-R-13");
  expect(canonical).toBe(String.raw`\sqrt[3]{x}\ \text{con}\ x=27`);
  const controls = [
    { source: canonical, expected: 3, backend: "((x)**(1/(3))) con x=(27)" },
    { source: String.raw`\sqrt[3]{x}\ \text{con}\ x=8`, expected: 2, backend: "((x)**(1/(3))) con x=(8)" },
    { source: String.raw`\sqrt[3]{y}\ \text{con}\ y=64`, expected: 4, backend: "((y)**(1/(3))) con y=(64)" },
  ];
  for (const { source, expected, backend } of controls) {
    const first = await evaluate(page, field, source, expected, backend);
    const second = await evaluate(page, field, first.reentry, expected);
    expect(second.requestId).not.toBe(first.requestId);
    evidence.push({ source, expected, ...first }, { source: first.reentry, expected, ...second });
  }
  await evaluate(page, field, "2+3", 5);
  expect(requests).toHaveLength(7);
  expect(requests.every((request) => request.url.endsWith("/api/v1/evaluate"))).toBe(true);
  expect(new Set(evidence.map((item) => item.requestId)).size).toBe(6);
  expect(pageErrors).toEqual([]);
  await testInfo.attach("SY-R-13-native-http-evidence", {
    body: JSON.stringify({ canonical, project: testInfo.project.name, requests, evidence, pageErrors }, null, 2),
    contentType: "application/json",
  });
});

test("SY-R-14 native original absolute value, signed controls and HTTP reentry", async ({ page }, testInfo) => {
  const pageErrors: string[] = [];
  const requests: Array<{ url: string; body: unknown }> = [];
  const evidence: Array<{ source: string; expected: number; requestId: string; reentry: string }> = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("request", (request) => {
    if (request.url().includes("/api/v1/") && request.method() === "POST") {
      requests.push({ url: request.url(), body: request.postDataJSON() });
    }
  });
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const canonical = fixture("SY-R-14");
  expect(canonical).toBe(String.raw`\left\lvert x\right\rvert\ \text{con}\ x=-4`);
  const controls = [
    // The existing typed-bars UI resolves the declared scalar, retaining abs
    // for real backend evaluation. The input itself remains the full fixture.
    { source: canonical, expected: 4, backend: "abs(-4)" },
    { source: String.raw`\left\lvert x\right\rvert+x\ \text{con}\ x=-4`, expected: 0, backend: "(abs(x)+x) con x=(-4)" },
    { source: String.raw`\left\lvert x\right\rvert+x\ \text{con}\ x=4`, expected: 8, backend: "(abs(x)+x) con x=(4)" },
    { source: String.raw`\left\lvert y\right\rvert\ \text{con}\ y=-7`, expected: 7, backend: "abs(-7)" },
  ];
  for (const { source, expected, backend } of controls) {
    const first = await evaluate(page, field, source, expected, backend);
    const second = await evaluate(page, field, first.reentry, expected);
    expect(second.requestId).not.toBe(first.requestId);
    evidence.push({ source, expected, ...first }, { source: first.reentry, expected, ...second });
  }
  await evaluate(page, field, "2+3", 5);
  expect(requests).toHaveLength(9);
  expect(requests.every((request) => request.url.endsWith("/api/v1/evaluate"))).toBe(true);
  expect(new Set(evidence.map((item) => item.requestId)).size).toBe(8);
  expect(pageErrors).toEqual([]);
  await testInfo.attach("SY-R-14-native-http-evidence", {
    body: JSON.stringify({ canonical, project: testInfo.project.name, requests, evidence, pageErrors }, null, 2),
    contentType: "application/json",
  });
});

test("SY-X-05 native30 grouping levels, scalar controls and HTTP reentry", async ({ page }, testInfo) => {
  const errors: string[] = [];
  const sources: Array<{ source: string; requestId: string; reentry: string }> = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const canonical = fixture("SY-X-05");
  expect(canonical).toBe(String.raw`\underbrace{(\cdots((1))\cdots)}_{30\text{ niveles}}`);
  for (const [inner, expected] of [["1", 1], ["7", 7], ["2+3", 5]] as const) {
    const source = "(".repeat(30) + inner + ")".repeat(30);
    expect(source.length).toBe(60 + inner.length);
    expect(source.match(/\(/g)).toHaveLength(30);
    expect(source.match(/\)/g)).toHaveLength(30);
    // evaluate verifies exact ingestion AND the unflattened HTTP request.
    const first = await evaluate(page, field, source, expected);
    const second = await evaluate(page, field, first.reentry, expected);
    expect(second.requestId).not.toBe(first.requestId);
    sources.push({ source, ...first }, { source: first.reentry, ...second });
  }
  await evaluate(page, field, "2+3", 5);
  expect(new Set(sources.map((item) => item.requestId)).size).toBe(6);
  expect(errors).toEqual([]);
  await testInfo.attach("SY-X-05-native-http-evidence", {
    body: JSON.stringify({ canonical, project: testInfo.project.name, sources, errors }, null, 2),
    contentType: "application/json",
  });
});

test("SY-X-06 native10000-character source, readable HTTP length rejection and recovery", async ({ page }, testInfo) => {
  testInfo.setTimeout(90000);
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const canonical = fixture("SY-X-06");
  expect(canonical).toBe(String.raw`\text{(entrada de 10 000 caracteres)}`);
  const source = "1+".repeat(4999) + "11";
  expect(source).toHaveLength(10000);
  await enter(field, source);
  const responsePromise = page.waitForResponse((response) => response.url().endsWith("/api/v1/evaluate") && response.request().method() === "POST");
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  const response = await responsePromise;
  expect(response.request().postDataJSON().expression).toBe(source);
  expect(response.status()).toBe(422);
  const rejected = await response.json();
  expect(rejected.success).toBe(false);
  expect(rejected.error_code).toBe("VALIDATION_ERROR");
  expect(rejected.result_latex).toBeNull();
  const resultAlert = page.locator('form[aria-labelledby="basic-mode-heading"]').getByRole("alert");
  await expect(resultAlert).toContainText("VALIDATION_ERROR");
  await expect(resultAlert).toContainText("Entrada demasiado larga: el máximo permitido es de 500 caracteres.");
  const recovered = await evaluate(page, field, "2+3", 5);
  const reentered = await evaluate(page, field, recovered.reentry, 5);
  expect(new Set([rejected.request_id, recovered.requestId, reentered.requestId]).size).toBe(3);
  expect(errors).toEqual([]);
  await testInfo.attach("SY-X-06-native-length-evidence", {
    body: JSON.stringify({ canonical, project: testInfo.project.name, sourceLength: source.length,
      source, rejected, recovered, reentered, errors }, null, 2),
    contentType: "application/json",
  });
});

test("SY-X-08 native principal complex root, HTTP reentry and finite recovery", async ({ page }, testInfo) => {
  const errors: string[] = [];
  const evidence: unknown[] = [];
  const ids: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const canonical = fixture("SY-X-08");
  expect(canonical).toBe(String.raw`\sqrt{-1}`);
  async function complex(source: string, backend: string) {
    await enter(field, source);
    const pending = page.waitForResponse(response => response.url().endsWith("/api/v1/evaluate") && response.request().method() === "POST");
    await page.getByRole("button", {name:"Evaluar", exact:true}).click();
    const response = await pending;
    expect(response.status()).toBe(200);
    expect(response.request().postDataJSON().expression).toBe(backend);
    const body = await response.json();
    expect(body.success).toBe(true);
    expect(body.result_type).toBe("scalar");
    expect(body.result_text).toBe("I");
    expect(body.result_latex).toBe("i");
    expect(body.result_approx).toBeNull();
    expect(body.error_code).toBeNull();
    expect(body.request_id).toBeTruthy();
    await expect(page.locator('[aria-live="polite"] .a11y-scale-result-lg .katex-html').last()).toHaveText("i");
    await expect(page.getByRole("alert")).toHaveCount(0);
    ids.push(body.request_id);
    evidence.push({source, backend, body});
    return body.result_latex as string;
  }
  await complex(await complex(canonical, "sqrt(-1)"), "i");
  ids.push((await evaluate(page, field, "i^2", -1)).requestId);
  const recovery = await evaluate(page, field, "2+3", 5);
  const again = await evaluate(page, field, recovery.reentry, 5);
  ids.push(recovery.requestId, again.requestId);
  expect(new Set(ids).size).toBe(5);
  expect(errors).toEqual([]);
  await testInfo.attach("SY-X-08-native-http-evidence", {body:JSON.stringify({domain:"existing principal complex branch", canonical, project:testInfo.project.name, evidence, ids, errors},null,2),contentType:"application/json"});
});

test("SY-X-13 original nested derivative, exact HTTP output reentry and recovery",async({page},testInfo)=>{
  const errors:string[]=[];
  const evidence:unknown[]=[];
  const ids:string[]=[];
  page.on("pageerror",error=>errors.push(error.message));
  await page.goto("/");
  const field=page.locator("math-field").first();
  await expect(field).toBeVisible();
  const original=fixture("SY-X-13");
  expect(original).toBe(String.raw`\frac{d}{dx}x^{x^{x}}`);
  const checkPython=String.raw`import json,sys,sympy as s
b=json.load(sys.stdin); x=s.Symbol('x',positive=True)
expected=x**(x**x)*(x**x*(s.log(x)+1)*s.log(x)+x**(x-1))
actual=s.sympify(b['result_text'],locals={'x':x})
assert not actual.has(s.Derivative)
assert s.simplify(actual-expected)==0
if 'input' in b:
 assert s.simplify(s.sympify(b['input'].replace('^','**'),locals={'x':x})-x**(x**x))==0
print('exact positive-real equivalence')`;
  async function symbolic(source:string,path:string){
    await field.evaluate((node,value)=>{
      (node as HTMLElement & {setValue(v:string):void}).setValue(value);
      node.dispatchEvent(new InputEvent("input",{bubbles:true,inputType:"insertText",data:value}));
    },source);
    const serialized=await field.evaluate(node=>(node as HTMLElement & {value:string}).value);
    expect(serialized).not.toBe("");
    const pending=page.waitForResponse(r=>r.url().endsWith(path)&&r.request().method()==="POST");
    await page.getByRole("button",{name:"Evaluar",exact:true}).click();
    const response=await pending;
    expect(response.status()).toBe(200);
    const payload=response.request().postDataJSON();
    if(path.endsWith("/derivative")){expect(payload.variable).toBe("x");expect(payload.order).toBe(1);}
    const body=await response.json();
    expect(body.success).toBe(true);expect(body.error_code).toBeNull();
    expect(body.result_latex).toBeTruthy();expect(body.request_id).toBeTruthy();
    const checked={result_text:body.result_text,...(path.endsWith("/derivative")?{input:payload.expression}:{})};
    expect(execFileSync("python",["-c",checkPython],{input:JSON.stringify(checked),timeout:10000,encoding:"utf8"}).trim()).toBe("exact positive-real equivalence");
    const visible=page.locator('[aria-live="polite"] .a11y-scale-result-lg .katex-html').last();
    await expect(visible).toBeVisible();await expect(visible).toContainText("x");
    await expect(page.getByRole("alert")).toHaveCount(0);
    ids.push(body.request_id);evidence.push({source,serialized,payload,body});
    return body.result_latex as string;
  }
  await symbolic(await symbolic(original,"/api/v1/derivative"),"/api/v1/evaluate");
  const recovered=await evaluate(page,field,"2+3",5);
  const reentered=await evaluate(page,field,recovered.reentry,5);
  ids.push(recovered.requestId,reentered.requestId);
  expect(new Set(ids).size).toBe(4);expect(errors).toEqual([]);
  await testInfo.attach("SY-X-13-native-http-evidence",{body:JSON.stringify({original,domain:"x>0; no complex branch claim",project:testInfo.project.name,evidence,ids,errors},null,2),contentType:"application/json"});
});

test("SY-X-14 original50 reciprocals show actual AST-depth limit and HTTP recovery",async({page},testInfo)=>{
  const errors:string[]=[];
  page.on("pageerror",e=>errors.push(e.message));
  await page.goto("/");
  const field=page.locator("math-field").first();await expect(field).toBeVisible();
  const canonical=fixture("SY-X-14");
  expect(canonical).toBe(String.raw`\underbrace{\frac{1}{\frac{1}{\cdots\frac{1}{x}}}}_{50\text{ niveles}}`);
  let source="x";for(let i=0;i<50;i++)source=String.raw`\frac{1}{${source}}`;
  expect(source.length).toBe(501);expect(source.match(/\\frac/g)).toHaveLength(50);
  await field.evaluate((node,value)=>{(node as HTMLElement & {setValue(v:string):void}).setValue(value);node.dispatchEvent(new InputEvent("input",{bubbles:true,inputType:"insertText",data:value}));},source);
  const serialized=await field.evaluate(node=>(node as HTMLElement & {value:string}).value);
  expect(serialized.match(/\\frac/g)).toHaveLength(50);
  const pending=page.waitForResponse(r=>r.url().endsWith("/api/v1/evaluate")&&r.request().method()==="POST");
  await page.getByRole("button",{name:"Evaluar",exact:true}).click();
  const response=await pending;expect(response.status()).toBe(200);
  const expression=response.request().postDataJSON().expression as string;
  expect(expression.match(/\//g)).toHaveLength(50);expect(expression.match(/x/g)).toHaveLength(1);
  expect(expression.length).toBeLessThanOrEqual(500);
  const rejected=await response.json();
  expect(rejected.success).toBe(false);expect(rejected.error_code).toBe("COMPLEXITY_LIMIT");
  expect(rejected.error_message).toContain("profundidad máxima de 30");
  expect(rejected.result_text).toBeNull();expect(rejected.result_latex).toBeNull();
  const alert=page.getByRole("alert").filter({hasText:"COMPLEXITY_LIMIT"});
  await expect(alert).toContainText("profundidad máxima de 30");
  await expect(page.locator(".a11y-scale-result-lg")).toHaveCount(0);
  const recovered=await evaluate(page,field,"2+3",5);
  const reentered=await evaluate(page,field,recovered.reentry,5);
  expect(new Set([rejected.request_id,recovered.requestId,reentered.requestId]).size).toBe(3);
  expect(errors).toEqual([]);
  await testInfo.attach("SY-X-14-native-http-limit-evidence",{body:JSON.stringify({canonical,source,serialized,expression,project:testInfo.project.name,rejected,recovered,reentered,errors,scope:"Rejection/recovery PASS only;50-layer mathematical parity remains BLOCKED"},null,2),contentType:"application/json"});
});

test("SY-X-15 original script text never executes or becomes HTML, then HTTP recovery",async({page},testInfo)=>{
  const probe=await installScriptProbe(page);
  const requests:Array<{url:string;body:unknown}>=[];
  page.on("request",request=>{if(request.url().includes("/api/v1/")&&request.method()==="POST")requests.push({url:request.url(),body:request.postDataJSON()});});
  await page.goto("/");
  const field=page.locator("math-field").first();await expect(field).toBeVisible();
  const source=fixture("SY-X-15");expect(source).toBe(String.raw`\text{<script>alert(1)</script>}`);
  await field.evaluate((node,value)=>{(node as HTMLElement & {setValue(v:string):void}).setValue(value);node.dispatchEvent(new InputEvent("input",{bubbles:true,inputType:"insertText",data:value}));},source);
  const serialized=await field.evaluate(node=>(node as HTMLElement & {value:string}).value);
  expect(serialized).toContain("<script>alert(1)</script>");
  const ingestion=await probe.assertInert();
  await page.getByRole("button",{name:"Evaluar",exact:true}).click();
  let outcome="";
  await expect.poll(async()=>{
    const alerts=await page.getByRole("alert").allInnerTexts();
    if(alerts.some(text=>text.trim()))return outcome="clear-error";
    const text=(await page.locator(".a11y-scale-result-lg").allInnerTexts()).join(" ");
    if(text.includes("<script>alert(1)</script>"))return outcome="inert-text";
    return "pending";
  }).not.toBe("pending");
  const notice=(await page.getByRole("alert").allInnerTexts()).join(" ");
  if(outcome==="clear-error")await expect(page.locator(".a11y-scale-result-lg")).toHaveCount(0);
  const rejected=await probe.assertInert();
  const invalidRequests=requests.length;
  const recovered=await evaluate(page,field,"2+3",5);
  const reentered=await evaluate(page,field,recovered.reentry,5);
  expect(reentered.requestId).not.toBe(recovered.requestId);
  expect(requests).toHaveLength(invalidRequests+2);
  const final=await probe.assertInert();
  await testInfo.attach("SY-X-15-native-inert-text-evidence",{body:JSON.stringify({source,serialized,project:testInfo.project.name,outcome,notice,ingestion,rejected,final,requests,recovered,reentered},null,2),contentType:"application/json"});
});

test("SY-X-15 probe positive control detects inert script insertion in closed shadow DOM",async({page},testInfo)=>{
  const evidence=await verifyInsertionControl(page,"/");
  await testInfo.attach("SY-X-15-probe-control",{body:JSON.stringify(evidence),contentType:"application/json"});
});

test("SY-X-16 file probe control detects and blocks only a synthetic sentinel",async({page},testInfo)=>{
  const evidence=await verifyFileProbeControl(page,"/");
  await testInfo.attach("SY-X-16-file-probe-control",{body:JSON.stringify(evidence),contentType:"application/json"});
});
test("SY-X-16 original input command is rejected without file fetch, then HTTP recovery",async({page},testInfo)=>{
  const probe=await installFileProbe(page);
  const requests:Array<{url:string;body:unknown}>=[];
  page.on("request",request=>{if(request.url().includes("/api/v1/")&&request.method()==="POST")requests.push({url:request.url(),body:request.postDataJSON()});});
  await page.goto("/");
  const field=page.locator("math-field").first();await expect(field).toBeVisible();
  const source=fixture("SY-X-16");expect(source).toBe(String.raw`\input{/etc/passwd}`);
  await field.evaluate((node,value)=>{(node as HTMLElement & {setValue(v:string):void}).setValue(value);node.dispatchEvent(new InputEvent("input",{bubbles:true,inputType:"insertText",data:value}));},source);
  const serialized=await field.evaluate(node=>(node as HTMLElement & {value:string}).value);
  expect(serialized).toContain("input");expect(serialized).toContain("/etc/passwd");
  const ingestion=probe.assertNoAccess();
  await page.getByRole("button",{name:"Evaluar",exact:true}).click();
  const alerts=page.getByRole("alert");await expect(alerts.first()).toBeVisible();
  const notice=(await alerts.allInnerTexts()).join(" ");expect(notice.trim()).not.toBe("");
  await expect(page.locator(".a11y-scale-result-lg")).toHaveCount(0);
  const rejected=probe.assertNoAccess();const invalidRequests=requests.length;
  const recovered=await evaluate(page,field,"2+3",5);
  const reentered=await evaluate(page,field,recovered.reentry,5);
  expect(recovered.requestId).not.toBe(reentered.requestId);expect(requests).toHaveLength(invalidRequests+2);
  const final=probe.assertNoAccess();
  await testInfo.attach("SY-X-16-native-file-command-evidence",{body:JSON.stringify({source,serialized,project:testInfo.project.name,notice,ingestion,rejected,final,requests,recovered,reentered},null,2),contentType:"application/json"});
});
test("SY-X-17 original shell escape command is rejected, then HTTP recovery",async({page},testInfo)=>{
  const probe=await installFileProbe(page);
  const requests:Array<{url:string;body:unknown}>=[];
  page.on("request",request=>{if(request.url().includes("/api/v1/")&&request.method()==="POST")requests.push({url:request.url(),body:request.postDataJSON()});});
  await page.goto("/");
  const field=page.locator("math-field").first();await expect(field).toBeVisible();
  const source=fixture("SY-X-17");expect(source).toBe(String.raw`\write18{ls}`);
  await field.evaluate((node,value)=>{(node as HTMLElement & {setValue(v:string):void}).setValue(value);node.dispatchEvent(new InputEvent("input",{bubbles:true,inputType:"insertText",data:value}));},source);
  const serialized=await field.evaluate(node=>(node as HTMLElement & {value:string}).value);
  expect(serialized).toContain("write");expect(serialized).toContain("18");expect(serialized).toContain("ls");
  const ingestion=probe.assertNoAccess();
  await page.getByRole("button",{name:"Evaluar",exact:true}).click();
  const alerts=page.getByRole("alert");await expect(alerts.first()).toBeVisible();
  const notice=(await alerts.allInnerTexts()).join(" ");expect(notice.trim()).not.toBe("");
  await expect(page.locator(".a11y-scale-result-lg")).toHaveCount(0);
  expect(notice).toContain("Comando TeX no permitido");
  expect(requests).toHaveLength(0); // local rejection must not fabricate invalid HTTP evidence
  const rejected=probe.assertNoAccess();const invalidRequests=requests.length;
  const recovered=await evaluate(page,field,"2+3",5);
  const reentered=await evaluate(page,field,recovered.reentry,5);
  expect(recovered.requestId).not.toBe(reentered.requestId);expect(requests).toHaveLength(invalidRequests+2);
  const final=probe.assertNoAccess();
  await testInfo.attach("SY-X-17-native-shell-command-evidence",{body:JSON.stringify({source,serialized,project:testInfo.project.name,notice,ingestion,rejected,final,requests,recovered,reentered},null,2),contentType:"application/json"});
});
test("SY-X-18 original Python-like command is rejected, then HTTP recovery",async({page},testInfo)=>{
  const probe=await installFileProbe(page);
  const requests:Array<{url:string;body:unknown}>=[];
  page.on("request",request=>{if(request.url().includes("/api/v1/")&&request.method()==="POST")requests.push({url:request.url(),body:request.postDataJSON()});});
  await page.goto("/");
  const field=page.locator("math-field").first();await expect(field).toBeVisible();
  const source=fixture("SY-X-18");expect(source).toBe(String.raw`__import__('os').system('ls')`);
  await field.evaluate((node,value)=>{(node as HTMLElement & {setValue(v:string):void}).setValue(value);node.dispatchEvent(new InputEvent("input",{bubbles:true,inputType:"insertText",data:value}));},source);
  const serialized=await field.evaluate(node=>(node as HTMLElement & {value:string}).value);
  // Subscript/prime formatting may change, but every payload letter must survive in order.
  expect(serialized.replace(/\\[A-Za-z]+/g,"").replace(/[^A-Za-z]/g,"")).toBe("importossystemls");
  const ingestion=probe.assertNoAccess();
  await page.getByRole("button",{name:"Evaluar",exact:true}).click();
  const alerts=page.getByRole("alert");await expect(alerts.first()).toBeVisible();
  const notice=(await alerts.allInnerTexts()).join(" ");expect(notice.trim()).not.toBe("");
  await expect(page.locator(".a11y-scale-result-lg")).toHaveCount(0);
  const rejected=probe.assertNoAccess();const invalidRequests=requests.length;
  const recovered=await evaluate(page,field,"2+3",5);
  const reentered=await evaluate(page,field,recovered.reentry,5);
  expect(recovered.requestId).not.toBe(reentered.requestId);expect(requests).toHaveLength(invalidRequests+2);
  const final=probe.assertNoAccess();
  await testInfo.attach("SY-X-18-native-python-command-evidence",{body:JSON.stringify({source,serialized,project:testInfo.project.name,notice,ingestion,rejected,final,requests,recovered,reentered},null,2),contentType:"application/json"});
});
test("SY-X-19 original file-read expression is rejected, then HTTP recovery",async({page},testInfo)=>{
  const probe=await installFileProbe(page);
  const requests:Array<{url:string;body:unknown}>=[];
  page.on("request",request=>{if(request.url().includes("/api/v1/")&&request.method()==="POST")requests.push({url:request.url(),body:request.postDataJSON()});});
  await page.goto("/");
  const field=page.locator("math-field").first();await expect(field).toBeVisible();
  const source=fixture("SY-X-19");expect(source).toBe(String.raw`open('/etc/passwd').read()`);
  await field.evaluate((node,value)=>{(node as HTMLElement & {setValue(v:string):void}).setValue(value);node.dispatchEvent(new InputEvent("input",{bubbles:true,inputType:"insertText",data:value}));},source);
  const serialized=await field.evaluate(node=>(node as HTMLElement & {value:string}).value);
  // Subscript/prime formatting may change, but every payload letter must survive in order.
  expect(serialized.replace(/\\[A-Za-z]+/g,"").replace(/[^A-Za-z]/g,"")).toBe("openetcpasswdread");
  const ingestion=probe.assertNoAccess();
  await page.getByRole("button",{name:"Evaluar",exact:true}).click();
  const alerts=page.getByRole("alert");await expect(alerts.first()).toBeVisible();
  const notice=(await alerts.allInnerTexts()).join(" ");expect(notice.trim()).not.toBe("");
  await expect(page.locator(".a11y-scale-result-lg")).toHaveCount(0);
  const rejected=probe.assertNoAccess();const invalidRequests=requests.length;
  const recovered=await evaluate(page,field,"2+3",5);
  const reentered=await evaluate(page,field,recovered.reentry,5);
  expect(recovered.requestId).not.toBe(reentered.requestId);expect(requests).toHaveLength(invalidRequests+2);
  const final=probe.assertNoAccess();
  await testInfo.attach("SY-X-19-native-file-read-evidence",{body:JSON.stringify({source,serialized,project:testInfo.project.name,notice,ingestion,rejected,final,requests,recovered,reentered},null,2),contentType:"application/json"});
});

const rejectionMessages: Record<string, string> = {
  "SY-X-01": "La expresión no puede estar vacía.",
  "SY-X-02": "La expresión no puede estar vacía.",
  "SY-X-03": "Sintaxis incompleta",
  "SY-R-12": "Entrada no matemática: escribe una expresión válida.",
  "SY-X-07": "Forma indeterminada: infinito menos infinito no está definido.",
};

for (const id of Object.keys(rejectionMessages)) {
  test(`${id} native source, readable local rejection and two real HTTP recoveries`, async ({ page }, testInfo) => {
    const pageErrors: string[] = [];
    const sent: Array<{ url: string; body: unknown }> = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));
    page.on("request", (request) => {
      if (request.url().includes("/api/v1/") && request.method() === "POST") {
        sent.push({ url: request.url(), body: request.postDataJSON() });
      }
    });
    await page.goto("/");
    const field = page.locator("math-field").first();
    await expect(field).toBeVisible();
    const canonical = fixture(id);
    if (id === "SY-X-01") expect(canonical).toBe("*(vacía)*");
    if (id === "SY-R-12") expect(canonical).toBe(String.raw`\text{no existe}`);
    if (id === "SY-X-07") expect(canonical).toBe(String.raw`\infty-\infty`);
    const source = id === "SY-X-01" ? "" : canonical;
    for (let cycle = 0; cycle < 2; cycle += 1) {
      const before = sent.length;
      await enter(field, source);
      await page.getByRole("button", { name: "Evaluar", exact: true }).click();
      const alert = page.getByRole("alert");
      await expect(alert).toContainText(rejectionMessages[id]);
      if (id === "SY-X-03" || id === "SY-R-12") await expect(alert).not.toContainText("vacía");
      expect(sent).toHaveLength(before); // local validation must not fabricate backend evidence
      const expected = id === "SY-X-07" ? (cycle === 0 ? 0 : 5) : cycle === 0 ? 5 : 9;
      const recovery = id === "SY-X-07" ? (cycle === 0 ? "3-3" : "2+3") : cycle === 0 ? "2+3" : "4+5";
      const first = await evaluate(page, field, recovery, expected);
      const second = await evaluate(page, field, first.reentry, expected);
      expect(second.requestId).not.toBe(first.requestId);
      expect(sent).toHaveLength(before + 2);
      expect(pageErrors).toEqual([]);
    }
    await testInfo.attach(`${id}-native-http-evidence`, {
      body: JSON.stringify({ id, project: testInfo.project.name, canonical, source, sent, pageErrors }, null, 2),
      contentType: "application/json",
    });
  });
}


test("SY-X-09 native extreme power bounded HTTP rejection and finite reentry", async ({ page }, testInfo) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const source = fixture("SY-X-09");
  expect(source).toBe("99999999999^{99999999999}");
  await enter(field, source);
  const responsePromise = page.waitForResponse(response =>
    response.url().endsWith("/api/v1/evaluate") && response.request().method() === "POST");
  await page.getByRole("button", { name: "Evaluar", exact: true }).click();
  const response = await responsePromise;
  expect(response.status()).toBe(200);
  expect(response.request().postDataJSON().expression).toBe("99999999999^(99999999999)");
  const rejected = await response.json();
  expect(rejected.success).toBe(false);
  expect(rejected.error_code).toBe("COMPLEXITY_LIMIT");
  expect(rejected.result_latex).toBeNull();
  expect(rejected.result_text).toBeNull();
  const resultAlert = page.locator('form[aria-labelledby="basic-mode-heading"]').getByRole("alert").filter({ hasText: "COMPLEXITY_LIMIT" });
  await expect(resultAlert).toContainText("COMPLEXITY_LIMIT");
  const recovery = await evaluate(page, field, "2+3", 5);
  const reentry = await evaluate(page, field, recovery.reentry, 5);
  expect(new Set([rejected.request_id, recovery.requestId, reentry.requestId]).size).toBe(3);
  expect(errors).toEqual([]);
  await testInfo.attach("SY-X-09-native-http-evidence", {
    body: JSON.stringify({ source, project:testInfo.project.name, rejected, recovery, reentry, errors }, null, 2),
    contentType:"application/json",
  });
});


test("SY-X-10 native astronomical nested power rejects before expansion and recovers", async ({page}, testInfo) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const source = fixture("SY-X-10");
  expect(source).toBe("10^{10^{10}}");
  await enter(field, source);
  const pending = page.waitForResponse(response =>
    response.url().endsWith("/api/v1/evaluate") && response.request().method() === "POST");
  await page.getByRole("button", {name:"Evaluar",exact:true}).click();
  const response = await pending;
  expect(response.status()).toBe(200);
  expect(response.request().postDataJSON().expression.replace(/[()]/g,"")).toBe("10^10^10");
  const rejected = await response.json();
  expect(rejected.success).toBe(false);
  expect(rejected.error_code).toBe("COMPLEXITY_LIMIT");
  expect(rejected.result_text).toBeNull();
  expect(rejected.result_latex).toBeNull();
  await expect(page.getByRole("alert").filter({hasText:"COMPLEXITY_LIMIT"})).toContainText("COMPLEXITY_LIMIT");
  const recovered = await evaluate(page,field,"2+3",5);
  const reentered = await evaluate(page,field,recovered.reentry,5);
  expect(new Set([rejected.request_id,recovered.requestId,reentered.requestId]).size).toBe(3);
  expect(errors).toEqual([]);
  await testInfo.attach("SY-X-10-native-http-evidence",{
    body:JSON.stringify({source,project:testInfo.project.name,rejected,recovered,reentered,errors},null,2),
    contentType:"application/json"
  });
});
test("SY-X-11 native astronomical nested power rejects before expansion and recovers", async ({page}, testInfo) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const source = fixture("SY-X-11");
  expect(source).toBe("9^{9^{9}}");
  await enter(field, source);
  const pending = page.waitForResponse(response =>
    response.url().endsWith("/api/v1/evaluate") && response.request().method() === "POST");
  await page.getByRole("button", {name:"Evaluar",exact:true}).click();
  const response = await pending;
  expect(response.status()).toBe(200);
  expect(response.request().postDataJSON().expression.replace(/[()]/g,"")).toBe("9^9^9");
  const rejected = await response.json();
  expect(rejected.success).toBe(false);
  expect(rejected.error_code).toBe("COMPLEXITY_LIMIT");
  expect(rejected.result_text).toBeNull();
  expect(rejected.result_latex).toBeNull();
  await expect(page.getByRole("alert").filter({hasText:"COMPLEXITY_LIMIT"})).toContainText("COMPLEXITY_LIMIT");
  const recovered = await evaluate(page,field,"2+3",5);
  const reentered = await evaluate(page,field,recovered.reentry,5);
  expect(new Set([rejected.request_id,recovered.requestId,reentered.requestId]).size).toBe(3);
  expect(errors).toEqual([]);
  await testInfo.attach("SY-X-11-native-http-evidence",{
    body:JSON.stringify({source,project:testInfo.project.name,rejected,recovered,reentered,errors},null,2),
    contentType:"application/json"
  });
});

test("SY-X-12 native non-elementary integral notice, finite integral recovery and reentry", async ({page}, testInfo) => {
  test.setTimeout(60_000);
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  const field = page.locator("math-field").first();
  await expect(field).toBeVisible();
  const source = fixture("SY-X-12");
  expect(source).toBe(String.raw`\int\sin\left(x^{x}\right)dx`);
  await enter(field, source);
  const pending = page.waitForResponse(response =>
    response.url().endsWith("/api/v1/integral") && response.request().method() === "POST");
  await page.getByRole("button", {name:"Evaluar", exact:true}).click();
  const response = await pending;
  expect(response.status()).toBe(200);
  const payload = response.request().postDataJSON() as {expression: string; variable: string; lower_bound?: string; upper_bound?: string};
  expect(payload.variable).toBe("x");
  expect(payload.lower_bound).toBeUndefined();
  expect(payload.upper_bound).toBeUndefined();
  const integrand = payload.expression.replace(/\s/g, "");
  expect(integrand).toMatch(/sin/i);
  expect(integrand).not.toMatch(/integral/i);
  const rejected = await response.json();
  expect(rejected.success).toBe(false);
  expect(rejected.error_code).toBe("UNSUPPORTED_OPERATION");
  expect(rejected.result_text).toBeNull();
  expect(rejected.result_latex).toBeNull();
  expect(String(rejected.error_message)).toContain("Sin forma elemental");
  const alert = page.getByRole("alert").filter({hasText:"UNSUPPORTED_OPERATION"});
  await expect(alert).toContainText("Sin forma elemental");
  await expect(page.locator(".a11y-scale-result-lg")).toHaveCount(0);

  await enter(field, String.raw`\int x\,dx`);
  const finitePending = page.waitForResponse(http =>
    http.url().endsWith("/api/v1/integral") && http.request().method() === "POST");
  await page.getByRole("button", {name:"Evaluar", exact:true}).click();
  const finiteResponse = await finitePending;
  expect(finiteResponse.status()).toBe(200);
  expect(String(finiteResponse.request().postDataJSON().expression).replace(/\s/g, "")).toBe("x");
  const finite = await finiteResponse.json();
  expect(finite.success).toBe(true);
  expect(String(finite.result_text)).toMatch(/x\*\*2\/2/);
  expect(String(finite.result_text)).toContain("+ C");
  expect(String(finite.result_text)).not.toMatch(/Integral/);
  expect(finite.request_id).toBeTruthy();
  expect(finite.request_id).not.toBe(rejected.request_id);
  await expect(page.getByRole("alert")).toHaveCount(0);

  const recovered = await evaluate(page, field, "2+3", 5);
  const reentered = await evaluate(page, field, recovered.reentry, 5);
  expect(new Set([rejected.request_id, finite.request_id, recovered.requestId, reentered.requestId]).size).toBe(4);
  expect(errors).toEqual([]);
  await testInfo.attach("SY-X-12-native-http-evidence", {
    body: JSON.stringify({
      source, project: testInfo.project.name, integrand, rejected, finite, recovered, reentered, errors,
    }, null, 2),
    contentType: "application/json",
  });
});


test("SY-X-20 native invalid Unicode source is rejected with finite HTTP recovery", async ({page}, testInfo) => {
  const errors:string[]=[];
  const requests:Array<{url:string;body:unknown}>=[];
  page.on("pageerror",e=>errors.push(e.message));
  page.on("request",request=>{
    if(request.url().includes("/api/v1/") && request.method()==="POST")
      requests.push({url:request.url(),body:request.postDataJSON()});
  });
  await page.goto("/");
  const field=page.locator("math-field").first();
  await expect(field).toBeVisible();
  const source=fixture("SY-X-20");
  expect(source).toBe("😀+1");
  expect([...source].map(c=>c.codePointAt(0))).toEqual([0x1f600,43,49]);
  await field.evaluate((node,value)=>{
    (node as HTMLElement & {setValue(v:string):void}).setValue(value);
    node.dispatchEvent(new InputEvent("input",{bubbles:true,inputType:"insertText",data:value}));
  },source);
  const serialized=await field.evaluate(node=>(node as HTMLElement & {value:string}).value);
  expect(serialized).toContain("😀");
  await page.getByRole("button",{name:"Evaluar",exact:true}).click();
  const alerts=page.getByRole("alert");
  await expect(alerts.first()).toBeVisible();
  const notice=(await alerts.allInnerTexts()).join(" ");
  expect(notice).toMatch(/car[aá]cter|inv[aá]lid|permitid|reconocid|sintaxis/i);
  await expect(page.locator(".a11y-scale-result-lg")).toHaveCount(0);
  const invalidRequests=requests.length;
  const recovered=await evaluate(page,field,"2+3",5);
  const reentered=await evaluate(page,field,recovered.reentry,5);
  expect(reentered.requestId).not.toBe(recovered.requestId);
  expect(requests).toHaveLength(invalidRequests+2);
  expect(errors).toEqual([]);
  await testInfo.attach("SY-X-20-native-unicode-evidence",{
    body:JSON.stringify({source,serialized,notice,invalidRequests,requests,project:testInfo.project.name,recovered,reentered,errors},null,2),
    contentType:"application/json"
  });
});


test("SY-X-21 native zero-width source has exact value or clear error and recovers",async({page},testInfo)=>{
  const errors:string[]=[];page.on("pageerror",e=>errors.push(e.message));
  await page.goto("/");
  const field=page.locator("math-field").first();await expect(field).toBeVisible();
  const source=fixture("SY-X-21");
  expect([...source].map(ch=>ch.codePointAt(0))).toEqual([49,0x200b,43,0x200b,50]);
  await field.evaluate((node,value)=>{
    (node as HTMLElement & {setValue(v:string):void}).setValue(value);
    node.dispatchEvent(new InputEvent("input",{bubbles:true,inputType:"insertText",data:value}));
  },source);
  const serialized=await field.evaluate(node=>(node as HTMLElement & {value:string}).value);
  await page.getByRole("button",{name:"Evaluar",exact:true}).click();
  const alert=page.getByRole("alert").first();
  const result=page.locator(".a11y-scale-result-lg").first();
  await expect.poll(async()=>{
    if(await alert.isVisible().catch(()=>false))return "error";
    if(await result.isVisible().catch(()=>false))return "value";
    return "pending";
  },{timeout:15000}).not.toBe("pending");
  const isError=await alert.isVisible().catch(()=>false);
  const notice=isError ? (await alert.innerText()).trim():"";
  if(isError){
    expect(notice).toMatch(/car[aá]cter|inv[aá]lid|permitid|reconocid|sintaxis|expresi[oó]n/i);
    await expect(result).toHaveCount(0);
  }else{
    const renderedValues=(await result.innerText()).trim().split(/\s+/);
    expect(renderedValues.length).toBeGreaterThan(0);
    for(const renderedValue of renderedValues)expect(renderedValue).toMatch(/^3(?:\.0+)?$/);
  }
  const first=await evaluate(page,field,"2+3",5);
  const second=await evaluate(page,field,first.reentry,5);
  expect(first.requestId).not.toBe(second.requestId);expect(errors).toEqual([]);
  await testInfo.attach("SY-X-21-native-evidence",{
    body:JSON.stringify({source,serialized,isError,notice,project:testInfo.project.name,first,second,errors},null,2),
    contentType:"application/json"
  });
});


test("SY-X-22 native 10000-digit source rejects clearly or stays exact, then recovers",async({page},testInfo)=>{
  test.setTimeout(120000);
  const errors:string[]=[];page.on("pageerror",e=>errors.push(e.message));
  await page.goto("/");
  const field=page.locator("math-field").first();await expect(field).toBeVisible();
  const source="9".repeat(10000)+"+1";
  expect(source.length).toBe(10002);
  await field.evaluate((node,value)=>{
    (node as HTMLElement & {setValue(v:string):void}).setValue(value);
    node.dispatchEvent(new InputEvent("input",{bubbles:true,inputType:"insertText",data:value}));
  },source);
  const serialized=await field.evaluate(node=>(node as HTMLElement & {value:string}).value);
  await page.getByRole("button",{name:"Evaluar",exact:true}).click();
  const alert=page.getByRole("alert").first();
  const result=page.locator(".a11y-scale-result-lg").first();
  await expect.poll(async()=>{
    if(await alert.isVisible().catch(()=>false))return "error";
    if(await result.isVisible().catch(()=>false))return "value";
    return "pending";
  },{timeout:30000}).not.toBe("pending");
  const rejected=await alert.isVisible().catch(()=>false);
  const notice=rejected?(await alert.innerText()).trim():"";
  if(rejected){
    expect(notice).toMatch(/longitud|tamañ|l[ií]mit|demasiad|car[aá]cter|inv[aá]lid|expresi[oó]n|sintaxis/i);
    await expect(result).toHaveCount(0);
  }else{
    const exact="1"+"0".repeat(10000);
    for(const value of (await result.innerText()).trim().split(/\s+/))expect(value).toBe(exact);
    expect(serialized.replace(/\s/g,"")).toContain("9".repeat(10000));
  }
  const first=await evaluate(page,field,"2+3",5);
  const second=await evaluate(page,field,first.reentry,5);
  expect(first.requestId).not.toBe(second.requestId);
  expect(errors).toEqual([]);
  await testInfo.attach("SY-X-22-native-evidence",{
    body:JSON.stringify({sourceLength:source.length,serializedLength:serialized.length,rejected,notice,project:testInfo.project.name,first,second,errors},null,2),
    contentType:"application/json"
  });
});
