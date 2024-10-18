import matplotlib
matplotlib.use('Agg')  # Use 'Agg' backend for non-GUI environments
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import numpy as np
from enum import Enum
import csv
import matplotlib.pyplot as plt
import time
from tqdm import tqdm  # for progress bar
from termcolor import colored  # for colored terminal output
import threading
import os


# Spotify Developer account credentials - replace these with your actual credentials
CLIENT_ID = "USE YOUR CLIENT ID FROM SPOTIFY HERE"
CLIENT_SECRET = "UE YOUR CLIENT SECRET FROM SPOTIFY HERE"
REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = "user-modify-playback-state user-read-playback-state playlist-modify-private playlist-read-private playlist-read-collaborative"

try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    ))
except spotipy.oauth2.SpotifyOauthError as e:
    print(f"Spotify Oauth Error: {e}")
    print("Please ensure your CLIENT_ID, CLIENT_SECRET, and REDIRECT_URI are correct.")
    raise

def list_available_devices():
    devices = sp.devices()
    if devices['devices']:
        print("Available Devices:")
        for i, device in enumerate(devices['devices']):
            print(f"{i+1}: {device['name']} (ID: {device['id']}, Type: {device['type']}, Active: {device['is_active']})")
    else:
        print("No active devices found.")
    return devices['devices']

def choose_device():
    devices = list_available_devices()
    if not devices:
        print("No devices available for playback.")
        return None

    while True:
        try:
            choice = int(input("Enter the number of the device you want to use for playback: ")) - 1
            if 0 <= choice < len(devices):
                return devices[choice]['id']
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(devices)}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")


# Define the 16 mood states based on valence and arousal using an enum
class Mood(Enum):
    HAPPY = 1
    CONTENT = 2
    RELAXED = 3
    CALM = 4
    EXCITED = 5
    ENERGETIC = 6
    TENSE = 7
    ANGRY = 8
    ANNOYED = 9
    FRUSTRATED = 10
    BORED = 11
    SAD = 12
    DEPRESSED = 13
    MISERABLE = 14
    DISTRESSED = 15
    FEARFUL = 16

mood_states = {
    Mood.HAPPY: ((0.7, 0.9), (0.7, 0.9)),
    Mood.CONTENT: ((0.7, 0.9), (0.3, 0.5)),
    Mood.RELAXED: ((0.3, 0.5), (0.3, 0.5)),
    Mood.CALM: ((0.1, 0.3), (0.3, 0.5)),
    Mood.EXCITED: ((0.7, 0.9), (0.9, 1.0)),
    Mood.ENERGETIC: ((0.5, 0.7), (0.9, 1.0)),
    Mood.TENSE: ((0.3, 0.5), (0.7, 0.9)),
    Mood.ANGRY: ((0.1, 0.3), (0.9, 1.0)),
    Mood.ANNOYED: ((0.1, 0.3), (0.7, 0.9)),
    Mood.FRUSTRATED: ((0.1, 0.3), (0.5, 0.7)),
    Mood.BORED: ((0.1, 0.3), (0.1, 0.3)),
    Mood.SAD: ((0.1, 0.3), (0.1, 0.3)),
    Mood.DEPRESSED: ((0.1, 0.3), (0.1, 0.3)),
    Mood.MISERABLE: ((0.0, 0.2), (0.1, 0.3)),
    Mood.DISTRESSED: ((0.1, 0.3), (0.5, 0.7)),
    Mood.FEARFUL: ((0.0, 0.2), (0.7, 0.9))
}

import os

def print_detailed_track_info(track_id):
    track = sp.track(track_id)
    features = sp.audio_features(track_id)[0]
    analysis = sp.audio_analysis(track_id)
    
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear the screen

    print("=" * 80)
    print(f"Track: {track['name']} by {', '.join([artist['name'] for artist in track['artists']])}")
    print(f"Album: {track['album']['name']}")
    print(f"Duration: {track['duration_ms'] / 1000:.2f} seconds")
    print(f"Popularity: {track['popularity']}/100")
    print("=" * 80)
    print("Audio Features:")
    print("=" * 80)
    print(f"| Valence: {features['valence']:.2f}       | Energy (Arousal): {features['energy']:.2f}    |")
    print(f"| Danceability: {features['danceability']:.2f} | Tempo: {features['tempo']:.2f} BPM          |")
    print(f"| Key: {features['key']}                   | Mode: {'Major' if features['mode'] == 1 else 'Minor'}           |")
    print("=" * 80)
    print("Audio Analysis Summary:")
    print("=" * 80)
    print(f"| Number of sections: {len(analysis['sections'])}  | Number of segments: {len(analysis['segments'])} |")
    print(f"| Number of bars: {len(analysis['bars'])}          | Number of beats: {len(analysis['beats'])}      |")
    print("=" * 80)


def calculate_distance(v1, v2):
    return np.sqrt((v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2)

def classify_mood(valence, arousal):
    for mood, ((v_min, v_max), (a_min, a_max)) in mood_states.items():
        if v_min <= valence <= v_max and a_min <= arousal <= a_max:
            return mood
    # Return a default mood if none matches
    return Mood.CALM

def get_tracks_audio_features(track_ids):
    batch_size = 50
    track_features = []

    for i in tqdm(range(0, len(track_ids), batch_size), desc="Extracting audio features"):
        batch = track_ids[i:i + batch_size]
        audio_features = sp.audio_features(batch)
        for feature in audio_features:
            if feature:
                track_features.append({
                    'id': feature['id'],
                    'valence': feature['valence'],
                    'arousal': feature['energy'],  # Using energy as a proxy for arousal
                    'tempo': feature['tempo']
                })

    return track_features


def search_songs_in_playlist(playlist_id):
    limit = 100
    offset = 0
    track_ids = []

    try:
        while True:
            results = sp.playlist_tracks(playlist_id, limit=limit, offset=offset)
            track_ids.extend([item['track']['id'] for item in results['items']])
            if len(results['items']) < limit:
                break
            offset += limit
    except spotipy.exceptions.SpotifyException as e:
        print(f"Error retrieving playlist tracks: {e}")
        if e.http_status == 403:
            print("Access to the playlist is forbidden. Please check your permissions.")
        raise

    return track_ids


def create_mood_playlist(track_features):
    mood_playlist = {mood: [] for mood in Mood}
    for feature in track_features:
        mood = classify_mood(feature['valence'], feature['arousal'])
        if mood is None:
            print(f"Warning: Track {feature['id']} with valence {feature['valence']} and arousal {feature['arousal']} could not be classified.")
            mood = Mood.CALM
        mood_playlist[mood].append((feature['id'], feature['valence'], feature['arousal'], feature['tempo']))
    return mood_playlist

def create_spotify_playlist(name, track_ids):
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user_id, name, public=False)
    sp.playlist_add_items(playlist['id'], [id for id, _, _, _ in track_ids])
    return playlist['id'], playlist['external_urls']['spotify']

def print_tracks_with_mood(track_features):
    for feature in track_features:
        mood = classify_mood(feature['valence'], feature['arousal'])
        track_name = sp.track(feature['id'])['name']
        print(f"Track: {track_name}, Mood: {mood.name.lower()}, "
              f"Valence: {feature['valence']:.2f}, Arousal: {feature['arousal']:.2f}")

def play_playlist(playlist_id):
    device_id = choose_device()
    if device_id:
        print(f"Starting playback on device ID: {device_id}")
        sp.start_playback(device_id=device_id, context_uri=f'spotify:playlist:{playlist_id}')
    else:
        print("Playback could not be started. No valid device selected.")

def stop_playback():
    playback = sp.current_playback()
    if playback and playback['is_playing']:
        sp.pause_playback()
        print("Playback stopped.")



def next_song():
    sp.next_track()

def previous_song():
    sp.previous_track()

def get_current_track():
    playback = sp.current_playback()
    if playback and playback['is_playing']:
        return playback['item']['id']
    return None


def monitor_playback():
    current_track_id = None
    while True:
        new_track_id = get_current_track()
        if new_track_id != current_track_id:
            current_track_id = new_track_id
            if current_track_id:
                print_detailed_track_info(current_track_id)
        time.sleep(5)


def print_menu():
    print("Select a mood:")
    for mood in Mood:
        print(f"{mood.value}: {mood.name.lower()}")
    print("q: Quit")

def save_playlist_to_csv(mood_name, track_ids):
    filename = f"{mood_name.lower()}_playlist.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Title', 'Artist(s)', 'Album', 'Valence', 'Arousal', 'Tempo (BPM)'])
        writer.writerow(['', '', '', '(0.0 to 1.0)', '(0.0 to 1.0)', ''])
        writer.writerow(['', '', '', '0.0: Negative', '0.0: Calm', ''])
        writer.writerow(['', '', '', '1.0: Positive', '1.0: Energetic', ''])
        writer.writerow([])  
        for track_id, valence, arousal, tempo in track_ids:
            track = sp.track(track_id)
            title = track['name']
            artists = ', '.join([artist['name'] for artist in track['artists']])
            album = track['album']['name']
            writer.writerow([title, artists, album, f"{valence:.2f}", f"{arousal:.2f}", f"{tempo:.2f}"])


### SAVE ALL FEATURES FROM INITIAL PLAYLIST
def save_all_features_to_csv(track_features, filename="all_track_features.csv"):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Track ID', 'Valence', 'Arousal (Energy)', 'Tempo (BPM)'])
        for feature in track_features:
            writer.writerow([feature['id'], f"{feature['valence']:.2f}", f"{feature['arousal']:.2f}", f"{feature['tempo']:.0f}"])
    print(f"All track features data saved to {filename}")


def visualize_mood_distribution(mood_playlist):
    mood_counts = {mood.name: len(tracks) for mood, tracks in mood_playlist.items()}
    moods = list(mood_counts.keys())
    counts = list(mood_counts.values())

    plt.figure(figsize=(12, 6))
    plt.bar(moods, counts)
    plt.title('Distribution of Songs Across Moods')
    plt.xlabel('Moods')
    plt.ylabel('Number of Songs')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('mood_distribution.png')
    plt.close()
    print("Mood distribution visualization saved as 'mood_distribution.png'")

def visualize_valence_arousal(track_features):
    # Define colors for each mood
    mood_colors = {
        Mood.HAPPY: 'yellow',
        Mood.CONTENT: 'green',
        Mood.RELAXED: 'blue',
        Mood.CALM: 'lightblue',
        Mood.EXCITED: 'red',
        Mood.ENERGETIC: 'orange',
        Mood.TENSE: 'purple',
        Mood.ANGRY: 'darkred',
        Mood.ANNOYED: 'brown',
        Mood.FRUSTRATED: 'pink',
        Mood.BORED: 'gray',
        Mood.SAD: 'navy',
        Mood.DEPRESSED: 'black',
        Mood.MISERABLE: 'darkgray',
        Mood.DISTRESSED: 'olive',
        Mood.FEARFUL: 'darkgreen'
    }

    plt.figure(figsize=(10, 10))
    for feature in track_features:
        valence = feature['valence']
        arousal = feature['arousal']
        mood = classify_mood(valence, arousal)
        color = mood_colors[mood]
        plt.scatter(valence, arousal, color=color, label=mood.name, alpha=0.6)

    plt.title('Valence-Arousal Distribution of Songs')
    plt.xlabel('Valence')
    plt.ylabel('Arousal')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.grid(True)
    # Create a legend with unique entries
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='upper right', bbox_to_anchor=(1.15, 1.15))
    plt.savefig('valence_arousal_distribution.png')
    plt.close()
    print("Valence-Arousal distribution visualization saved as 'valence_arousal_distribution.png'")

def get_audio_analysis(track_id):
    return sp.audio_analysis(track_id)

def print_detailed_track_info(track_id):
    track = sp.track(track_id)
    features = sp.audio_features(track_id)[0]
    analysis = get_audio_analysis(track_id)

    print(f"\nDetailed information for track: {track['name']} by {', '.join([artist['name'] for artist in track['artists']])}")
    print(f"Album: {track['album']['name']}")
    print(f"Duration: {track['duration_ms'] / 1000:.2f} seconds")
    print(f"Popularity: {track['popularity']}/100")
    print(f"\nAudio Features:")
    print(f"  Valence: {features['valence']:.2f}")
    print(f"  Energy (Arousal): {features['energy']:.2f}")
    print(f"  Danceability: {features['danceability']:.2f}")
    print(f"  Tempo: {features['tempo']:.2f} BPM")
    print(f"  Key: {features['key']}")
    print(f"  Mode: {'Major' if features['mode'] == 1 else 'Minor'}")
    print(f"\nAudio Analysis Summary:")
    print(f"  Number of sections: {len(analysis['sections'])}")
    print(f"  Number of segments: {len(analysis['segments'])}")
    print(f"  Number of bars: {len(analysis['bars'])}")
    print(f"  Number of beats: {len(analysis['beats'])}")

def recommend_similar_tracks(track_id, limit=5):
    recommendations = sp.recommendations(seed_tracks=[track_id], limit=limit)
    print(f"\nSimilar tracks to '{sp.track(track_id)['name']}':")
    for i, track in enumerate(recommendations['tracks'], 1):
        print(f"{i}. {track['name']} by {', '.join([artist['name'] for artist in track['artists']])}")

def main():
    playlist_id = '1ZR15nmAfxkQCxBgC72AJW'
    try:
        track_ids = search_songs_in_playlist(playlist_id)
        track_features = get_tracks_audio_features(track_ids)

        # Save all track features to a CSV file for the Cluster analysis
        save_all_features_to_csv(track_features)

        mood_playlist = create_mood_playlist(track_features)

        # Visualize mood distribution and valence-arousal distribution
        visualize_mood_distribution(mood_playlist)
        visualize_valence_arousal(track_features)

        # Monitor playback in a separate thread to constantly watch the song that is playing
        monitor_thread = threading.Thread(target=monitor_playback)
        monitor_thread.daemon = True
        monitor_thread.start()

        while True:
            print_menu()
            print("q: Quit")
            user_input = input("Enter your choice (1-16 for moods, or 'q' to quit): ")

            if user_input.lower() == 'q':
                print("Thank you for using the mood-based music player. Goodbye!")
                stop_playback()
                break

            try:
                choice = int(user_input)
                if 1 <= choice <= 16:
                    mood_selection = Mood(choice)
                    if mood_selection in mood_playlist and mood_playlist[mood_selection]:
                        playlist_id, playlist_url = create_spotify_playlist(f'{mood_selection.name.capitalize()} Playlist', mood_playlist[mood_selection])
                        print(f'Created playlist: {playlist_url}')

                        # Play the first song of the new playlist
                        play_playlist(playlist_id)

                        # Save the playlist to a CSV
                        save_playlist_to_csv(mood_selection.name, mood_playlist[mood_selection])

                        # Show visualizations for the selected mood
                        visualize_mood_distribution(mood_playlist)
                        visualize_valence_arousal(track_features)

                        # Print detailed track info
                        track_to_play = mood_playlist[mood_selection][0][0]  # First track in the playlist
                        print_detailed_track_info(track_to_play)
                    else:
                        print(f"No tracks found for the mood: {mood_selection.name.lower()}")
                else:
                    print("Invalid choice. Please enter a number between 1 and 16.")
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 16 or 'q' to quit.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()