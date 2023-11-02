from lyricsgenius import Genius
import pandas as pd

# Define your Genius API access token
genius = Genius('api-here')


# Function to get song annotations and return them as a DataFrame
def get_annotations_as_dataframe(song_name, artist_name):
    song = genius.search_song(song_name, artist_name)
    if song:
        annotations = genius.song_annotations(song.id)
        annotations_data = []
        for annotation, explanations in annotations:
            for explanation in explanations:
                annotations_data.append({'Annotation': annotation, 'Explanation': explanation[0]})
        return pd.DataFrame(annotations_data)
    else:
        return "Song not found."

# User input
artist_name = input("Enter the artist name: ")
song_name = input("Enter the song name: ")

# Get annotations as a DataFrame
annotations_df = get_annotations_as_dataframe(song_name, artist_name)

# Display the DataFrame
print(annotations_df)

# Save the DataFrame to a CSV file
annotations_df.to_csv('annotations.csv', index=False)