import csv
from flask import Response  # type: ignore[import]

def export_logs(logs):
    def generate():
        yield 'User,Item,Locker,Timestamp,Action\n'
        for log in logs:
            yield f'{log.user_id},{log.item_id},{log.locker_id},{log.timestamp},{log.action_type}\n'
    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=logs.csv"})

def export_inventory(items):
    def generate():
        yield 'Item,Locker\n'
        for item in items:
            yield f'{item.name},{item.locker.name if item.locker else ""}\n'
    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=inventory.csv"}) 