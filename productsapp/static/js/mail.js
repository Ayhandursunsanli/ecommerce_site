
function sendEmail(event) {
    event.preventDefault(); // Formun varsayılan gönderme işlemini durdurur.

    const name = document.getElementById('inputName').value;
    const surname = document.getElementById('inputSurname').value;
    const email = document.getElementById('inputEmail').value;
    const message = document.getElementById('inputMessage').value;

    const subject = 'Mesaj from ' + name + ' ' + surname;
    const body = 'Email: ' + email + '\n\n' + message;

    const mailtoLink = 'mailto:lampadaaydinlatma@gmail.com' +
                        '?subject=' + encodeURIComponent(subject) +
                        '&body=' + encodeURIComponent(body);

    window.location.href = mailtoLink;
}