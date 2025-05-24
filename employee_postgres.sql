-- Drop tables if they exist
DROP TABLE IF EXISTS employee_projects;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

-- Create departments table
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

-- Create employees table
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name TEXT,
    department_id INTEGER,
    salary INTEGER,
    FOREIGN KEY(department_id) REFERENCES departments(id)
);

-- Create projects table
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name TEXT,
    budget INTEGER
);

-- Create employee_projects table
CREATE TABLE employee_projects (
    employee_id INTEGER,
    project_id INTEGER,
    role TEXT,
    FOREIGN KEY(employee_id) REFERENCES employees(id),
    FOREIGN KEY(project_id) REFERENCES projects(id)
);

-- Insert departments
INSERT INTO departments (name) VALUES 
    ('Engineering'),
    ('Marketing'),
    ('HR');

-- Insert employees
INSERT INTO employees (name, department_id, salary) VALUES 
    ('Alice', 1, 120000),
    ('Bob', 2, 90000),
    ('Charlie', 1, 110000),
    ('Diana', 3, 80000);

-- Insert projects
INSERT INTO projects (name, budget) VALUES 
    ('Website Redesign', 50000),
    ('New Product Launch', 150000),
    ('Recruitment Drive', 30000);

-- Insert employee_projects
INSERT INTO employee_projects (employee_id, project_id, role) VALUES 
    (1, 1, 'Lead Developer'),
    (2, 1, 'Marketing Manager'),
    (3, 2, 'Engineer'),
    (4, 3, 'Recruiter');
