To connect to postgres, create a postgres.yaml file in credentials/ with this content:

```yaml
staging:
  host: 10.20.0.28
  port: 5433
  database: ETL_Staging_Dev | etl_staging_prod
  username: your-etl-username
  password: your-etl-password
```

Then you can use `pd` like this:

```python
from connectors.postgres import get_engine
engine = get_engine("staging")
df = pd.read_sql_query(f"select * from {schema_name}.{table_name} LIMIT 100", con=engine)
```

Happy coding!