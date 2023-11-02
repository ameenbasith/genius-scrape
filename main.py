from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Set up the WebDriver
driver = webdriver.Chrome()  # Use the appropriate WebDriver for your browser

# Navigate to the Genius page with lyrics and annotations
url = 'https://genius.com/Frank-ocean-rushes-lyrics'
driver.get(url)

# Initialize lists to store lyrics and annotations
lyrics = []
annotations = []

# Loop through clickable elements (lyrics) and extract data
elements = driver.find_elements(By.CLASS_NAME, 'your-clickable-element-class')
for element in elements:
    element.click()  # Click the clickable element to reveal the annotation

    # Extract the lyric
    lyric = element.text
    lyrics.append(lyric)

    # Extract the annotation
    annotation_elements = driver.find_elements(By.CLASS_NAME, 'annotation-class')
    for annotation_element in annotation_elements:
        annotation = annotation_element.text
        annotations.append(annotation)

    time.sleep(5)  # Wait for 5 seconds

# Clean up and close the browser
driver.quit()
