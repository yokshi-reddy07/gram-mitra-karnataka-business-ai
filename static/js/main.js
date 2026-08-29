
const translations = {
 en:{nav_home:"Home",nav_dashboard:"Dashboard",nav_analysis:"Analysis",nav_copilot:"AI Copilot",nav_login:"Login",nav_signup:"Get Started",hero_title:"Turn local insight into a stronger business.",hero_text:"Gram Mitra helps aspiring micro-entrepreneurs understand market opportunity, competition, seasonal demand, project cost and indicative financing.",hero_cta:"Start Business Analysis →",hero_secondary:"See how it works",features_title:"Everything needed for a better first business decision.",footer:"Smarter decisions for local entrepreneurs"},
 kn:{nav_home:"ಮುಖಪುಟ",nav_dashboard:"ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",nav_analysis:"ವ್ಯವಹಾರ ವಿಶ್ಲೇಷಣೆ",nav_copilot:"AI ಸಹಾಯಕ",nav_login:"ಲಾಗಿನ್",nav_signup:"ಪ್ರಾರಂಭಿಸಿ",hero_title:"ಸ್ಥಳೀಯ ಮಾಹಿತಿಯನ್ನು ಉತ್ತಮ ವ್ಯವಹಾರ ನಿರ್ಧಾರವಾಗಿ ರೂಪಿಸಿ.",hero_text:"ಗ್ರಾಮ ಮಿತ್ರ ಮಾರುಕಟ್ಟೆ ಅವಕಾಶ, ಸ್ಪರ್ಧೆ, ಋತುಮಾನ, ಯೋಜನಾ ವೆಚ್ಚ ಮತ್ತು ಹಣಕಾಸಿನ ಅಂದಾಜನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ.",hero_cta:"ವ್ಯವಹಾರ ವಿಶ್ಲೇಷಣೆ ಪ್ರಾರಂಭಿಸಿ →",hero_secondary:"ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ ನೋಡಿ",features_title:"ನಿಮ್ಮ ಮೊದಲ ವ್ಯವಹಾರ ನಿರ್ಧಾರಕ್ಕೆ ಬೇಕಾದ ಮುಖ್ಯ ಮಾಹಿತಿ.",footer:"ಸ್ಥಳೀಯ ಉದ್ಯಮಿಗಳಿಗೆ ಉತ್ತಮ ನಿರ್ಧಾರಗಳು"}
};
function applyLanguage(lang){
 document.documentElement.lang=lang==="kn"?"kn":"en";
 document.querySelectorAll("[data-i18n]").forEach(el=>{const k=el.dataset.i18n;if(translations[lang][k])el.textContent=translations[lang][k]});
 localStorage.setItem("gramMitraLang",lang);
 const b=document.getElementById("langToggle");if(b)b.textContent=lang==="en"?"ಕನ್ನಡ":"English";
}
document.addEventListener("DOMContentLoaded",()=>{let lang=localStorage.getItem("gramMitraLang")||"en";applyLanguage(lang);document.getElementById("langToggle")?.addEventListener("click",()=>applyLanguage((localStorage.getItem("gramMitraLang")||"en")==="en"?"kn":"en"))});
