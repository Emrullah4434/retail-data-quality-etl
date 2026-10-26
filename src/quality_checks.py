from pathlib import Path
import sqlite3
DB=Path(__file__).resolve().parents[1]/'outputs'/'retail_warehouse.sqlite'
with sqlite3.connect(DB) as c:
    queries={
      'Row count': 'SELECT COUNT(*) FROM retail_fact',
      'Duplicate transaction IDs': 'SELECT COUNT(*)-COUNT(DISTINCT transaction_id) FROM retail_fact',
      'Invalid net sales': 'SELECT COUNT(*) FROM retail_fact WHERE net_sales < 0',
      'Distinct orders': 'SELECT COUNT(DISTINCT order_id) FROM retail_fact',
      'Monthly totals': "SELECT substr(transaction_date,1,7) as month, round(sum(net_sales),2) FROM retail_fact GROUP BY month ORDER BY month"
    }
    for label,sql in queries.items(): print(label,':',c.execute(sql).fetchall() if label=='Monthly totals' else c.execute(sql).fetchone()[0])
    assert c.execute('SELECT COUNT(*)-COUNT(DISTINCT transaction_id) FROM retail_fact').fetchone()[0]==0
    assert c.execute('SELECT COUNT(*) FROM retail_fact WHERE net_sales < 0').fetchone()[0]==0
