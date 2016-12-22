/**
 * Created by geddy on 21/12/2016.
 */
var frm = $('#buy');
frm.submit(function (ev) {
    $.ajax({
        type: frm.attr('method'),
        url: "/buyCurrency",
        headers: {  "token": ""+sessionStorage['token'],
                    "uid":sessionStorage["uid"]
                },
        data: frm.serialize(),
        success: function (data) {
            console.log(data)

        }
    });
    ev.preventDefault();
});