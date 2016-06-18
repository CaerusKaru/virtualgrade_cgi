
var requestPage = new XMLHttpRequest();
var requestStudents = new XMLHttpRequest();
var loadCard = new XMLHttpRequest();

function gradingOn()
{   
    $('#data #content li').click(function () {
        $('#data #content li').removeClass("active");
        $( this ).addClass("active");
        requestPage.abort();
        requestStudents.abort();
        loadCard.abort();
        $('#data #pages').remove();
        $('#data #scorecard').remove();
        $('#data #students').remove();
        $('#data #inprogress').remove();
        $('#data #completed').remove();
        $('#data #error').remove();
        $('#data #pdfpages').remove();

        requestPage = $.post("cgi-bin/loadPages.cgi", {"classID" : this.id }, function (data) {
            $('#data').append(data);
            onePageOn();
        });
    });
}

function onePageOn()
{
    $('#data #pages li').click(function() {
        $('#data #pages li').removeClass("active");
        $( this ).addClass("active"); 
        var course = $('#data #content li.active')[0].id;
        requestStudents.abort();
        loadCard.abort();
        $('#data #students').remove();
        $('#data #inprogress').remove();
        $('#data #completed').remove();
        $('#data #error').remove();
        $('#data #scorecard').remove();
        $('#data #pdfpages').remove();

        requestStudents = $.post("cgi-bin/loadGrading.cgi", {"classID" : course, "page" : this.id}, function (data) {
/* DEBUG 
            var myWindow = window.open("", "MsgWindow", "width=200,height=100");
            myWindow.document.write(data);
*/
            $('#data').append(data);
            studentListen();
            pdfListen();
        });
    });
}

function studentSearch(course, student, page, pageNum)
{
    var searchHeader = {
        "classID" : course,
        "page" : page,
        "student" : student,
        "pageNum" : pageNum
    };
    loadCard = $.post("cgi-bin/loadScorecard.cgi", searchHeader, function (data) {
         if (data.search("console") == -1) {
             alert("Unable to load student to grade");
             return;
         }

        $('#console').remove();
        $('#data #scorecard').remove();
/* DEBUG
            var myWindow = window.open("", "MsgWindow", "width=200,height=100");
            myWindow.document.write(data);
*/
        $('body').append(data);
    });
}

function getPDFPage(course, page, pageNum, prev)
{
    var randomHeader = {
        "classID" : course,
        "page" : page,
        "student" : "",
        "pageNum" : pageNum,
        "prev" : prev
    };
    loadCard = $.post("cgi-bin/loadScorecard.cgi", randomHeader, function (data) {

        if (data.search("console") == -1) {
            alert("Unable to load student to grade");
            return;
        }
        $('#console').remove();
        $('#data #scorecard').remove();
/* DEBUG
            var myWindow = window.open("", "MsgWindow", "width=200,height=100");
            myWindow.document.write(data);
*/
         $('body').append(data);
     });
}

function pdfListen()
{
    $('#data #pdfpages a:not(progress)').click(function() {
        var inner = this.text;
        if (inner == "Search") {
            var course = $('#data #content li.active')[0].id;
            var stuSearch = $(this).siblings('input').val();
            var pageNum = $(this).siblings('a').html();
            var page = $('#data #pages li.active')[0].id;
            studentSearch(course, stuSearch, page, pageNum);
        }
        else {
            var course = $('#data #content li.active')[0].id;
            var page = $('#data #pages li.active')[0].id;
            getPDFPage(course, page, inner, "");
        }
    });
}

function genScoring()
{
    $('#nav').hide();
    $('#data').hide();
    $('#console').show();
    $('body').addClass('drawing');
    addPDFListen();
    init();
}

function addPDFListen()
{
    $('#score').on("input", function() {
        $('#score_value').val(this.value);
    });
    $('#score_value').on("input", function() {
        if (Number(this.value) > Number($(this).attr("max")))
            this.value = $(this).attr("max");
        $('#score').val(this.value);
    });
    $('#exCredit').on("input", function() {
        $('#exCredit_value').val(this.value);
    });
    $('#exCredit_value').on("input", function() {
        if (Number(this.value) > Number($(this).attr("max")))
            this.value = $(this).attr("max");
        $('#exCredit').val(this.value);
    });

}

function maxScore()
{
    $('#score').val($('#score').attr("max"));
    $('#score_value').val($('#score_value').attr("max"));
}

function maxExtra()
{
    $('#exCredit').val($('#exCredit').attr("max"));
    $('#exCredit_value').val($('#exCredit_value').attr("max"));
}

function save(type) {
    var curStu = $('#studentValue').html();
    var course = $('#data #content li.active')[0].id;
    var pageNum = $('#pageValue').html();
    var page = $('#data #pages li.active')[0].id;

    saveSVG(course, page, pageNum, curStu);
    if (type == "close")
        closePDF();
    else if (type == "next") {
        getPDFPage(course, page, pageNum, curStu);        
    }
}

function getPDFScore()
{
    var sc = [];
    var score = $('#score_value').val();
    var ex = $('#exCredit_value').val();

    sc.push(score);
    sc.push(ex);

    return sc;
}

function saveSVG(course, page, pageNum, curStu)
{
    var svgFile = $('#Layer_1').prop('outerHTML');
    var sc = JSON.stringify(getPDFScore());

    // (1) compile necessary information to save a file, which is student (dir), course.assignment.page (filled with svgFile)

    $.post("cgi-bin/savePDF.cgi", {"classID":course, "page":page, "student":curStu, "pageNum":pageNum, "svg":svgFile, "sc":sc}, function (data) {
/* DEBUG 
            var myWindow = window.open("", "MsgWindow", "width=200,height=100");
            myWindow.document.write(data);
*/
    });
}

function goSearch()
{
    var stuName = $('#studentSearch').val();
    if (stuName == "") {
        alert("Error: no student name given");
        return;
    }
    var course = $('#data #content li.active')[0].id;
    var page = $('#data #pages li.active')[0].id;
    var pageNum = $('#pageValue').html();
    studentSearch(course, stuName, page, pageNum);
}

function pageSearch()
{
    var pageNum = $('#pageSearch').val();
    if (pageNum == "") {
        alert("Error: no page number given");
        return;
    }
    var course = $('#data #content li.active')[0].id;
    var page = $('#data #pages li.active')[0].id;       
    getPDFPage(course, page, pageNum, "");
}

function skip(type) {
    var curStu = $('#studentValue').html();
    var course = $('#data #content li.active')[0].id;
    var pageNum = $('#pageValue').html();
    var page = $('#data #pages li.active')[0].id;

    if (type == "close")
        closePDF();
    else if (type == "next") {
        getPDFPage(course, page, pageNum, curStu);
    }
}

function closePDF()
{
    $('#console').remove();
    $('#nav').show();
    $('#data').show();
    $('#pdfpages').remove();
    $('body').removeClass('drawing');
    var course = $('#data #content li.active')[0].id;
    var page = $('#data #pages li.active')[0].id;
    requestStudents = $.post("cgi-bin/loadGrading.cgi", {"classID" : course, "page" : page}, function (data) {
/* DEBUG 
            var myWindow = window.open("", "MsgWindow", "width=200,height=100");
            myWindow.document.write(data);
*/
        $('#data').append(data);
        pdfListen();
    });
}

function studentListen()
{
    $('#data #students li:not(.title)').click(function() {
        $('#data #students li').removeClass("active");
        $('#data #inprogress li').removeClass("active");
        $('#data #completed li').removeClass("active");
        $( this ).addClass("active");
        var username = this.id;
        var course = $('#data #content li.active')[0].id;
        var page = $('#data #pages li.active')[0].id;
        loadCard.abort();
        $('#data #scorecard').remove();
        loadCard = $.post("cgi-bin/loadScorecard.cgi", {"classID" : course, "page" : page, "student" : username}, function (data) {
//              $('#data #scorecard').remove();
              $('body').append(data);

                    $('#nav').hide();
                $('#data').hide();
                $('#console').show();

              scoreListen();
        });
    });
    $('#data #inprogress li:not(.title)').click(function() {
        $('#data #students li').removeClass("active");
        $('#data #inprogress li').removeClass("active");
        $('#data #completed li').removeClass("active");
        $( this ).addClass("active");
        var username = this.id;
        var course = $('#data #content li.active')[0].id;
        var page = $('#data #pages li.active')[0].id;
        loadCard.abort();
        $('#data #scorecard').remove();
        loadCard = $.post("cgi-bin/loadScorecard.cgi", {"classID" : course, "page" : page, "student" : username}, function (data) {
//              $('#data #scorecard').remove();
              $('body').append(data);
                $('#nav').hide();
                $('#data').hide();
                $('#console').show();

              scoreListen();
        });
    });
    $('#data #completed li:not(.title)').click(function() {
        $('#data #students li').removeClass("active");
        $('#data #inprogress li').removeClass("active");
        $('#data #completed li').removeClass("active");
        $( this ).addClass("active");
        var username = this.id;
        var course = $('#data #content li.active')[0].id;
        var page = $('#data #pages li.active')[0].id;
        loadCard.abort();
        $('#data #scorecard').remove();
        loadCard = $.post("cgi-bin/loadScorecard.cgi", {"classID" : course, "page" : page, "student" : username}, function (data) {
//              $('#data #scorecard').remove();
              $('body').append(data);

                $('#nav').hide();
                $('#data').hide();
                $('#console').show();

              scoreListen();
        });
    });
}          
