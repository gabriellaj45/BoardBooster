$(document).ready(function() {
    $('#thePic').click(function(){
        $.ajax({
           url: "{{ url_for ('getImage') }}",
           type: "GET",
           success: function(response) {
               $("#theImage").attr('src', '/static/' + response);
           },
          error: function(xhr) {
            //Do Something to handle error
          }
        });
    });
});