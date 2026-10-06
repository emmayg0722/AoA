// Playwright CLI verification; records stay in the loopback fixture.
async (page) => {
  const errors=[],calls=[];let viewing=false;
  page.on('pageerror',error=>errors.push(error.message));
  const github=/https:\/\/(api\.github\.com|raw\.githubusercontent\.com)\//;
  await page.context().route(github,async route=>{
    const request=route.request();if(viewing) calls.push({url:request.url(),method:request.method(),headers:request.headers()});
    const response=await page.request.post('http://127.0.0.1:4323/gateway',{data:{url:request.url(),options:{method:request.method(),headers:request.headers(),body:request.postData()}}});await route.fulfill({response});
  });
  await page.goto('http://127.0.0.1:4321/project-workspace/?example=nordkap');await page.locator('#workspace').waitFor({state:'visible'});
  await page.getByRole('button',{name:'Use as starting project',exact:true}).click();
  await page.getByLabel('Client',{exact:true}).fill('Viewer verification fixture');await page.getByLabel('Project name',{exact:true}).fill('Saved viewer fixture');await page.getByLabel('Your name',{exact:true}).fill('Fixture owner');await page.locator('#consent').check();
  await page.getByRole('button',{name:'Create project',exact:true}).click();await page.locator('#connectionDialog').waitFor({state:'visible'});await page.getByLabel('GitHub token',{exact:true}).fill('test-valid');await page.getByRole('button',{name:'Continue',exact:true}).click();await page.locator('#workspace').waitFor({state:'visible'});
  const id=new URL(page.url()).searchParams.get('project'),before=await (await page.request.get('http://127.0.0.1:4323/inspect')).json();
  await page.getByRole('button',{name:'Switch project',exact:true}).click();
  // Force a stale writer journal to prove readers only see saved GitHub values.
  const originalJournal=await page.evaluate(id=>{
    const key=`aoa_workspace_pending:emmayg0722/AoA:${id}:${sessionStorage.getItem('aoa_workspace_tab')}`;
    const journal=JSON.stringify({schemaVersion:1,id,baseline:{},values:{aoa_ai_strategy_v1:{fields:{vision:'Unsaved private writer draft'}}}});
    localStorage.setItem(key,journal);localStorage.setItem('viewer-legacy-draft','Untouched');return {key,journal};
  },id);
  // Reload drops the owner's credential and follows the invitation entry path.
  viewing=true;await page.goto('http://127.0.0.1:4321/project-workspace/?project='+id);
  await page.getByRole('button',{name:'Open project',exact:true}).waitFor();
  if(await page.getByLabel('Your name',{exact:true}).isVisible() || await page.locator('#consent').isVisible()) throw new Error('Viewer needs identity/consent');
  await page.getByRole('button',{name:'Open project',exact:true}).click();await page.locator('#viewNotice').waitFor({state:'visible'});
  if(await page.locator('#connectionDialog').isVisible() || await page.getByRole('button',{name:'Save now',exact:true}).isVisible() || await page.locator('#projectOptions').isVisible()) throw new Error('Viewer has authentication or write controls');
  const registry=await (await page.request.get('http://127.0.0.1:4321/project-workspace/registry.json')).json();
  for(const phase of registry) {
    await page.locator('#phaseNav').getByRole('button',{name:phase.title,exact:false}).click();
    for(const tool of phase.tools) {
      await page.locator('#toolList').getByRole('button',{name:tool.title,exact:false}).click();
      await page.waitForFunction(()=>document.querySelector('#toolFrame').contentDocument?.readyState==='complete');
      const result=await page.evaluate(key=>{
        const frame=document.querySelector('#toolFrame').contentWindow,doc=frame.document;
        const original=frame.localStorage.getItem(key),parentValue=ToolkitWorkspace.bridge.get(key);
        frame.localStorage.setItem(key,'{"changed":"Denied"}');frame.localStorage.removeItem(key);
        ToolkitWorkspace.bridge.set(key,'{"changed":"Denied"}',parentValue);
        return {protected:frame.localStorage.getItem(key)===original&&ToolkitWorkspace.bridge.get(key)===parentValue,
          editable:[...doc.querySelectorAll('input,textarea,select,button')].filter(node=>!node.disabled&&!node.readOnly&&!(node.tagName==='BUTTON'&&['zoomStep(1.2)','zoomStep(1/1.2)','fitBoard()','toggleFocus()','currentDimIdx--;renderDimension();','currentDimIdx++;renderDimension();','showResults();'].includes(node.getAttribute('onclick')))).length};
      },tool.key);
      if(!result.protected || result.editable) throw new Error('Unprotected view-only tool: '+tool.title+' '+JSON.stringify(result));
      if(tool.key==='aoa_usecase_board_v1') {
        const frame=page.frameLocator('#toolFrame');
        if(!await frame.getByRole('button',{name:'Zoom in',exact:true}).isEnabled()) throw new Error('View-only board cannot zoom');
        await frame.getByRole('button',{name:'Zoom in',exact:true}).click();
        const node=frame.locator('.node').first(),initial=await node.getAttribute('style'),box=await node.boundingBox();
        await page.mouse.move(box.x+20,box.y+20);await page.mouse.down();await page.mouse.move(box.x+80,box.y+80);await page.mouse.up();
        if(await node.getAttribute('style')!==initial) throw new Error('Viewer dragged a saved board node');
      }
      await page.getByRole('button',{name:'← Phase tools',exact:true}).click();
    }
  }
  await page.getByRole('button',{name:'Master project report',exact:true}).click();
  await page.frameLocator('#toolFrame').locator('[data-i18n="statPrivacy"]').waitFor();
  await page.waitForFunction(()=>document.querySelector('#toolFrame').contentDocument.readyState==='complete');
  if(!(await page.frameLocator('#toolFrame').locator('[data-i18n="statPrivacy"]').textContent()).includes('View-only')) throw new Error('Report has the wrong storage mode');
  await page.request.post('http://127.0.0.1:4323/external',{data:{path:`projects/${id}/phase-02-strategy-roadmap/ai-strategy-planning/state.json`,field:'vision',value:'New saved owner vision'}});
  await page.getByRole('button',{name:'Load latest saved work',exact:true}).click();await page.waitForFunction(()=>document.getElementById('saveStatus').textContent.startsWith('Viewing latest'));
  await page.getByRole('button',{name:'Phase 2 — Strategy & Roadmap',exact:false}).click();await page.locator('#toolList').getByRole('button',{name:'AI Strategy Planning',exact:false}).click();
  await page.waitForFunction(()=>document.querySelector('#toolFrame').contentDocument.readyState==='complete');
  if(await page.frameLocator('#toolFrame').locator('[data-eng="vision"]').inputValue()!=='New saved owner vision') throw new Error('Viewer refresh missed saved work');
  const storage=await page.evaluate(key=>({journal:localStorage.getItem(key),legacy:localStorage.getItem('viewer-legacy-draft')}),originalJournal.key);
  if(storage.journal!==originalJournal.journal || storage.legacy!=='Untouched') throw new Error('Viewing changed an editor journal or legacy draft');
  await page.getByRole('button',{name:'Switch project',exact:true}).click();await page.getByLabel('Existing project',{exact:true}).selectOption(id);await page.getByRole('button',{name:'Open project',exact:true}).click();await page.locator('#viewNotice').waitFor({state:'visible'});
  await page.getByRole('button',{name:'Switch project',exact:true}).click();if(!await page.locator('#invitationFields').evaluate(node=>node.open)) await page.locator('#invitationFields summary').click();await page.getByLabel('Project ID from an invitation',{exact:true}).fill('missing-project');await page.getByRole('button',{name:'Open project',exact:true}).click();await page.waitForFunction(()=>document.getElementById('entryStatus').textContent.includes('does not exist'));
  await page.getByLabel('Project ID from an invitation',{exact:true}).fill('../invalid');await page.getByRole('button',{name:'Open project',exact:true}).click();await page.waitForFunction(()=>document.getElementById('entryStatus').textContent.includes('Invalid project ID'));
  if(await page.locator('#connectionDialog').isVisible()) throw new Error('Invalid ID requested a token');
  await page.setViewportSize({width:390,height:844});if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)) throw new Error('Mobile viewer entry overflow');await page.setViewportSize({width:1440,height:1000});
  const after=await (await page.request.get('http://127.0.0.1:4323/inspect')).json();
  if(JSON.stringify(after.files[`projects/${id}/project.json`])!==JSON.stringify(before.files[`projects/${id}/project.json`])) throw new Error('Viewer wrote membership');
  if(calls.some(call=>call.method!=='GET'||call.headers.authorization||call.url==='https://api.github.com/user')) throw new Error('Viewer authenticated or wrote GitHub');
  if(errors.length) throw new Error('Viewer runtime errors: '+errors.join('; '));
  console.log(JSON.stringify({id,tools:45,anonymousRequests:calls.length,membersUnchanged:true,journalUnchanged:true}));
  await page.context().unroute(github);
}
