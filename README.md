# Global Chosung Crossword

This is a multilingual Chosung (initial consonant) crossword puzzle game.

## Features

- **Daily Puzzles**: New puzzles are generated daily.
- **Multilingual Support**: Hints are available in English, Korean, Chinese, Japanese, Vietnamese, Indonesian, Russian, French, and Spanish.
- **Interactive Interface**: Play directly in your browser with a virtual keyboard.

## How to Run

1.  **Generate Puzzles**:
    Run the Python script to generate a new puzzle for the day.

    ```bash
    python3 generate_crossword.py
    ```

    This reads words from `dict_data.csv` and appends a new puzzle to `puzzles.json`.

2.  **Play the Game**:
    Open `index.html` in a web browser.
    Since this game fetches `puzzles.json`, it does not work locally. You need to upload it to GitHub or another web server to play.

## Files

- `index.html`: The main game interface.
- `generate_crossword.py`: Script to generate puzzles.
- `dict_data.csv`: Dictionary data source.
- `puzzles.json`: Database of generated puzzles.

## Note

The data in `dict_data.csv` uses data from the National Institute of Korean Language's Basic Korean Dictionary (국립국어원 한국어기초사전).
https://github.com/spellcheck-ko/korean-dict-nikl
