import sqlite3 
import json 
from typing import List, Dict, Any, Optional 
from pathlib import Path 

class CardDB: 
    def __init__(self, db_path: str = None): 
        self.db_path = db_path or Path(__file__).parent / "cards.db" 
        self._init_db() 
    
    def _init_db(self): 
        conn = sqlite3.connect(self.db_path) 
        conn.execute(''' 
            CREATE TABLE IF NOT EXISTS card_records ( 
                player TEXT, 
                round INTEGER, 
                card TEXT, 
                weighting REAL 
            ) 
        ''') 
        conn.commit() 
        conn.close() 
    
    def add(self, player: str, round: int, card: str, weighting: float = 1.0): 
        conn = sqlite3.connect(self.db_path) 
        conn.execute('INSERT INTO card_records VALUES (?, ?, ?, ?)', 
                     (player, round, card, weighting)) 
        conn.commit() 
        conn.close() 
    
    def add_batch(self, records: List[Dict[str, Any]]): 
        conn = sqlite3.connect(self.db_path) 
        for r in records: 
            conn.execute('INSERT INTO card_records VALUES (?, ?, ?, ?)', 
                        (r['player'], r['round'], r['card'], r['weighting'])) 
        conn.commit() 
        conn.close() 
    
    def get_all(self) -> str: 
        conn = sqlite3.connect(self.db_path) 
        rows = conn.execute('SELECT player, round, card, weighting FROM card_records').fetchall() 
        conn.close() 
        return json.dumps([{ 
            "player": r[0], "round": r[1], "card": r[2], "weighting": r[3] 
        } for r in rows], ensure_ascii=False, indent=2) 
    
    def get_player(self, player: str) -> str: 
        conn = sqlite3.connect(self.db_path) 
        rows = conn.execute( 
            'SELECT player, round, card, weighting FROM card_records WHERE player = ? ORDER BY round', 
            (player,) 
        ).fetchall() 
        conn.close() 
        return json.dumps([{ 
            "player": r[0], "round": r[1], "card": r[2], "weighting": r[3] 
        } for r in rows], ensure_ascii=False, indent=2) 
    
    def get_round(self, round: int) -> str: 
        conn = sqlite3.connect(self.db_path) 
        rows = conn.execute( 
            'SELECT player, round, card, weighting FROM card_records WHERE round = ?', 
            (round,) 
        ).fetchall() 
        conn.close() 
        return json.dumps([{ 
            "player": r[0], "round": r[1], "card": r[2], "weighting": r[3] 
        } for r in rows], ensure_ascii=False, indent=2) 
    
    def clear(self): 
        conn = sqlite3.connect(self.db_path) 
        conn.execute('DELETE FROM card_records') 
        conn.commit() 
        conn.close() 

if __name__ == "__main__": 
    db = CardDB() 
    db.add("A", 1, "heart J", 0.8) 
    db.add("B", 1, "spade A", 0.9) 
    print(db.get_all()) 
