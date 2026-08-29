
const fmt=n=>"₹ "+Number(n||0).toLocaleString("en-IN");
async function initCategories(){
 const el=document.getElementById("category"); if(!el)return;
 const res=await fetch("/api/categories"); const data=await res.json();
 Object.keys(data).forEach(k=>el.add(new Option(k,k)));
}
async function runAnalysis(e){
 e.preventDefault();
 const button=e.target.querySelector("button[type=submit]");button.disabled=true;button.textContent="Analyzing…";
 try{
  const payload={district:district.value,taluk:taluk.value,village:village.value,category:category.value,capital:capital.value,address:address.value};
  const res=await fetch("/api/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
  if(!res.ok)throw new Error("Analysis failed");
  const result=await res.json();localStorage.setItem("gramMitraReport",JSON.stringify(result));location.href="/report";
 }catch(err){alert("Something went wrong. Please try again.");console.error(err)}
 finally{button.disabled=false;button.textContent="Generate Business Analysis →"}
}
function li(list,values){list.innerHTML="";(values||[]).forEach(v=>{const x=document.createElement("li");x.textContent=v;list.appendChild(x)})}
function renderReport(){
 const raw=localStorage.getItem("gramMitraReport");if(!raw)return;
 const d=JSON.parse(raw);document.getElementById("emptyReport")?.classList.add("hidden");document.getElementById("reportContent")?.classList.remove("hidden");
 document.getElementById("reportLocation").textContent=[d.location.district,d.location.taluk,d.location.village].filter(Boolean).join(" · ");
 document.getElementById("viability").textContent=d.viability_score+"/10";document.getElementById("summary").textContent=d.summary;
 projectCost.textContent=fmt(d.project_cost);margin.textContent=fmt(d.required_margin);loan.textContent=fmt(d.loan_90);quarterly.textContent=fmt(d.quarterly_payment);
 marketOpportunity.textContent=d.market_opportunity;competition.textContent=d.competitor_density;season.textContent=d.seasonal_analysis;pricing.textContent=d.pricing;marketReach.textContent=d.market_reach;
 workingCapital.textContent=fmt(d.working_capital)+" recommended as an indicative working-capital buffer.";scheme.textContent=d.scheme+" · "+d.interest_rate+"% p.a. estimate · "+d.repayment_years+" years.";
 li(bestBusinesses,d.best_businesses);li(threats,d.threats);
 const sg=document.getElementById("swotGrid");sg.className="swot-grid";sg.innerHTML="";
 Object.entries(d.swot||{}).forEach(([k,v])=>{const box=document.createElement("div");box.className="swot-item";box.innerHTML=`<h3>${k[0].toUpperCase()+k.slice(1)}</h3>`;const ul=document.createElement("ul");v.forEach(x=>{const l=document.createElement("li");l.textContent=x;ul.appendChild(l)});box.appendChild(ul);sg.appendChild(box)});
 document.getElementById("pdfBtn")?.addEventListener("click",async()=>{
   const b=document.getElementById("pdfBtn");b.textContent="Preparing PDF…";b.disabled=true;
   try{const r=await fetch("/download-report",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(d)});if(!r.ok)throw Error();const blob=await r.blob();const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="Gram_Mitra_Business_Report.pdf";a.click();URL.revokeObjectURL(a.href)}
   catch(e){alert("Could not generate PDF. Please try again.")}finally{b.textContent="Download PDF";b.disabled=false}
 });
}
document.addEventListener("DOMContentLoaded",()=>{initCategories();document.getElementById("analysisForm")?.addEventListener("submit",runAnalysis);renderReport()});
