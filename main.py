from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up the WebDriver
driver = webdriver.Chrome()  # Use the appropriate WebDriver for your browser

# Request user input for the artist name and song name
artist_name = input("Enter the artist name: ")
song_name = input("Enter the song name: ")

# Process the artist name and song name to replace spaces with hyphens
artist_name = artist_name.replace(" ", "-")
song_name = song_name.replace(" ", "-")

# Generate the URL using the artist name and song name
sample_url = f'https://genius.com/{artist_name}-{song_name}-lyrics'

driver.get(sample_url)

# Wait for the iframe to load
wait = WebDriverWait(driver, 10)
wait.until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, 'iframe.AppleMusicPlayerdesktop__Iframe-sc-13x6a26-3')))

# Loop through clickable elements (lyrics) and extract data
elements = driver.find_elements(By.CLASS_NAME, 'ReferentFragmentdesktop__ClickTarget-sc-110r0d9-0')
lyrics = []

for element in elements:
    element.click()  # Click the clickable element to reveal the annotation

    # Extract the lyric
    lyric = element.text
    lyrics.append(lyric)

# Print the collected lyrics
print("Lyrics:")
for lyric in lyrics:
    print(lyric)

# Clean up and close the browser
driver.quit()
