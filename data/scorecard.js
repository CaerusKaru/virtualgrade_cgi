
function getScores()
{
    var sc = {
        scores: [],
        summary: "",
        inp: true
    };
    var com = true;
    $('#data #scorecard input').each(function(i, obj) {
        if ($(obj).val() == '')
            com = false;
        sc["scores"].push($(obj).val());
    });

    sc["summary"] = $('#data #scorecard textarea').val();

    sc["inp"] = !com;

    return sc;
}

function scoreListen()
{
    $('#data #scorecard input').change(function () {
        var max = Number($(this).attr("max"));
        if (Number($(this).val()) > max)
            $(this).val(max);
    });
    $('#data #scorecard #save').click(function () {
        $(this).text("Saving...");
        var course = $('#data #content li.active')[0].id;
        var page = $('#data #pages li.active')[0].id;
        var scorecard = getScores();
        var student = $('#data li.active').not('#data #content li.active').not('#data #pages li.active');
        var header = {
            "classID" : course,
            "page" : page,
            "scorecard" : JSON.stringify(scorecard),
            "student" : student[0].id
        };

        $.post("cgi-bin/saveCard.cgi", header, function (data) {
/* DEBUG 
            var myWindow = window.open("", "MsgWindow", "width=200,height=100");
            myWindow.document.write(data);
*/
            if (scorecard["inp"])
                $('#data #inprogress ul').append(student[0]);
            else
                $('#data #completed ul').append(student[0]);

// will get this to sort alphabetically at some point...
//            $('#data #inprogress ul').children("li").sort();
//            $('#data #completed ul').children("li").sort();

            $('#data #scorecard #save').text("Saved!");
            window.setTimeout(function() {
                $('#data #scorecard #save').text("Save");
            }, 1500);
        });
    });
}