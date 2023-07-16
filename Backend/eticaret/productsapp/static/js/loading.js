// 3 saniye boyunca loading ekranı için -- ya bu seçilecek

window.addEventListener('DOMContentLoaded', function() {
    var loadingScreen = document.getElementById('loading-screen');
    loadingScreen.style.display = 'flex';
});

// Tüm sayfa içeriği yüklendikten sonra loading ekranını gizle
window.addEventListener('load', function() {
    setTimeout(function() {
        var loadingScreen = document.getElementById('loading-screen');
        loadingScreen.style.display = 'none';
    }, 1000);
});

//ekran ne zaman yüklenirse o zaman kaybolması için -- ya bu seçilecek

// window.addEventListener('DOMContentLoaded', function() {
//     var loadingScreen = document.getElementById('loading-screen');
//     loadingScreen.style.display = 'flex';
// });

// // Tüm sayfa içeriği yüklendiğinde loading ekranını gizle
// window.addEventListener('load', function() {
//     var loadingScreen = document.getElementById('loading-screen');
//     loadingScreen.style.display = 'none';
// });
