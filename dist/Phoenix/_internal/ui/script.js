const orbWrap = document.getElementById("orbWrap");
const conversation = document.getElementById("conversation");

const STATES = {
    idle: "Awaiting wake word...",
    listening: "Listening...",
    thinking: "Thinking...",
    speaking: "Speaking..."
};

function setState(state) {

    if (!STATES[state]) return;

    orbWrap.className = `orb-wrap ${state}`;

    if (conversation) {
        conversation.innerText = STATES[state];
    }
}

function setConversation(text){

    if(conversation){
        conversation.innerText = text;
    }

}

window.PhoenixUI = {
    setState,
    setConversation
};


// --------------------
// Background Stars
// --------------------

const sparkleContainer = document.getElementById("sparkles");

for(let i=0;i<50;i++){

    const star=document.createElement("div");

    star.className="sparkle";

    const size=1+Math.random()*2;

    star.style.width=size+"px";
    star.style.height=size+"px";

    star.style.left=Math.random()*100+"vw";
    star.style.top=Math.random()*100+"vh";

    star.style.animationDuration=3+Math.random()*5+"s";
    star.style.animationDelay=Math.random()*5+"s";

    star.style.setProperty("--peak",0.2+Math.random()*0.5);

    sparkleContainer.appendChild(star);

}

setState("idle");