-- Drop tables if they exist
DROP TABLE IF EXISTS employee_projects;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS clients;
DROP TABLE IF EXISTS project_clients;
 
-- Create departments table
CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
 
-- Create employees table
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    department_id INTEGER,
    salary INTEGER,
    hire_date DATE,
    FOREIGN KEY(department_id) REFERENCES departments(id)
);
 
-- Create projects table
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    budget INTEGER,
    start_date DATE,
    end_date DATE
);
 
-- Create clients table
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_info TEXT
);
 
-- Create employee_projects table
CREATE TABLE employee_projects (
    employee_id INTEGER,
    project_id INTEGER,
    role TEXT,
    hours_worked INTEGER,
    FOREIGN KEY(employee_id) REFERENCES employees(id),
    FOREIGN KEY(project_id) REFERENCES projects(id)
);
 
-- Create project_clients table
CREATE TABLE project_clients (
    project_id INTEGER,
    client_id INTEGER,
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(client_id) REFERENCES clients(id)
);
 
-- Insert departments
INSERT INTO departments (name) VALUES
    ('Engineering'),
    ('Marketing'),
    ('HR'),
    ('Sales'),
    ('Finance');
 
-- Insert employees
INSERT INTO employees (name, department_id, salary, hire_date) VALUES
    ('Alice', 1, 120000, '2020-01-15'),
    ('Bob', 2, 90000, '2019-03-22'),
    ('Charlie', 1, 110000, '2021-06-10'),
    ('Diana', 3, 80000, '2018-11-05'),
    ('Eve', 4, 95000, '2022-02-28'),
    ('Frank', 5, 105000, '2017-07-19'),
    ('Grace', 1, 115000, '2020-09-23'),
    ('Hank', 2, 92000, '2019-12-11');
 
-- Insert projects
INSERT INTO projects (name, budget, start_date, end_date) VALUES
    ('Website Redesign', 50000, '2023-01-01', '2023-06-30'),
    ('New Product Launch', 150000, '2023-02-15', '2023-08-15'),
    ('Recruitment Drive', 30000, '2023-03-01', '2023-04-30'),
    ('Sales Campaign', 70000, '2023-04-01', '2023-09-30'),
    ('Financial Audit', 60000, '2023-05-01', '2023-07-31');
 
-- Insert clients
INSERT INTO clients (name, contact_info) VALUES
    ('Client A', 'clientA@example.com'),
    ('Client B', 'clientB@example.com'),
    ('Client C', 'clientC@example.com'),
    ('Client D', 'clientD@example.com');
 
-- Insert employee_projects
INSERT INTO employee_projects (employee_id, project_id, role, hours_worked) VALUES
    (1, 1, 'Lead Developer', 200),
    (2, 1, 'Marketing Manager', 150),
    (3, 2, 'Engineer', 180),
    (4, 3, 'Recruiter', 100),
    (5, 4, 'Sales Lead', 220),
    (6, 5, 'Auditor', 160),
    (7, 2, 'Senior Developer', 190),
    (8, 4, 'Assistant Manager', 140),
    (1, 2, 'Developer', 210),
    (2, 2, 'Manager', 160),
    (3, 3, 'Engineer', 190),
    (4, 4, 'Recruiter', 110),
    (5, 5, 'Sales Lead', 230),
    (6, 1, 'Auditor', 170),
    (7, 2, 'Senior Developer', 200),
    (8, 3, 'Assistant Manager', 150);
 
-- Insert project_clients
INSERT INTO project_clients (project_id, client_id) VALUES
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 1),
    (5, 4);