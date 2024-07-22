# Probabilistic Model of Bilateral Lymphatic Spread in Head and Neck Cancer

This repository contains the data, the code, and the manuscript of our (next upcoming) publication on modelling lymphatic tumor progression in head and neck squamous cell carcinomas.

## Viewing the Document

I usually try to push the latest changes to the [GitHub pages of the repository](https://rmnldwg.github.io/bilateral-paper). So, without cloning the repository, you can read a mostly up-to-date version of the draft there.

## Build and Reproduce Locally

To compute results and render the manuscript locally, clone the repository and `cd` into it.

```sh
git clone https://github.com/rmnldwg/bilateral-paper
cd bilateral-paper
```

## Software Requirements

The paper is written using [Quarto], a tool that lets you write in a flavour of [Markdown], which can the be rendered and exported into a wide range of output formats, including LaTeX (and PDF from that), HTML, DOCX, and so on.

### Installing Quarto

Quarto may be installed from [here][Quarto]. Their homepage also has a nice documentation and can help you set up your preferred way of writing the document. I'd recommend using [VS Code] if you have that installed, or just any plain [text editor] in combination with a browser for the live preview of the document as you write.

Of course it is nice if you use an editor that supports syntax highlighting at least of [Markdown], and ideally of Quarto's specific Markdown extension. As mentioned, [VS Code] is a great choice, but [Sublime Text] is also neat.

You may choose to install a TinyTeX distribution via the Quarto tool to ensure any necessary packages can be installed by Quarto. For this, run:

```sh
quarto install tinytex
```

[Quarto]: https://quarto.org/docs/get-started/
[VS Code]: https://quarto.org/docs/tools/vscode.html
[text editor]: https://quarto.org/docs/tools/text-editors.html
[Sublime Text]: https://www.sublimetext.com/

### Python 3.10

Since all the figures are created using Python version 3.10 - either via dedicated scripts or Python code embedded in the Quarto document - that should be present on your system as well. To check your installed Python version, enter this into a terminal:

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

[Python homepage]: https://python.org

## Fetch the Data

All patient data tables we have used in this work are made publicly available by us. For example, you can interactively explore the data on [LyProX], a web-based dashboard we created to motivate fellow researchers to share their data with us.

But for this paper, you can automatically fetch the data in CSV format by running the following command:

```sh
dvc update -R data
```

This instructs the [DVC] tool to fetch the data from the GitHub repository [lydata], where we store these datasets

[lydata]: https://github.com/rmnldwg/lydata

## Reproduce the Computations

The sampling of the models may take quite a while and is orchestrated by the tool [DVC]. There is not really a need to rerun these computations as all results are stored in an Azure blob storage container. To fetch them, run

But if you want to reproduce this part, too, then go ahead and run

```sh
dvc pull -r azure
```

But if you want to rerun the full, lengthy computations as well, then simply do this:

```sh
dvc repro
```

Regardless of what you do, you should now have some `.hdf5` files in the `models` directory (or rather in its subdirectories). These contain the drawn samples and computed risks and prevalences.

[DVC]: https://dvc.org

## Start the Live Preview

To start a preview at the local address <localhost:8000>, simply run this command:

```sh
quarto preview
```

And now you should be able to read the beautifully displayed HTML version of our paper in you browser. For a LaTeX/PDF output, run this:

```sh
quarto render --to pdf
```
