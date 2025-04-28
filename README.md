# Genius Lyrics Analyzer & Songwriter's Workshop

## The Problem

Songwriters often struggle with:
- Understanding what makes lyrics complex and impactful
- Figuring out how their favorite artists craft such compelling lyrics
- Analyzing rhyme patterns, vocabulary richness, and thematic elements
- Getting inspiration for their own songwriting process
- Finding the right balance of vocabulary diversity and accessibility

Current lyric analysis tools focus mostly on basic metrics or require manual analysis, making it difficult to get meaningful insights that can actually improve one's songwriting.

## The Solution

The Genius Lyrics Analyzer is a web application that analyzes song lyrics from Genius.com to determine complexity, vocabulary richness, and annotation density, then provides actionable insights for your own creative process. It bridges the gap between analysis and creation by providing:

1. **In-depth Analysis**: Analyzes songs from your favorite artists to identify what makes their lyrics work
2. **Objective Metrics**: Measures vocabulary richness, annotation density, and thematic content
3. **Songwriter's Workshop**: Transforms those insights into practical tools for your own writing
4. **Real-time Feedback**: Analyzes your draft lyrics and suggests improvements based on your targets

## Features

### Analysis Tools
- Analyze an artist's top songs, an entire album, or a single song
- Calculate complexity metrics:
  - Lexical diversity (vocabulary richness)
  - Annotation density (how well-annotated the song is on Genius)
  - Word usage patterns
  - Sentiment analysis
- Rank songs by overall complexity
- Visualize the results with interactive charts
- View lyrics alongside their annotations

### Songwriter's Workshop
- Set complexity targets based on songs you admire
- Get theme inspiration from analyzed lyrics
- Draft and analyze your own lyrics in real-time
- Get feedback on your rhyme patterns and word usage
- Find rhymes based on the songs you've analyzed

## Screenshots

[Insert screenshots here when available]

## Installation

1. Make sure you have Python 3.7+ installed
2. Clone this repository or download the files
3. Install the required packages:

```bash
pip install streamlit lyricsgenius pandas matplotlib nltk scikit-learn
```

4. Download NLTK data (this will be done automatically on first run, but you can also run):

```bash
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('stopwords')"
```

## Configuration

1. Get a Genius API token:
   - Create an account on [Genius.com](https://genius.com/)
   - Go to [API Clients](https://genius.com/api-clients)
   - Create a new API client
   - Copy your Client Access Token

2. Update the `config.py` file with your token:
   ```python
   GENIUS_API_TOKEN = "your_token_here"
   ```

3. You can also adjust the analysis weights in this file if you want to change how the complexity score is calculated.

## Usage

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your web browser at http://localhost:8501

### Analyzing Songs

1. Enter the artist name in the sidebar
2. Choose the analysis type:
   - Artist's Top Songs: Analyzes the most popular songs by the artist
   - Album: Analyzes all songs in a specific album
   - Single Song: Analyzes just one song

3. Fill in the additional fields based on your selection
4. Click "Run Analysis"
5. View the results in the various tabs:
   - Overview: Summary of the analysis
   - Song Rankings: Table of songs ranked by complexity
   - Visualizations: Charts showing the analysis
   - Annotations: Lyrics with their annotations

### Using the Songwriter's Workshop

1. After analyzing songs, go to the Songwriter's Workshop tab
2. Note the complexity targets and theme ideas derived from your analysis
3. Use the lyric drafting area to write your own lyrics
4. Click "Analyze My Lyrics" to get feedback on:
   - Word count and vocabulary richness
   - How your lyrics compare to your complexity target
   - Detected rhyme patterns
   - Most frequently used words
5. Use the Rhyme Suggester when you need help finding the right rhyme

## How Complexity is Measured

The analysis includes several metrics:

1. **Lexical Diversity**: The ratio of unique words to total words, measuring vocabulary richness
2. **Annotation Density**: The number of annotations relative to song length
3. **Composite Score**: A weighted combination of the above metrics

## Example Workflows

### For Analysis
- Analyze Kendrick Lamar's "To Pimp a Butterfly" album to understand its lyrical complexity
- Compare Bob Dylan's early work with his later albums
- Discover which songs in an artist's catalog have the richest annotations

### For Songwriting
- Analyze songs in a genre you want to write in
- Set a complexity target based on those songs
- Draft your lyrics in the workshop
- Get real-time feedback on how your lyrics compare
- Use the theme suggestions to overcome writer's block

## Future Enhancements

Planned features include:
- Phonetic rhyme analysis for more accurate rhyme detection
- Co-occurrence analysis to identify related themes
- Emotional arc visualization through the song
- Metaphor and simile detection
- Integration with music theory tools

## Credits

This application uses:
- The [LyricsGenius](https://github.com/johnwmillr/LyricsGenius) library to interact with the Genius API
- [Streamlit](https://streamlit.io/) for the web interface
- [NLTK](https://www.nltk.org/) for natural language processing
- [Matplotlib](https://matplotlib.org/) for data visualization
- [Pandas](https://pandas.pydata.org/) for data analysis

## Medium

Read more about this project here:
https://medium.com/@ameenbasith2000/breaking-down-lyrics-how-i-built-a-tool-to-analyze-song-complexity-and-enhance-songwriting-d3f8778065e3
