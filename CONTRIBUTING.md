# Contributing

This guide explains how to add your work to this project. In open source projects, the CONTRIBUTING.md file (this file!) is where you'll find step-by-step instructions for how to make changes to the codebase properly.

Don't worry if some of these steps feel unfamiliar! We're using a workflow called "fork and pull request" - it's the same process used at companies like Microsoft, Google, and Meta when their engineers collaborate on code. Here's how it works:

1. First, you'll create your own copy (called a "fork") of this project on GitHub
2. Make your changes in your copy
3. Submit those changes back to the main repository

This might seem like extra steps compared to editing files directly, but there's a good reason: When you fork the repository, you get your own copy that's permanently linked to your GitHub profile. This means:

- Every contribution you make is properly credited to you
- Your work appears in your GitHub portfolio (perfect for job or grad school applications!)
- Future employers/schools can see not just your code, but also how well you:
  - Collaborate with others through code reviews
  - Write clear documentation and commit messages
  - Handle feedback professionally
  - Maintain high code quality standards
- You can safely experiment without worrying about breaking anything
- You can still contribute changes back to the main project seamlessly

It's like having your own personal workspace that's connected to the main project. Many of today's most popular open source projects, like React, TensorFlow, and VS Code, use this exact same workflow - and their hiring managers specifically look for these collaboration skills.

## Getting Started: Setting Up Your Copy

1. First, fork (make your own copy of) this repository:
   - Go to [https://github.com/akhilkarra/options-hedge](https://github.com/akhilkarra/options-hedge)
   - Click the "Fork" button in the top-right corner
   - Wait for GitHub to create your copy
   - You'll be redirected to your fork (it should show YOUR-USERNAME/options-hedge)

2. Check that the fork worked:
   - Your GitHub URL should now be `https://github.com/YOUR-USERNAME/options-hedge`
   - You should see "forked from akhilkarra/options-hedge" under the repository name
   - The commit history and code should be identical to the original

3. Clone your fork to your computer (replace YOUR-USERNAME with your actual GitHub username):

   ```bash
   git clone https://github.com/YOUR-USERNAME/options-hedge.git
   cd options-hedge

   # Check that the clone worked
   git remote -v
   # You should see:
   # origin  https://github.com/YOUR-USERNAME/options-hedge.git (fetch)
   # origin  https://github.com/YOUR-USERNAME/options-hedge.git (push)
   ```

4. Set up a connection to the original repository (so you can get updates later):

   ```bash
   git remote add upstream https://github.com/akhilkarra/options-hedge.git

   # Verify it worked - you should now see both origin and upstream:
   git remote -v
   # You should see four lines:
   # origin    https://github.com/YOUR-USERNAME/options-hedge.git (fetch)
   # origin    https://github.com/YOUR-USERNAME/options-hedge.git (push)
   # upstream  https://github.com/akhilkarra/options-hedge.git (fetch)
   # upstream  https://github.com/akhilkarra/options-hedge.git (push)
   ```

5. Set up your coding environment (we use Python's virtual environments to keep things clean):

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

6. Install Gurobi (we use this for optimization):
   - Follow the installation guide at [Gurobi Installation Guide](https://www.gurobi.com/documentation/quickstart.html)
   - Get and set up your Gurobi license (they offer free academic licenses!)

## Making Changes

1. Get the latest updates from the original repository:

   ```bash
   # Switch to your main branch
   git checkout main

   # Get updates from the original repository (upstream)
   git fetch upstream

   # Add those updates to your fork's main branch
   git rebase upstream/main

   # Update your fork on GitHub
   git push origin main
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
