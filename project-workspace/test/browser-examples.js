// Run with playwright-cli run-code --filename against the loopback static preview.
// No GitHub fixture, token or external write is needed for this example flow.
async (page) => {
  const errors=[],github=[];
  const onError=error=>errors.push(error.message);
  const onRequest=request=>{if(request.url().startsWith('https://api.github.com/')) github.push(request.method()+' '+request.url());};
  page.on('pageerror',onError);page.on('request',onRequest);
  const origin='http://127.0.0.1:4321';
  const registry=await (await page.request.get(origin+'/project-workspace/registry.json')).json();
  await page.goto(origin+'/project-workspace/?example=nordkap');
  await page.locator('#workspace').waitFor({state:'visible'});
  await page.evaluate(()=>localStorage.setItem('aoa_ai_strategy_v1',JSON.stringify({fields:{vision:'Legacy fixture draft'}})));
  const stores=await page.evaluate(()=>Object.fromEntries(Object.entries(localStorage).filter(([key])=>key!=='aoa_lang')));
  if(!/42 of 45/.test(await page.locator('#exampleNotice').innerText())) throw new Error('Wrong source coverage');
  for (const phase of registry) for (const tool of phase.tools) {
    await page.getByRole('button',{name:phase.title,exact:false}).click();
    await page.locator('#toolList').getByRole('button',{name:tool.title,exact:false}).click();
    const expected=new URL(tool.href,origin+'/').pathname;
    await page.waitForFunction(expected=>document.querySelector('#toolFrame').contentWindow.location.pathname===expected,expected);
    const frame=page.frameLocator('#toolFrame');await frame.locator('h1').first().waitFor();
    if(!await page.locator('#toolFrame').evaluate(iframe=>!!Object.getOwnPropertyDescriptor(iframe.contentWindow,'localStorage').value)) throw new Error('Unscoped tool: '+tool.title);
    if(tool.key==='aoa_usecase_board_v1') {
      if(await frame.locator('.node-title').filter({hasText:'Loss reported (FNOL)'}).count()!==1) throw new Error('Board not populated');
      if(await frame.getByRole('button',{name:'● Go live',exact:true}).isVisible()) throw new Error('Board-only connection shown');
    }
  }
  const phase=registry[1];
  const strategy=()=>page.frameLocator('#toolFrame').locator('[data-eng="vision"]');
  async function openStrategy() {
    await page.getByRole('button',{name:phase.title,exact:false}).click();
    await page.locator('#toolList').getByRole('button',{name:'AI Strategy Planning',exact:false}).click();
    await strategy().waitFor();
  }
  await openStrategy();const original=await strategy().inputValue();
  if(!original.includes('Nordkap')) throw new Error('Existing strategy sample missing');
  const edit='Temporary example strategy edit';await strategy().fill(edit);
  await page.getByRole('button',{name:'Master project report',exact:true}).click();
  const report=page.frameLocator('#toolFrame').locator('#report');await report.waitFor();
  const text=await report.innerText();
  if(!text.includes(edit) || !text.includes('ROI Analysis') || !text.includes('Nordkap Insurance')) throw new Error('Report did not assemble the project');
  const reportNote=await page.frameLocator('#toolFrame').locator('[data-i18n="statPrivacy"]').innerText();
  if(!reportNote.includes('fictional example')) throw new Error('Report disclosure missing');
  await openStrategy();if(await strategy().inputValue()!==edit) throw new Error('Navigation lost temporary work');
  await page.getByRole('button',{name:'Reset example',exact:true}).click();
  await page.locator('#overview').waitFor({state:'visible'});await openStrategy();
  if(await strategy().inputValue()!==original) throw new Error('Reset failed');
  await strategy().fill('Temporary before refresh');await page.reload();await page.locator('#workspace').waitFor({state:'visible'});await openStrategy();
  if(await strategy().inputValue()!==original) throw new Error('Refresh failed');
  const after=await page.evaluate(()=>Object.fromEntries(Object.entries(localStorage).filter(([key])=>key!=='aoa_lang')));
  if(JSON.stringify(stores)!==JSON.stringify(after)) throw new Error('Examples changed legacy drafts or wrote recovery state');
  if(github.length) throw new Error('Example contacted GitHub API: '+github.join('; '));
  if(errors.length) throw new Error('Runtime errors: '+errors.join('; '));
  page.off('pageerror',onError);page.off('request',onRequest);
  await page.getByRole('button',{name:'Switch project',exact:true}).click();await page.locator('#entry').waitFor({state:'visible'});
  for (const [id,client,node] of [['nordvik','Nordvik Furniture','Range and demand plan'],['gronhoj','Grønhøj Foods','Grower contracts and crop plan']]) {
    await page.getByLabel('Existing project',{exact:true}).selectOption('example:'+id);await page.getByRole('button',{name:'Load example project',exact:true}).click();await page.locator('#workspace').waitFor({state:'visible'});
    if(!/1 of 45/.test(await page.locator('#exampleNotice').innerText())) throw new Error('Discovery coverage overstated');
    await page.locator('#toolList').getByRole('button',{name:'Use Case Discovery Board',exact:false}).click();
    await page.frameLocator('#toolFrame').locator('.node-title').filter({hasText:node}).waitFor();
    const clientField=page.frameLocator('#toolFrame').locator('[data-eng="client"]');
    if(await clientField.inputValue()!==client) throw new Error('Example client leaked');
    await page.getByRole('button',{name:'Switch project',exact:true}).click();await page.locator('#entry').waitFor({state:'visible'});
  }
  await page.setViewportSize({width:390,height:844});
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)) throw new Error('Mobile overflow');
  await page.setViewportSize({width:1440,height:1000});
}
