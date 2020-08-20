$(document).ready(function(){
    function encodeImageFileAsURL() {

        var filesSelected = $("#image").prop('files');
        if (filesSelected.length > 0) {
            var fileToLoad = filesSelected[0];

            var fileReader = new FileReader();

            fileReader.onload = function(fileLoadedEvent) {
                var srcData = fileLoadedEvent.target.result; // <--- data: base64
                console.log(srcData)
                $('#image_display').attr('src', srcData)
                $('#hidden_binary').val(srcData)

               
            }
            fileReader.readAsDataURL(fileToLoad);
        }
    }


    $('#image').change(function() {
        encodeImageFileAsURL()
    })

});
  