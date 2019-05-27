import json
# import xml
import csv
import toml
from pathlib import Path
from datetime import date

# TodoManager creates a directory with json files for todos
class TodoManager(object):
    STATUS_ALL = 'all'
    STATUS_DONE = 'done'
    STATUS_PENDING = 'pending'
    CATEGORY_GENERAL = 'general'

    """pass in path which becomes a path object 
    if directory exists, don't create a new directory
    if end of path is not directory, but file, raise error"""
    def __init__(self, base_todos_path, doc_type=None, create_dir=True):
        self.base_todos_path = base_todos_path
        self.path = Path(self.base_todos_path)
        self.doc_type = doc_type
        if not doc_type:
            self.doc_type = 'json'
        
        if self.path.exists() and not self.path.is_dir():
            raise ValueError('Path is invalid')
        if not self.path.exists():
            if not create_dir:
                raise ValueError(" Directory doesn't exist")
            self.path.mkdir(parents=True)
    
    # list todo items by category
    def list(self, status=STATUS_ALL, category=CATEGORY_GENERAL):
        todos = {}
        doc_ext = '*.{}'.format(self.doc_type)
        for todo_path in self.path.glob(doc_ext):
#             print(todo_path)
            with todo_path.open('r') as fp:
                if self.doc_type == 'json':
                    document = json.load(fp)
                if self.doc_type == 'toml':
                    document = toml.load(fp)
                if self.doc_type == 'csv':
                    document = csv.reader(fp)
#                 print(document)
#                 if self.doc_type == 'xml':
#                     document = xml.load(fp)
                
                
                    
                if 'category_name' not in document or 'todos' not in document:
                    raise ValueError(('Invalid {} todo format.').format(self.doc_type))
                
                category_todos = []
                for todo in document['todos']:
                    if status == self.STATUS_ALL or todo['status'] == status:
                        category_todos.append(todo)
                todos[document['category_name']] = category_todos

        return todos
                

    # takes new task, set category, set due_on, add to list
    def new(self, task, category=CATEGORY_GENERAL, description=None,
            due_on=None):

        if due_on:
            if type(due_on) == date:
                due_on = due_on.isoformat()
            elif type(due_on) == str:
                # all good
                pass
            else:
                raise ValueError('Invalid due_on type. Must be date or str')

        todo_file_name = '{}.{}'.format(category, self.doc_type)
        path = self.path / todo_file_name
        
        todos = {
            'category_name': category.title(),
            'todos': []
        }
        
        if path.exists():
            with path.open('r') as fp:
                if self.doc_type == 'json':
                    todos = json.load(fp)
                if self.doc_type == 'toml':
                    todos = toml.load(fp)
                if self.doc_type == 'csv':
                    reader = csv.reader(fp)
                    todos = dict(reader)
                    todos.update({'todos': todos['todos']})
#                 if self.doc_type == 'xml':
#                     document = xml.load(fp)
                
                
        todo = {
            'task': task,
            'description': description,
            'due_on': due_on,
            'status': self.STATUS_PENDING
        }

        todos['todos'].append(todo)

        with path.open('w') as fp:
            if self.doc_type == 'json':
                todos = json.dump(todos, fp, indent=2)
            if self.doc_type == 'toml':
                todos = toml.dumps(todos, fp)
            if self.doc_type == 'csv':
                writer = csv.writer(fp)
                todos = dict(writer)
                for key, value in todos.items():
                    writer.writerow([key, value])
#             if self.doc_type == 'xml':
#                     todos = xml.dump(fp)
            
            