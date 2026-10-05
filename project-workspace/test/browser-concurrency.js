// Playwright CLI scenario; all API requests must use the isolated mock gateway.
async (page) => {
  await page.getByRole('button',{name:'Phase 2 — Strategy & Roadmap',exact:false}).click();
  await page.locator('#toolList').getByRole('button',{name:'AI Strategy Planning',exact:false}).click();
  const id=new URL(page.url()).searchParams.get('project');
  const path=`projects/${id}/phase-02-strategy-roadmap/ai-strategy-planning/state.json`;
  const tool=page.frameLocator('#toolFrame');await tool.locator('[data-eng=vision]').waitFor();
  await page.request.post('http://127.0.0.1:4323/external',{data:{path,field:'alignment',value:'Remote independent strategy field'}});
  await tool.locator('[data-eng=vision]').fill('Local independent strategy field');
  await page.getByRole('button',{name:'Save now',exact:true}).click();
  await page.locator('#saveStatus').filter({hasText:'Saved to GitHub'}).waitFor();
  let state=await (await page.request.get('http://127.0.0.1:4323/inspect')).json();
  if (state.files[path].data.fields.alignment!=='Remote independent strategy field') throw new Error('Remote field was lost');
  await page.request.post('http://127.0.0.1:4323/external',{data:{path,field:'vision',value:'Remote conflicting vision'}});
  await tool.locator('[data-eng=vision]').fill('Local conflicting vision');
  await page.getByRole('button',{name:'Save now',exact:true}).click();await page.locator('#conflicts').waitFor({state:'visible'});
  state=await (await page.request.get('http://127.0.0.1:4323/inspect')).json();
  if (state.files[path].data.fields.vision!=='Remote conflicting vision') throw new Error('Conflict silently overwrote remote work');
  await page.getByRole('button',{name:'Keep my conflicting edits',exact:true}).click();
  await page.locator('#conflicts').waitFor({state:'hidden'});await page.locator('#saveStatus').filter({hasText:'Saved to GitHub'}).waitFor();
  state=await (await page.request.get('http://127.0.0.1:4323/inspect')).json();
  if (state.files[path].data.fields.vision!=='Local conflicting vision' || state.files[path].data.fields.alignment!=='Remote independent strategy field') throw new Error('Conflict resolution lost independent work');
}
