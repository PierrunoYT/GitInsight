import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dotenv import load_dotenv

class GitHubContributionTracker:
    def __init__(self):
        load_dotenv()
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.username = os.getenv('GITHUB_USERNAME')
        self.headers = {'Authorization': f'token {self.github_token}'} if self.github_token else {}
        self.data_dir = 'data'
        self.ensure_data_directory()

    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def fetch_contributions(self, days=365):
        """Fetch contribution data from GitHub"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # GitHub API endpoint for user events
        url = f'https://api.github.com/users/{self.username}/events'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: {response.status_code}")
        
        events = response.json()
        
        # Process events into contribution data
        contributions = []
        for event in events:
            event_date = datetime.strptime(event['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            if start_date <= event_date <= end_date:
                contributions.append({
                    'date': event_date.date(),
                    'type': event['type'],
                    'repo': event['repo']['name']
                })
        
        return pd.DataFrame(contributions)

    def analyze_contributions(self, df):
        """Analyze contribution patterns"""
        analysis = {
            'total_contributions': len(df),
            'contribution_types': df['type'].value_counts().to_dict(),
            'active_repositories': df['repo'].nunique(),
            'daily_average': len(df) / df['date'].nunique() if not df.empty else 0
        }
        return analysis

    def visualize_contributions(self, df, save_path=None):
        """Create visualization of contribution patterns"""
        plt.figure(figsize=(12, 6))
        
        # Daily contribution count
        daily_counts = df.groupby('date').size()
        daily_counts.plot(kind='bar', alpha=0.7)
        
        plt.title('GitHub Contributions Over Time')
        plt.xlabel('Date')
        plt.ylabel('Number of Contributions')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()

    def save_data(self, df, analysis):
        """Save contribution data and analysis"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save raw data
        df.to_csv(f'{self.data_dir}/contributions_{timestamp}.csv', index=False)
        
        # Save analysis
        with open(f'{self.data_dir}/analysis_{timestamp}.txt', 'w') as f:
            for key, value in analysis.items():
                f.write(f'{key}: {value}\n')

def main():
    tracker = GitHubContributionTracker()
    
    try:
        # Fetch and process contributions
        contributions_df = tracker.fetch_contributions()
        
        # Analyze data
        analysis_results = tracker.analyze_contributions(contributions_df)
        
        # Visualize
        tracker.visualize_contributions(
            contributions_df,
            save_path=f'{tracker.data_dir}/contribution_graph.png'
        )
        
        # Save results
        tracker.save_data(contributions_df, analysis_results)
        
        print("Contribution analysis completed successfully!")
        print("\nSummary:")
        for key, value in analysis_results.items():
            print(f"{key}: {value}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
