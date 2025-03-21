import os
import sys
import logging
from src.workflow import JsonProcessingWorkflow, run_workflow

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/main.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filemode='a'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the application."""
    try:
        logger.info("Starting JSON processing workflow")
        
        # Create a custom workflow with the local json_files directory
        workflow = JsonProcessingWorkflow(json_dir="json_files")
        
        # Start the API service
        workflow.start_api_service()
        
        # Process all JSON files
        output_file = workflow.process_json_files()
        
        if output_file:
            logger.info(f"Workflow completed successfully. Results in: {output_file}")
            return 0
        else:
            logger.error("Workflow failed")
            return 1
    
    except Exception as e:
        logger.error(f"Unhandled exception in main: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())