from db_utility import PostgresDB

def analyze_database(save_to_file=False):
    """
    Connect to PostgreSQL database, analyze structure and save results to file
    """
    # Connect to database
    db = PostgresDB()
    db.connect()
    
    results = []
    
    # Get all tables in the database (excluding system tables)
    tables_query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name;
    """
    
    tables = db.execute_query(tables_query)
    
    if not tables:
        results.append("No tables found in the database.")
    else:
        results.append(f"Found {len(tables)} tables in the database:")
        results.append("=" * 50)
        
        # For each table, get its columns
        for table_row in tables:
            table_name = table_row[0]
            results.append(f"\nTABLE: {table_name}")
            results.append("-" * 50)
            
            # Get column information
            columns_query = """
            SELECT column_name, data_type, character_maximum_length, 
                   column_default, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position;
            """
            
            columns = db.execute_query(columns_query, [table_name])
            
            if columns:
                # Column headers
                results.append(f"{'Column Name':<20} {'Data Type':<25} {'Nullable':<10} {'Default':<20}")
                results.append(f"{'-'*20:<20} {'-'*25:<25} {'-'*10:<10} {'-'*20:<20}")
                
                for col in columns:
                    col_name = col[0]
                    data_type = col[1]
                    
                    # Add length for character types
                    if col[2]:
                        data_type += f"({col[2]})"
                        
                    is_nullable = "YES" if col[4] == "YES" else "NO"
                    default_val = col[3] if col[3] else "NULL"
                    
                    results.append(f"{col_name:<20} {data_type:<25} {is_nullable:<10} {default_val:<20}")
            
            # Get primary key information
            pk_query = """
            SELECT c.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name)
            JOIN information_schema.columns AS c ON c.table_schema = tc.constraint_schema
                AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
            WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_name = %s;
            """
            
            pk_columns = db.execute_query(pk_query, [table_name])
            
            if pk_columns:
                pk_cols = ", ".join([pk[0] for pk in pk_columns])
                results.append(f"\nPrimary Key: {pk_cols}")
            
            # Get foreign key information
            fk_query = """
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = %s;
            """
            
            fk_columns = db.execute_query(fk_query, [table_name])
            
            if fk_columns:
                results.append("\nForeign Keys:")
                for fk in fk_columns:
                    results.append(f"  {fk[0]} -> {fk[1]}.{fk[2]}")
            
            # Table row count (approximate)
            count_query = f"SELECT COUNT(*) FROM {table_name};"
            count_result = db.execute_query(count_query)
            
            if count_result:
                results.append(f"\nRow Count: {count_result[0][0]}")
    
    # Close the database connection
    db.close()
    
    txt_results = "\n".join(results)
    if save_to_file:
        with open("cache/db_analysis.txt", "w") as f:
            f.write(txt_results)
        print(f"Database analysis has been saved to cache/db_analysis.txt")
    return txt_results

if __name__ == "__main__":
    analyze_database() 