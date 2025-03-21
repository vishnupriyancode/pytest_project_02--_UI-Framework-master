#!/usr/bin/env python3
"""
Command-line interface for the Large-Scale JSON Processing & API Integration solution.
This script provides an easy way to run different components of the system.
"""

import os
import sys
import argparse
import asyncio
import logging
from datetime import datetime

# Configure logging
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up the environment for running the scripts"""
    # Add current directory to path if necessary
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Create necessary directories
    output_dir = os.path.join(current_dir, "output")
    logs_dir = os.path.join(current_dir, "logs")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

async def run_processor(db_export=False, db_type='sqlite', input_dir=None):
    """Run the JSON processor"""
    # Import here to avoid circular imports
    from large_scale_json_processor import JSONProcessor
    
    try:
        # Create processor instance
        processor = JSONProcessor()
        
        # Override input directory if specified
        if input_dir:
            processor.json_files_dir = input_dir
            logger.info(f"Using custom input directory: {input_dir}")
        
        # Process files
        results = await processor.process_json_files()
        
        if db_export:
            # Save results to database
            try:
                from db_storage import get_db_connection
                
                logger.info(f"Saving results to {db_type} database...")
                db = get_db_connection(db_type=db_type)
                db_result = db.save_processing_results(results)
                
                if db_result.get('status') == 'success':
                    logger.info(f"Successfully saved {db_result.get('records_saved', 0)} records to database")
                    
                    # Export database to Excel
                    excel_path = db.export_to_excel()
                    if excel_path:
                        logger.info(f"Exported database to Excel: {excel_path}")
                    else:
                        logger.warning("Failed to export database to Excel")
                else:
                    logger.error(f"Failed to save to database: {db_result.get('error', 'Unknown error')}")
                    
            except ImportError:
                logger.error("Database module not found. Run 'pip install -r requirements.txt' to install dependencies.")
            except Exception as e:
                logger.error(f"Error during database export: {str(e)}")
        
        # Return results for further processing if needed
        return results
        
    except Exception as e:
        logger.error(f"Error in processor: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def generate_test_data():
    """Generate test JSON files"""
    try:
        from generate_large_json import main as generator_main
        generator_main()
    except ImportError:
        logger.error("Generate module not found. Run 'pip install -r requirements.txt' to install dependencies.")
    except Exception as e:
        logger.error(f"Error generating test data: {str(e)}")

async def process_folder(folder_path, edit_id="Edit 1"):
    """Process all JSON files in a specific folder"""
    # Import here to avoid circular imports
    from large_scale_json_processor import JSONProcessor
    
    try:
        # Create processor instance
        processor = JSONProcessor()
        
        # Process folder
        logger.info(f"Processing folder: {folder_path} with Edit ID: {edit_id}")
        result = await processor.process_folder(folder_path, edit_id)
        
        # Save results to Excel
        excel_path = processor.save_results_to_excel()
        if excel_path:
            logger.info(f"Results saved to Excel: {excel_path}")
        
        return result
    except Exception as e:
        logger.error(f"Error processing folder: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'status': 'error',
            'message': f'Failed to process folder {folder_path}',
            'error': str(e)
        }

async def process_edit1_jsons():
    """Process JSONs specifically from the Edit1_jsons folder"""
    # Get the absolute path to Edit1_jsons folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    edit1_jsons_dir = os.path.join(script_dir, "Edit1_jsons")
    
    if not os.path.exists(edit1_jsons_dir):
        logger.error(f"Edit1_jsons directory not found at {edit1_jsons_dir}")
        return []
    
    logger.info(f"Processing JSONs from {edit1_jsons_dir}")
    return await process_folder(edit1_jsons_dir, "Edit 1")

def main():
    """Parse command line arguments and run the appropriate function"""
    parser = argparse.ArgumentParser(
        description='Large-Scale JSON Processing & API Integration',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Define commands as sub-parsers
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate test JSON files')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process JSON files and send to API')
    process_parser.add_argument('--db', action='store_true', help='Save results to database')
    process_parser.add_argument('--db-type', choices=['sqlite', 'postgresql'], default='sqlite',
                             help='Database type (default: sqlite)')
    process_parser.add_argument('--input-dir', type=str, help='Custom input directory for JSON files')
    
    # Process folder command
    folder_parser = subparsers.add_parser('process-folder', help='Process all JSON files in a folder')
    folder_parser.add_argument('--folder-path', type=str, required=True, help='Path to folder containing JSON files')
    folder_parser.add_argument('--edit-id', type=str, default='Edit 1', help='Edit ID to apply (default: Edit 1)')
    
    # Process Edit1_jsons command
    edit1_parser = subparsers.add_parser('process-edit1', help='Process JSON files from Edit1_jsons folder')
    
    # Process with database export command
    db_parser = subparsers.add_parser('db-export', help='Process and save results to database')
    db_parser.add_argument('--type', choices=['sqlite', 'postgresql'], default='sqlite',
                         help='Database type (default: sqlite)')
    
    # All-in-one command
    all_parser = subparsers.add_parser('all', help='Generate test data, process files, and save to database')
    all_parser.add_argument('--db-type', choices=['sqlite', 'postgresql'], default='sqlite',
                         help='Database type (default: sqlite)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up environment
    setup_environment()
    
    # Execute command
    if args.command == 'generate':
        generate_test_data()
    elif args.command == 'process':
        asyncio.run(run_processor(
            db_export=args.db, 
            db_type=args.db_type,
            input_dir=args.input_dir
        ))
    elif args.command == 'process-folder':
        asyncio.run(process_folder(args.folder_path, args.edit_id))
    elif args.command == 'process-edit1':
        asyncio.run(process_edit1_jsons())
    elif args.command == 'db-export':
        asyncio.run(run_processor(db_export=True, db_type=args.type))
    elif args.command == 'all':
        generate_test_data()
        asyncio.run(run_processor(db_export=True, db_type=args.db_type))
    else:
        # If no command is provided, show help
        parser.print_help()

if __name__ == "__main__":
    main() 