import json
import pytest
import shutil

from pathlib import Path
from datetime import date

from todos import TodoManager


TESTING_PATH = '__todos_testing'

# all 3 of the following fixtures will be a foundation for non fixture tests
# we can call upon these 3 fixtures to have a sort of 'setup' for our tests


# A path object will be created with the TESTING_PATH set up (but we need our 
# todos.py __init__ to actually create it as a dir)

@pytest.fixture
def path():
    return Path(TESTING_PATH)


# path object will mkdir ('__todos_testing' dir)

@pytest.fixture
def todos_dir_empty(path):
    path.mkdir()

    # essentially functions as return
    yield path

    # clean up - removes everything in the directory
    shutil.rmtree(str(path.absolute()))

    
# we add json files to the new created  '__todos_testing' dir
# '__todos_testing'
#      -programming.json
#      -reviews.json
    
@pytest.fixture
def todos_with_categories(todos_dir_empty):
    cat1 = todos_dir_empty / 'programming.json'
    cat2 = todos_dir_empty / 'reviews.json'

    with cat1.open('w') as fp:
        json.dump({
            'category_name': 'Programming',
            'todos': [{
                'task': 'Practice Pathlib',
                'description': 'Investigate Pathlib and file creation',
                'due_on': '2018-03-25',
                'status': 'pending'
            }, {
                'task': 'Finish rmotrgram',
                'description': 'Finish before class to start reviewing',
                'due_on': '2018-03-21',
                'status': 'done'
            }]
        }, fp, indent=2)

    with cat2.open('w') as fp:
        json.dump({
            'category_name': 'Reviews',
            'todos': [{
                'task': 'Review rmotrgram',
                'description': 'Finish review before weekend',
                'due_on': '2018-03-28',
                'status': 'pending'
            }]
        }, fp, indent=2)

    return todos_dir_empty


# within each test, it is a blank slate (path does'nt exist (yet!))
# our __init__ will define the path as an actual dir (making it exist)
# also note, we pass in 'path' as a parameter which is one of the 
# fixtures above

def test_todos_dir_is_created(path):
    assert not path.exists()

    manager = TodoManager(TESTING_PATH)
    assert path.exists()
    assert path.is_dir()

    # Clean up
    shutil.rmtree(str(path.absolute()))

    
# combine both programming.json/reviews.json into central todos
# reformat category_name value to be the key of below todos dict
    
def test_todo_list_status_all(todos_with_categories):
    manager = TodoManager(TESTING_PATH)
    todos = manager.list()
    assert todos == {
        'Programming': [{
            'task': 'Practice Pathlib',
            'description': 'Investigate Pathlib and file creation',
            'due_on': '2018-03-25',
            'status': 'pending'
        }, {
            'task': 'Finish rmotrgram',
            'description': 'Finish before class to start reviewing',
            'due_on': '2018-03-21',
            'status': 'done'
        }],
        'Reviews': [{
            'task': 'Review rmotrgram',
            'description': 'Finish review before weekend',
            'due_on': '2018-03-28',
            'status': 'pending'
        }]
    }

    
# filter for status 'pending'

def test_todo_list_status_pending(todos_with_categories):
    manager = TodoManager(TESTING_PATH)
    todos = manager.list(status=TodoManager.STATUS_PENDING)
    assert todos == {
        'Programming': [{
            'task': 'Practice Pathlib',
            'description': 'Investigate Pathlib and file creation',
            'due_on': '2018-03-25',
            'status': 'pending'
        }],
        'Reviews': [{
            'task': 'Review rmotrgram',
            'description': 'Finish review before weekend',
            'due_on': '2018-03-28',
            'status': 'pending'
        }]
    }

    
# filter for status 'done'    

def test_todo_list_status_done(todos_with_categories):
    manager = TodoManager(TESTING_PATH)
    todos = manager.list(status=TodoManager.STATUS_DONE)
    assert todos == {
        'Programming': [{
            'task': 'Finish rmotrgram',
            'description': 'Finish before class to start reviewing',
            'due_on': '2018-03-21',
            'status': 'done'
        }],
        'Reviews': []
    }


def test_create_new_todo_general_empty_dir_default_vals(todos_dir_empty):
    manager = TodoManager(TESTING_PATH)
    manager.new('New Testing Task')

    general_todos_path = todos_dir_empty / 'general.json'

    assert general_todos_path.exists()
    with general_todos_path.open('r') as fp:
        todos = json.load(fp)

    assert todos == {
        'category_name': 'General',
        'todos': [{
            'task': 'New Testing Task',
            'description': None,
            'due_on': None,
            'status': 'pending'
        }]
    }


def test_create_new_todo_general_empty_dir_due_str(todos_dir_empty):
    manager = TodoManager(TESTING_PATH)
    manager.new(
        'New Testing Task',
        description='A new task to test...',
        due_on='2018-03-28')

    general_todos_path = todos_dir_empty / 'general.json'

    assert general_todos_path.exists()
    with general_todos_path.open('r') as fp:
        todos = json.load(fp)

    assert todos == {
        'category_name': 'General',
        'todos': [{
            'task': 'New Testing Task',
            'description': 'A new task to test...',
            'due_on': '2018-03-28',
            'status': 'pending'
        }]
    }


def test_create_new_todo_general_empty_dir_due_date(todos_dir_empty):
    manager = TodoManager(TESTING_PATH)
    manager.new(
        'New Testing Task',
        description='A new task to test...',
        due_on=date(2018, 3, 1))

    general_todos_path = todos_dir_empty / 'general.json'

    assert general_todos_path.exists()
    with general_todos_path.open('r') as fp:
        todos = json.load(fp)

    assert todos == {
        'category_name': 'General',
        'todos': [{
            'task': 'New Testing Task',
            'description': 'A new task to test...',
            'due_on': '2018-03-01',
            'status': 'pending'
        }]
    }


def test_create_new_todo_other_category_empty_dir(todos_dir_empty):
    manager = TodoManager(TESTING_PATH)
    manager.new(
        'New Testing Task',
        category='programming',
        description='A new task to test...',
        due_on=date(2018, 3, 1))

    general_todos_path = todos_dir_empty / 'programming.json'

    assert general_todos_path.exists()
    with general_todos_path.open('r') as fp:
        todos = json.load(fp)

    assert todos == {
        'category_name': 'Programming',
        'todos': [{
            'task': 'New Testing Task',
            'description': 'A new task to test...',
            'due_on': '2018-03-01',
            'status': 'pending'
        }]
    }


def test_create_new_todo_with_existing_todos(todos_with_categories):
    manager = TodoManager(TESTING_PATH)
    manager.new(
        'New Testing Task',
        category='programming',
        description='A new task to test...',
        due_on=date(2018, 3, 1))

    general_todos_path = todos_with_categories / 'programming.json'

    assert general_todos_path.exists()
    with general_todos_path.open('r') as fp:
        todos = json.load(fp)

    assert todos == {
        'category_name': 'Programming',
        'todos': [{
            'task': 'Practice Pathlib',
            'description': 'Investigate Pathlib and file creation',
            'due_on': '2018-03-25',
            'status': 'pending'
        }, {
            'task': 'Finish rmotrgram',
            'description': 'Finish before class to start reviewing',
            'due_on': '2018-03-21',
            'status': 'done'
        }, {  # New todo:
            'task': 'New Testing Task',
            'description': 'A new task to test...',
            'due_on': '2018-03-01',
            'status': 'pending'
        }]
    }
