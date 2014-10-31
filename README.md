# Topcoder plugin for Sublime Text 2 / 3

Plugin that takes a copy-pasted topcoder problem description in a sublime tab (python only for now) and parses out common features:

* className
* signature
* test cases

Then generates a new sublime tab where it populates className, signature, and writes some test cases for you

TODOs:
1. handle multiple argument signatures
2. handle other topcoder languages
3. refactor code for handling test cases

## Installation

### Package Control

The easiest way to install this is with [Package
Control](http://wbond.net/sublime\_packages/package\_control).

 * If you just went and installed Package Control, you probably need to restart Sublime Text 2 before doing this next bit.
 * Bring up the Command Palette (Command+Shift+p on OS X, Control+Shift+p on Linux/Windows).
 * Select "Package Control: Install Package" (it'll take a few seconds)
 * Select Topcoder when the list appears.

Package Control will automatically keep Quick File Creator up to date with the latest
version.

### Clone from GitHub

Alternatively, you can clone the repository directly from GitHub into your Packages directory:

    git clone http://github.com/charlieyan/topcoderSublimePlugin

## Key bindings

The plugin now installs key bindings automatically. Alternatively you can set
up your own key bindings like this by adding to your user key bindings file:

    { "keys": ["ctrl+shift+t"], "command": "topcoder" }