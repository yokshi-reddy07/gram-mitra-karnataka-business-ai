
let locationData = {};
async function initLocations(){
 const res=await fetch("/api/locations"); locationData=await res.json();
 const district=document.getElementById("district"); if(!district)return;
 Object.keys(locationData).sort().forEach(d=>district.add(new Option(d,d)));
 district.addEventListener("change",()=>{
   const taluk=document.getElementById("taluk");taluk.innerHTML='<option value="">Select taluk</option>';
   (locationData[district.value]||[]).forEach(t=>taluk.add(new Option(t,t)));
 });
 document.getElementById("liveLocation")?.addEventListener("click",useLocation);
}
function useLocation(){
 const status=document.getElementById("locationStatus");status.textContent="Requesting your location…";
 if(!navigator.geolocation){status.textContent="Geolocation is not supported by this browser.";return;}
 navigator.geolocation.getCurrentPosition(async pos=>{
  const {latitude,longitude}=pos.coords;
  status.textContent=`Location received: ${latitude.toFixed(5)}, ${longitude.toFixed(5)}.`;
  document.getElementById("address").value=`GPS: ${latitude.toFixed(5)}, ${longitude.toFixed(5)}`;
 },err=>{status.textContent="Location could not be accessed. You can still select district and taluk manually.";},{enableHighAccuracy:true,timeout:10000});
}
document.addEventListener("DOMContentLoaded",initLocations);
