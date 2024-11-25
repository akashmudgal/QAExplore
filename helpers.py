from selenium.webdriver import Chrome
from selenium.webdriver.remote.webelement import WebElement
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import base64


def get_runtime_object_id(driver: Chrome, input_element: WebElement) -> int:
    # Set the global variable on the window object
    driver.execute_script("""
        (function(fileInput) {
            window.__tellurium_chromerinode = fileInput;
        })(arguments[0]);
    """, input_element)

    # Evaluate the global variable to get its remote object ID
    evaluate_response = driver.execute_cdp_cmd("Runtime.evaluate", {
        "expression": "window.__tellurium_chromerinode"
    })

    # Delete the global variable from the window object
    driver.execute_script("""
        (function() {
            delete window.__tellurium_chromerinode;
        })();
    """)

    # Extract the remote object ID from the evaluation response
    remote_object_id = evaluate_response['result']['objectId']

    # # Request the DOM node ID using the remote object ID
    # request_node_response = driver.execute_cdp_cmd("DOM.requestNode", {
    #     "objectId": remote_object_id
    # })

    # # Extract and return the node ID
    # return request_node_response['nodeId']
    return remote_object_id

def get_event_listeners(driver: Chrome, input_element: WebElement):
        # Get the remote object id
        remote_object_id=get_runtime_object_id(driver,input_element)

        # get the event listeners associated
        event_listeners = driver.execute_cdp_cmd("DOMDebugger.getEventListeners",{"objectId": remote_object_id, 'depth': -1, 'pierce': True})

        return event_listeners

def get_image_similarity_score(base64_image1, base64_image2):
    # Decode the base64 encoded images
    image1_data = base64.b64decode(base64_image1)
    image2_data = base64.b64decode(base64_image2)
    
    # Convert the binary data to numpy arrays
    nparr1 = np.frombuffer(image1_data, np.uint8)
    nparr2 = np.frombuffer(image2_data, np.uint8)
    
    # Decode the numpy arrays to OpenCV images
    image1 = cv2.imdecode(nparr1, cv2.IMREAD_COLOR)
    image2 = cv2.imdecode(nparr2, cv2.IMREAD_COLOR)
    
    # Convert the images to grayscale
    gray_image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray_image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    
    # Compute SSIM between the two images
    similarity_score, diff = ssim(gray_image1, gray_image2, full=True)
    
    return similarity_score