# PROS branchline

a remote depot housing community templates for PROS development

usage:

install it by running
```shell
$ pip install .
```

you'll have to do this every time an edit is made, because the new packaging tools don't yet support editable installations
with pyproject.toml

add a valid YAML file (you can look at the sample file for reference) to ./templates and run
```shell
$ build-depot pros-branchline ./templates
```
to generate pros-branchline.json, a valid remote depot file

### TODO
- [ ] automate running this tool with a github action
- [ ] get some real templates in here
- [ ] publish to the world