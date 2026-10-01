## Session 1 — [10/1/26]

### Prompt used
[Add error handling to the get_task function in @services/tasks.py. Do not change the function signature. Run pytest -v when done.]

### What Claude did
[Claude correctly added error handling for a missing task associated with a task id being looked up in /services/tasks.py. It correctly added error handling using the provided errors.py and didn't raise raw exceptions. It also tested the code and ran pytest -v as it should have. The only issue is it did not run "ruff" which is my python code linter. ]

### Observation
[It correctly used the NotFoundError() function from "@utils/errors.py". This was the file that I specified it should use in my CLAUDE.md (in the architecture section) to do any error handling. This was followed correctly. I included commands for running and installing pytest (it didn't need to install pytest). Claude successfully ran pytest -v since it was specified to do that both the prompt and in the CLAUDE.md "- Run: `pytest -v` and `ruff check .` before finishing any tasks" however, it did not run ruff. I originally did task 1 for this PA 4 on my laptop and then transferred the repo over with github to finish the assignment on my desktop. However my desktop did not have ruff installed and I did not give sufficient instructions for downloading it if it was not installed so claude just told me to install it myself. This is not what I intended since I want claude to be self sufficient and to download any required tools to do the linting and the software validation. Because of this I need to update the CLAUDE.md to include detailed instructions for downloading these tools and to specify that claude is expected to download these if they do not currently exist on my instance of WSL.]

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
Claude not only added the docstrings to look similar to users.py (specified in this rule: Google-style docstrings are required on every function with "args:", "Returns: ", and "Raises: " sections that match "get_user" from @services/users.py) but it also added validation (ValidationError) from errors.py without me prompting it to (this is also coming from a CLAUDE.md rule: Raise only "AppError" subclasses from @utils/errors.py never raise raw exceptions)]

### CLAUDE.md update (if any)
[
I am changing these rules to now match the powershell environment:
- If a tool needs to be downloaded with sudo and the user has not already provided sudo access run `sudo -v` and ask them to input their password
- Install commands: 'see @install_commands.txt for detailed install commands for all tools (always download missing tools)'
I am replacing them with these lines:
- If a tool needs to be downloaded assume powershell is being used. If the user is using wsl prompt them to switch to powershell as nothing in this project is linux specific
- Install commands: `pip install -r requirements.txt`
removed:
- Before installing any tools run `sudo apt update`
@install_commands.txt

I fixed this typo:
-Raise only "AppError" subclasses from @utils/error.py never raise raw exceptions
as
- Raise only "AppError" subclasses from @utils/errors.py never raise raw exceptions
]