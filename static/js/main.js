// Hide Loader

window.onload=function(){

const loader=document.getElementById("loader");

if(loader){

loader.style.display="none";

}

}

// Scroll Button

const topBtn=document.getElementById("topBtn");

window.onscroll=function(){

if(document.documentElement.scrollTop>300){

topBtn.style.display="block";

}else{

topBtn.style.display="none";

}

}

topBtn.onclick=function(){

window.scrollTo({

top:0,

behavior:"smooth"

});

}

// AI Button

const chatBtn=document.getElementById("chatBtn");

chatBtn.onclick=function(){

alert("🤖 AI Assistant will be added in the next phase!");

}