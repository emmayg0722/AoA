// Playwright CLI scenario using only the isolated loopback GitHub fixture.
async (page) => {
  await page.context().route('https://api.github.com/**',async route=>{
    const request=route.request();
    const response=await page.request.post('http://127.0.0.1:4323/gateway',{data:{url:request.url(),options:{method:request.method(),headers:request.headers(),body:request.postData()}}});
    await route.fulfill({response});
  });
  await page.goto('http://127.0.0.1:4321/project-workspace/?example=nordkap');await page.locator('#workspace').waitFor({state:'visible'});
  await page.getByRole('button',{name:'Phase 2 — Strategy & Roadmap',exact:false}).click();
  await page.locator('#toolList').getByRole('button',{name:'AI Strategy Planning',exact:false}).click();
  const vision=()=>page.frameLocator('#toolFrame').locator('[data-eng="vision"]');await vision().waitFor();await page.waitForFunction(()=>document.querySelector('#toolFrame').contentDocument.readyState==='complete');
  await vision().fill('Edited example starting point');
  // A failed reset must retain the active example and its temporary edits.
  await page.route('**/sample-data/engagement-nordkap/roi-analysis.json',route=>route.fulfill({status:503,body:'Unavailable fixture'}));
  await page.getByRole('button',{name:'Reset example',exact:true}).click();
  await page.waitForFunction(()=>document.getElementById('saveStatus').textContent.includes('Example could not load'));
  if(await vision().inputValue()!=='Edited example starting point') throw new Error('Failed source load replaced work');
  await page.unroute('**/sample-data/engagement-nordkap/roi-analysis.json');
  await page.getByRole('button',{name:'Use as starting project',exact:true}).click();await page.locator('#entry').waitFor({state:'visible'});
  if(!await page.locator('#startingExample').isVisible() || !(await page.locator('#startingExampleText').innerText()).includes('fictional')) throw new Error('Copy disclosure missing');
  if(await page.locator('#connectionDialog').isVisible()) throw new Error('Connection displayed before creating');
  await page.getByLabel('Client',{exact:true}).fill('Example copy fixture');await page.getByLabel('Project name',{exact:true}).fill('Copied engagement fixture');
  await page.getByLabel('Your name',{exact:true}).fill('Example architect');
  await page.getByLabel('I understand the repository visibility and can publish the information I enter.').check();
  await page.getByRole('button',{name:'Create project',exact:true}).click();await page.locator('#connectionDialog').waitFor({state:'visible'});
  await page.getByLabel('GitHub token',{exact:true}).fill('test-valid');await page.getByRole('button',{name:'Continue',exact:true}).click();
  await page.locator('#workspace').waitFor({state:'visible'});
  const id=new URL(page.url()).searchParams.get('project');if(!id) throw new Error('Copy did not create its own project');
  if(await page.locator('#resetExample').isVisible() || !await page.locator('#save').isVisible()) throw new Error('Real project retained example mode');
  if(!(await page.locator('#members').innerText()).includes('fictional example')) throw new Error('Copy provenance missing');
  await page.getByRole('button',{name:'Phase 2 — Strategy & Roadmap',exact:false}).click();await page.locator('#toolList').getByRole('button',{name:'AI Strategy Planning',exact:false}).click();await vision().waitFor();
  if(await vision().inputValue()!=='Edited example starting point') throw new Error('Copy lost the current example state');
  if(await page.frameLocator('#toolFrame').locator('[data-eng="client"]').inputValue()!=='Example copy fixture') throw new Error('Copied client header stale');
  const saved=await (await page.request.get('http://127.0.0.1:4323/inspect')).json();
  const files=saved.files;
  if(!files['projects/'+id+'/phase-10-roi-analysis-cost-optimization/roi-analysis/state.json'].data) throw new Error('Whole project was not copied');
  if(files['projects/'+id+'/phase-01-discovery-assessment/ai-maturity-assessment/state.json'].data!==null) throw new Error('Unrelated client sample mixed in');
  await page.getByRole('button',{name:'Switch project',exact:true}).click();await page.locator('#entry').waitFor({state:'visible'});
  if(await page.locator('#startingExample').isVisible()) throw new Error('Completed copy seed not cleared');
  await page.getByLabel('Client',{exact:true}).fill('Empty project fixture');await page.getByLabel('Project name',{exact:true}).fill('Empty after copy');
  await page.getByRole('button',{name:'Create project',exact:true}).click();await page.locator('#workspace').waitFor({state:'visible'});
  await page.getByRole('button',{name:'Phase 2 — Strategy & Roadmap',exact:false}).click();await page.locator('#toolList').getByRole('button',{name:'AI Strategy Planning',exact:false}).click();await vision().waitFor();
  if(await vision().inputValue()!=='') throw new Error('Seed leaked into an empty project');
  await page.getByRole('button',{name:'Switch project',exact:true}).click();await page.locator('#entry').waitFor({state:'visible'});
  await page.getByLabel('Join existing',{exact:true}).check();await page.getByLabel('Existing project',{exact:true}).selectOption('example:nordkap');await page.getByRole('button',{name:'Load example project',exact:true}).click();await page.locator('#workspace').waitFor({state:'visible'});
  await page.getByRole('button',{name:'Phase 2 — Strategy & Roadmap',exact:false}).click();await page.locator('#toolList').getByRole('button',{name:'AI Strategy Planning',exact:false}).click();await vision().waitFor();
  if(!(await vision().inputValue()).includes('Nordkap')) throw new Error('Copy mutated the source example');
  await page.getByRole('button',{name:'Use as starting project',exact:true}).click();await page.locator('#entry').waitFor({state:'visible'});
  await page.getByRole('button',{name:'Start with empty tools instead',exact:true}).click();
  if(await page.locator('#startingExample').isVisible()) throw new Error('Cancel seed failed');
  await page.context().unroute('https://api.github.com/**');
}
