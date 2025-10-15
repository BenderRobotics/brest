# Bender Robotics Embedded Systems Toolkit documentation builder

## Building
To build the most recent documentation offline, follow the steps in the main README (`.\..\README.md`).

The documentation is by default built only upon tagged commits.
This can complicate development or update of the documentation.
To include the version of documentation that is currently being worked on, change the `current_branch` parameter in `.\conf.py` to the branch with the changes.
To view the documentation generated for the enabled current branch, go to the generated documentation and switch to the version called the same as the current branch.
- Default state:
    ``` python

    current_branch = 'none'
    ```
- Example of enabling current branch:
    ``` python

    current_branch = r'feature/3465-doc-design-and-version'
    ```

## Customizing the look
The customization is done on multiple places.
Most of the customization is done via theme built-in functionalities that can be controlled in `.\conf.py`.
For information on possibilities please refer to the theme documentation https://sphinx-rtd-theme.readthedocs.io/en/stable/configuring.html.

The brest documentation version is altered a bit. The customization is so far handled by a *.css* file `.\_static\brest.css`.

### Specific modifications
- Title
    - The title is located in the upper left corner. It is the package name.
    - The string is explicitly set (`conf.py` - `#PY-002`).
    - The font size is explicitly set (`brest.css` - `#CSS-001`).
    - The title has normally "house" icon next to it.
        - The icon is suppressed (`brest.css` - `#CSS-002`).
- Logo
    - Logo picture is usually located just under the title.
    - It can be enabled by setting `html_logo` variable (`conf.py` - `#PY-005`).
        - Enabled.
    - Space between Logo and Title is adjusted (`brest.css` - `#CSS-003`).
- Favicon
    - Explicitly set (`conf.py` - `#PY-006`).
- Version
    - Version identifier is located just under the logo.
    - The string has to be set in variable `version` (`conf.py` - `#PY-001`).
    - It's visibility is explicitly set (`brest.css` `#CSS-005`).
    - Space between Logo and Version is adjusted (`brest.css`- `#CSS-004`).
- Navigation menu
    - Navigation menu is located on the left side.
        - The background color is explicitly set (`conf.py` - `#PY-004`).
    - By default the top level items in the menu change color to blueish when clicked.
        - The color has been set to match the global color (`brest.css` - `#CSS-006`).
    - Navigation for narrow page.
        - The color in packed state and width in unpacked state were set to explicit values (`brest.css` - `#CSS-009`).
- Breadcrumbs
    - This part is located at the top of the page and shows the active section.
    - There is a "home" icon for returning back to the *index* of the documentation.
        - This icon's size is explicitly set (`brest.css` - `#CSS-007`).
- Other
    - The template comes with a *View page source* link button.
        - The button is disabled (`brest.css` - `#CSS-008`).
    - The template has possibility of "previous" and "next" buttons.
        - The buttons are disabled (`conf.py` - `#PY-004`).
    - The template enables to show copyright text.
        - The text is explicitly set (`conf.py` - `#PY-004`).

## Customizing the versioning capabilities
The versioning is done by adjusted python package `sphinx-versions`.
For information on the package refer to the corresponding README file located in: `.\..\cm\sphinx-versions\`.

## Changelog

### [0.0.13] - 2021-11-18
- Switched theme from `alabaster` to `sphinx_rtd_theme`.
- Added versioning capabilities.
- Updated old docs to the new theme.
- Set versioned docs generation to take only tagged versions with updated theme.
