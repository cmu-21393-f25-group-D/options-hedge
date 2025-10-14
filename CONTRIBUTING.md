# Contributing

This guide explains how to add your work to this project. As a team member and direct collaborator, you have write access to the repository and can push branches directly.

## Why This Workflow?

We're using a branch-based workflow with pull requests. This is the same process used at companies like Microsoft, Google, and Meta when their engineers collaborate on code. Here's why it works well:

- **Your contributions are properly credited** - Every commit shows your name and GitHub profile
- **Safe experimentation** - Work on feature branches without affecting the main codebase
- **Code review process** - Team members review each other's work before merging
- **Quality control** - Pre-commit hooks and CI checks ensure code standards
- **Clear history** - Easy to track what changed, when, and why
- **Portfolio ready** - Your work on this repo appears on your GitHub profile

## Getting Started: Setting Up Your Local Copy

1. Clone the repository directly (you're a collaborator, no fork needed!):

   ```bash
   git clone https://github.com/cmu-21393-f25-group-D/options-hedge.git
   cd options-hedge

   # Verify the clone worked
   git remote -v
   # You should see:
   # origin  https://github.com/cmu-21393-f25-group-D/options-hedge.git (fetch)
   # origin  https://github.com/cmu-21393-f25-group-D/options-hedge.git (push)
   ```

2. Set up your coding environment (we use Python's virtual environments to keep things clean):

   ```bash
   # Install our environment manager
   pip install uv

   # Create a virtual environment in the .venv folder
   uv venv

   # Activate the environment (choose the right command for your system)
   source .venv/bin/activate     # On Mac/Linux
   .venv\Scripts\activate        # On Windows

   # Install all the development tools
   uv pip install -e ".[dev]"

   # Set up automatic code quality checks
   pre-commit install
   ```

3. Install Gurobi (we use this for optimization):
   - Follow the installation guide at [Gurobi Installation Guide](https://www.gurobi.com/documentation/quickstart.html)
   - Get and set up your Gurobi license (they offer free academic licenses!)

## Making Changes

1. Get the latest updates from the repository:

   ```bash
   # Switch to your main branch
   git checkout main

   # Get the latest changes
   git pull origin main
   ```

2. Create a new branch for your changes:

   ```bash
   # For adding a new feature:
   git checkout -b feature/what-im-adding

   # For fixing a bug:
   git checkout -b fix/what-im-fixing

   # For updating docs:
   git checkout -b docs/what-im-changing
   ```

3. Make your changes! As you work, our pre-commit hooks will automatically:
   - Format your code with Ruff
   - Fix common style issues
   - Check for errors with Ruff
   - Run type checking with mypy

   These checks run every time you make a commit. If any issues are found:
   - Formatting issues will be fixed automatically
   - Other issues will be reported so you can fix them
   - After fixes, add the changes and commit again

   You can also run checks manually at any time:

   ```bash
   # Run all checks
   pre-commit run --all-files

   # Run tests
   uv run pytest
   ```

   If any checks show errors, don't worry! The error messages will guide you on what to fix.

4. Save your changes to GitHub:

   ```bash
   # Add all your changes
   git add .

   # Create a commit - pre-commit hooks will run automatically
   git commit -m "feat: Add a cool new feature"    # If you added something new
   git commit -m "fix: Fix the calculation bug"    # If you fixed a bug
   git commit -m "docs: Update the instructions"   # If you updated docs

   # Send your changes to your fork on GitHub
   git push origin your-branch-name
   ```

5. **Creating the Pull Request**
   - Push your changes to your fork with `git push origin your-branch-name`
   - Go to the original repository on GitHub
   - Click "Pull Requests" > "New Pull Request"
   - Click "compare across forks"
   - Select your fork and branch
   - Fill in the PR template completely
   - Link any related issues (if you're fixing a specific issue)

## What Happens Next?

1. Your pull request enters a collaborative review phase. Everyone in the project (yes, including you!) is encouraged to:
   - Review other people's code and provide feedback
   - Ask questions if something isn't clear
   - Suggest improvements or alternative approaches
   - Share knowledge and explain concepts

   Remember: Your reviews of others' code are just as visible on your GitHub profile as your own contributions. Thoughtful code reviews show potential employers/schools that you can analyze code critically and communicate professionally.

2. When others review your code, they might suggest some improvements. This is normal and helps demonstrate your professionalism! You can:
   - Ask questions about the suggestions
   - Discuss alternative approaches
   - Learn from others' experience
   - Share your reasoning for your implementation

   All these discussions stay on GitHub forever - they're a great showcase of your ability to collaborate and handle feedback professionally.

3. If you need to make changes based on the review, here's how:

   ```bash
   # Make the suggested changes in your code

   # Add and commit them
   git add .
   git commit -m "fix: Update based on review feedback"

   # Get any new changes from main
   git fetch upstream
   git rebase upstream/main

   # Update your PR
   git push -f origin your-branch-name
   ```

4. This review-update cycle might happen a few times - that's perfectly normal! It's how we maintain the high code quality that makes this project stand out. When someone looks at this repository in your portfolio, they'll see:
   - Clean, well-documented code
   - Professional communication
   - Thoughtful code reviews
   - Continuous improvement through feedback

5. Once the changes look good and reviewers approve, we'll merge your work. Congratulations - you've not only made the project better but also demonstrated valuable professional skills!

## Style Guide

Our code style is automatically enforced by pre-commit hooks, which will:

- Format code according to Ruff's standards
- Fix common style issues
- Check type hints
- Ensure consistent formatting

When writing code, you should also:

- Add type hints (like `def add(x: float, y: float) -> float:`)
- Write clear docstrings explaining what your code does
- Add comments for complex parts
- Write tests for new features

These practices help make our code more maintainable and easier to understand.
