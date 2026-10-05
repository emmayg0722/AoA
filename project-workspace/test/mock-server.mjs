// Disposable loopback-only browser test gateway. Never deploy or use as a backend.
import {createServer} from 'node:http';
import {FakeGithub} from './fake-github.mjs';
const api=new FakeGithub();
const server=createServer(async (request,response) => {
  try {
    if (request.url==='/inspect') {response.setHeader('Content-Type','application/json');response.end(JSON.stringify({head:api.head,files:api.snapshots.get(api.head)}));return;}
    let raw='';for await (const chunk of request) raw+=chunk;const body=JSON.parse(raw || '{}');
    if (request.url==='/fail') {api.failUpdate=body.enabled;response.end('{}');return;}
    if (request.url==='/external') {api.external(files=>{files[body.path].data.fields[body.field]=body.value;});response.end('{}');return;}
    if (request.url!=='/gateway') {response.writeHead(404);response.end('{}');return;}
    const url=body.url.replace('/repos/emmayg0722/AoA','/repos/test/toolkit');const result=await api.request(url,body.options);
    response.writeHead(result.status,{'Content-Type':'application/json'});response.end(await result.text());
  } catch (error) {response.writeHead(500);response.end(JSON.stringify({message:error.message}));}
});
server.listen(4323,'127.0.0.1',()=>console.log('Isolated GitHub API fixture on 127.0.0.1:4323'));
