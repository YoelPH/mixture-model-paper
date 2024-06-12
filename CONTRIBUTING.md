# How to Collaborate

This document explains how to collaboratively write on this paper draft.

## Viewing the Document

First, I always try to push the latest changes to the [GitHub pages of the repository](https://rmnldwg.github.io/bilateral-paper). So, without cloning the repository, you can read a mostly up-to-date version of the draft there.

## Get the Repository

For collaborating, what you want to do is head over to the [remote repository on GitHub][this repo]. There, towards the top right of the page, you'll find a "fork" button (in between "watch" and "star"). Click that to create a fork (i.e. a copy owned by you) of this repository under your username.

Now you should be able to clone (i.e. download) your forked repository by running the below command in a terminal:

```sh
git clone git@github.com:<username>/bilateral-paper
```

Where you replace `<username>` with your GitHub username. Change your working directory to be inside of that repo via `cd bilateral-paper`.

> [!NOTE]
> If this fails, you might need to configure an `ssh` connection to GitHub.com. There is a very detailed explanation of this in the [GitHub documentation]. Particularily, the guide [how to create and add keypairs]. That documentation is available for all operating systems.

[GitHub documentation]: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/about-ssh
[how to create and add keypairs]: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account

## Software Requirements

Now, some software needs to be installed:

### Quarto

The application that renders the text-based markup format into HTML, LaTeX, DOCX, and whatever else one wants, is called "Quarto" and may be installed from [their homepage]. The homepage also has a nice documentation and can help you set up your preferred way of writing the document. I'd recommend using [VS Code] if you have that installed, or just any plain [text editor] in combination with a browser for the live preview of the document as you write.

Of course it is nice if you use an editor that supports syntax highlighting at least of [Markdown], and ideally of Quarto's specific Markdown extension. As mentioned, [VS Code] is a great choice, but [Sublime Text] is also neat.

You may choose to install a TinyTeX distribution via the Quarto tool to ensure any necessary packages can be installed by Quarto. For this, run:

```sh
quarto install tinytex
```

[their homepage]: https://quarto.org/docs/get-started/
[VS Code]: https://quarto.org/docs/tools/vscode.html
[text editor]: https://quarto.org/docs/tools/text-editors.html
[Sublime Text]: https://www.sublimetext.com/

### Python 3.10

All the figures are created using Python version 3.10. To check your installed Python version, enter this into a terminal:

```sh
python --version
```

If it does not return anything greater or equal to `3.10`, head over to the [Python homepage] and see how you can install it on your system.

> [!TIP]
> I'd highly recommend using a virtual environment using `venv` (or any other virtual environment manager). To create one, enter these commands in your terminal (while inside the `bilateral-paper` repository):
>
> ```sh
> python -m venv .venv
> source .venv/bin/activate
> pip install -U pip
> ```

Then, install the Python packages that are used to create the plots and results from the `requirements.txt` file via this command:

```sh
pip install -r requirements.txt
```

Now your Python environment should be good to go!

> [!WARNING]
> Don't forget to activate the environment each time you want to work on the draft by running:
>
> ```sh
> source .venv/bin/activate
> ```
>
> from within the `bilateral-paper` repository.

[this repo]: https://github.com/rmnldwg/bilateral-paper
[Python homepage]: https://python.org

## Start the Live Preview

If you are working in VS Code, then open the `manuscript.qmd` file (which is the main manuscript of the paper) and click the little "Preview" button on the top right of the windows where the file is open.

When you use a normal text editor, run `quarto preview manuscript.qmd` in your terminal. Running this command should open a browser window where an HTML preview of the document is rendered (ideally with all figures). You can now have your text editor and browser preview window next to each other and see how the preview updates as you type.

## Authoring in Quarto's Markdown-based Syntax

The Quarto website has some [nice explanations and help pages][Markdown basics] on how to author scientific documents with their system. It is really simple and based on [Markdown], which is intended to be easily legible in its source format.

[Markdown basics]: https://quarto.org/docs/authoring/markdown-basics.html
[Markdown]: https://daringfireball.net/projects/markdown/

## Merge your Changes Back into the Original Repository

Finally, you want your work (e.g. edits or new paragraphs) to be reflected in the original repository. They should be *merged* with the edits of the other authors.

To learn how this works, read this great and detailed guide on [how to contribute to open source projects] (because that's essentially what we're doing here).

[how to contribute to open source projects]: https://www.dataschool.io/how-to-contribute-on-github/
