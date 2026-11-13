# Checks

Run the same checks as the workflow:

```sh
python3 -m compileall -q server.py support scripts
python3 tests/check_page_js.py
python3 -m unittest discover -s tests -v
```
