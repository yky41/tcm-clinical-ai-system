#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from neo4j import GraphDatabase

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IM_Sys.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()


    # 连接到数据库
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "12345678"
    driver = GraphDatabase.driver(uri, auth=(username, password))

    # 打开数据库的会话
    with driver.session() as session:
        # 这里可以执行一些操作，例如运行Cypher查询或者其他管理任务
        session.run("CALL dbms.components()")