from datetime import datetime

from models import Session, Task

import argparse
from fpdf import FPDF


def add_task(title, description, status):
    session = Session()
    task = Task(title=title, description=description, status=status)
    session.add(task)
    session.commit()
    print(f"Задача добавлена: ID {task.id}")


def list_tasks(status=None):
    session = Session()
    query = session.query(Task)
    if status:
        query = query.filter(Task.status == status)
    tasks = query.all()
    for task in tasks:
        print(f"{task.id} | {task.title} | {task.status} | {task.created_at}")


def update_task(task_id, **kwargs):
    session = Session()
    task = session.query(Task).get(task_id)
    if not task:
        print("Ошибка: задача не найдена")
        return
    for key, value in kwargs.items():
        setattr(task, key, value)
    session.commit()
    print(f"Задача {task_id} обновлена")


def delete_task(task_id):
    session = Session()
    task = session.query(Task).get(task_id)
    if not task:
        print("Ошибка: задача не найдена")
        return
    session.delete(task)
    session.commit()
    print(f"Задача {task_id} удалена")


def to_pdf(title="Tasks Report", output="report.pdf"):
    session = Session()
    tasks = session.query(Task).all()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    def safe_text(text):
        if isinstance(text, str):
            return text.encode('latin-1', errors='replace').decode('latin-1')
        return str(text)

    pdf.cell(200, 10, txt=safe_text(title), ln=1, align="C")

    headers = ["ID", "Title", "Description", "Status", "Date"]
    col_widths = [10, 50, 80, 30, 20]
    
    for header, width in zip(headers, col_widths):
        pdf.cell(width, 10, safe_text(header), 1)
    pdf.ln()

    for task in tasks:
        pdf.cell(col_widths[0], 10, safe_text(task.id), 1)
        pdf.cell(col_widths[1], 10, safe_text(task.title), 1)
        pdf.cell(col_widths[2], 10, safe_text(task.description), 1)
        pdf.cell(col_widths[3], 10, safe_text(task.status), 1)
        pdf.cell(col_widths[4], 10, safe_text(task.created_at.strftime("%Y-%m-%d")), 1)
        pdf.ln()

    pdf.output(output)
    print(f"PDF-отчет сохранен как {output}")


def main():
    parser = argparse.ArgumentParser(description="Менеджер задач")
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--title", required=True)
    add_parser.add_argument("--desc", required=True)
    add_parser.add_argument("--status", default="todo")

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--status")

    update_parser = subparsers.add_parser("update")
    update_parser.add_argument("--id", type=int, required=True)
    update_parser.add_argument("--status")
    update_parser.add_argument("--title")
    update_parser.add_argument("--desc")

    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("--id", type=int, required=True)

    pdf_parser = subparsers.add_parser("topdf")
    pdf_parser.add_argument("--title", default="Tasks Report")
    pdf_parser.add_argument("--output", default="report.pdf")

    args = parser.parse_args()

    if args.command == "add":
        add_task(args.title, args.desc, args.status)
    elif args.command == "list":
        list_tasks(args.status)
    elif args.command == "update":
        update_data = {}
        if args.status: update_data["status"] = args.status
        if args.title: update_data["title"] = args.title
        if args.desc: update_data["description"] = args.desc
        update_task(args.id, **update_data)
    elif args.command == "delete":
        delete_task(args.id)
    elif args.command == "topdf":
        to_pdf(args.title, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()