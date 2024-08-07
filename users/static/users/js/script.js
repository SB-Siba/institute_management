let sidebar = document.querySelector(".sidebar");
let sidebarBtn = document.querySelector(".sidebarBtn");
sidebarBtn.onclick = function() {
  sidebar.classList.toggle("active");
  if(sidebar.classList.contains("active")){
  sidebarBtn.classList.replace("bx-menu" ,"bx-menu-alt-right");
}else
  sidebarBtn.classList.replace("bx-menu-alt-right", "bx-menu");
}
const hamburger = document.querySelector("#toggle-btn")

hamburger.addEventListener("click",function(){
    document.querySelector("#sidebar").classList.toggle("expand");
});


function toggleChevron(element) {
    const chevronIcon = element.querySelector('.chevron-icon');
    chevronIcon.classList.toggle('rotate');
}