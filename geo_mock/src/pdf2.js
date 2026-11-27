const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
const a=process.argv;
await p.goto('file://'+a[2],{waitUntil:'networkidle'});await p.pdf({path:a[4],format:'A4',printBackground:true,preferCSSPageSize:true});
await p.goto('file://'+a[3],{waitUntil:'networkidle'});await p.pdf({path:a[5],format:'A4',printBackground:true,margin:{top:'15mm',bottom:'16mm',left:'15mm',right:'15mm'},displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="width:100%;text-align:center;font-size:10px;font-family:IPAGothic">- <span class="pageNumber"></span> -</div>'});
await b.close();})();
