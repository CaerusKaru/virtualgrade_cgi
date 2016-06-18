
function adminOn()
{   
    $('#data #content li').click(function () {
        $('#data #content li').removeClass("active");        
        $( this ).addClass("active");
        $.post('cgi-bin/loadAdmin.cgi', {"classID" : this.id}, function (data) {
            $('#data #admin').remove();
            $('#data #menu').remove();
            $('#data').append(data);
            adminListeners();
        });
    });
}

function adminListeners()
{
    $('#data #admin li').click(function () {
        $('#data #admin li').removeClass("active");
        $( this ).addClass("active");
        $('#data #menu').remove();
        var course = $('#data #content li.active')[0].id;
        $.post("cgi-bin/loadMenu.cgi", {"menu":this.id, "classID":course}, function (data) {
            $('#data').append(data);
            menuListeners();                
        });
    });        
}

function menuListeners()
{
    // this listener is for the publishing page only, which uses the special toggle button
    $('#data #menu ul li label input.switch-input').click(function () {
        var page = $(this).parent().parent()[0].id;
        var publish = this.checked ? "y" : "n";
        var course = $('#data #content li.active')[0].id;
        if (this.id != "com")
            $.post("cgi-bin/publish.cgi", {"classID":course, "publish":publish, "page":page}, function (data) {
                var myWindow = window.open("", "MsgWindow", "width=200,height=100");
                myWindow.document.write(data);
            });
        else
            $.post("cgi-bin/publish_com.cgi", {"classID":course,"publish":publish, "page":page});
    });
}
