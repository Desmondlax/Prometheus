const primaryheader = document.querySelector(".primary-header");
const mobilenav = document.querySelector(".mobile-nav");
const primarynav = document.querySelector(".primary-nav");
const displaycount = document.getElementById("reveal-button");
const result = document.getElementById("result-container");
const canda = document.getElementById("count-holder-a");
const candb = document.getElementById("count-holder-b");
const candaname = document.getElementById("candidatea_name");
const candbname = document.getElementById("candidateb_name");
var votecountA;
var votecountB;
var vc_a;
var vc_b;
window.copystuff = copystuff;
window.onload = function displayvotecount(){};

mobilenav.addEventListener('click', () => {
    primarynav.hasAttribute("data-visible") 
    ? mobilenav.setAttribute('aria-expanded', false) 
    : mobilenav.setAttribute('aria-expanded', true);
    primarynav.toggleAttribute("data-visible");
    primaryheader.toggleAttribute("data-overlay");
})

displaycount.addEventListener('click', displayvotecount)

function copystuff(zkproofstatement) {
    // Get the text field
    zkproofstatement = document.getElementById("zkproofstatement").value = document.getElementById("zkproofstatement").innerHTML;
     // Copy the text inside the text field
    navigator.clipboard.writeText(zkproofstatement);
};

function displayvotecount() {

    votecountA = parseInt(canda.innerHTML);
    votecountB = parseInt(candb.innerHTML);

    vc_a = votecountA.toString();
    vc_b = votecountB.toString();

    document.getElementById("candidatea_votecount").textContent = vc_a;
    document.getElementById("candidateb_votecount").textContent = vc_b;

    displaycount.style.display="none"
    result.style.display="grid"
    
    if (votecountA > votecountB) {
        document.getElementById("result-container").innerText = "The winner is " + candaname.innerHTML + "!"
    }
    else if (votecountB > votecountA) {
        document.getElementById("result-container").innerText = "The winner is " + candbname.innerHTML + "!"
    }
    else {
        document.getElementById("result-container").innerText = "It's a tie!"
    }
};


