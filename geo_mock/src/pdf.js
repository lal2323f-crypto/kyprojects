const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
for(let i=2;i<process.argv.length;i+=2){await p.goto('file://'+process.argv[i],{waitUntil:'networkidle'});await p.pdf({path:process.argv[i+1],format:'A4',printBackground:true,preferCSSPageSize:true});}
await b.close();})();
