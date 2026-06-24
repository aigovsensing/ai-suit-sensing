
import pymysql

def get_db_conn():
    return pymysql.connect(
        host="mariadb",
        user="root",
        password="password",
        database="ai_lawsuits"
    )

def insert_cases(cases):
    conn = get_db_conn()
    try:
        cur = conn.cursor()
        for c in cases:
            # Map new unified structure to existing DB schema
            cur.execute("""
            INSERT IGNORE INTO lawsuits
            (case_name,company,court,state,file_date,case_type,url)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                c.get("case_name"), 
                c.get("defendant", c.get("company", "Unknown")), 
                c.get("court"), 
                c.get("country", "NA"), 
                c.get("file_date"), 
                c.get("reason", c.get("case_type", "unknown")), 
                c.get("url")
            ))
        conn.commit()
    finally:
        conn.close()
