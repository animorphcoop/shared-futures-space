# Shared Futures Space
## Django/Wagtail + Postgres + Redis + Celery

- Build containers
```docker-compose up --build```

- After cloning for the first time: 
- `git-crypt unlock` 
- (assuming your public key has been given access). See .gitattributes for the files this affects.


To enter shell
```docker-compose exec app sh```


To run Django-related administrative commands
```docker-compose exec app django-admin startapp healerapp```
OR
```docker-compose exec app python3 manage.py startapp healerapp```


Create superuser

```docker-compose exec app python3 manage.py createsuperuser```

```docker-compose exec app python3 manage.py collectstatic```

Migrations

```docker-compose exec app python3 manage.py makemigrations && docker-compose exec app python3 manage.py migrate```

Running Tests
```
$ docker-compose exec app pytest tests
$ pyre
```
(they'll also run automatically on gitlab after a push)

---

### Using Static Typing
The key to effective use of static typing is the principle *"make illegal state unrepresentable"*. The type of a variable should cover precisely the set of values
it's expected to have and nothing else - that is, if a variable taking some specific value would cause
an error, the type system should be used to ensure that it can't take that value. That way, most kinds
of errors become type errors, and type errors are (hopefully) caught before runtime. This approach
means thinking about what each variable really represents.

#### The python type system in particular

A variable can be annotated when it is declared: `a_whole_number**: int** = 42`
A function can likewise be annotated at declaration, including its return type:
```
def add(A**: float**, B**: float**)** -> float**:
  return A + B
```
Parametric and otherwise special types must be imported from the typing library ([docs](https://docs.python.org/3/library/typing.html)).
These include:
- `List[T]`, `Dict[T,S]` - lists of type T and dicts from T to S (eg. `List[int]` or `Dict[str,bool]`)
- `Tuple[T1,T2,...,Tn]` - the type of an n-tuple of the given types. You can write `Tuple[T,...]` (ellipsis is literal) for a tuple of any number of Ts
- `Union[T1,T2,...,Tn]` - the type of a value which is one of a set of types. eg. `Union[str, int, List[int]]` accepts strings, integers and lists of integers
- `Optional[T]` - equivalent to `Union[T, None]`
- `Any` - matches any value at all
- `TypedDict` - dicts with specific known keys, which can be used to construct custom types like so:
```
class LabelledBinaryTree(TypedDict):
  label: str
  left: Optional[LabelledBinaryTree]
  right: Optional[LabelledBinaryTree]

tree: LabelledBinaryTree =
  {'label': 'root',
   'left': { 'label': 'leaf 1', 'left': None, 'right': None },
   'right': { 'label': 'leaf 2',
             'left': None,
             'right': { 'label': 'leaf 3', 'left': None, 'right': None}}}
```
### The type checker
run `pyre` to type check. The file `.pyre_configuration` must list the location of your python `site-packages` in its `search_path` key.
It will only type check functions that have their types declared, unless the file begins with `# pyre-strict`. If pyre is wrong about the type of something, you can suppress the error with `# pyre-ignore[n]` where n is the error type number that appears in the pyre output.
---

- Adding management commands:
management applies to the django naming convention: https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/


- Celery integration: 
http://celery.readthedocs.org/en/latest/django/first-steps-with-django.html

---

**NOTE: before using in a public-facing environment, don't forget to change the default credentials! They're in `app_variables.env`, `db_pg_variables.env`, `sfs/settings/local.py` and `.gitlab_ci.yml`**

---
Occasionally, issues with spinning new containers out of existing images might occur.


To stop containers and remove them along with images

```docker stop $(docker ps -a -q)```

```docker system prune -a```

Alternatively, to start from a clean slate 
```docker-compose build --force-rm --no-cache && docker-compose up```

---

Inspiration in regards to setting the path for venv in Dockerfile: https://pythonspeed.com/articles/activate-virtualenv-dockerfile/

```docker-compose exec app pip3 -V```
returns /home/app/venv/lib/python3.9/site-packages/pip (python 3.9)


---

Changed directory structure to nest all apps within one dir
https://stackoverflow.com/questions/22841764/best-practice-for-django-project-working-directory-structure
https://github.com/Mischback/django-project-skeleton/blob/development/project_name/settings/common.py


--- 
Editing and deleting accounts need to be address
current pattern : account/10/delete/



---
When adding celery task, restarting its container is required.

