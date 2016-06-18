
var requestPage = new XMLHttpRequest();
var requestCard = new XMLHttpRequest();
var myWindow = null;

function gradeOn()
{   
    $('#data #content li').click(function () {
        $('#data #content li').removeClass("active");
        $('#data #grades').remove();
        $( this ).addClass("active");
        requestPage.abort();
        requestCard.abort();
        requestPage = $.post("cgi-bin/loadAssign.cgi", {"classID" : this.id }, function (data) {
            $('#data #grades').remove();
            $('#data').append(data);
            downloadOn();
        });
    });
}

function downloadOn()
{
    $('#data #grades a').click(function () {
        assignment = $($(this).parent().siblings()[0]).text();
        var course = $('#data #content li.active')[0].id;
        if (myWindow && !myWindow.closed)
                myWindow.close();

        else {
            if (this.text == "scorecard") {
                requestCard = $.post("cgi-bin/loadROC.cgi", {"classID" : course, "page" : assignment}, function (data) {
                    myWindow = window.open("", "commentWindow", "");
                    if (myWindow)
                            myWindow.document.write(data);
                    else 
                        alert("Warning: you must enable popups or use a non-Safari browser");
                });
            }
            else if (this.text == "pdf") {
                $('#courseDownload').val(course);
                $('#pageDownload').val(assignment);
                $("#downloadPDF").submit();
            }

/*            requestCard = $.ajax({
                url: "cgi-bin/loadROC.cgi",
                type: "POST",
                dataType: 'binary',
                //headers:{'Content-Type':'application/pdf'},
                data:{"classID" : course, "page" : assignment},
                processData: false,
                success: function(data) {
                    myWindow = window.open("", "commentWindow", "");
                    if (myWindow) {
                        myWindow.document.write(data);
                    }
                    else 
                        alert("Warning: you must enable popups or use a non-Safari browser");
                }
            });*/
        }

    });
}