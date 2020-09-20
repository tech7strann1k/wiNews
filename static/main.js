function sendData(url) {
    console.log(url);
    var data = ('url=' + url);
    var request = new XMLHttpRequest();
    request.open('GET', `?${data}/`);
    request.send();
}