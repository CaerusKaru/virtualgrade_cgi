var board;
var gesture;
var line;
var brush;
var radius;
var svg, svgDoc, svgWrap, svgImage;
var svgNS = "http://www.w3.org/2000/svg";

var offsetX, offsetY;

var mode;

var width, height;

var draggingElement = null, clickX, clickY, lastMoveX = 0, lastMoveY = 0, moveX = 0, moveY = 0;

var editing = false;

var font = "Helvetica";
var fontSize = 30; // equivalent to 12pt I think...

var fontOffset = 2.5;

var fontColor = "#000000";

var initText = "Click to edit!";

var noSelect = '.insideforeign[contenteditable="false"] {-webkit-touch-callout: none; -webkit-user-select: none; -khtml-user-select: none; -moz-user-select: none; -ms-user-select: none; user-select: none; }';

var svgSpanStart = '<tspan dy="1.2em" x="'
var svgSpanEnd = '</tspan>'

var htmlNewLine = '<br>'

function init() {
    svg = document.getElementById("board");

    /* Get initial values for svg doc */
    svgDoc = svg;//.contentDocument;
    board = document.getElementById('Layer_1');
    svgImage = board.getElementById('image0');

    /* * * * * Find dimensions and offset * * * * */    

    var viewBox = board.getAttribute('viewBox');
    var viewBoxValues = viewBox.split(' ');
    svg_width = parseFloat(viewBoxValues[2]);
    svg_height = parseFloat(viewBoxValues[3]);

    abs_height = $(svg).css("height");
    abs_height = Number(abs_height.substring(0, abs_height.length-2));

    offsetX = svg_height / abs_height;
    offsetY = offsetX;

    width = svg_width / offsetX;
   
    /* * * * * Fix dimensions of the image * * * * */
    board.setAttribute("preserveAspectRatio", "xMidYMin meet");
    board.setAttribute("height", abs_height);
    board.setAttribute("width", width);
    svgImage.setAttribute("x", "0");
    svgImage.setAttribute("y", "0");

    $(svg).css("width", width+"px");

    //offsetX = width / svg.offsetWidth; /* ideally these are identical */
    //offsetY = height / svg.offsetHeight;

    board.style.cursor = "auto";

    /* * * * * Initialize art values * * * * */
    gesture = false, line = '', brush = 'black', radius = 2.5;
}

/* TODO: Zoom and pan */

function text() {
    if (mode == "drag")
        dragUnListen();
    else if (mode == "draw")
        drawUnListen();
    else if (mode == "select")
        selectUnListen();
    else if (mode == "text")
        return;
    mode = "text";
    textListen();
}

function draw() {
    if (mode == "text")
        textUnListen();
    else if (mode == "drag")
        dragUnListen();
    else if (mode == "select")
        selectUnListen();
    else if (mode == "draw")
        return;
    mode = "draw";
    drawListen();
}

function drag() {
    if (mode == "draw")
        drawUnListen();
    else if (mode == "text")
        textUnListen();
    else if (mode == "select")
        selectUnListen();
    else if (mode == "drag")
        return;
    mode = "drag";
    dragListen();
}


function selectElements() {
    if (mode == "draw")
        drawUnListen();
    else if (mode == "text")
        textUnListen();
    else if (mode == "drag")
        dragUnListen();
    else if (mode == "select")
        return;
    mode = "select";
    selectListen();
}

function dragListen() {
    setDragCursor("up");
    board.addEventListener("mouseup", dragUp, false);
    board.addEventListener("touchend", dragUp, false);
    board.addEventListener("mousemove", dragMove, false);
    board.addEventListener("touchmove", dragMove, false);

    var elements = board.children;
    for (var i = 1; i < elements.length; i++) {
        elements[i].addEventListener("touchstart", dragDown, false);
        elements[i].addEventListener("mousedown", dragDown, false);
    }
}

function dragUnListen() {
    var elements = board.children;
    board.removeEventListener("mouseup", dragUp, false);
    board.removeEventListener("touchend", dragUp, false);
    board.removeEventListener("mousemove", dragMove, false);
    board.removeEventListener("touchmove", dragMove, false);
    for (var i = 1; i < elements.length; i++) {
        elements[i].removeEventListener("mousedown", dragDown, false);
        elements[i].removeEventListener("touchstart", dragDown, false);
    }
}

function dragDown(evt) {
    setDragCursor("down");
    evt.preventDefault();
    draggingElement = evt.currentTarget;
    if (draggingElement) {
        clickX = (evt.clientX || evt.touches[0].clientX);
        clickY = (evt.clientY || evt.touches[0].clientY);
        lastMoveX = Number(draggingElement.getAttribute("dragx"));
        lastMoveY = Number(draggingElement.getAttribute("dragy"));
    }
}

function setDragCursor(type) {
    if (type == "up") {
        board.style.cursor = "move";
        board.style.cursor = "grab";
        board.style.cursor = "-moz-grab";
        board.style.cursor = "-webkit-grab";
    }
    if (type == "down") {
        board.style.cursor = "move";
        board.style.cursor = "grabbing";
        board.style.cursor = "-moz-grabbing";
        board.style.cursor = "-webkit-grabbing";
    }
}

function dragUp(evt) {
    evt.preventDefault();
    setDragCursor("up");
    if (draggingElement) {
        draggingElement.setAttribute("dragx", moveX);
        draggingElement.setAttribute("dragy", moveY);
    }
    draggingElement = null;
}

function dragMove(evt) {
    evt.preventDefault();
    if (draggingElement) {
        moveX = Number(lastMoveX + (((evt.clientX || evt.touches[0].clientX) - clickX))*offsetX);
        moveY = Number(lastMoveY + (((evt.clientY || evt.touches[0].clientY) - clickY))*offsetY);
        draggingElement.setAttribute("transform", "translate(" + moveX + "," + moveY + ")");
    }
}

function textListen() {
    board.style.cursor = "auto";
/*    board.addEventListener('mousedown', textStart);
    board.addEventListener('touchstart', textStart);

    var elements = board.getElementsByClassName("insideforeign");
    for (var i = 0; i < elements.length; i++) {
        elements[i].setAttribute("contenteditable", "true");
    }
*/

    $('svg').on('mouseenter','text', function() {
        createNode($(this));
    });
    $('svg').click(function (evt) {
        if (evt.target.className == "insideforeign" && evt.target.id == "editing")
            return;
        else if (evt.target.className == "insideforeign" && evt.target.id != "editing") {
            removeActive();
            evt.target.id = "editing";
            editing = true;
        }
        else if (evt.target.className != "insideforeign" && editing) {
                // save our progress here, set everything back to null
            removeActive();
            editing = false;
        }
        else if (evt.target.className != "insideforeign" && !editing) {
            var local = getLocalMouse(evt);
            createNode(createTextNode(local, evt));
            editing = true;
        }
    });

    $('#fontColor').slideDown();
    $('#fontSize').slideDown();
}

function getLocalMouse(evt) {
    var pt = board.createSVGPoint();
    pt.x = evt.clientX || evt.touches[0].clientX;
    pt.y = evt.clientY || evt.touches[0].clientY;
    var localpoint = pt.matrixTransform(board.getScreenCTM().inverse());

    return localpoint;
}

function removeActive()
{
    var activeNode = $('div#editing.insideforeign');
    if (activeNode.length == 0)
        return;
    var activeParent = $(activeNode).parent();
    var realText = $('svg text#'+$(activeParent).attr('id'));
    var x = Number(realText.attr("x") + realText.attr("dragx"));
    var htmlText = $(activeNode).html();
    $(realText).html(htmlToSVG(unescape(htmlText), x));
    $(realText).show();
    $(activeParent).remove();
}

// html has <br>, we replace them with <tspan>...</tspan>
// then we bookend with <tspan> and </tspan>

function htmlToSVG(htmlText, x)
{
    if (!htmlText.includes(htmlNewLine))
        return htmlText;

    var svgText = htmlText.replace(new RegExp(htmlNewLine, 'g'), svgSpanEnd + svgSpanStart + x + '">');

    svgText = svgText.replace(new RegExp('></tspan>', 'g'), '> </tspan>');

    svgText = '<tspan x="' + x + '">' + svgText + svgSpanEnd;

    return svgText;
}

// TODO: Finish this, and then also account for edge case of only &nbsp; lines (how to account for user-implemented &nbsp;?)
function SVGToHtml(svgText)
{
    console.log(unescape($(svgText).html()));

    var htmlText = $(svgText).html().replace(/&lt;tspan[^&gt;]*&gt;/, '').replace(/<tspan[^>]*>/, '').replace(/lt;tspan[^&gt;]*&gt;/g, '<br>').replace(/&lt;\/tspan&gt;/g, '').replace(/<tspan[^>]*>/g, '<br>').replace(/<\/tspan>/g, '');

    console.log(htmlText);

    return unescape(htmlText);
}

function createTextNode(point, evt)
{
    var text = document.createElementNS(svgNS, 'text');
    text.setAttributeNS(null, 'font-family', font);
    text.setAttributeNS(null, 'font-size', fontSize+"px");
    text.setAttributeNS(null, 'fill', fontColor);

    text.setAttributeNS(null, 'x', point.x);
    text.setAttributeNS(null, 'y', point.y);

    var id = Date.now();

    text.setAttributeNS(null, 'id', Date.now());

    var initSpan = document.createElementNS(svgNS, 'tspan');
    initSpan.setAttributeNS(null, "x", point.x);
    initSpan.setAttributeNS(null, "dy", "1.2em");

    var spanText = document.createTextNode(initText);

    initSpan.appendChild(spanText);
    text.appendChild(initSpan);

    text.setAttributeNS(null, "dragx", "0");
    text.setAttributeNS(null, "dragy", "0");
    $('#Layer_1').append(text);
    $('#Layer_1').html($('#Layer_1').html());

    return $('svg text#'+id);
}

function createNode(node)
{
    var dragx = Number($(node).attr("dragx"));
    var dragy = Number($(node).attr("dragy"));

    var x = Number($(node).attr("x"));
    var y = Number($(node).attr("y"));

    var fSize = $(node).attr("font-size");
    var fontFamily = $(node).attr("font-family");
    var fontColor = $(node).attr("fill");
    var curText = SVGToHtml(node);

    var myforeign = document.createElementNS(svgNS, 'foreignObject')
    var textdiv = document.createElement("div");
    var textnode = document.createTextNode(curText);

    textdiv.style.fontSize = fSize;
    textdiv.style.fontFamily = fontFamily;
    textdiv.innerHTML = curText;
    textdiv.setAttribute("contentEditable", "true");
    textdiv.setAttribute("width", "auto");
    textdiv.style.display = "inline-block";
    textdiv.style.color = fontColor;
    myforeign.setAttribute("width", "100%");
    myforeign.setAttribute("height", "100%");
    myforeign.setAttribute("id", $(node).attr('id'));
    myforeign.classList.add("foreign"); //to make div fit text
    myforeign.style.textAlign = "left";
    myforeign.style.position = "relative";
    myforeign.style.x = Number(dragx+x);
    myforeign.style.y = Number(dragy+y - fSize.substring(0,fSize.length - 2));
    textdiv.classList.add("insideforeign"); //to make div fit text

    //myforeign.setAttributeNS(null, "transform", "translate(" + Number(dragx+x) + " " + Number(dragy+y) + ")");

    document.getElementById("Layer_1").appendChild(myforeign);
    myforeign.appendChild(textdiv);
    $(node).hide();

    $(textdiv).mouseleave(function () {
        if (this.id != "editing") {
            $('svg text#'+this.parentNode.id).show();
            $(this.parentNode).remove();
        }
    });
}


function textUnListen() {
//    board.removeEventListener('mousedown', textStart);
//    board.removeEventListener('touchstart', textStart);

    $('#fontColor').hide();
    $('#fontSize').hide();
/*
    var elements = board.getElementsByClassName("insideforeign");
    for (var i = 0; i < elements.length; i++) {
        elements[i].setAttribute("contenteditable", "false");
    }
    mouseDownText = false;
*/
    removeActive();
    $('foreignobject').remove();
    $('svg').off('mouseenter','text');
    $('svg').off('click');
    $('div.insideforeign').off('mouseleave');
}

function drawUnListen() {

    $('#drawColor').hide();
    $('#drawWidth').hide();

    document.getElementById('cursor').style = "";
    board.removeEventListener('mousedown', lineStart);
    board.removeEventListener('touchstart', lineStart);
    board.removeEventListener('mousemove', lineMove);
    board.removeEventListener('touchmove', lineMove);
    board.removeEventListener('mouseup', lineEnd);
    board.removeEventListener('touchend', lineEnd);
}

function drawListen() {
    board.style.cursor = "none";

    $('#drawWidth').slideDown();
    $('#drawColor').slideDown();

    board.addEventListener('mousedown', lineStart);
    board.addEventListener('touchstart', lineStart);
    board.addEventListener('mousemove', lineMove);
    board.addEventListener('touchmove', lineMove);
    board.addEventListener('mouseup', lineEnd);
    board.addEventListener('touchend', lineEnd);
//  document.getElementById('upload').addEventListener('change', importSVG);
}

function lineStart(e) {
    line = 'M' + ((e.clientX || e.touches[0].clientX)*offsetX) + ',' + ((e.clientY || e.touches[0].clientY)*offsetY) + ' ';
    document.getElementById('cursor').style.opacity = 1;
    gesture = true;
    e.preventDefault();
}

function lineMove(e) {
    if (gesture == true) {
        line += 'L' + ((e.clientX || e.touches[0].clientX)*offsetX) + ',' + ((e.clientY || e.touches[0].clientY)*offsetY) + ' ';
        trace(e.clientX || e.touches[0].clientX, e.clientY || e.touches[0].clientY);
    }
    document.getElementById('cursor').style.top = e.clientY - radius + 'px';
    document.getElementById('cursor').style.left = e.clientX - radius + 'px';
}

function lineEnd(e) {
    line += 'L' + ((e.clientX || e.changedTouches[0].clientX)*offsetX) + ',' + ((e.clientY || e.changedTouches[0].clientY)*offsetY);
    //document.getElementById('cursor').style.opacity = 0.5;
    var dots = document.getElementsByClassName('dot');
    for(var i = dots.length - 1; i >= 0; i--) {
        dots[i].remove();
    }
    var path = document.createElementNS(svgNS, 'path');
    path.setAttributeNS(null, 'd', line);
    path.setAttributeNS(null, 'fill', 'none');
    path.setAttributeNS(null, 'stroke-linecap', 'round');
    path.setAttributeNS(null, 'stroke', document.getElementById('color').value);
    path.setAttributeNS(null, 'stroke-width', document.getElementById('width').value*2);
    //path.setAttributeNS(null, "dragx", (e.clientX || e.changedTouches[0].clientX)*offsetX);
    //path.setAttributeNS(null, "dragy", (e.clientY || e.changedTouches[0].clientY)*offsetY);
    board.appendChild(path);
    board.innerHTML = board.innerHTML;
    gesture = false;
    //localStorage.svg = new XMLSerializer().serializeToString(board);
}

function undo() {
    var paths = board.children;
    if (paths.length != 1)
        board.removeChild(paths[paths.length - 1]);
}

function clean(type) {
    var paths = board.children;
    var min = 0;
    if (type == "all")
        min = 1; // to ignore image0
    else if (type == "text")
        paths = board.querySelectorAll('text');
    else if (type == "lines")
        paths = board.querySelectorAll('path');
    if (paths.length > min && confirm("Are you sure?") == true) {
        for (i = paths.length - 1; i >= min; i--) {
            board.removeChild(paths[i]);
        }
    }
}
/*
function download() {
    var link = document.createElement('a'), time = Date.now(), svg = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">' + new XMLSerializer().serializeToString(board);
    link.id = time;
    link.setAttribute('download', 'sketch.svg');
    link.href = 'data:text/html;charset=utf-8,' + encodeURIComponent(svg);
    document.body.appendChild(link);
    document.getElementById(time).dispatchEvent(new MouseEvent('click'));
    document.getElementById(time).parentNode.removeChild(document.getElementById(time));
}
*/
function selectListen() {
    board.style.cursor = "default";
    var paths = board.children;
    for (i = paths.length - 1; i >= 1; i--) {
        $(paths[i]).addClass("selectable");
        paths[i].addEventListener("click", clickSelect, false);
    }
}

function selectUnListen() {
    $("#Layer_1>.active").removeClass("active");
    $("#Layer_1>.selectable").removeClass("selectable");
    var paths = board.children;
    for (i = paths.length - 1; i >= 1; i--) {
        paths[i].removeEventListener("click", clickSelect);
    }
    document.removeEventListener("keydown", clickRemove);
}

function clickSelect(evt) {
    var target = evt.target;
    $("#Layer_1>.active").removeClass("active");
    if (target.className == "insideforeign")
        target = target.parentElement;
    $(target).addClass("active");
    document.addEventListener("keydown", clickRemove, false);
}

function clickRemove(evt) {
    if (evt.path[0].localName == "input")
        return;
    if (evt.keyCode == 8 || evt.keyCode == 46) {
        evt.preventDefault();
        $('#Layer_1>.active').remove();
    }
}

function trace(x, y) {
    var dot = document.createElement('div');
    dot.className = 'dot';
    dot.style.top = y - radius + 'px';
    dot.style.left = x - radius + 'px';
    dot.style.background = brush;
    dot.style.width = dot.style.height = (radius * 2)/(offsetX/2) + 'px';
    document.body.appendChild(dot);
}
/*
function importSVG(e) {
    var file = e.target.files[0];
    if (file) {
        var reader = new FileReader();
        reader.onload = function (e) {
            var content = e.target.result;
            board.innerHTML = content;
        };
    }
    reader.readAsText(file);
}
*/
function setFontSize(val) {
    fontSize = val * fontOffset;
}