
// inputtaki ürün adetlerinin 0 ve eksi değere düşmesi engellnir
const adetInputs = document.getElementsByClassName("adetInput");

for (let i = 0; i < adetInputs.length; i++) {
    adetInputs[i].addEventListener("input", function () {
        if (adetInputs[i].value <= 0) {
            adetInputs[i].value = 1; // 0 veya eksi değerleri 1 olarak değiştirin veya başka bir varsayılan değer belirleyin
        }
    });
}






var MainImg = document.getElementById('MainImg');
var smallimg = document.getElementsByClassName('small-img');

smallimg[0].onclick = function () {
    MainImg.src = smallimg[0].src;
}
smallimg[1].onclick = function () {
    MainImg.src = smallimg[1].src;
}
smallimg[2].onclick = function () {
    MainImg.src = smallimg[2].src;
}








