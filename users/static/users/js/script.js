const hamburger = document.querySelector("#toggle-btn")

hamburger.addEventListener("click",function(){
    document.querySelector("#sidebar").classList.toggle("expand");
});


function toggleChevron(element) {
    const chevronIcon = element.querySelector('.chevron-icon');
    chevronIcon.classList.toggle('rotate');
}
