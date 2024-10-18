Here is a draft for the `README.md` file:

---

# Mood-Based Playlist Generator

This project is a mood-based music player developed as an undergraduate project at the Department of Electrical & Computer Engineering, University of Peloponnese for the course "Digital Sound and Image Processing." The project was performed by Kalogeropoulos A. and Andrikou D., under the supervision of Associate Prof. Athanasios Koutras.

## Description

The Mood-Based Playlist Generator creates music playlists based on the user's mood using Spotify's API. It classifies songs into 16 different mood states based on their audio features such as valence (positivity) and arousal (energy level), and generates mood-specific playlists. The project includes the following functionalities:

1. **Audio Feature Extraction:** Retrieves audio features from Spotify to classify tracks by mood.
2. **Mood Classification:** Uses valence and arousal values to classify tracks into 16 mood categories, including happy, sad, energetic, relaxed, and more.
3. **Playlist Creation:** Automatically generates mood-specific playlists on Spotify.
4. **Playback Control:** Allows users to play, pause, and skip tracks, as well as view detailed track information.
5. **Visualization:** Displays graphical representations of the distribution of songs across moods and valence-arousal mapping.

## Features

- **Automatic mood classification of songs based on audio features**
- **Creation of playlists tailored to specific moods**
- **Real-time playback monitoring and control**
- **Saving and exporting playlists and audio features to CSV files**
- **Visualizations of mood distributions and valence-arousal maps**

## Requirements

To run this project, the following dependencies must be installed:

- Python 3.7 or higher
- `spotipy` for Spotify API interaction
- `matplotlib` for visualization
- `numpy` for numerical operations
- `tqdm` for progress bars
- `termcolor` for colored terminal output

You will also need to set up a Spotify Developer account and obtain the following:

- **Client ID** and **Client Secret** for the Spotify API
- **Redirect URI** for OAuth authentication

## Setup Instructions

1. **Install Python Dependencies:**
   ```
   pip install spotipy matplotlib numpy tqdm termcolor
   ```

2. **Configure Spotify API Credentials:**
   - Replace the placeholder values for `CLIENT_ID`, `CLIENT_SECRET`, and `REDIRECT_URI` in the code with your Spotify developer account credentials.

3. **Run the Application:**
   ```
   python moodplaylist.py
   ```

   - The program will guide you through the steps for selecting a mood, creating a playlist, and starting playback.

## Usage Notes

- Ensure you have an active Spotify account and that the device you want to play music on is available for playback.
- The application requires a network connection to access the Spotify API and download track information.
- Visualizations will be saved as PNG files in the current working directory.

## License

This project is intended for educational purposes and should not be used for commercial applications without proper licensing.

---

Feel free to adjust the details or add more information to suit your needs.
