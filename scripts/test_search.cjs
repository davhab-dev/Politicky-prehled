const fs=require('fs'),vm=require('vm'),assert=require('assert');
let code=fs.readFileSync(require('path').join(__dirname,'../app.js'),'utf8');
code=code.slice(code.indexOf('// Search all saved'),code.indexOf('function setupSearch()'));
const fields={'#search':{value:'Letná'},'#searchSort':{value:'relevance'}};
const ctx={Map,URL,Date,AbortSignal,console,$:k=>fields[k],archiveEntries:[]};vm.createContext(ctx);
const row=(id,title,importance,date)=>({url:'https://example.com/'+id,title,importance,published_at:date||'2026-11-11T00:00:00Z'});
ctx.latestData={articles:[row('a','Protest na Letné',''),row('b','Jiná zpráva','Akce na Letnou navazuje.'),row('c','Letní dovolená','')]};
vm.runInContext(code,ctx);
vm.runInContext(`searchCache.set('old',{updated_at:'2026-11-01T00:00:00Z',articles:${JSON.stringify([row('a','Protest na Letné',''),row('d','Starší článek','Dav na Letné','2026-11-01T00:00:00Z')])}})`,ctx);
for(const q of ['Letná','letne','LETNOU']){fields['#search'].value=q;assert.equal(vm.runInContext('searchArticles().length',ctx),3);}
fields['#searchSort'].value='newest';assert.equal(vm.runInContext('searchArticles().at(-1).title',ctx),'Starší článek');
fields['#search'].value='letna protest';assert.equal(vm.runInContext('searchArticles().length',ctx),1);
fields['#search'].value='nesmysl';assert.equal(vm.runInContext('searchArticles().length',ctx),0);
assert.equal(vm.runInContext(`searchKey({url:'https://x.cz/a?utm_source=z#anchor'})`,ctx),'https://x.cz/a');
assert.equal(vm.runInContext(`wordMatches('letni','letna')`,ctx),false);
assert.equal(vm.runInContext(`fieldMatches('Česká vláda','ceska')`,ctx),true);
console.log('PASS: archived articles, hidden analyses, inflections, accents, no summer false match, deduplication, sorting, multiple terms, empty results, URL normalization');
