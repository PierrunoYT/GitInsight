# GitHub Contribution Tracker

A Python-based tool for analyzing and visualizing your GitHub contributions locally. Track your coding activity, analyze contribution patterns, and gain insights into your development productivity.

## Features

- Local contribution analysis
- Offline performance tracking
- Personal productivity insights
- Contribution visualization
- Historical data storage

## Requirements

- Python 3.8+
- GitHub Personal Access Token

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/github-contribution-tracker.git
cd github-contribution-tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your GitHub credentials:
```
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username
```

## Usage

Run the tracker:
```bash
python github_tracker.py
```

The script will:
1. Fetch your GitHub contribution data
2. Analyze contribution patterns
3. Generate visualizations
4. Save the results in the `data` directory

## Output

The tool generates several files in the `data` directory:
- `contributions_[timestamp].csv`: Raw contribution data
- `analysis_[timestamp].txt`: Analysis results
- `contribution_graph.png`: Visual representation of your contributions

## Data Analysis

The tool provides insights including:
- Total number of contributions
- Types of contributions (commits, pull requests, issues, etc.)
- Active repositories
- Daily contribution averages

## Privacy

All data is stored locally on your machine. No data is sent to external servers beyond the initial GitHub API calls.
