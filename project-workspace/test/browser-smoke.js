// Run with playwright-cli run-code --filename after installing the isolated gateway route.
async (page) => {
  const errors=[];const onError=error=>errors.push(error.message);page.on('pageerror',onError);
  const registry=await (await page.request.get('http://127.0.0.1:4321/project-workspace/registry.json')).json();
  for (const phase of registry) for (const tool of phase.tools) {
    await page.getByRole('button',{name:phase.title,exact:false}).click();
    await page.locator('#toolList').getByRole('button',{name:tool.title,exact:false}).click();
    const frame=page.frameLocator('#toolFrame');await frame.locator('body').waitFor();
    const expected=new URL(tool.href,'http://127.0.0.1:4321/').pathname;
    await page.waitForFunction(expected => document.querySelector('#toolFrame').contentWindow.location.pathname===expected,expected);
    await frame.locator('h1').first().waitFor();
    const bridged=await page.locator('#toolFrame').evaluate(iframe => !!Object.getOwnPropertyDescriptor(iframe.contentWindow,'localStorage').value);
    if (!bridged) throw new Error('Storage was not scoped: '+tool.title);
    if (tool.key==='aoa_usecase_board_v1' && await frame.getByRole('button',{name:'● Go live',exact:true}).isVisible()) throw new Error('Nested board connection visible');
  }
  page.off('pageerror',onError);if (errors.length) throw new Error('Tool runtime errors: '+errors.join('; '));
}
