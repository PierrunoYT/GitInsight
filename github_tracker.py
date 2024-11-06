import os
import logging
from typing import Dict, List, Optional
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GitHubContributionTracker:
    def __init__(self):
        """Initialize the GitHub Contribution Tracker with environment variables and setup."""
        load_dotenv()
        self._validate_env_vars()
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.username = os.getenv('GITHUB_USERNAME')
        self.headers = {'Authorization': f'token {self.github_token}'} if self.github_token else {}
        self.data_dir = 'data'
        self.ensure_data_directory()

    def _validate_env_vars(self) -> None:
        """Validate required environment variables are set."""
        required_vars = ['GITHUB_TOKEN', 'GITHUB_USERNAME']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    def ensure_data_directory(self) -> None:
        """Create data directory if it doesn't exist."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Created data directory: {self.data_dir}")

    def fetch_contributions(self, days: int = 365) -> pd.DataFrame:
        """
        Fetch contribution data from GitHub with pagination support.
        
        Args:
            days (int): Number of days of history to fetch (default: 365)
            
        Returns:
            pd.DataFrame: DataFrame containing contribution data
            
        Raises:
            ValueError: If days is not a positive integer
            requests.RequestException: If API request fails
        """
        if not isinstance(days, int) or days <= 0:
            raise ValueError("Days must be a positive integer")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        url = f'https://api.github.com/users/{self.username}/events'
        contributions = []
        page = 1

        while True:
            try:
                response = requests.get(
                    f"{url}?page={page}",
                    headers=self.headers,
                    timeout=10
                )
                response.raise_for_status()
                
                # Check rate limits
                remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
                if remaining == 0:
                    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                    wait_time = reset_time - datetime.now().timestamp()
                    if wait_time > 0:
                        logger.warning(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
                        break

                events = response.json()
                if not events:  # No more events
                    break

                for event in events:
                    event_date = datetime.strptime(event['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                    if event_date < start_date:
                        return pd.DataFrame(contributions)
                    if event_date <= end_date:
                        contributions.append({
                            'date': event_date.date(),
                            'type': event['type'],
                            'repo': event['repo']['name']
                        })

                page += 1
                
            except requests.RequestException as e:
                logger.error(f"Failed to fetch data: {str(e)}")
                raise

        return pd.DataFrame(contributions)

    def analyze_contributions(self, df: pd.DataFrame) -> Dict:
        """
        Analyze contribution patterns.
        
        Args:
            df (pd.DataFrame): DataFrame containing contribution data
            
        Returns:
            Dict: Analysis results
        """
        if df.empty:
            logger.warning("No contributions found in the specified time period")
            return {
                'total_contributions': 0,
                'contribution_types': {},
                'active_repositories': 0,
                'daily_average': 0
            }

        analysis = {
            'total_contributions': len(df),
            'contribution_types': df['type'].value_counts().to_dict(),
            'active_repositories': df['repo'].nunique(),
            'daily_average': len(df) / df['date'].nunique()
        }
        return analysis

    def visualize_contributions(
        self,
        df: pd.DataFrame,
        save_path: Optional[str] = None,
        figsize: tuple = (12, 6)
    ) -> None:
        """
        Create visualization of contribution patterns.
        
        Args:
            df (pd.DataFrame): DataFrame containing contribution data
            save_path (str, optional): Path to save the visualization
            figsize (tuple): Figure size (width, height)
        """
        if df.empty:
            logger.warning("No data to visualize")
            return

        plt.figure(figsize=figsize)
        
        daily_counts = df.groupby('date').size()
        daily_counts.plot(kind='bar', alpha=0.7)
        
        plt.title('GitHub Contributions Over Time')
        plt.xlabel('Date')
        plt.ylabel('Number of Contributions')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Saved visualization to {save_path}")
        else:
            plt.show()
        plt.close()

    def save_data(self, df: pd.DataFrame, analysis: Dict) -> None:
        """
        Save contribution data and analysis.
        
        Args:
            df (pd.DataFrame): DataFrame containing contribution data
            analysis (Dict): Analysis results
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save raw data
        data_path = f'{self.data_dir}/contributions_{timestamp}.csv'
        df.to_csv(data_path, index=False)
        logger.info(f"Saved contribution data to {data_path}")
        
        # Save analysis
        analysis_path = f'{self.data_dir}/analysis_{timestamp}.txt'
        with open(analysis_path, 'w') as f:
            for key, value in analysis.items():
                f.write(f'{key}: {value}\n')
        logger.info(f"Saved analysis to {analysis_path}")

def main() -> None:
    """
    Main function to run the GitHub contribution tracking process.
    Fetches, analyzes, visualizes, and saves GitHub contribution data.
    """
    tracker = GitHubContributionTracker()
    
    try:
        logger.info("Fetching GitHub contributions...")
        contributions_df = tracker.fetch_contributions()
        
        logger.info("Analyzing contribution data...")
        analysis_results = tracker.analyze_contributions(contributions_df)
        
        logger.info("Creating visualization...")
        tracker.visualize_contributions(
            contributions_df,
            save_path=f'{tracker.data_dir}/contribution_graph.png'
        )
        
        logger.info("Saving results...")
        tracker.save_data(contributions_df, analysis_results)
        
        logger.info("Contribution analysis completed successfully!")
        print("\nSummary:")
        for key, value in analysis_results.items():
            print(f"{key}: {value}")
            
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
