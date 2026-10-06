// Isolated API fixture. No request from this fixture reaches GitHub.
export class FakeGithub {
  constructor() {
    this.snapshots = new Map([['head-0', {'projects/index.json':{schemaVersion:1,projects:[]}}]]);
    this.trees = new Map();this.commits = new Map();this.head='head-0';this.count=0;
    this.failUpdate=false;this.beforeUpdate=null;this.calls=[];
  }
  async request(url,options={}) {
    const path=new URL(url).pathname;const method=options.method || 'GET';const body=options.body ? JSON.parse(options.body) : undefined;
    this.calls.push({path,method,body,headers:options.headers});
    const response=(value,status=200) => new Response(JSON.stringify(value),{status});
    if (new URL(url).hostname==='raw.githubusercontent.com') {
      const [,owner,repo,ref,...file]=path.split('/').map(decodeURIComponent);
      if (owner!=='test' || repo!=='toolkit') throw new Error('Unexpected raw repository');
      const value=this.snapshots.get(ref)?.[file.join('/')];
      return value===undefined ? response({},404) : response(value);
    }
    if (path==='/user') return (options.headers?.Authorization || options.headers?.authorization)==='Bearer test-valid' ? response({login:'test-architect'}) : response({message:'Bad credentials'},401);
    if (path==='/repos/test/toolkit') return response({private:false,permissions:{push:true}});
    if (path.endsWith('/git/ref/heads/codex/project-data')) return response({object:{sha:this.head}});
    if (path.includes('/contents/')) {
      const file=decodeURIComponent(path.split('/contents/')[1]);const ref=new URL(url).searchParams.get('ref');
      const value=this.snapshots.get(ref)?.[file];return value===undefined ? response({},404) : response({encoding:'base64',content:Buffer.from(JSON.stringify(value)).toString('base64')});
    }
    if (method==='GET' && path.includes('/git/commits/')) return response({tree:{sha:'tree:'+path.split('/').at(-1)}});
    if (method==='POST' && path.endsWith('/git/trees')) {
      const files=structuredClone(this.snapshots.get(body.base_tree.replace('tree:','')));if (!files) throw new Error('Missing base tree');
      for (const entry of body.tree) files[entry.path]=JSON.parse(entry.content);
      const sha='new-tree-'+(++this.count);this.trees.set(sha,files);return response({sha});
    }
    if (method==='POST' && path.endsWith('/git/commits')) {
      const sha='new-head-'+(++this.count);this.commits.set(sha,body);this.snapshots.set(sha,this.trees.get(body.tree));return response({sha});
    }
    if (method==='PATCH' && path.includes('/git/refs/heads/')) {
      if (body.force!==false) throw new Error('Unsafe branch update');
      if (this.failUpdate) return response({message:'Write rejected'},403);
      if (this.beforeUpdate) {const action=this.beforeUpdate;this.beforeUpdate=null;action();}
      if (this.commits.get(body.sha).parents[0]!==this.head) return response({message:'Not a fast forward'},422);
      this.head=body.sha;return response({object:{sha:this.head}});
    }
    throw new Error('Unexpected API request: '+method+' '+path);
  }
  external(change) {
    const files=structuredClone(this.snapshots.get(this.head));change(files);
    this.head='external-'+(++this.count);this.snapshots.set(this.head,files);
  }
}
