import sqlite3


class SQLighter:
    def __init__(self, database):
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def get_groups(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM groups').fetchall()

    def add_group(self, id, title, type):
        with self.connection:
            self.cursor.execute('INSERT OR REPLACE INTO groups (id, title, type) VALUES (?, ?, ?)', (id, title, type))
            self.connection.commit()

    def remove_group(self, id):
        with self.connection:
            self.cursor.execute('DELETE FROM groups WHERE id = ?', id)
            self.connection.commit()

    def get_masks(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM masks').fetchall()
