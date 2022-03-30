# **Changelog**

This project adheres to *Semantic Versioning http://semver.org*.

## **`1.1.3.post3.BR - 2022-03-30`**

**Changes**
- Set `click` version to fixed value (8) to prevent compatibility issue
    - `AttributeError: module 'click' has no attribute 'get_os_args'`
    - https://github.com/streamlit/streamlit/issues/4555

## **`1.1.3.post2.BR - 2021-06-03`**

**Changes**
- Added optional removal of `_static` and `.doctree` directories after build of each version (except root)
- Replaced function `add_stylesheet` in sphinx_.py by `add_css_file`
    - `add_stylesheet` depracated and no longer supported in Sphinx

## **`1.1.3.post1.BR - 2021-04-10`**

**Changes**
- Moved changelog to separate file
- Added blacklisting capability
- Added capability to simplify vesion names using pattern matching

## **`1.1.3.post0.BR - 2021-03-20`**

**Fixes**
- Only return pdf_url if pdf is available
- Bug fix proposed by astoorangi (https://github.com/astoorangi/sphinx-versions)

## **`1.1.3 - 2019-07-18`**

**Changes**
- Fix pdf copy target directory

## **`1.1.2 - 2019-07-18`**

**Changes**
- Removes the rest of `unicode` function calls

## **`1.1.1 - 2019-07-18`**

**Changes**
- Removes compatibility with Python 2 (and make it work properly on Pyhton 3 : removing a call to `unicode` function)

## **`1.1.0 - 2019-07-18`**

**Changes**
- Add `-P pdf-file-name.pdf` option, thanks to `Anybotics fork <https://github.com/ANYbotics/sphinx-versions>`

## **`1.0.1 - 2019-04-23`**

**Changes**
- Update sphinx version from 1.8.4 to 1.8.5

## **`1.0.0 - 2018-12-08`**

**Changes**
- From *sphinxcontrib-versionning* *v2.2.1*, added compatibility with *Sphinx 1.8.2*.
- From *sphinxcontrib-versionning* *v2.2.1*, removed `push` commands, considered not core for our own usage.
- Migrates to ``pipenv`` as the recommanded installation process.
- Use `-s` option instead of `--no-patch` in `git show` (this is for git 1.8.3.1 compatibility).