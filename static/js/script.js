const input = document.getElementById("searchInput");
const box = document.getElementById("suggestions");

if(input){

input.addEventListener("input", async ()=>{

    const text=input.value;

    if(text.length<2){

        box.innerHTML="";

        return;

    }

    const response=await fetch("/suggest?q="+text);

    const data=await response.json();

    box.innerHTML="";

    data.suggestions.forEach(word=>{

        const div=document.createElement("div");

        div.className="suggestion";

        div.textContent=word;

        div.onclick=()=>{

            input.value=word;

            box.innerHTML="";

        };

        box.appendChild(div);

    });

});

document.addEventListener("click",(e)=>{

    if(e.target!==input){

        box.innerHTML="";

    }

});

}
const themeButton = document.getElementById("themeToggle");

if(themeButton){

    if(localStorage.getItem("theme")==="light"){

        document.body.classList.add("light-mode");

        themeButton.textContent="☀️";

    }

    themeButton.addEventListener("click",()=>{

        document.body.classList.toggle("light-mode");

        if(document.body.classList.contains("light-mode")){

            localStorage.setItem("theme","light");

            themeButton.textContent="☀️";

        }else{

            localStorage.setItem("theme","dark");

            themeButton.textContent="🌙";

        }

    });

}