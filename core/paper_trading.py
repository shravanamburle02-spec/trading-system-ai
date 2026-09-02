"""
Master Trading System - Paper Trading & Automated Trade Journal
Manages Virtual Portfolio, Active Positions, Real-Time PnL tracking,
and persistent SQLite-based Trade Journaling.
"""

import json
import sqlite3
import datetime
import pandas as pd

DB_FILE = "trading_journal.db"

class PaperTradingEngine:
    @staticmethod
    def get_connection():
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def init_db(cls, default_capital=300000.0):
        """Initializes tables if they do not exist."""
        conn = cls.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS account (
                id INTEGER PRIMARY KEY,
                balance REAL,
                initial_capital REAL,
                updated_at TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS active_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                strategy_name TEXT,
                strategy_type TEXT,
                legs_json TEXT,
                entry_time TEXT,
                entry_spot REAL,
                net_credit_debit REAL,
                lot_size INTEGER,
                sl_price REAL,
                tgt_price REAL,
                confluence_pct REAL,
                status TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                strategy_name TEXT,
                strategy_type TEXT,
                entry_time TEXT,
                exit_time TEXT,
                entry_spot REAL,
                exit_spot REAL,
                pnl REAL,
                confluence_pct REAL,
                exit_reason TEXT,
                notes TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS adjustment_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id INTEGER,
                symbol TEXT,
                adjustment_type TEXT,
                description TEXT,
                timestamp TEXT
            )
        """)

        # Initialize default capital if empty
        cursor.execute("SELECT COUNT(*) FROM account")
        if cursor.fetchone()[0] == 0:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO account (id, balance, initial_capital, updated_at) VALUES (1, ?, ?, ?)",
                           (default_capital, default_capital, now))

        conn.commit()
        conn.close()

    @classmethod
    def update_position_legs(cls, pos_id, new_legs_json, additional_credit=0.0):
        """Updates position legs after an automated defensive rebalance."""
        cls.init_db()
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE active_positions 
            SET legs_json = ?, net_credit_debit = net_credit_debit + ? 
            WHERE id = ?
        """, (new_legs_json, additional_credit, pos_id))
        conn.commit()
        conn.close()

    @classmethod
    def log_adjustment(cls, trade_id, symbol, adjustment_type, description):
        """Logs an automated defensive adjustment event."""
        cls.init_db()
        conn = cls.get_connection()
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO adjustment_logs (trade_id, symbol, adjustment_type, description, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (trade_id, symbol, adjustment_type, description, now))
        conn.commit()
        conn.close()

    @classmethod
    def get_adjustment_logs(cls):
        """Fetches all automated rebalancing logs."""
        cls.init_db()
        conn = cls.get_connection()
        df = pd.read_sql_query("SELECT * FROM adjustment_logs ORDER BY id DESC LIMIT 50", conn)
        conn.close()
        return df

    @classmethod
    def get_account(cls):
        """Fetches current virtual balance and total realized PnL."""
        cls.init_db()
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM account WHERE id = 1")
        row = cursor.fetchone()
        conn.close()

        if row:
            balance = row['balance']
            initial = row['initial_capital']
            total_realized_pnl = balance - initial
            return {
                'balance': round(balance, 2),
                'initial_capital': round(initial, 2),
                'realized_pnl': round(total_realized_pnl, 2),
                'return_pct': round((total_realized_pnl / initial) * 100, 2)
            }
        return {'balance': 500000.0, 'initial_capital': 500000.0, 'realized_pnl': 0.0, 'return_pct': 0.0}

    @classmethod
    def execute_paper_trade(cls, symbol, strategy_dict, spot, confluence_pct=80.0, lot_size=25):
        """Executes a virtual trade and adds to active positions."""
        cls.init_db()
        conn = cls.get_connection()
        cursor = conn.cursor()

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        legs_json = json.dumps(strategy_dict.get('legs', []))
        strat_name = strategy_dict.get('strategy_name', 'Custom Setup')
        strat_type = strategy_dict.get('type', 'Directional')
        sl = float(strategy_dict.get('stop_loss', 0.0))
        tgt = float(strategy_dict.get('target_1', 0.0))
        entry_price = float(strategy_dict.get('entry_price', 0.0))

        cursor.execute("""
            INSERT INTO active_positions (symbol, strategy_name, strategy_type, legs_json, entry_time, entry_spot, net_credit_debit, lot_size, sl_price, tgt_price, confluence_pct, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (symbol, strat_name, strat_type, legs_json, now, spot, entry_price, lot_size, sl, tgt, confluence_pct, 'OPEN'))

        conn.commit()
        trade_id = cursor.lastrowid
        conn.close()
        return trade_id

    @classmethod
    def get_open_positions(cls):
        """Returns all open paper trades."""
        cls.init_db()
        conn = cls.get_connection()
        df = pd.read_sql_query("SELECT * FROM active_positions WHERE status = 'OPEN'", conn)
        conn.close()
        return df

    @classmethod
    def close_position(cls, pos_id, exit_spot, pnl_inr, exit_reason="Manual Close"):
        """Closes an active position and logs to Trade Journal."""
        cls.init_db()
        conn = cls.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM active_positions WHERE id = ?", (pos_id,))
        pos = cursor.fetchone()
        if not pos:
            conn.close()
            return False

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insert into Trade Journal
        cursor.execute("""
            INSERT INTO trade_journal (symbol, strategy_name, strategy_type, entry_time, exit_time, entry_spot, exit_spot, pnl, confluence_pct, exit_reason, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pos['symbol'], pos['strategy_name'], pos['strategy_type'], pos['entry_time'], now,
              pos['entry_spot'], exit_spot, pnl_inr, pos['confluence_pct'], exit_reason, f"Auto-closed with {pnl_inr:+.2f} PnL"))

        # Update position status
        cursor.execute("UPDATE active_positions SET status = 'CLOSED' WHERE id = ?", (pos_id,))

        # Update virtual balance
        cursor.execute("UPDATE account SET balance = balance + ?, updated_at = ? WHERE id = 1", (pnl_inr, now))

        conn.commit()
        conn.close()
        return True

    @classmethod
    def get_journal(cls):
        """Returns completed trade journal records."""
        cls.init_db()
        conn = cls.get_connection()
        df = pd.read_sql_query("SELECT * FROM trade_journal ORDER BY id DESC", conn)
        conn.close()
        return df

    @classmethod
    def reset_account(cls, new_capital=500000.0):
        """Resets virtual portfolio to initial state."""
        cls.init_db()
        conn = cls.get_connection()
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("UPDATE account SET balance = ?, initial_capital = ?, updated_at = ? WHERE id = 1",
                       (new_capital, new_capital, now))
        cursor.execute("DELETE FROM active_positions")
        cursor.execute("DELETE FROM trade_journal")
        cursor.execute("DELETE FROM adjustment_logs")
        conn.commit()
        conn.close()
