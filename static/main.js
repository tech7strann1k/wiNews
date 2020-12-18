(function format_html() {
    div = document.getElementsByName('div')
    console.log(div)
    images = document.getElementsByClassName('article_img')
    console.log(images)
    for(img of images) {
        if (img.naturalWidth < 500) 
            img.parentNode.removeChild(img) 
    }
})