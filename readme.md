# Rec-Arch

## Install

```bash
conda create -n rec-arch python=3.12
conda activate rec-arch
pip install -r requirements.txt
```

Also, add a file named `.env` in the root directory of the project with the following content:

```env
OPENAI_API_KEY="your-openai-api-key"
```

Put the dataset in the `database` directory. The dataset should be in the following format:


## Usage

To start the Rec-Arch program with user interface, run the following command:

```bash
python main.py
```

If you want to use the program in terminal, you can use the following commands:

```bash
python query.py --query "minimalism form" --database "path/to/dataset"
```

If you want to build the database on a new dataset, you can use the following command:

```bash
python build.py --path "path/to/dataset"
```