import csv
import random
import os
import sys
import json
import base64
import urllib.parse
from datetime import datetime, timedelta

class CrosswordGenerator:
    def __init__(self, width, height, csv_path):
        self.width = width
        self.height = height
        self.grid = [['.' for _ in range(width)] for _ in range(height)]
        self.words_to_place = []
        self.placed_words = []
        self.csv_path = csv_path

    def load_words(self):
        """Loads unique init_writtenForm words from CSV."""
        if not os.path.exists(self.csv_path):
            print(f"Error: File not found at {self.csv_path}")
            return False

        loaded_items = []
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word = row.get('init_writtenForm', '').strip()
                    # Filter: must be valid, not too long for grid
                    if word and len(word) <= max(self.width, self.height):
                        loaded_items.append(row)
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return False
        
        # Group by init_writtenForm and pick one random entry for each unique init_writtenForm
        unique_map = {}
        for item in loaded_items:
            w = item['init_writtenForm']
            if w not in unique_map:
                unique_map[w] = []
            unique_map[w].append(item)
            
        self.words_to_place = []
        for w, items in unique_map.items():
            self.words_to_place.append(random.choice(items))
            
        random.shuffle(self.words_to_place)
        return True

    def print_grid(self):
        """Prints the grid to console."""
        print("-" * (self.width * 2 + 1))
        for row in self.grid:
            print(" " + " ".join(row))
        print("-" * (self.width * 2 + 1))

    def is_valid_position(self, word, row, col, direction):
        """
        Checks if a word can be placed at (row, col) with direction (0=horiz, 1=vert).
        Returns True if valid.
        """
        dr, dc = (0, 1) if direction == 0 else (1, 0)
        
        # Check bounds
        if row + dr * len(word) > self.height or col + dc * len(word) > self.width:
            return False
            
        # Check start and end boundaries (word shouldn't touch others head-to-tail immediately)
        # Check cell before the word
        pre_r, pre_c = row - dr, col - dc
        if 0 <= pre_r < self.height and 0 <= pre_c < self.width:
            if self.grid[pre_r][pre_c] != '.':
                return False
        
        # Check cell after the word
        end_r = row + dr * len(word)
        end_c = col + dc * len(word)
        if 0 <= end_r < self.height and 0 <= end_c < self.width:
            if self.grid[end_r][end_c] != '.':
                return False

        has_intersection = False
        
        for i, char in enumerate(word):
            curr_r = row + dr * i
            curr_c = col + dc * i
            curr_cell = self.grid[curr_r][curr_c]

            if curr_cell == '.':
                # If cell is empty, check neighbors (orthogonal to direction)
                # to ensure we don't create adjacent words unintentionally.
                # Orthogonal check:
                check_dr, check_dc = (1, 0) if direction == 0 else (0, 1)
                
                n1_r, n1_c = curr_r + check_dr, curr_c + check_dc
                n2_r, n2_c = curr_r - check_dr, curr_c - check_dc
                
                if 0 <= n1_r < self.height and 0 <= n1_c < self.width:
                    if self.grid[n1_r][n1_c] != '.':
                        return False
                if 0 <= n2_r < self.height and 0 <= n2_c < self.width:
                    if self.grid[n2_r][n2_c] != '.':
                        return False

            elif curr_cell == char:
                has_intersection = True
            else:
                # Collision with different character
                return False
        
        # For the very first word, intersection isn't required. 
        # For subsequent words, we generally want an intersection to form a crossword.
        if not self.placed_words:
            return True
            
        return has_intersection

    def place_word(self, item, row, col, direction):
        word = item['init_writtenForm']
        dr, dc = (0, 1) if direction == 0 else (1, 0)
        for i, char in enumerate(word):
            self.grid[row + dr * i][col + dc * i] = char
        
        info = item.copy()
        info.update({
            'row': row,
            'col': col,
            'dir': direction
        })
        self.placed_words.append(info)

    def generate(self):
        if not self.words_to_place:
            return

        # Place the first word in the middle roughly
        first_item = self.words_to_place.pop(0)
        first_word = first_item['init_writtenForm']
        
        direction = random.choice([0, 1])
        start_row = (self.height - (len(first_word) if direction == 1 else 1)) // 2
        start_col = (self.width - (len(first_word) if direction == 0 else 1)) // 2
        
        self.place_word(first_item, start_row, start_col, direction)
        
        # Try to place subsequent words
        # Limit attempts to prevent infinite loops
        max_failures = 100
        failures = 0
        
        words_idx = 0
        while words_idx < len(self.words_to_place) and failures < max_failures:
            candidate_item = self.words_to_place[words_idx]
            candidate_word = candidate_item['init_writtenForm']
            
            placed = False
            
            # Try to intersect with existing placed words
            # Iterate through all cells of the grid to find potential intersection points
            potential_positions = []
            
            # Find all coordinates where a character of candidate_word matches a character on grid
            for i, char in enumerate(candidate_word):
                for pr in range(self.height):
                    for pc in range(self.width):
                        if self.grid[pr][pc] == char:
                            # Try Horizontal
                            start_col_h = pc - i
                            if 0 <= start_col_h:
                                potential_positions.append((0, pr, start_col_h))
                            
                            # Try Vertical
                            start_row_v = pr - i
                            if 0 <= start_row_v:
                                potential_positions.append((1, start_row_v, pc))

            random.shuffle(potential_positions)
            
            for direction, r, c in potential_positions:
                if self.is_valid_position(candidate_word, r, c, direction):
                    self.place_word(candidate_item, r, c, direction)
                    placed = True
                    break
            
            if placed:
                self.words_to_place.pop(words_idx)
                # Reset failures because we made progress
                failures = 0
                # Don't increment words_idx because the list shifted
            else:
                words_idx += 1
                failures += 1
                # If we cycled through all words, shuffle and try again or just stop
                if words_idx >= len(self.words_to_place):
                    break

def main():
    # Setup paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(current_dir, 'dict_data.csv')
    
    print(f"Generating 8x8 Crossword using: {csv_file}")
    
    cw = CrosswordGenerator(8, 8, csv_file)
    if cw.load_words():
        cw.generate()
        cw.print_grid()
        
        puzzle_data = []
        for idx, w in enumerate(cw.placed_words):
            direction_str = "H" if w['dir'] == 0 else "V"
            word = w.get('writtenForm', '')
            
            # Encoding word
            word_encoded = base64.b64encode(urllib.parse.quote(word).encode()).decode()

            # Construct hint dictionary
            hint_dict = {
                "en": w.get("lemma_en", ""),
                "ko": w.get("lemma_ko", ""),
                "cn": w.get("lemma_cn", ""),
                "jp": w.get("lemma_jp", ""),
                "vn": w.get("lemma_vn", ""),
                "id": w.get("lemma_id", ""),
                "ru": w.get("lemma_ru", ""),
                "fr": w.get("lemma_fr", ""),
                "es": w.get("lemma_es", "")
            }
            
            puzzle_data.append({
                "id": idx + 1,
                "dir": direction_str,
                "row": w['row'],
                "col": w['col'],
                "word_enc": word_encoded,
                "hints": hint_dict
            })
            
        # Tomorrow's date
        tomorrow = datetime.now() + timedelta(days=1)
        puzzle_date = tomorrow.strftime('%Y-%m-%d')
        
        final_json_obj = {
            "date": puzzle_date,
            "gridSize": 8,
            "puzzleData": puzzle_data
        }
        
        final_output = [final_json_obj]
            
        print("\nFinal JSON Output:")
        print(json.dumps(final_output, ensure_ascii=False, indent=4))
        
    else:
        print("Failed to initialize crossword generator.")

if __name__ == "__main__":
    main()
