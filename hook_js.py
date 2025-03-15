hook_js = """(function() {
    window.xpaths = [];
    var rect = {};
    window.mouseIsDown = false;
    window.end_select = false;
    window.copyTextToClipboard = function (xpath) {
        // e.stopPropagation();
        try {
            navigator.clipboard.writeText(xpath);
            console.log('Text copied to clipboard');
        } catch (err) {
            console.error('Could not copy text: ', err);
        }
    }
    window.resetSelect = function() {
        window.mouseIsDown = false;
        window.end_select = false;
        selectionDiv.style.width = "0px"
        selectionDiv.style.height = "0px"
        selectionDiv.innerHTML = ""
        console.log("重新选择")
    }
    function createSelectionDiv() {
        var selectionDiv = document.getElementById("crawler-area")
        if (!selectionDiv) {
            var selectionDiv = document.createElement('div');
            selectionDiv.id = "crawler-area"
            selectionDiv.style.border = "3px dashed #0099FF";
            selectionDiv.style.position = "absolute";
            selectionDiv.style.background = "#ffffff";
            selectionDiv.style.opacity = 0.7;
            selectionDiv.style.pointerEvents = "none";
            selectionDiv.style.zIndex = "1000";
            selectionDiv.style.color = "#000";
            selectionDiv.style.fontWeight = "Bold"
            selectionDiv.style.pointerEvents = "auto"
            document.body.appendChild(selectionDiv);
        }
        return selectionDiv;
    }
    var selectionDiv = createSelectionDiv();
    document.addEventListener('mousedown', function(e) {
        if (window.end_select || window.mouseIsDown ) return;
        window.mouseIsDown = true;
        rect.startX = e.pageX;
        rect.startY = e.pageY;
        console.log(e.pageX, e.pageY, e.clientX, e.clientY);
        selectionDiv.style.left = e.pageX + 'px';
        selectionDiv.style.top = e.pageY + 'px';
        selectionDiv.innerText = selectionDiv.style.left + " " + selectionDiv.style.top + " " + rect.startX + " " +rect.startY ;
    });
    document.addEventListener('mousemove', function(e) {
        if (window.end_select || !window.mouseIsDown ) return;
        var x = Math.min(e.pageX, rect.startX);
        var y = Math.min(e.pageY, rect.startY);
        var w = Math.abs(e.pageX - rect.startX);
        var h = Math.abs(e.pageY - rect.startY);
        selectionDiv.style.left = x + 'px';
        selectionDiv.style.top = y + 'px';
        selectionDiv.style.width = w + 'px';
        selectionDiv.style.height = h + 'px';
    });
    document.addEventListener('mouseup', function(e) {
        if (window.end_select || !window.mouseIsDown ) return;
        if (parseInt(selectionDiv.style.width) < 100 ||
            parseInt(selectionDiv.style.height) < 80 ) return;
        window.mouseIsDown = false
        window.end_select = true
        // Find elements within the selected region
        var current_center_x = e.clientX - (e.pageX - rect.startX) / 2;
        var current_center_y = e.clientY - (e.pageY - rect.startY) / 2;
        var elements = document.elementsFromPoint(current_center_x, current_center_y) ;
        console.log(elements);
        // elements.forEach(function(element) {
        var xpath = getXPathForElement(elements[1]);
        window.xpath = xpath;
        // });
        selectionDiv.innerHTML = `
          请复制下面xpath至客户端: </br>${window.xpath}
          <div><button onclick="copyTextToClipboard('${window.xpath}')">复制</button>&nbsp;&nbsp;&nbsp;&nbsp;
          <button onclick="resetSelect()">重选</button></div>
        `
    });
    function getXPathForElement(element) {
        var idx, path = '';
        for (; element && element.nodeType == Node.ELEMENT_NODE; element = element.parentNode) {
            idx = Array.from(element.parentNode.childNodes).filter(node => node.nodeName == element.nodeName).indexOf(element) + 1;
            idx = (idx > 1) ? `[${idx}]` : '';
            path = '/' + element.nodeName.toLowerCase() + idx + path;
        }
        return path;
    }
})();"""