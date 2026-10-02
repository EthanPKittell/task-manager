## Session 1 — [10/1/26]

### Prompt used
[Add error handling to the get_task function in @services/tasks.py. Do not change the function signature. Run pytest -v when done.]

### What Claude did
[Claude correctly added error handling for a missing task associated with a task id being looked up in /services/tasks.py. It correctly added error handling using the provided errors.py and didn't raise raw exceptions. It also tested the code and ran pytest -v as it should have. The only issue is it did not run "ruff" which is my python code linter. ]

### Observation
[It correctly used the NotFoundError() function from "@utils/errors.py". This was the file that I specified it should use in my CLAUDE.md (in the architecture section) to do any error handling. This was followed correctly. I included commands for running and installing pytest (it didn't need to install pytest). Claude successfully ran pytest -v since it was specified to do that both the prompt and in the CLAUDE.md "- Run: `pytest -v` and `ruff check .` before finishing any tasks" however, it did not run ruff. I originally did task 1 for this PA 4 on my laptop and then transferred the repo over with github to finish the assignment on my desktop. However my desktop did not have ruff installed and I did not give sufficient instructions for downloading it if it was not installed so claude just told me to install it myself. This is not what I intended since I want claude to be self sufficient and to download any required tools to do the linting and the software validation. Because of this I need to update the CLAUDE.md to include detailed instructions for downloading these tools and to specify that claude is expected to download these if they do not currently exist on my instance of WSL. Overall session 1 needed 2 corrections: adding extra hand holding rules to install these tools with sudo when they are missing in WSL and adding a txt file with explicit commands to download these tools for extra insurance.]

### CLAUDE.md update (if any)
[I had to add these three lines to "commands" to counteract claudes inability to install missing tools:
- Install commands: see @install_commands.txt for detailed install commands for all tools (always download missing tools)
- If a tool needs to be downloaded with sudo and the user has not already provided sudo access run `sudo -v` and ask them to input their password
- Before installing any tools run `sudo apt update`
I added this to "conventions" just for safe measure:
- When following the @install_commands.txt for tool installation always download tools using the -y flag so WSL does not ask for a Y/n confirmation
I removed this line since it added no value:
- Install command: `pip install -r requirements.txt` (this would have probably worked for powershell not WSL)
]




## Session 2 — [10/1/26]
### Prompt used
[Refactor create_task in @services/tasks.py to match the style of get_user in @services/users.py exactly. Run pytest -v when done. Download ruff and flask if these tools are missing and run ruff on changed or new code. Fix any issues with installation along the way.]

### What Claude did
[Claude correctly refactored tasks.py to match the style of get_user in /services/users.py. More or less it added similar doc strings and added extra validation which was not there originally. Overall this was a solid implementation of this refactoring. Claude also added three new tests for create_task (valid, blank title, unknown user). The existing tests were untouched. Claude once again was unable to download ruff or flask.]

### Observation
[Once again Claude was unable to install ruff and flask even with extra rules for having the user use "sudo -v" to allow for sudo commands to run without the user being involved. I couldn't even run "! sudo -v" to put in a password for shell commands in the claude prompt as I was unable to get the password query to show up. Also doing sudo -v beforehand didn't work either. I am switching to powershell as nothing in the project requires a linux filesystem or shell scripts. I am adding requirements to CLAUDE.md to have the user do all tool installations and running code in powershell only so I can just use pip instead of messing with claude not being able to use sudo or run with root user. These wsl specific rules like "Before installing any tools run `sudo apt update`" have now been deleted to fix this issue.
Claude not only added the docstrings to look similar to users.py (specified in this rule: Google-style docstrings are required on every function with "args:", "Returns: ", and "Raises: " sections that match "get_user" from @services/users.py) but it also added validation (ValidationError) from errors.py without me prompting it to (this is also coming from a CLAUDE.md rule: Raise only "AppError" subclasses from @utils/errors.py never raise raw exceptions) Overall Session 2 needed 1 correction to fix future prompt output: switching my shell from WSL to powershell.]

### Honest failure
I should have never used WSL to begin with and this stunted the output of both prompts up until this point. I was not aware that Claude Code runs all its commands without an interactive terminal, so sudo could not prompt me for a password. Going forward unless my project absolutely requires linux commands I will use powershell with Claude Code.

### CLAUDE.md update (if any)
[
I am changing these rules to now match the powershell environment:
- If a tool needs to be downloaded with sudo and the user has not already provided sudo access run `sudo -v` and ask them to input their password
- Install commands: 'see @install_commands.txt for detailed install commands for all tools (always download missing tools)'
I am replacing them with these lines:
- If a tool needs to be downloaded assume powershell is being used. If the user is using wsl prompt them to switch to powershell as nothing in this project is linux specific
- Install commands: `pip install -r requirements.txt`
removed:
- When following the @install_commands.txt for tool installation always download tools using the -y flag so WSL does not ask for a Y/n confirmation
- Before installing any tools run `sudo apt update`
@install_commands.txt

I fixed this typo:
-Raise only "AppError" subclasses from @utils/error.py never raise raw exceptions
as
- Raise only "AppError" subclasses from @utils/errors.py never raise raw exceptions
]

## Session 3 — [10/1/26]
### Prompt used
[Add a new function to @services/tasks.py that returns all tasks for a given user_id. Follow the same pattern as the existing functions. Add a test for it. Run pytest -v when done. Install any tools that are missing using.]

### What Claude did
[Claude correctly installed all missing tools and was able to run lint. It did not however, do anything with the 6 failures that occurred from doing a ruff lint for the first time so it correctly did not edit anything further:

The ruff errors:
- Import sorting (I001): app.py, routes/api.py and tests/test_tasks.py. The test file's import line is the one I extended, but it was already unsorted.
- Unused import (F401): process_order in routes/api.py.
- Blind pytest.raises(Exception) (B017): the two existing tests test_process_order_invalid and test_get_task_invalid. Fixing these means editing existing tests, *****which CLAUDE.md forbids.*****

I will add behavior to fix this by having claude bring up each lint to the user and mend the issue depending on their response.

On top of this Claud successfully implemented the new function I requested. It looks identical to other functions implemented will all the same traits outlined in the conventions section. 2 tests were also added and claude correctly did not edit existing tests even with the lint results (outlined in Do-Not-Touch: "- For existing tests in @tests/test_tasks.py never edit or delete them..." )

Session 1 needed 2 CLAUDE.md corrections, session 2 needed 1 correction, session 3 needed 1.
]

### Observation
[Similar to "### What Claude did" it correctly implemented the new function taking inspiration from the "conventions section". Claude added 2 new tests and did not exit anything else in the specified @tests/test_tasks.py test location. All 9 tests passed when Claude ran pytest -v specified in my CLAUDE.md "- Run: `pytest -v` and `ruff check .` before finishing any tasks". Only weird result is the first ever lint after it installed all tools. I did not set up any behavior for this so I need to have Claude ask the user how to proceed if any lint errors do occur. Overall this session went well for the output in my opinion and requires a small lint behavior change to CLAUDE.md. Other than that I am happy with the function implementation and results.]

### CLAUDE.md update (if any)
[Changed the commands rule to include behavior after running the lint command:
- Lint: `ruff check .` ask the user how to handle each lint error if any occur]
