// Playwright CLI scenario for the combined project chooser and deferred access.
async (page) => {
  const writes=[],errors=[];
  const onRequest=request=>{if(request.url().startsWith('https://api.github.com/')&&request.method()!=='GET') writes.push(request.url());};
  const onError=error=>errors.push(error.message);page.on('request',onRequest);page.on('pageerror',onError);
  await page.context().route(/https:\/\/(api\.github\.com|raw\.githubusercontent\.com)\//,route=>route.fulfill({status:403,contentType:'application/json',body:'{"message":"Unavailable client index fixture"}'}));
  await page.goto('http://127.0.0.1:4321/project-workspace/');
  await page.locator('#projectList optgroup[label="Example projects"] option').first().waitFor({state:'attached'});
  if(!await page.getByLabel('Join existing',{exact:true}).isChecked()) throw new Error('Join is not the default');
  if(await page.getByRole('heading',{name:'Connect to GitHub',exact:true}).count()) throw new Error('Connection card still exists');
  if(await page.locator('#connectionDialog').isVisible()) throw new Error('Access requested on entry');
  if(await page.locator('#projectList optgroup[label="Example projects"] option').count()!==3) throw new Error('Examples missing from the shared list');
  await page.waitForFunction(()=>document.getElementById('entryStatus').textContent.includes('Examples remain available'));
  for (const [id,client,node] of [['nordkap','Nordkap Insurance','Loss reported (FNOL)'],['nordvik','Nordvik Furniture','Range and demand plan'],['gronhoj','Grønhøj Foods','Grower contracts and crop plan']]) {
    await page.getByLabel('Existing project',{exact:true}).selectOption('example:'+id);
    if(await page.getByLabel('Your name',{exact:true}).isVisible() || await page.locator('#consent').isVisible()) throw new Error('Example requires project identity');
    await page.getByRole('button',{name:'Load example project',exact:true}).click();await page.locator('#workspace').waitFor({state:'visible'});
    if(await page.locator('#connectionDialog').isVisible()) throw new Error('Example requested access');
    if((await page.locator('#activeClient').textContent()).trim()!==client) throw new Error('Wrong example selected');
    await page.locator('#toolList').getByRole('button',{name:'Use Case Discovery Board',exact:false}).click();
    await page.frameLocator('#toolFrame').locator('.node-title').filter({hasText:node}).waitFor();
    await page.getByRole('button',{name:'Switch project',exact:true}).click();await page.locator('#entry').waitFor({state:'visible'});
  }
  if(writes.length) throw new Error('Example selection wrote to GitHub');
  await page.context().unroute(/https:\/\/(api\.github\.com|raw\.githubusercontent\.com)\//);
  await page.context().route(/https:\/\/(api\.github\.com|raw\.githubusercontent\.com)\//,async route=>{
    const request=route.request();const response=await page.request.post('http://127.0.0.1:4323/gateway',{data:{url:request.url(),options:{method:request.method(),headers:request.headers(),body:request.postData()}}});await route.fulfill({response});
  });
  await page.getByLabel('Create new',{exact:true}).check();
  await page.getByLabel('Client',{exact:true}).fill('Deferred access fixture');await page.getByLabel('Project name',{exact:true}).fill('Deferred project fixture');
  await page.getByLabel('Your name',{exact:true}).fill('Creating architect');await page.locator('#consent').check();
  await page.getByRole('button',{name:'Create project',exact:true}).click();await page.locator('#connectionDialog').waitFor({state:'visible'});
  await page.getByRole('button',{name:'Cancel',exact:true}).click();await page.locator('#connectionDialog').waitFor({state:'hidden'});
  if(await page.getByLabel('Client',{exact:true}).inputValue()!=='Deferred access fixture' || writes.length) throw new Error('Cancel lost form or created a project');
  await page.getByRole('button',{name:'Create project',exact:true}).click();await page.locator('#connectionDialog').waitFor({state:'visible'});
  await page.getByLabel('GitHub token',{exact:true}).fill('invalid-test');await page.getByRole('button',{name:'Continue',exact:true}).click();
  await page.waitForFunction(()=>document.getElementById('connectionStatus').textContent.includes('rejected this token'));
  if(await page.getByLabel('GitHub token',{exact:true}).inputValue()!=='' || writes.length) throw new Error('Invalid connection retained a token or created a project');
  // Cancel an in-flight connection; late read responses must not resume creation.
  let release;const gate=new Promise(resolve=>{release=resolve;});
  await page.context().route('https://api.github.com/user',async route=>{await gate;await route.fallback();});
  await page.getByLabel('GitHub token',{exact:true}).fill('test-valid');await page.getByRole('button',{name:'Continue',exact:true}).click();
  await page.getByRole('button',{name:'Cancel',exact:true}).click();release();
  await page.waitForFunction(()=>document.getElementById('connect').disabled===false);
  if(writes.length || await page.locator('#workspace').isVisible()) throw new Error('Late connection resumed a canceled operation');
  await page.context().unroute('https://api.github.com/user');
  await page.getByRole('button',{name:'Create project',exact:true}).click();await page.locator('#connectionDialog').waitFor({state:'visible'});
  await page.getByLabel('GitHub token',{exact:true}).fill('test-valid');await page.getByRole('button',{name:'Continue',exact:true}).click();
  await page.locator('#workspace').waitFor({state:'visible'});const id=new URL(page.url()).searchParams.get('project');
  if(!id || await page.locator('#connectionDialog').isVisible()) throw new Error('Valid connection did not resume create');
  await page.getByRole('button',{name:'Phase 2 — Strategy & Roadmap',exact:false}).click();await page.locator('#toolList').getByRole('button',{name:'AI Strategy Planning',exact:false}).click();
  const vision=()=>page.frameLocator('#toolFrame').locator('[data-eng="vision"]');await vision().waitFor();await page.waitForFunction(()=>document.querySelector('#toolFrame').contentDocument.readyState==='complete');await vision().fill('Saved client fixture work');
  await page.getByRole('button',{name:'Save now',exact:true}).click();await page.waitForFunction(()=>document.getElementById('saveStatus').textContent.startsWith('Saved to GitHub'));
  await page.locator('#projectOptions summary').click();await page.getByRole('button',{name:'Reconnect GitHub',exact:true}).click();await page.locator('#connectionDialog').waitFor({state:'visible'});
  await page.getByRole('button',{name:'Cancel',exact:true}).click();
  if(await vision().inputValue()!=='Saved client fixture work') throw new Error('Reconnect cancel changed the open tool');
  await page.getByRole('button',{name:'Forget token and leave',exact:true}).click();await page.locator('#entry').waitFor({state:'visible'});
  await page.getByLabel('Join existing',{exact:true}).check();await page.getByLabel('Existing project',{exact:true}).selectOption(id);
  if(await page.locator('#projectList optgroup[label="Example projects"] option').count()!==3) throw new Error('Clients replaced the example options');
  const savedWrites=writes.length;
  if(await page.getByLabel('Your name',{exact:true}).isVisible()) throw new Error('Viewer needs a participant name');
  await page.getByRole('button',{name:'Open project',exact:true}).click();await page.locator('#workspace').waitFor({state:'visible'});
  if(await page.locator('#connectionDialog').isVisible() || !await page.locator('#viewNotice').isVisible() || writes.length!==savedWrites) throw new Error('Viewing requested access or wrote membership');
  await page.getByRole('button',{name:'Phase 2 — Strategy & Roadmap',exact:false}).click();await page.locator('#toolList').getByRole('button',{name:'AI Strategy Planning',exact:false}).click();await vision().waitFor();
  if(await vision().inputValue()!=='Saved client fixture work') throw new Error('Joining lost saved client state');
  await page.getByRole('button',{name:'Edit with GitHub access',exact:true}).click();await page.locator('#connectionDialog').waitFor({state:'visible'});
  await page.getByRole('button',{name:'Cancel',exact:true}).click();
  if(!await page.locator('#viewNotice').isVisible() || !(await vision().evaluate(node=>node.readOnly))) throw new Error('Canceled editing removed viewing protection');
  await page.getByRole('button',{name:'Edit with GitHub access',exact:true}).click();await page.getByLabel('GitHub token',{exact:true}).fill('test-valid');await page.getByRole('button',{name:'Continue',exact:true}).click();await page.locator('#entry').waitFor({state:'visible'});
  await page.getByLabel('Your name',{exact:true}).fill('Returning editor');await page.locator('#consent').check();await page.getByRole('button',{name:'Join project',exact:true}).click();await page.locator('#workspace').waitFor({state:'visible'});
  if(await page.locator('#viewNotice').isVisible() || !await page.getByRole('button',{name:'Save now',exact:true}).isVisible()) throw new Error('Authenticated editor could not resume the existing project');
  await page.getByRole('button',{name:'Switch project',exact:true}).click();await page.locator('#entry').waitFor({state:'visible'});
  await page.setViewportSize({width:390,height:844});if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)) throw new Error('Mobile entry overflow');await page.setViewportSize({width:1440,height:1000});
  if(errors.length) throw new Error('Entry runtime errors: '+errors.join('; '));
  page.off('request',onRequest);page.off('pageerror',onError);await page.context().unroute(/https:\/\/(api\.github\.com|raw\.githubusercontent\.com)\//);
}
