from selenium import webdriver
from selenium.webdriver.common.by import By

# Set up the WebDriver
driver = webdriver.Chrome()  # Use the appropriate WebDriver for your browser

# Sample URLs for testing, replace with actual URLs
sample_urls = [
    'https://genius.com/Frank-ocean-rushes-lyrics',
    'https://genius.com/Frank-ocean-ivy-lyrics',
    'https://genius.com/Frank-ocean-thinkin-bout-you-lyrics',
]

# Initialize lists to store lyrics and annotations
lyrics = []
annotations = []

for sample_url in sample_urls:
    driver.get(sample_url)

    # Loop through clickable elements (lyrics) and extract data
    elements = driver.find_elements(By.CLASS_NAME, 'ReferentFragmentdesktop__ClickTarget-sc-110r0d9-0')
    for element in elements:
        element.click()  # Click the clickable element to reveal the annotation

        # Extract the lyric
        lyric = element.text
        lyrics.append(lyric)

        # Extract the annotation
        annotation_elements = driver.find_elements(By.CLASS_NAME, 'BaseAnnotationdesktop__InnerContainer-sc-1l72s1l-1')
        for annotation_element in annotation_elements:
            annotation = annotation_element.text
            annotations.append(annotation)

# Print the collected lyrics and annotations
print("All Collected Lyrics:")
for lyric in lyrics:
    print(lyric)

print("All Collected Annotations:")
for annotation in annotations:
    print(annotation)

# Clean up and close the browser
driver.quit()
