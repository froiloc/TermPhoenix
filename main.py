# main.py - Enhanced project handling
def main():
    parser = argparse.ArgumentParser(description='TermPhoenix')
    parser.add_argument('--project-name', required=True)
    parser.add_argument('--url', required=True)
    parser.add_argument('--recreate-if-exists', action='store_true')
    
    args = parser.parse_args()
    
    db_manager = DatabaseManager(f"projects/{args.project_name}.db", args.project_name)
    
    if db_manager.db_path.exists() and not args.recreate_if_exists:
        # Continue existing project
        conn = sqlite3.connect(db_manager.db_path)
        print(f"📁 Continuing existing project: {args.project_name}")
    else:
        # Create new project
        conn = db_manager.initialize_project(args.recreate_if_exists)
        print(f"🆕 Created new project: {args.project_name}")
