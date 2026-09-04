def analyze_growth_trends(subscriber_data):
    """
    Analyzes trends in subscriber growth based on historical data.
    
    Args:
        subscriber_data (list): A list of subscriber counts over time.
        
    Returns:
        dict: A dictionary containing growth trends and future milestone estimates.
    """
    trends = {}
    
    if len(subscriber_data) < 2:
        return {"error": "Not enough data to analyze trends."}
    
    daily_changes = [subscriber_data[i] - subscriber_data[i - 1] for i in range(1, len(subscriber_data))]
    trends['average_daily_growth'] = sum(daily_changes) / len(daily_changes)
    
    trends['total_growth'] = subscriber_data[-1] - subscriber_data[0]
    
    # Estimate future milestones
    current_count = subscriber_data[-1]
    milestones = [1000, 5000, 10000, 50000, 100000]
    trends['estimated_milestones'] = {milestone: (milestone - current_count) / trends['average_daily_growth'] if trends['average_daily_growth'] > 0 else float('inf') for milestone in milestones if milestone > current_count}
    
    return trends

def generate_growth_report(trends):
    """
    Generates a report based on the analyzed trends.
    
    Args:
        trends (dict): A dictionary containing growth trends and estimates.
        
    Returns:
        str: A formatted report string.
    """
    report = "Subscriber Growth Trends Report\n"
    report += "===============================\n"
    
    if 'error' in trends:
        report += trends['error']
    else:
        report += f"Average Daily Growth: {trends['average_daily_growth']:.2f} subscribers\n"
        report += f"Total Growth: {trends['total_growth']} subscribers\n"
        report += "Estimated Time to Reach Milestones:\n"
        
        for milestone, days in trends['estimated_milestones'].items():
            report += f" - {milestone} subscribers: {days:.1f} days\n"
    
    return report 