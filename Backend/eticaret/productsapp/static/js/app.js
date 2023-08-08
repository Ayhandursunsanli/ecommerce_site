
// inputtaki ürün adetlerinin 0 ve eksi değere düşmesi engellnir
// const adetInputs = document.getElementsByClassName("adetInput");

// for (let i = 0; i < adetInputs.length; i++) {
//     adetInputs[i].addEventListener("input", function () {
//         if (adetInputs[i].value <= 0) {
//             adetInputs[i].value = 1; // 0 veya eksi değerleri 1 olarak değiştirin veya başka bir varsayılan değer belirleyin
//         }
//     });
// }


// Yatay input butonlarının işlevi için eklendi

$('.input-number-increment').click(function () {
    var $input = $(this).parents('.input-number-group').find('.input-number');
    var val = parseInt($input.val(), 10);
    if (!isNaN(val) && val < 5) { // Kontrol ekle: 5'ten büyük olmamalı
        $input.val(val + 1);
    }
});

$('.input-number-decrement').click(function () {
    var $input = $(this).parents('.input-number-group').find('.input-number');
    var val = parseInt($input.val(), 10);
    if (!isNaN(val) && val > 1) { // Kontrol ekle: 1'den küçük olmamalı
        $input.val(val - 1);
    }
});




// Ürün detay sayfasındaki small resimlerin tıklanabilmesi için

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






