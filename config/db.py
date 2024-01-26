from sqlalchemy import create_engine, MetaData

engine = create_engine('mysql+pymysql://root:sqlserver@localhost:3306/fastapi_project')

meta_data = MetaData()