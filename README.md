# Upgrade Talon `community`

Helper for performing upgrades to get the latest version of the [Talon `community` repository](https://github.com/talonhub/community). Please see https://youtu.be/Nbz7A9pGkQ0 for a detailed walkthrough of using this utility.

## Assumptions

- You have a fork of `community`
- You haven't altered your pre-commit config. If you don't know what that means, then you are fine 😊

## Installation

1. Install [`pipx`](https://pypa.github.io/pipx/)
2. Run `pipx install pre-commit`
3. Run `pipx install upgrade-talon-community`

## How to run

1. **IMPORTANT** Push your local changes from your main Talon user directory to your fork. If you don't know how to do that, please ask on the [Talon Slack](https://talonvoice.com/chat) in the #upgrade-community channel.
2. Run `upgrade-talon-community`
3. If necessary, resolve any merge conflicts, commit, then re-run `upgrade-talon-community`
4. Repeat steps 2-3 until it says you're done
5. Do a pull from your main Talon user directory
6. Restart Talon and look in the log file for errors

## How it works

This utility clones a clean copy of your user files from your GitHub repo to a folder on your hard drive, and then attempts to perform a git merge with the latest version of knausj. The knausj repo has a few commits that were simply autoformatting, which can be challenging to merge, so we handle those specially by just running the autoformatter on your code. See https://youtu.be/Nbz7A9pGkQ0 and the code of this repository for more details.
