# bokete_crawl

Boketeのクローリング

# Usage

## Activation

In project dir, run the following commands.

### Poetry

```
$ poetry lock
$ poetry install --no-dev
$ poetry shell
```

### pip

```
$ pip install .
```

## crawling and scraping

$ scrapy crawl odai -o foo.jl --logfile=bar.txt