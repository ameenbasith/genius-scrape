from lyricsgenius import Genius
import pandas as pd

# Define your Genius API access token
genius = Genius('insert token')


# Function to get song annotations and return them as a DataFrame
def get_annotations_as_dataframe(song):
    annotations = genius.song_annotations(song.id)
    annotations_data = []
    for annotation, explanations in annotations:
        for explanation in explanations:
            annotations_data.append({'Annotation': annotation, 'Explanation': explanation[0]})
    return pd.DataFrame(annotations_data)

# User input
artist_name = input("Enter the artist name: ")
album_name = input("Enter the album name: ")

# Search for the album
album = genius.search_album(album_name, artist_name)
if album:
    annotations_data = []
    for song in album.tracks:
        annotations_df = get_annotations_as_dataframe(song)
        if not annotations_df.empty:
            annotations_data.append(annotations_df)
    if annotations_data:
        album_annotations_df = pd.concat(annotations_data, ignore_index=True)

        # Display the DataFrame
        print(album_annotations_df)

        # Save the DataFrame to a CSV file
        album_annotations_df.to_csv(f'{album_name}_annotations.csv', index=False)
    else:
        print("No annotations found for the album.")
else:
    print("Album not found.")
