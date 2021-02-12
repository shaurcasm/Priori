# Table and database creation reference: https://www.sqlitetutorial.net/sqlite-python/create-tables/
"""
public static String strSeparator = "__,__";
public static String convertArrayToString(String[] array){
    String str = "";
    for (int i = 0;i<array.length; i++) {
        str = str+array[i];
        // Do not append comma at the end of last element
        if(i<array.length-1){
            str = str+strSeparator;
        }
    }
    return str;
}
public static String[] convertStringToArray(String str){
    String[] arr = str.split(strSeparator);
    return arr;
}
"""
import csv
import sys
import os
import tkinter as tk
import sqlite3
from sqlite3 import Error


def main():
    # r string or Raw string. Treats "\" as a literal character.
    DB_FILE = r"projects.db"

    sql_create_projects_table = """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            importance BOOLEAN NOT NULL CHECK (importance IN (0, 1)),
            deadline DATE NOT NULL,
            team TEXT,
            repo TEXT,
            status TEXT NOT NULL CHECK (status IN ("active", "planning", "delegate", "luxury")),
            technology TEXT
        );
    """

    sql_create_tasks_table = """
        CREATE TABLE IF NOT EXISTS tasks (
            id integer PRIMARY KEY,
            name text NOT NULL,
            importance boolean NOT NULL CHECK (importance IN (0, 1)),
            deadline date NOT NULL,
            designated_to text,
            eta date,
            status text NOT NULL CHECK (status IN ("active", "planning", "delegate", "luxury")),
            project_id integer NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        );
    """

    # Creat a database connection
    db = create_connection(DB_FILE)

    # Create tables
    if db is not None:
        # Create projects table
        create_table(db, sql_create_projects_table)

        # Create tasks table
        create_table(db, sql_create_tasks_table)
    else:
        print("Error! cannot create the database connection")


    # Initialise the root UI layer
    root = tk.Tk()
    # Give the window a title
    root.title("Priori - Project manager")
    root.geometry("600x600")

    display_active_project(db, root)


    add_project_button = tk.Button(root, text="Add Project", command=lambda: add_project(db, root), bd=3)
    add_project_button.pack(pady=30)


    root.mainloop()


def save_project(db, project):
    sql_insert_project = "INSERT INTO projects (name, importance, deadline, team, repo, status, technology) VALUES (:name, :importance, :deadline, :team, :repo, :status, :technology)"

    # Database cursor
    cursor = db.cursor()

    # Save to database
    try:
        cursor.execute(sql_insert_project, {
            'name': project['name'].get(),
            'importance': project['importance'].get(),
            'deadline': project['deadline'].get(),
            'team': project['team'].get(),
            'repo': project['repo'].get(),
            'status': project['status'].get(),
            'technology': project['technology'].get()
        })
        
        db.commit()

        project['name'].delete(0, tk.END)
        project['importance'].delete(0, tk.END)
        project['deadline'].delete(0, tk.END)
        project['team'].delete(0, tk.END)
        project['repo'].delete(0, tk.END)
        project['status'].delete(0, tk.END)
        project['technology'].delete(0, tk.END)

    except Error as e:
        print(e)

    return


def add_project(db, root):
    new_project_window = tk.Toplevel(bd=30)
    new_project_window.title("New Project")

    # Added "weighted" rows and columns around the core 
    # form to center them according to window. Sort of like
    # Attaching an absolute element to a relative element in css.
    new_project_window.grid_rowconfigure(0, weight=1)
    new_project_window.grid_rowconfigure(9, weight=1)
    new_project_window.grid_columnconfigure(0, weight=1)
    new_project_window.grid_columnconfigure(3, weight=1)

    # UI entry
    new_project_name_label =  tk.Label(new_project_window, text="Project Name: ")
    new_project_name_label.grid(row=1, column=1, padx=15, pady=15)
    new_project_name = tk.Entry(new_project_window, width=30)
    new_project_name.grid(row=1, column=2, padx=15, pady=15)

    new_project_importance_label =  tk.Label(new_project_window, text="Importance: ")
    new_project_importance_label.grid(row=2, column=1, padx=15, pady=15)
    new_project_importance = tk.Entry(new_project_window, width=30)
    new_project_importance.grid(row=2, column=2, padx=15, pady=15)

    new_project_deadline_label =  tk.Label(new_project_window, text="Deadline: ")
    new_project_deadline_label.grid(row=3, column=1, padx=15, pady=15)
    new_project_deadline = tk.Entry(new_project_window, width=30)
    new_project_deadline.grid(row=3, column=2, padx=15, pady=15)

    new_project_team_label =  tk.Label(new_project_window, text="Team: ")
    new_project_team_label.grid(row=4, column=1, padx=15, pady=15)
    new_project_team = tk.Entry(new_project_window, width=30)
    new_project_team.grid(row=4, column=2, padx=15, pady=15)

    new_project_repo_label =  tk.Label(new_project_window, text="Repo: ")
    new_project_repo_label.grid(row=5, column=1, padx=15, pady=15)
    new_project_repo = tk.Entry(new_project_window, width=30)
    new_project_repo.grid(row=5, column=2, padx=15, pady=15)

    new_project_status_label =  tk.Label(new_project_window, text="Status: ")
    new_project_status_label.grid(row=6, column=1, padx=15, pady=15)
    new_project_status = tk.Entry(new_project_window, width=30)
    new_project_status.grid(row=6, column=2, padx=15, pady=15)

    new_project_technology_label =  tk.Label(new_project_window, text="Technology: ")
    new_project_technology_label.grid(row=7, column=1, padx=15, pady=15)
    new_project_technology = tk.Entry(new_project_window, width=30)
    new_project_technology.grid(row=7, column=2, padx=15, pady=15)

    new_project_object = {
        'name': new_project_name,
        'importance': new_project_importance,
        'deadline': new_project_deadline,
        'team': new_project_team,
        'repo': new_project_repo,
        'status': new_project_status,
        'technology': new_project_technology
    }

    save_button = tk.Button(new_project_window, text="Save Project", command=lambda: save_project(db, new_project_object), bd=3)
    save_button.grid(row=8, column=1, columnspan=2, pady=(30, 0))

    return


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: database object or None
    """
    db = None
    try:
        db = sqlite3.connect(db_file)
        return db
    except Error as e:
        print(e)

    return db


def create_table(db, create_table_sql):
    """ create a table from the create_table_sql statement
    :param db: database object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        cursor = db.cursor()
        cursor.execute(create_table_sql)
    except Error as e:
        print(e)

    return


def display_active_project(db, root):
    # We are going to query for active status projects, that are important
    # Sorted by deadline date(urgency) just in case more than one active project.
    active_status = "active"
    cursor = db.execute("SELECT * FROM projects WHERE status = ? AND importance = 1 ORDER BY deadline ASC LIMIT 1", (active_status,))
    # Fetches only one row from the "selected" row(s) from cursor.
    project = cursor.fetchone()
    #print(project)

    # Active Project Frame
    active_frame = tk.LabelFrame(root, text="Active Project")
    active_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Error handling/No active projects. Probably display a luxury/delegative project, who knows.
    if project is None:
        no_active_project_label = tk.Label(active_frame, text="No Active Project")
        no_active_project_label.pack(padx=30, pady=30)
        print("No active Projects")

        return

    # cursor.fetchone() returns a tuple of the row(s), its a static list, so
    # accessed with array denotion. Keep the access to id, useful for updating
    # this particular project.
    project_id = project[0]
    project_name = project[1]
    project_importance = project[2]
    project_deadline = project[3]
    project_team = project[4]
    project_repo = project[5]
    project_status = project[6]
    project_technology = project[7]

    # Added "weighted" rows and columns around the core 
    # form to center them according to window. Sort of like
    # Attaching an absolute element to a relative element in css.
    active_frame.grid_rowconfigure(0, weight=1)
    active_frame.grid_rowconfigure(9, weight=1)
    active_frame.grid_columnconfigure(0, weight=1)
    active_frame.grid_columnconfigure(3, weight=1)

    project_name_label = tk.Label(active_frame, text="Project Name: ")
    project_name_label.grid(row=1, column=1, padx=30, pady=(30, 0))
    project_name = tk.Label(active_frame, text=project_name)
    project_name.grid(row=1, column=2, padx=30, pady=(30, 0))

    project_importance_label = tk.Label(active_frame, text="Importance: ")
    project_importance_label.grid(row=2, column=1, padx=30, pady=(30, 0))
    project_importance = tk.Label(active_frame, text=project_importance)
    project_importance.grid(row=2, column=2, padx=30, pady=(30, 0))

    project_deadline_label = tk.Label(active_frame, text="Deadline: ")
    project_deadline_label.grid(row=3, column=1, padx=30, pady=(30, 0))
    project_deadline = tk.Label(active_frame, text=project_deadline)
    project_deadline.grid(row=3, column=2, padx=30, pady=(30, 0))

    project_team_label = tk.Label(active_frame, text="Team Members: ")
    project_team_label.grid(row=4, column=1, padx=30, pady=(30, 0))
    project_team = tk.Label(active_frame, text=project_team)
    project_team.grid(row=4, column=2, padx=30, pady=(30, 0))

    project_repo_label = tk.Label(active_frame, text="Repository: ")
    project_repo_label.grid(row=5, column=1, padx=30, pady=(30, 0))
    project_repo = tk.Label(active_frame, text=project_repo)
    project_repo.grid(row=5, column=2, padx=30, pady=(30, 0))

    project_status_label = tk.Label(active_frame, text="Status: ")
    project_status_label.grid(row=6, column=1, padx=30, pady=(30, 0))
    project_status = tk.Label(active_frame, text=project_status)
    project_status.grid(row=6, column=2, padx=30, pady=(30, 0))

    project_technology_label = tk.Label(active_frame, text="Tech Stack: ")
    project_technology_label.grid(row=7, column=1, padx=30, pady=(30, 0))
    project_technology = tk.Label(active_frame, text=project_technology)
    project_technology.grid(row=7, column=2, padx=30, pady=(30, 0))

    # Edit project Button - Command to Edit project window, leading to UPDATE sql command
    edit_project_button = tk.Button(active_frame, text="Edit Project", bd=3)
    edit_project_button.grid(row=8, column=1, columnspan=2, pady=(30, 0))

    return


class Project:
    def __init__(self, name, importance, deadline, team, repo, process, tech_stack):
        self.name = name
        self.importance = importance
        self.deadline = deadline    # Date format
        self.team = team or None
        self.repo = repo
        self.process = [process]
        self.tech_stack = tech_stack


    # Edit 
    def edit():

        return

    
    # Save to database with a queue number to denote position in priority
    def save():

        return


if  __name__ == "__main__":
    main() 