# cli_analyzer.py - Command-line version of the Genius Lyrics Analyzer

import os
from genius_analyzer import GeniusLyricsAnalyzer
from config import GENIUS_API_TOKEN, MAX_TOP_SONGS


def print_divider():
    """Print a divider line"""
    print("-" * 80)


def main():
    """Main function for the command-line analyzer"""
    print_divider()
    print("Genius Lyrics Analyzer - Command Line Version")
    print_divider()

    # Get the token
    token = GENIUS_API_TOKEN
    if not token:
        token = input("Enter your Genius API token: ")

    # Create the analyzer
    print("Initializing analyzer...")
    analyzer = GeniusLyricsAnalyzer(token)

    # Menu loop
    while True:
        print_divider()
        print("Select an analysis option:")
        print("1. Analyze an artist's top songs")
        print("2. Analyze an album")
        print("3. Analyze a single song")
        print("4. Exit")
        print_divider()

        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            # Analyze artist's top songs
            artist_name = input("Enter artist name: ")
            max_songs = int(input(f"How many songs to analyze (1-{MAX_TOP_SONGS})? "))
            max_songs = min(max(1, max_songs), MAX_TOP_SONGS)

            print(f"Analyzing top {max_songs} songs by {artist_name}...")
            results = analyzer.run_analysis(
                artist_name,
                max_songs=max_songs,
                status_callback=print
            )

            # Print results
            display_results(results)

        elif choice == "2":
            # Analyze album
            artist_name = input("Enter artist name: ")
            album_name = input("Enter album name: ")

            print(f"Analyzing album '{album_name}' by {artist_name}...")
            results = analyzer.run_analysis(
                artist_name,
                album_name=album_name,
                status_callback=print
            )

            # Print results
            display_results(results)

        elif choice == "3":
            # Analyze single song
            artist_name = input("Enter artist name: ")
            song_name = input("Enter song name: ")

            print(f"Analyzing song '{song_name}' by {artist_name}...")
            results = analyzer.run_analysis(
                artist_name,
                song_name=song_name,
                status_callback=print
            )

            # Print results
            display_results(results)

        elif choice == "4":
            # Exit
            print("Exiting Genius Lyrics Analyzer")
            break

        else:
            print("Invalid choice. Please enter a number from 1 to 4.")


def display_results(results):
    """Display analysis results in the console"""
    if not results or 'songs_df' not in results or results['songs_df'].empty:
        print("No results found.")
        return

    print_divider()
    print("ANALYSIS RESULTS")
    print_divider()

    # Number of songs analyzed
    songs_df = results['songs_df']
    num_songs = len(songs_df)
    print(f"Analyzed {num_songs} songs")
    print()

    # Top songs by complexity
    ranked_songs = results.get('ranked_songs')
    if ranked_songs is not None and not ranked_songs.empty:
        print("Top Songs by Complexity:")
        for i, row in ranked_songs.head(5).iterrows():
            print(f"{i + 1}. {row['title']} - Score: {row['complexity_score']:.4f}")
        print()

    # Average metrics
    print("Average Metrics:")
    print(f"- Words per song: {songs_df['word_count'].mean():.1f}")
    print(f"- Unique words per song: {songs_df['unique_word_count'].mean():.1f}")
    print(f"- Lexical diversity: {songs_df['lexical_diversity'].mean():.4f}")
    print(f"- Annotations per song: {songs_df['annotation_count'].mean():.1f}")
    print()

    # Output files
    output_files = results.get('output_files', {})
    if output_files:
        print("Output Files:")
        for file_type, file_path in output_files.items():
            print(f"- {file_type}: {file_path}")
        print()

    # Ask if user wants to see details
    show_details = input("Do you want to see detailed song rankings? (y/n): ").lower()
    if show_details == 'y':
        print_divider()
        print("DETAILED SONG RANKINGS")
        print_divider()

        # Print header
        print(f"{'RANK':<5}{'SONG':<30}{'LEXICAL DIV.':<15}{'ANNOTATIONS':<15}{'SCORE':<10}")
        print("-" * 75)

        # Print each song
        for i, row in ranked_songs.iterrows():
            print(
                f"{i + 1:<5}{row['title'][:28]:<30}{row['lexical_diversity']:<15.4f}{row['annotation_count']:<15}{row['complexity_score']:<10.4f}")

    # Check if visualization was created
    if 'visualization_file' in output_files and os.path.exists(output_files['visualization_file']):
        print_divider()
        print(f"Visualization saved to: {output_files['visualization_file']}")
        print("Open this file to see the complexity analysis charts.")

    input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()