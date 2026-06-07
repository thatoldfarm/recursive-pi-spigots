# recursive-pi-spigots
A method for finding 'spigots' in the decimal expansion of pi.

---

```python
#!/usr/bin/env python3
"""
Spigot finder using SQLite for disk-based storage.
Zero memory issues - uses database instead of RAM.
No terminal output, writes only to spigots.txt.

KEY FEATURE: If you DON'T delete spigots_temp.db, it will STACK findings
from multiple runs (allowing cumulative analysis across different pi files).
"""

import sys
import sqlite3
import os

def has_ge_2_missing_digits(sequence):
    """Check if sequence has at least 2 missing digits (i.e., uses <= 8 unique digits)."""
    return len(set(sequence)) <= 8

def find_spigots(file_path, window_size=12, chunk_size=500000):
    """
    Uses SQLite to store counts on disk, avoiding memory limits.
    
    If spigots_temp.db already exists, it will APPEND to existing data.
    To start fresh, manually delete spigots_temp.db and spigots_temp.db-journal.
    """
    db_path = "spigots_temp.db"

    # ONLY clean up if you want fresh start - COMMENTED OUT FOR STACKING
    # if os.path.exists(db_path):
    #     os.remove(db_path)
    # if os.path.exists(db_path + "-journal"):
    #     os.remove(db_path + "-journal")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist (allows stacking)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sequences (
            seq TEXT PRIMARY KEY,
            count INTEGER DEFAULT 0,
            pos1 INTEGER,
            pos2 INTEGER,
            pos3 INTEGER,
            pos4 INTEGER,
            pos5 INTEGER,
            first_seen TEXT,
            last_seen TEXT
        )
    """)

    absolute_pos = 0
    overlap = window_size - 1

    with open(file_path, 'r') as f:
        while True:
            chunk = f.read(chunk_size + overlap)
            if not chunk:
                break

            for i in range(len(chunk) - window_size + 1):
                seq = chunk[i:i+window_size]
                if not has_ge_2_missing_digits(seq):
                    continue

                abs_i = absolute_pos + i

                # Check if we've seen this sequence before
                cursor.execute("SELECT count, pos1, pos2, pos3, pos4, pos5 FROM sequences WHERE seq = ?", (seq,))
                row = cursor.fetchone()
                
                if row is None:
                    # First occurrence
                    cursor.execute("""
                        INSERT INTO sequences (seq, count, pos1, first_seen, last_seen) 
                        VALUES (?, 1, ?, datetime('now'), datetime('now'))
                    """, (seq, abs_i))
                elif row[0] == 1:
                    # Second occurrence - record both positions
                    cursor.execute("""
                        UPDATE sequences SET count = 2, pos2 = ?, last_seen = datetime('now') 
                        WHERE seq = ?
                    """, (abs_i, seq))
                elif row[0] == 2:
                    # Third occurrence
                    cursor.execute("""
                        UPDATE sequences SET count = 3, pos3 = ?, last_seen = datetime('now') 
                        WHERE seq = ?
                    """, (abs_i, seq))
                elif row[0] == 3:
                    # Fourth occurrence
                    cursor.execute("""
                        UPDATE sequences SET count = 4, pos4 = ?, last_seen = datetime('now') 
                        WHERE seq = ?
                    """, (abs_i, seq))
                elif row[0] == 4:
                    # Fifth occurrence
                    cursor.execute("""
                        UPDATE sequences SET count = 5, pos5 = ?, last_seen = datetime('now') 
                        WHERE seq = ?
                    """, (abs_i, seq))
                else:
                    # 6+ occurrences - just update last seen
                    cursor.execute("""
                        UPDATE sequences SET count = count + 1, last_seen = datetime('now') 
                        WHERE seq = ?
                    """, (seq,))

            conn.commit()  # Commit periodically to avoid large transactions
            absolute_pos += len(chunk) - overlap

    # Get all sequences with their positions
    cursor.execute("SELECT seq, count, pos1, pos2, pos3, pos4, pos5 FROM sequences WHERE count >= 2")
    spigots = cursor.fetchall()

    conn.close()
    # NOTE: We're NOT deleting the DB file so findings can stack across runs
    # os.remove(db_path)  # Commented out to preserve stacking capability

    return [(seq, [pos for pos in [pos1, pos2, pos3, pos4, pos5] if pos is not None]) 
            for seq, count, pos1, pos2, pos3, pos4, pos5 in spigots]

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 spigot_finder.py <pi_digits_file.txt>")
        sys.exit(1)

    pi_file = sys.argv[1]
    print(f"[*] Analyzing {pi_file} for spigots...")
    print("[!] NOTE: Database file (spigots_temp.db) will be PRESERVED for stacking across runs")
    print("[!] To start fresh, manually delete spigots_temp.db and spigots_temp.db-journal")
    
    spigots = find_spigots(pi_file)

    with open("spigots.txt", "w") as f:
        for seq, pos in spigots:
            f.write(f"{seq}:{','.join(map(str, pos))}\n")
    
    print(f"[+] Found {len(spigots)} spigots with >=2 occurrences")
    print(f"[+] Results saved to spigots.txt")
    print(f"[+] Database preserved in spigots_temp.db for future stacking")

if __name__ == "__main__":
    main()
```
