// Two browser participants, using an isolated API fixture and dummy credentials.
async (page) => {
  await page.getByRole('button',{name:'Phase 2 — Strategy & Roadmap',exact:false}).click();
  await page.locator('#toolList').getByRole('button',{name:'AI Strategy Planning',exact:false}).click();
  const first=page.frameLocator('#toolFrame');await first.locator('[data-eng=vision]').waitFor();
  await page.context().route('https://api.github.com/user',async route => {
    if (route.request().headers().authorization==='Bearer test-second') await route.fulfill({json:{login:'fixture-teammate'}});
    else await route.fallback();
  });
  const second=await page.context().newPage();await second.goto(page.url());
  await second.getByLabel('GitHub token',{exact:true}).fill('test-second');
  await second.getByRole('button',{name:'Connect',exact:true}).click();await second.getByText('Connected as fixture-teammate.',{exact:true}).waitFor();
  await second.getByLabel('Your name',{exact:true}).fill('Second browser participant');await second.getByLabel('I understand the repository visibility').check();
  await second.getByRole('button',{name:'Join project',exact:true}).click();await second.locator('#members').filter({hasText:'Second browser participant'}).waitFor();
  if (!(await second.locator('#members').textContent()).includes('Browser tester')) throw new Error('Joining replaced another member');
  await second.getByRole('button',{name:'Phase 2 — Strategy & Roadmap',exact:false}).click();
  await second.locator('#toolList').getByRole('button',{name:'AI Strategy Planning',exact:false}).click();
  const collaborator=second.frameLocator('#toolFrame');await collaborator.locator('[data-eng=metrics]').fill('Second participant saved metrics');
  await second.getByRole('button',{name:'Save now',exact:true}).click();await second.locator('#saveStatus').filter({hasText:'Saved to GitHub'}).waitFor();
  await first.locator('[data-eng=vision]').fill('First participant saved vision');
  await page.getByRole('button',{name:'Save now',exact:true}).click();await page.locator('#saveStatus').filter({hasText:'Saved to GitHub'}).waitFor();
  const id=new URL(page.url()).searchParams.get('project');const state=await (await page.request.get('http://127.0.0.1:4323/inspect')).json();
  const data=state.files[`projects/${id}/phase-02-strategy-roadmap/ai-strategy-planning/state.json`].data;
  if (data.fields.vision!=='First participant saved vision' || data.fields.metrics!=='Second participant saved metrics') throw new Error('Two-browser collaboration lost a field');
  await second.close();
}
