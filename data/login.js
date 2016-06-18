
function addListeners(user) {

        $('#nav li:not(#logo)').click(function () {
                $('#nav li:not(#logo)').removeClass("active");
                $( this ).addClass("active");
            $('#data').html("");                
            if (this.id == "grades") {
                $.post("cgi-bin/gradePage.cgi", {}, function (data) {
                    $('#data').html(data);
                    gradeOn();
                });
            }
            else if (this.id == "grading") {
                $.post("cgi-bin/gradingPage.cgi", {}, function (data) {
                    $('#data').html(data);
                    gradingOn();
                });
            }
            else if (this.id == "admin") {
                $.post("cgi-bin/adminPage.cgi", {}, function (data) {
                    $('#data').html(data);
                    adminOn();
                });
            }
        });
}

function login() {
    $.post("cgi-bin/loadUser.cgi", {}, function (data) {

        var admin_list = data.admin.split(",");
        var grading_list = data.grading.split(",");
        var user = data.user;

        var isGrader = (grading_list.length != 0);
        var isAdmin = (admin_list.length != 0);

        if (!isAdmin)
            $('#nav #admin').css("display", "none");
        else
            $('#nav #admin').css("visibility", "visible");
        if (!isGrader)
            $('#nav #grading').css("display", "none");
        else
            $('#nav #grading').css("visibility", "visible");

        $('#nav #namespace').css("visibility", "visible");

        $('#nav #grades').addClass("active");
        $('#nav #name').append(user);

        $.post("cgi-bin/gradePage.cgi", {"username": user}, function (data) {
            $('#data').html(data);
            gradeOn();
        });
        addListeners(user);
    });
}