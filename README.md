# Upgrade `knausj`

Helper for performing `knausj` upgrades.

## Assumptions

- You have a fork of `knausj`
- You haven't altered your pre-commit config. If you don't know what that means, then you are fine 😊

## Installation

1. Install [`pipx`](https://pypa.github.io/pipx/)
2. Run `pipx install upgrade-knausj`

## How to run

1. Push your changes to your fork
2. Run `upgrade-knausj`
3. If necessary, resolve any merge conflicts, commit, then re-run `upgrade-knausj`
4. Repeat steps 2-3 until it says you're done
5. Do a pull from your main Talon user directory
6. Restart Talon and look in the log file for errors
