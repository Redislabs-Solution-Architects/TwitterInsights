# Contributor's Guide

## Prerequisites

  + Python 3.6 or 3.7
  + Pip
  + Anaconda 3.7 (recommended)
  + PubNub

## Installation

Download or clone the repository from [GitHub source](https://github.com/danlowen/TwitterInsights), then navigate to the repository from the command-line:

```sh
cd GitHub/TwitterInsights/
```

Create and activate a new virtual environment called something like "twitter-insights-env", as necessary:

```sh
conda create -n twitter-insights-env
conda activate twitter-insights-env
```

Inside the virtual environment, install package dependencies, including Flask:

```sh
pip install 'pubnub>=4.1.6'
```

## Usage

```sh
python ingest.py
```
