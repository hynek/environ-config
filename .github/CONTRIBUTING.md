# How To Contribute

Thank you for considering contributing to *environ-config*!
It's people like *you* who make it such a great tool for everyone.

This document intends to make contribution more accessible by codifying tribal knowledge and expectations.
Don't be afraid to open half-finished PRs, and ask questions if something is unclear!

Please note that this project is released with a Contributor [Code of Conduct](https://github.com/hynek/environ-config/blob/main/.github/CODE_OF_CONDUCT.md).
By participating in this project you agree to abide by its terms.
Please report any harm to [Hynek Schlawack] in any way you find appropriate.


## Workflow

- No contribution is too small!
  Please submit as many fixes for typos and grammar bloopers as you can!
- Try to limit each pull request to *one* change only.
- Since we squash on merge, it's up to you how you handle updates to the `main` branch.
  Whether you prefer to rebase on `main` or merge `main` into your branch, do whatever is more comfortable for you.
- *Always* add tests and docs for your code.
  This is a hard rule; patches with missing tests or documentation won't be merged.
- Make sure your changes pass our [CI].
  You won't get any feedback until it's green unless you ask for it.
  For the CI to pass, the coverage must be 100%.
  If you have problems to test something, open anyway and ask for advice.
  In some situations, we may agree to add an `# pragma: no cover`.
- Once you've addressed review feedback, make sure to bump the pull request with a short note, so we know you're done.
- Don’t break backwards-compatibility.


## Local Development Environment

You can (and should) run our test suite using [Nox].
However, you’ll probably want a more traditional environment as well.

First, create a [virtual environment](https://virtualenv.pypa.io/) so you don't break your system-wide Python installation.
We recommend using the Python version from the `.python-version-default` file in project's root directory.

If you're using [*direnv*](https://direnv.net), you can automate the creation of a virtual environment with the correct Python version by adding the following `.envrc` to the project root after cloning it:

```bash
layout python python$(cat .python-version-default)
```

[Create a fork](https://github.com/hynek/environ-config/fork) of the repository and clone it:

```console
$ git clone git@github.com:YOU/environ-config.git
```

Or if you prefer to use Git via HTTPS:

```console
$ git clone https://github.com/YOU/environ-config.git
```

> **Warning**
> - **Before** you start working on a new pull request, use the "*Sync fork*" button in GitHub's web UI to ensure your fork is up to date.
> - **Always create a new branch off `main` for each new pull request.**
>   Yes, you can work on `main` in your fork and submit pull requests.
>   But this will *inevitably* lead to you not being able to synchronize your fork with upstream and having to start over.

Change into the newly created directory and after activating a virtual environment, install an editable version of *environ-config* along with its tests and docs requirements:

```console
$ cd environ-config
$ python -Im pip install --upgrade pip  # PLEASE don't skip this step
$ python -Im pip install -e . --group dev
```

At this point,

```console
$ python -Im pytest
```

For documentation, you can use:

```console
$ nox --session docs -- watch
```

This will build the documentation, and then watch for changes and rebuild it whenever you save a file.

To just build the documentation and run doctests, use:

```console
$ nox --session docs
```

You will find the built documentation in `docs/_build/html`.

---

To avoid committing code that violates our style guide, we strongly advise you to install [*pre-commit*] and its hooks:

```console
$ pre-commit install
```

This is not strictly necessary, because our [Nox] file contains an environment that runs:

```console
$ pre-commit run --all-files
```

and our CI has integration with [pre-commit.ci](https://pre-commit.ci).
But it's way more comfortable to run it locally and *git* catching avoidable errors.


## Code

- Obey [PEP 8] and [PEP 257].
  We use the `"""`-on-separate-lines style for docstrings with [Napoleon](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html)-style API documentation:

  ```python
  def func(x: str) -> str:
      """
      Do something.

      Args:
        x: A very important parameter.

      Returns:
        The result of doing something.
      """
  ```

  Please note that unlike everything else, the API docstrings are still [reStructuredText].
- If you add or change public APIs, tag the docstring using `..  versionadded:: 16.0.0 WHAT` or `..  versionchanged:: 16.2.0 WHAT`.
- We use [Ruff](https://ruff.rs/) to sort our imports and format our code with a line length of 79 characters.
  As long as you run our full [Nox] suite before committing, or install our [*pre-commit*] hooks (ideally you'll do both – see [*Local Development Environment*](#local-development-environment) above), you won't have to spend any time on formatting your code at all.
  If you don't, [CI] will catch it for you – but that seems like a waste of your time!


## Tests

- Write your asserts as `expected == actual` to line them up nicely:

  ```python
  x = f()

  assert 42 == x.some_attribute
  assert "foo" == x._a_private_attribute
  ```

- To run the test suite, all you need is a recent [Nox].
  It will ensure the test suite runs with all dependencies against all Python versions just as it will in our [CI].
- Write [good test docstrings](https://jml.io/pages/test-docstrings.html).
- If you've changed or added public APIs, please update our type stubs (files ending in `.pyi`).


## Documentation

- We use [Markdown] everywhere except in `docs/api.rst` and docstrings.

- Use [semantic newlines] in [reStructuredText] and [Markdown] files (files ending in `.rst` and `.md`):

  ```markdown
  This is a sentence.
  This is another sentence.
  ```

- If you start a new section, add two blank lines before and one blank line after the header, except if two headers follow immediately after each other:

  ```markdown
  Last line of previous section.


  ## Header of New Top Section

  ###  Header of New Section

  First line of new section.
  ```


### Changelog

If your change is noteworthy, there needs to be a changelog entry in [`CHANGELOG.md`](https://github.com/hynek/environ-config/blob/main/CHANGELOG.md), so our users can learn about it!

- As with other docs, please use [semantic newlines] in the changelog.
- Make the last line a link to your pull request.
  You probably have to open it first to know the number.
- Wrap symbols like modules, functions, or classes into backticks so they are rendered in a `monospace font`.
- Wrap arguments into asterisks like in docstrings:
  `Added new argument *an_argument*.`
- If you mention functions or other callables, add parentheses at the end of their names:
  `environ.func()` or `environ.Class.method()`.
  This makes the changelog a lot more readable.
- Prefer simple past tense or constructions with "now".
  For example:

  * Added `environ.func()`.
  * `environ.func()` now doesn't crash the Large Hadron Collider anymore when passed the *foobar* argument.


#### Example entries

```markdown
- Added `environ.func()`.
  The feature really *is* awesome.
  [#1](https://github.com/hynek/environ-config/pull/1)
```

or:

```markdown
- `environ.func()` now doesn't crash the Large Hadron Collider anymore when passed the *foobar* argument.
  The bug really *was* nasty.
  [#1](https://github.com/hynek/environ-config/pull/1)
```


[CI]: https://github.com/hynek/environ-config/actions
[Hynek Schlawack]: https://hynek.me/about/
[*pre-commit*]: https://pre-commit.com/
[Nox]: https://nox.thea.codes/
[semantic newlines]: https://rhodesmill.org/brandon/2012/one-sentence-per-line/
[reStructuredText]: https://www.sphinx-doc.org/en/stable/usage/restructuredtext/basics.html
[Markdown]: https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax
