# **sphinx-versions**

Sphinx extension that allows building versioned docs for self-hosting.

- Python 3.4, and 3.5 supported on Linux and OS X.
- Python 3.4, and 3.5 supported on Windows (both 32 and 64 bit versions of Python).

Full documentation: https://sphinx-versions.readthedocs.io/en/latest/

This project is, for the most part, a fork of https://github.com/Robpol86/sphinxcontrib-versioning and later https://github.com/Smile-SA/sphinx-versions, with some additions and removals.

## **How to use**

Most basic usage:

``` bash

sphinx-versions --help
sphinx-versions build --help

```

## Whitelisting / Blacklisting
- if no list is defined, everything is included
- if a whitelist is defined, everything that does not match at least one item, is excluded
- if a blacklist is defined, everything that matches at least one item, is excluded
- if whitelist and blacklist are present at the same time: whitelist is applied first and on the result is applied blacklist

**Note:** Blacklisting was added in `1.1.3.post1.BR` and therefore is not documented in the full documentation, but it can be used the same way as whitelisting:

``` python

# whitelisting tuples
scv_whitelist_tags
scv_whitelist_branches
# blacklisting tuples
scv_blacklist_tags
scv_blacklist_branches

```

## Name simplification

**Note:** Name simplification was added in `1.1.3.post1.BR` and therefore is not documented in the full documentation.

It is possible to simplify names if there are no clashes after simplification. If there are clashes, the simplification is not performed on the clashing items.

To simplify a name, sub-pattern searching has to be used in whitelisting:

``` python

# The following line will cause the algorithm to attempt name simplification e.g. from 0.0.1.doc to 0.0.1
scv_whitelist_tags = (
    re.compile(r'^([0-9]+\.[0-9]+\.[0-9]+)\.doc$'),
)

# The following line will not cause the algorithm to attempt name simplification
scv_whitelist_tags = (
    re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+\.doc$'),
)

```

## Delete redundant directories

**Note:** Directory deletion was added in `1.1.3.post2.BR` and therefore is not documented in the full documentation.

Directories `_static` and `.doctree` are in each version by default. In order to save space they can be removed.

``` python

# The following command triggers the deletion
scv_delete_static = True

```
