import sqlite3


conn = sqlite3.connect('autori.db')
c = conn.cursor()
c.execute(' DROP TABLE IF EXISTS AUTORI' )
c.execute('CREATE TABLE AUTORI (Id INTEGER PRIMARY KEY AUTOINCREMENT, Nume VARCHAR(50) NOT NULL, Data_nasterii DATE NOT NULL, Tara VARCHAR(50) NOT NULL)')
c.execute('INSERT INTO AUTORI(Nume, Data_nasterii, Tara) VALUES (?, ?, ?)', [ 'plm', 'plm', 'plm'])
conn.commit()
conn.close()
