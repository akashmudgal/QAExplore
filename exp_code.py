from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import time

def get_actionable_elements(driver):
    script = """
    function getClickableElements(){
        var elements = document.querySelectorAll('*');
        var clickableElements = [];
        var selectElements = [];
        var textElements = [];
        var stateSequence = [];
        elements.forEach(function(element) {
            if(!(element.display == "none" || element.visibility == "hidden" || element.ariaHidden || element.hiddden) && !(['HTML','HEAD','LINK','STYLE','SCRIPT','META','BODY'].includes(element.nodeName))){
                if (element.nodeName == 'SELECT'){
                    selectElements.push(element);
                    stateSequence.push(element.nodeName);
                }
                else if (element.nodeName != 'OPTION' && (element.onclick || element.href || element.oncontextmenu || ['button','submit','radio','checkbox'].includes(element.type)) || element.role == 'button' ) {
                    clickableElements.push(element);
                    stateSequence.push(element.nodeName);
                }
                else if (element.isContentEditable || ['search','email','password','text'].includes(element.type)) {
                    textElements.push(element);
                    stateSequence.push(element.nodeName);
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
    return getClickableElements();
    """
    
    elements = driver.execute_script(script)
    return elements

# Example usage
driver = webdriver.Chrome()
driver.get("http://teams.microsoft.com")

# Wait for the page to load and JavaScript to execute
time.sleep(5)

clickable_elements,sequence = get_actionable_elements(driver)

print(f"Found {len(clickable_elements)} clickable elements.")
for element in clickable_elements:
    print(f"Tag: {element.tag_name}, Text: {element.text}, Attributes: {element.get_attribute('outerHTML')}")

driver.quit()




# Example usage
driver = webdriver.Chrome()
driver.get("http://teams.microsoft.com")

clickable_elements = get_clickable_elements(driver)
print(f"Found {len(clickable_elements)} clickable elements.")
for element in clickable_elements:
    print(f"Tag: {element.tag_name}, Text: {element.text}")

driver.quit()
