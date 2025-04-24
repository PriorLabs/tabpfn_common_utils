# tabpfn-common-utils

## Installation
Install uv if not done already.

```bash
uv sync
```
installs all dependencies into a virtual environment.

Activate the venv
```bash
source .venv/bin/activate
```
This is optional and each command could be prefixed with `uv run` instead.


# Development
## Code Style
Also, to encourage better coding practices, `ruff` has been added to the pre-commit hooks. This will ensure that the code is formatted properly before being committed. To enable pre-commit (if you haven't), run the following command:
```sh
pre-commit install
```

### Type Checking
`pyright` is added as type checker to the repository.  

Because of legacy untyped code it has broad excludes for existing packages.  
New code must be typed and pass type checking.  
The old code will be typed along the way until type checking passes.

### Adding dependencies
```bash
uv add <dependency_name>
```
will add it to the current package.

There are other options like `--group dev` for development dependencies and `--group <name>` for arbitrary groups.

`uv` will update the lockfile in `uv.lock` with the exact set of dependencies used. Please commit the lock file to source control.