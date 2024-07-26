# Development for the NCCARenderFarm

You're interested in development, good on you! This program should be a good challenge for you to work on, and hopefully you'll be able to make it grow.

## Rules

1. Be respectful of others, this is a chance for you all to learn.
2. Don't leave broken code. If you break something, fix it! Or undo the changes you've made.
3. Try to document!

## Getting Started

This project uses git to manage development. so it is strongly recommended you have a bit of knowledge of git (pushing, pulling, branches, merging) before attempting to work on development. (you dont want to be the person who breaks the code)

To get started, you'll first need to git clone the nccarenderfarmtools repository, as well as setup vscode for development.

### Linux
On linux, navigate to your parent folder in a terminal, and then `git clone https://github.com/cjhosken/NCCARenderFarmTools`. You can then open it in vscode. Then, run `linux_setup.sh`

It is strongly recommended you have a bit of knowledge of git (pushing, pulling, branches, merging) before attempting to work on development. (you dont want to be the person who breaks the code)


### Windows

On windows, first install git and vscode from Apps Anywhere. Run vscode, and in the source control panel, choose initialize reposoity. Enter `cjhosken/NCCARenderFarmTools`

Open the project and then run `window_setup.bat`

### Running and Python linting

Install the python extension for vscode, 

You then need to select your interpreter. `Ctrl-Shift-P > Python: Select Interpreter`

Select the pyenv python version, which can be found in:
 - Linux: ``/home/{username}/.pyenv/versions/{python-version}/bin``
 - Windows: ``C:/Users/{username}/.pyenv/pyenv-win/versions/{python-version}/bin``

Using this interpreter for your code will allow you tee all the python linting for specific modules. 

*If you intend to add new python modules, you'll need to rerun the setup script.*

Once the interpreter is setup, navigate to NCCARenderFarm/main.py. You can then run the application using the play button in the top right. (no need to constantly rebuild!)

Now you should be able to start developing the tool.

## Documentation

I've tried to make the code as well documented as possible, and I plead you do the same (for the sake of others). If you get stuck understanding a concept, ChatGPT is extremely useful.

## Where do I start? / Github Issue Page

If you're new to development and want to help, but don't know what to do, a good place to start would be looking at the [issues page](https://github.com/cjhosken/NCCARenderFarmTools/issues) on the [GitHub repository](https://github.com/cjhosken/NCCARenderFarmTools).

There likely will be issues with the software that users need solving. Labels may need to be assigned to different issues, but hopefully users will figure that out.

All problems labelled ```low-priority-task``` are ones that should be simple fixes. If you want to challenge yourself, look at issues labelled `bug` or `feature`. Anything labelled `waiting-on-it` are things that IT needs to deal with. Sending an email to IT about it is a good place to get started on that.

## IT Issues

When you come across issues with IT, such as not having the correct software versions installed, and similar things like that, please be patient with them. It may take a while for them to fufill your requests.

## Code Authors

In `NCCARenderFarm/config/app.py` there is a variable called APPLICATION_AUTHORS.

If you feel that you've contributed large amounts to the project, feel free to add yourself to APPLICATION_AUTHORS. This is done on a trust basis. Please don't remove other people's names without their permission.


## Support
If you get very stuck, the lecturers are bound to help you with your coding problems. Otherwise, Google and ChatGPT are very viable options for writing you code.

If you want to get in contact with the original author, Christopher Hosken, you can do so [here](mailto:hoskenchristopher@gmail.com).