window.generateAbsXpath = function generateAbsXpath(element) {
    if (element.tagName.toLowerCase() === 'html')
        return '/html[1]';
    if (element.tagName.toLowerCase() === 'body')
        return '/html[1]/body[1]';
    var ix = 0;
    var siblings = element.parentNode.childNodes;
    for (var i = 0; i < siblings.length; i++) {
        var sibling = siblings[i];
        if (sibling === element) {
            if (element.tagName.toLowerCase()
                .includes('svg')) {
                return "this node is the child of svg & svg child don't support xpath so xpath can't be generated for this element.";
            } else {
                var absXpath = generateAbsXpath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                return absXpath;
            }
        }
        if (sibling.nodeType === 1 && sibling.tagName.toLowerCase() === element.tagName.toLowerCase()) {
            ix++;
        }
    }
}

window.isInsideIframe = function isInsideIframe(node) {
    var child = true;
    var frameOrNot = node.ownerDocument;
    while (child) {
        try {
            var temp = frameOrNot.ownerDocument;
            frameOrNot = temp;
        } catch (err) {
            child = false;
        }
    }
    return frameOrNot !== document;
}

window.generateRelXpath = function generateRelXpath(element) {

    let tempXpath = "";
    let indexes = [];
    let matchIndex = [];

    var innerText = element.textContent.trim()
        .slice(0, 50);
    var tagName = element.tagName.toLowerCase();
    // if(isInsideIframe(element)){
    //     return "this element is inside iframe so xpath can't be generated.";
    // }
    if (tagName.includes('svg') && tempXpath) {
        tempXpath = "this node is the child of svg & svg child don't support xpath so xpath can't be generated for this element.";
        return tempXpath;
    }
    if (tagName.includes('svg') && !tempXpath) {
        tagName = "*";
    }
    if (innerText.includes("'")) {
        containsText = '[contains(text(),"' + innerText + '")]';
        equalsText = '[text()="' + innerText + '"]';
    } else {
        containsText = "[contains(text(),'" + innerText + "')]";
        equalsText = "[text()='" + innerText + "']";
    }
    if (element.tagName.toLowerCase()
        .includes('html')) {
        return '/html' + tempXpath;
    }
    var attr = "";
    var attrValue = "";
    if (element.id !== '') {
        tempXpath = '//' + tagName + "[@id='" + element.id + "']" + tempXpath;
        var totalMatch = document.evaluate(tempXpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null)
            .snapshotLength;
        if (totalMatch === 1) {
            return tempXpath;
        } else {
            tempXpath = tempXpath;
        }
    } else if (element.attributes.length != 0) {
        for (var i = 0; i < element.attributes.length; i++) {
            attr = element.attributes[i].name;
            attrValue = element.attributes[i].nodeValue;
            if (attrValue != null && attrValue != "" && !attr.includes("style") && !attr.includes("xpath")) {
                break;
            }
        }
        if (attrValue != null && attrValue != "" && !attr.includes("xpath")) {
            var xpathWithoutAttribute = tempXpath;
            var xpathWithAttribute = "";
            if (attrValue.includes("'")) {
                if (attrValue.charAt(0) === " " || attrValue.charAt(attrValue.length - 1) === " ") {
                    xpathWithAttribute = '//' + tagName + '[contains(@' + attr + ',"' + attrValue.trim() + '")]' + tempXpath;
                } else {
                    xpathWithAttribute = '//' + tagName + '[@' + attr + '="' + attrValue + '"]' + tempXpath;
                }
            } else {
                if (attrValue.charAt(0) === " " || attrValue.charAt(attrValue.length - 1) === " ") {
                    xpathWithAttribute = '//' + tagName + "[contains(@" + attr + ",'" + attrValue.trim() + "')]" + tempXpath;
                } else {
                    xpathWithAttribute = '//' + tagName + "[@" + attr + "='" + attrValue + "']" + tempXpath;
                }
            }
            var totalMatch = document.evaluate(xpathWithAttribute, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null)
                .snapshotLength;
            if (totalMatch === 1) {
                return xpathWithAttribute;
            } else if (innerText && element.getElementsByTagName('*')
                .length === 0) {
                var containsXpath = xpathWithAttribute + containsText;
                var totalMatch = document.evaluate(containsXpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null)
                    .snapshotLength;
                if (totalMatch === 0) {
                    var equalsXpath = xpathWithAttribute + equalsText;
                    var totalMatch = document.evaluate(equalsXpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null)
                        .snapshotLength;
                    if (totalMatch === 1) {
                        return equalsXpath;
                    }
                } else if (totalMatch === 1) {
                    return containsXpath;
                } else if (attrValue.includes('/') || innerText.includes('/')) {
                    if (attrValue.includes('/')) {
                        containsXpath = xpathWithoutAttribute + containsText;
                    }
                    if (innerText.includes('/')) {
                        containsXpath = containsXpath.replace(containsText, "");
                    }
                    tempXpath = containsXpath;
                } else {
                    tempXpath = containsXpath;
                }
            } else {
                tempXpath = xpathWithAttribute;
                if (attrValue.includes('/')) {
                    tempXpath = "//" + tagName + xpathWithoutAttribute;
                }
            }
        } else if (attrValue == null || attrValue == "" || attr.includes("xpath")) {
            tempXpath = "//" + tagName + tempXpath;
        }
        if (tagName.includes('*')) {
            tagName = " ";
            return tempXpath;
        }
    } else if (attrValue == "" && innerText && element.getElementsByTagName('*')
        .length === 0) {
        var containsXpath = '//' + tagName + containsText + tempXpath;
        var totalMatch = document.evaluate(containsXpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null)
            .snapshotLength;
        if (totalMatch === 0) {
            tempXpath = '//' + tagName + equalsText + tempXpath;
            var totalMatch = document.evaluate(tempXpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null)
                .snapshotLength;
            if (totalMatch === 1) {
                return tempXpath;
            }
        } else if (totalMatch === 1) {
            return containsXpath;
        } else {
            tempXpath = containsXpath;
        }
    } else {
        tempXpath = "//" + tagName + tempXpath;
    }
    var ix = 0;
    var siblings = element.parentNode.childNodes;
    for (var i = 0; i < siblings.length; i++) {
        var sibling = siblings[i];
        if (sibling === element) {
            indexes.push(ix + 1);
            tempXpath = generateRelXpath(element.parentNode);
            if (!tempXpath.includes("/")) {
                return tempXpath;
            } else {
                var totalMatch = document.evaluate(tempXpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null)
                    .snapshotLength;
                if (totalMatch === 1) {
                    return tempXpath;
                } else {
                    tempXpath = "/" + tempXpath.replace(/\/\/+/g, '/');
                    var regSlas = /\/+/g;
                    var regBarces = /[^[\]]+(?=])/g;
                    while ((match = regSlas.exec(tempXpath)) != null) {
                        matchIndex.push(match.index);
                    }
                    for (var j = 0; j < indexes.length; j++) {
                        if (j === 0) {
                            var lastTag = tempXpath.slice(matchIndex[matchIndex.length - 1]);
                            if ((match = regBarces.exec(lastTag)) != null) {
                                lastTag = lastTag.replace(regBarces, indexes[j]);
                                tempXpath = tempXpath.slice(0, matchIndex[matchIndex.length - 1]) + lastTag;
                            } else {
                                tempXpath = tempXpath + "[" + indexes[j] + "]";
                            }
                        } else {
                            var lastTag = tempXpath.slice(matchIndex[matchIndex.length - (j + 1)], matchIndex[matchIndex.length - (j)]);
                            if ((match = regBarces.exec(lastTag)) != null) {
                                lastTag = lastTag.replace(regBarces, indexes[j]);
                                tempXpath = tempXpath.slice(0, matchIndex[matchIndex.length - (j + 1)]) + lastTag + tempXpath.slice(matchIndex[matchIndex.length - j]);
                            } else {
                                tempXpath = tempXpath.slice(0, matchIndex[matchIndex.length - j]) + "[" + indexes[j] + "]" + tempXpath.slice(matchIndex[matchIndex.length - j]);
                            }
                        }
                        var totalMatch = document.evaluate(tempXpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null)
                            .snapshotLength;
                        if (totalMatch === 1) {
                            var regSlashContent = /([a-zA-Z])([^/]*)/g;
                            var length = tempXpath.match(regSlashContent)
                                .length;
                            for (var k = j + 1; k < length - 1; k++) {
                                var lastTag = tempXpath.match(/\/([^\/]+)\/?$/)[1];
                                var arr = tempXpath.match(regSlashContent);
                                arr.splice(length - k, 1, '/');
                                var relXpath = "";
                                for (var i = 0; i < arr.length; i++) {
                                    if (arr[i]) {
                                        relXpath = relXpath + "/" + arr[i];
                                    } else {
                                        relXpath = relXpath + "//" + arr[i];
                                    }
                                }
                                relXpath = (relXpath + "/" + lastTag)
                                    .replace(/\/\/+/g, '//');
                                var totalMatch = document.evaluate(relXpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null)
                                    .snapshotLength;
                                if (totalMatch === 1) {
                                    tempXpath = relXpath;
                                }
                            }
                            return tempXpath.replace('//html', '');;
                        }
                    }
                }
            }
        }
        if (sibling.nodeType === 1 && sibling.tagName.toLowerCase() === element.tagName.toLowerCase()) {
            ix++;
        }
    }
}
window.getNodename = function getNodename(element) {
    var name = "",
        className;

    // Ensure element.className is treated as a string
    className = String(element.className);

    if (element.classList.length) {
        name = [element.tagName.toLowerCase()];
        className = className.trim();
        className = className.replace(/  +/g, ' ');
        name.push(className.split(" ").join("."));
        name = name.join(".");
    }
    return name;
}

window.getChildNumber = function getChildNumber(node) {
    var classes = {},
        i, firstClass, uniqueClasses;
    var parentNode = node.parentNode,
        childrenLen;
    childrenLen = parentNode.children.length;
    for (i = 0; i < childrenLen; i++) {
        if (parentNode.children[i].classList.length) {
            firstClass = parentNode.children[i].classList[0];
            if (!classes[firstClass]) {
                classes[firstClass] = [parentNode.children[i]]
            } else {
                classes[firstClass].push(parentNode.children[i])
            }
        }
    }
    uniqueClasses = Object.keys(classes)
        .length || -1;
    var obj = {
        childIndex: -1,
        childLen: childrenLen
    }
    if (classes[Object.keys(classes)[0]] === childrenLen) {
        obj.childIndex = Array.prototype.indexOf.call(classes[node.classList[0]], node);
        obj.childLen = classes[Object.keys(classes)[0]].length;
        return obj
    } else if (uniqueClasses && uniqueClasses !== -1 && uniqueClasses !== childrenLen) {
        obj.childIndex = Array.prototype.indexOf.call(parentNode.children, node);
        obj.childLen = classes[Object.keys(classes)[0]].length;
        return obj
    } else if (uniqueClasses === -1) {
        obj.childIndex = Array.prototype.indexOf.call(parentNode.children, node);
        obj.childLen = childrenLen;
        return obj
    } else {
        return obj
    }
}
window.parents = function parents(element, _array) {
    var name, index;
    if (_array === undefined) {
        _array = [];
    } else {
        index = getChildNumber(element);
        name = getNodename(element);
        if (name) {
            if (index.childLen >= 1 && index.childIndex !== -1) {
                name += ":nth-child(" + (index.childIndex + 1) + ")"
            }
            _array.push(name);
        } else if (_array.length < 5) {
            name = element.tagName.toLowerCase();
            if (index.childIndex !== -1) {
                name += ":nth-child(" + (index.childIndex + 1) + ")"
            }
            _array.push(name);
        }
    }
    if (element.tagName !== 'BODY') return parents(element.parentNode, _array);
    else return _array;
}

window.generateCSS = function generateCSS(el) {
    if (!(el instanceof Element))
        return;
    var path = parents(el, []);
    path = path.reverse();
    var lastNode = path.slice(path.length - 1, path.length);
    var _path = path.slice(0, path.length - 1);
    if (_path.length != 0) {
        return _path.join(" ") + " > " + lastNode;
    } else { //hack for body tag which is the 1st tag in html page
        return lastNode;
    }
}

window.getLocator = function getLocator(element){
    let locator="";
    try{
        // try to generate relative Xpath
        locator = generateRelXpath(element);
    }
    catch{
        locator = generateCSS(element)
    }

    return locator;
}

window.getInteractiveElements = function getInteractiveElements(){
    var elements = document.querySelectorAll('*');
    var clickableElements = [];
    var selectElements = [];
    var textElements = [];
    var stateSequence = [];
    elements.forEach(function(element) {
        if(!(element.display == "none" || element.visibility == "hidden" || element.ariaHidden || element.hiddden || element.type == "hidden") && !(['HTML','HEAD','LINK','STYLE','SCRIPT','META','BODY','TITLE'].includes(element.nodeName))){
            if (element.nodeName == 'SELECT'){
                let locator = getLocator(element);
                selectElements.push({tag_name: element.nodeName.toLowerCase(),locator: locator,element: element});
                let elText=document.title+element.nodeName+element.placeholder+element.ariaLabel+element.textContent
                stateSequence.push(elText.replaceAll(" ","").replaceAll("\n","").replaceAll("undefined","").replaceAll("null",""));
            }
            else if (element.nodeName != 'OPTION' && (element.onclick || element.href || ['button','submit','radio','checkbox'].includes(element.type)) || element.role == 'button' ) {
                let locator = getLocator(element);
                clickableElements.push({tag_name: element.nodeName.toLowerCase(), locator: locator,element: element});
                let elText=document.title+element.nodeName+element.placeholder+element.ariaLabel+element.textContent
                stateSequence.push(elText.replaceAll(" ","").replaceAll("\n","").replaceAll("undefined","").replaceAll("null",""));
            }
            else if (element.isContentEditable || element.nodeName.toLowerCase() == 'textarea' || ['search','email','password','text'].includes(element.type)) {
                let locator = getLocator(element);
                textElements.push({tag_name: element.nodeName.toLowerCase(), locator: locator,element: element});
                let elText=document.title+element.nodeName+element.placeholder+element.ariaLabel+element.textContent
                stateSequence.push(elText.replaceAll(" ","").replaceAll("\n","").replaceAll("undefined","").replaceAll("null",""));
            }
        }
    });
    return [
        {
            clickable: clickableElements,
            selectElements: selectElements,
            editable: textElements,
        },
        stateSequence.join('')
    ]
}